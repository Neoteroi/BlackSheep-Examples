from datetime import datetime
from typing import List

from blacksheep import WebSocket
from .message import Message


class Connection:
    def __init__(self, socket: WebSocket, client_id: str):
        self.socket = socket
        self.client_id = client_id

    async def receive(self) -> Message:
        data = await self.socket.receive_json()
        message = Message(**data)
        return message

    async def send(self, message: Message):
        await self.socket.send_json(message.asdict())


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[Connection] = []

    async def connect(self, websocket: WebSocket, client_id: str) -> Connection:
        await websocket.accept()
        connection = Connection(websocket, client_id)
        await self.greet(connection)
        self.active_connections.append(connection)
        return connection

    async def disconnect(self, connection: Connection):
        self.active_connections.remove(connection)
        await self.bye(connection)

    async def manage(self, connection: Connection):
        message = await connection.receive()
        await self.broadcast(message)

    async def broadcast(self, message: Message):
        print('Broadcast to %s connections' % len(self.active_connections))
        for connection in self.active_connections:
            await connection.send(message)

    async def greet(self, connection: Connection):
        message = Message(
            author='Server',
            timestamp=datetime.now().isoformat(),
            text=f'{connection.client_id} enters the chat',
        )
        await self.broadcast(message)

    async def bye(self, connection: Connection):
        message = Message(
            author='Server',
            timestamp=datetime.now().isoformat(),
            text=f'{connection.client_id} disconnected',
        )
        await self.broadcast(message)
