import asyncio
from typing import Optional
from crypto.kdf import derive_room_key
from crypto.encrypt import fernet_from_key, encrypt, decrypt
from protocol.messages import encode, decode
from client.ui import input_loop, ColoredUI


class ChatClient: #client side
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.fernet = None
        self.ui = ColoredUI()
        self.is_connected = False
    
    async def connect(self) -> bool:
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        except ConnectionRefusedError:
            self.ui.print_error(f"Could not connect to {self.host}:{self.port}")
            return False
        except Exception as e:
            self.ui.print_error(f"Connection failed: {e}")
            return False
        
        try:
            self.writer.write(encode({"type": "auth", "password": self.password}))
            await self.writer.drain()
        except Exception as e:
            self.ui.print_error(f"Authentication send failed: {e}")
            return False
        
        try:
            line = await asyncio.wait_for(self.reader.readline(), timeout=5.0)
        except asyncio.TimeoutError:
            self.ui.print_error("Server did not respond in time")
            return False
        
        if not line:
            self.ui.print_error("Server closed connection")
            return False
        
        try:
            msg = decode(line)
        except Exception as e:
            self.ui.print_error(f"Invalid server response: {e}")
            return False
        
        if msg.get("type") == "error":
            self.ui.print_error(msg.get("message", "Authentication failed"))
            await self.close()
            return False
        
        if msg.get("type") != "init":
            self.ui.print_error("Unexpected server response")
            await self.close()
            return False
        
        try:
            room_salt = bytes.fromhex(msg["room_salt"])
            room_key = derive_room_key(self.password, room_salt)
            self.fernet = fernet_from_key(room_key)
        except Exception as e:
            self.ui.print_error(f"Encryption setup failed: {e}")
            await self.close()
            return False
        
        self.is_connected = True
        self.ui.print_success(f"Connected to secure room as '{self.username}'")
        
        return True
    
    async def send_message(self, text: str):
        if not self.is_connected or not self.writer:
            return
        
        try:
            encrypted_text = encrypt(self.fernet, text)
            msg = {"type": "message", "user": self.username, "text": encrypted_text}
            self.writer.write(encode(msg))
            await self.writer.drain()
        except Exception as e:
            self.ui.print_error(f"Failed to send message: {e}")
    
    async def close(self):
        await self.send_message(f"[{self.username} left the room]")
        self.is_connected = False
        
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception:
                pass
        
        self.ui.print_info("You left the room.")
    
    async def receive_messages(self):
        try:
            while self.is_connected and self.reader:
                line = await self.reader.readline()
                
                if not line:
                    self.ui.print_system("Server closed connection", reprint_prompt=True, prompt_username=self.username)
                    break
                
                try:
                    msg = decode(line)
                except Exception as e:
                    self.ui.print_error(f"Failed to decode message: {e}")
                    continue
                
                if msg["type"] == "message":
                    try:
                        text = decrypt(self.fernet, msg["text"])
                        sender = msg["user"]
                        
                        if sender != self.username: #não mostra a propria mensagem, pra não duplicar...
                            self.ui.print_message(sender, text, reprint_prompt=True, prompt_username=self.username)
                        
                    except Exception as e:
                        self.ui.print_error(f"Failed to decrypt message: {e}")
                
                elif msg["type"] == "system":
                    self.ui.print_system(msg["text"], reprint_prompt=True, prompt_username=self.username)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            if self.is_connected:
                self.ui.print_error(f"Receive error: {e}")
    
    async def run(self):
        if not await self.connect():
            return
        
        await self.send_message(f"[{self.username} joined the room]")
        
        try:
            await asyncio.gather(
                input_loop(self.send_message, self.close, self.ui, self.username),
                self.receive_messages()
            )
        except Exception as e:
            self.ui.print_error(f"Client error: {e}")
        finally:
            await self.close()


async def start_client(host: str, port: int, username: str, password: str):
    client = ChatClient(host, port, username, password)
    await client.run()