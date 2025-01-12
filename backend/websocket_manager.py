from typing import Dict, List, Set
from fastapi import WebSocket, status
import models
import schemas

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[WebSocket, int] = {}
        self.user_connections: Dict[int, List[WebSocket]] = {}
        self.user_channels: Dict[int, Set[int]] = {}
        self.total_connections = 0

    async def connect(self, websocket: WebSocket, user_id: int, channels: list[int], max_connections_per_user: int, max_total_connections: int):
        if self.total_connections >= max_total_connections:
            await websocket.close(code=status.WS_1013_TRY_AGAIN_LATER)
            return False

        if user_id in self.user_connections and len(self.user_connections[user_id]) >= max_connections_per_user:
            await websocket.close(code=status.WS_1013_TRY_AGAIN_LATER)
            return False

        await websocket.accept()
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        
        self.user_connections[user_id].append(websocket)
        self.user_channels[user_id] = set(channels)
        self.total_connections += 1
        return True

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
                self.total_connections -= 1
                
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
                    del self.user_channels[user_id]

    def add_channel_for_user(self, user_id: int, channel_id: int):
        if user_id in self.user_channels:
            self.user_channels[user_id].add(channel_id)

    async def broadcast_to_channel(self, message: dict, channel_id: int):
        disconnected_websockets = []
        for user_id, channels in self.user_channels.items():
            if channel_id in channels:
                if user_id in self.user_connections:
                    for websocket in self.user_connections[user_id]:
                        try:
                            await websocket.send_json(message)
                        except RuntimeError:
                            disconnected_websockets.append((websocket, user_id))
        
        for websocket, user_id in disconnected_websockets:
            self.disconnect(websocket, user_id)

    async def broadcast_member_joined(self, channel_id: int, user: schemas.User):
        message = {
            "type": "member_joined",
            "channel_id": channel_id,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "picture": user.picture
            }
        }
        await self.broadcast_to_channel(message, channel_id)

    async def broadcast_member_left(self, channel_id: int, user_id: int):
        message = {
            "type": "member_left",
            "channel_id": channel_id,
            "user_id": user_id
        }
        await self.broadcast_to_channel(message, channel_id)

    async def broadcast_role_updated(self, channel_id: int, user_id: int, role: str):
        message = {
            "type": "role_updated",
            "channel_id": channel_id,
            "user_id": user_id,
            "role": role
        }
        await self.broadcast_to_channel(message, channel_id)

    async def broadcast_privacy_updated(self, channel_id: int, is_private: bool):
        message = {
            "type": "privacy_updated",
            "channel_id": channel_id,
            "is_private": is_private
        }
        await self.broadcast_to_channel(message, channel_id)

    async def broadcast_channel_created(self, channel: models.Channel):
        """Broadcast channel creation event to all members of the channel."""
        message = {
            "type": "channel_created",
            "channel": {
                "id": channel.id,
                "name": channel.name,
                "description": channel.description,
                "owner_id": channel.owner_id,
                "created_at": channel.created_at.isoformat(),
                "is_private": channel.is_private,
                "is_dm": channel.is_dm,
                "users": [
                    {
                        "id": user.id,
                        "email": user.email,
                        "name": user.name,
                        "picture": user.picture
                    } for user in channel.users
                ]
            }
        }
        await self.broadcast_to_channel(message, channel.id)

    async def broadcast_file_upload(self, channel_id: int, file_upload: models.FileUpload, message: models.Message):
        """Broadcast file upload event to channel members"""
        message_data = {
            "type": "file_upload",
            "channel_id": channel_id,
            "file": {
                "id": file_upload.id,
                "message_id": file_upload.message_id,
                "file_name": file_upload.file_name,
                "content_type": file_upload.content_type,
                "file_size": file_upload.file_size,
                "uploaded_at": file_upload.uploaded_at.isoformat(),
                "uploaded_by": file_upload.uploaded_by
            },
            "message": {
                "id": message.id,
                "content": message.content,
                "user_id": message.user_id,
                "channel_id": message.channel_id,
                "created_at": message.created_at.isoformat()
            }
        }
        await self.broadcast_to_channel(message_data, channel_id)

    async def broadcast_file_deleted(self, channel_id: int, file_id: int, message_id: int):
        """Broadcast file deletion event to channel members"""
        message_data = {
            "type": "file_deleted",
            "channel_id": channel_id,
            "file_id": file_id,
            "message_id": message_id
        }
        await self.broadcast_to_channel(message_data, channel_id)

# Create a single instance of the manager
manager = ConnectionManager() 