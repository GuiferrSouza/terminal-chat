import asyncio
from typing import Set
from asyncio import StreamWriter

class ServerState:
    def __init__(self, password: str):
        self.password = password
        self.clients: Set[StreamWriter] = set()
        self._lock = asyncio.Lock()
    
    async def join(self, writer: StreamWriter) -> int:
        async with self._lock:
            self.clients.add(writer)
            return len(self.clients)
    
    async def leave(self, writer: StreamWriter) -> int:
        async with self._lock:
            self.clients.discard(writer)
            return len(self.clients)
    
    async def broadcast(self, data: bytes, exclude: StreamWriter = None) -> int:
        async with self._lock:
            clients_snapshot = list(self.clients)
        
        successful = 0
        failed_clients = []
        
        for client in clients_snapshot:
            if exclude and client == exclude:
                continue
            
            try:
                client.write(data)
                await client.drain()
                successful += 1
            except Exception:
                failed_clients.append(client)
        
        if failed_clients:
            async with self._lock:
                for client in failed_clients:
                    self.clients.discard(client)
                    try:
                        client.close()
                    except Exception:
                        pass
        
        return successful
    
    async def get_client_count(self) -> int:
        async with self._lock:
            return len(self.clients)
    
    def verify_password(self, password: str) -> bool:
        return password == self.password