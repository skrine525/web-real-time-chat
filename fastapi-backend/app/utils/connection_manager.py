import json
from fastapi import WebSocket


# Класс для управления веб-сокетами
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, username: str, websocket: WebSocket):
        self.active_connections[username] = websocket

    def disconnect(self, username: str):
        del self.active_connections[username]

    async def send_message_to_receiver(self, event_text: dict):
        event = json.loads(event_text)
        
        try:
            receiver_websocket = self.active_connections[event["receiver"]]
            await receiver_websocket.send_text(event_text)
        except KeyError:
            pass
        
        