import asyncio
import os
import logging
from protocol.messages import encode, decode, create_error_message, create_init_message
from server.state import ServerState

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

class ChatServer:
    def __init__(self, password: str):
        self.state = ServerState(password)
        self.room_salt = os.urandom(16)
        logger.info("Server initialized with new room salt")
    
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        client_addr = writer.get_extra_info('peername')
        logger.info(f"New connection from {client_addr}")
        
        try:
            try:
                line = await asyncio.wait_for(reader.readline(), timeout=10.0)
            except asyncio.TimeoutError:
                logger.warning(f"Authentication timeout from {client_addr}")
                writer.close()
                return
            
            if not line:
                logger.warning(f"Client {client_addr} closed connection before auth")
                writer.close()
                return
            
            try:
                msg = decode(line)
            except Exception as e:
                logger.error(f"Failed to decode auth from {client_addr}: {e}")
                writer.close()
                return
            
            if msg.get("type") != "auth":
                logger.warning(f"Invalid message type from {client_addr}: {msg.get('type')}")
                writer.close()
                return
            
            if not self.state.verify_password(msg.get("password", "")):
                logger.warning(f"Authentication failed from {client_addr}")
                writer.write(encode(create_error_message("authentication failed")))
                await writer.drain()
                writer.close()
                return
            
            writer.write(encode(create_init_message(self.room_salt.hex())))
            await writer.drain()
            
            client_count = await self.state.join(writer)
            logger.info(f"Client {client_addr} authenticated. Total clients: {client_count}")
            
            while True:
                line = await reader.readline()
                
                if not line:
                    logger.info(f"Client {client_addr} disconnected")
                    break
                
                try:
                    msg = decode(line)
                    await self.state.broadcast(encode(msg))
                    
                except Exception as e:
                    logger.error(f"Error processing message from {client_addr}: {e}")
                    continue
        
        except asyncio.CancelledError:
            logger.info(f"Client {client_addr} handler cancelled")
            raise
        
        except Exception as e:
            logger.error(f"Unexpected error handling client {client_addr}: {e}")
        
        finally:
            client_count = await self.state.leave(writer)
            logger.info(f"Client {client_addr} removed. Remaining clients: {client_count}")
            
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass


async def start_server(host: str, port: int, password: str):
    server_instance = ChatServer(password)
    
    try:
        server = await asyncio.start_server(server_instance.handle_client, host, port)
        
        addr = server.sockets[0].getsockname()
        logger.info(f"Server listening on {addr[0]}:{addr[1]}")
        print(f"\n{'='*50}")
        print(f"Chat Server Started")
        print(f"{'='*50}")
        print(f"Address: {addr[0]}:{addr[1]}")
        print(f"Password protection: Enabled")
        print(f"{'='*50}\n")
        print("Press Ctrl+C to stop the server\n")
        
        async with server:
            await server.serve_forever()
    
    except OSError as e:
        if e.errno == 98: #em uso
            logger.error(f"Port {port} is already in use")
            print(f"\nError: Port {port} is already in use.")
            print("Please choose a different port or stop the other process.\n")
        else:
            logger.error(f"Failed to start server: {e}")
            print(f"\nError starting server: {e}\n")
    
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        print("\nShutting down server...")
    
    except Exception as e:
        logger.error(f"Unexpected server error: {e}", exc_info=True)
        print(f"\nServer error: {e}\n")