from typing import Dict, List, Set, Literal
from fastapi import WebSocket, status
from datetime import datetime, timedelta
from . import models
from . import schemas
from .database import SessionLocal
from .ai_service import generate_user_persona_profile
import asyncio
import logging

# Configure logging
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

# Define possible user statuses
UserStatus = Literal["online", "away", "offline"]

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[WebSocket, int] = {}
        self.user_connections: Dict[int, List[WebSocket]] = {}
        self.user_channels: Dict[int, Set[int]] = {}
        self.total_connections = 0
        # Add status tracking
        self.user_statuses: Dict[int, UserStatus] = {}
        self.last_activity: Dict[int, datetime] = {}
        # Status timeouts
        self.AWAY_TIMEOUT = timedelta(seconds=5)  # setting to 30 seconds for testing
        # self.AWAY_TIMEOUT = timedelta(minutes=5)  # Mark as away after 5 minutes of inactivity
        self.CHECK_INTERVAL = 5  # Check every 30 seconds

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
        
        # Set initial status
        self.user_statuses[user_id] = "online"
        self.last_activity[user_id] = datetime.now()
        
        # Broadcast status change
        await self.broadcast_status_change(user_id, "online")
        return True

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
                self.total_connections -= 1
                
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
                    del self.user_channels[user_id]
                    # Clean up status tracking
                    if user_id in self.user_statuses:
                        del self.user_statuses[user_id]
                    if user_id in self.last_activity:
                        del self.last_activity[user_id]
                    # Broadcast offline status
                    asyncio.create_task(self.broadcast_status_change(user_id, "offline"))
                    # Generate user profile in background
                    asyncio.create_task(self._generate_profile_on_disconnect(user_id))

    async def _generate_profile_on_disconnect(self, user_id: int):
        """Generate user profile in background after disconnect"""
        try:
            
            db = SessionLocal()
            try:
                await asyncio.to_thread(generate_user_persona_profile, db, user_id)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error generating profile for user {user_id}: {e}")

    async def update_user_activity(self, user_id: int):
        """Update the last activity timestamp for a user"""
        if user_id in self.user_connections:
            logger.debug(f"Updating activity for user {user_id}")
            self.last_activity[user_id] = datetime.now()
            # If user was away, set them back to online
            if self.user_statuses.get(user_id) == "away":
                logger.info(f"Setting user {user_id} back to online")
                self.user_statuses[user_id] = "online"
                await self.broadcast_status_change(user_id, "online")
                logger.info(f"User {user_id} status broadcast complete")

    async def check_away_status(self, user_id: int):
        """Check if specific user should be marked as away due to inactivity"""
        if user_id in self.last_activity and user_id in self.user_statuses:
            current_time = datetime.now()
            time_since_activity = current_time - self.last_activity[user_id]
            logger.debug(f"Checking away status for user {user_id}:")
            logger.debug(f"Time since activity: {time_since_activity}")
            logger.debug(f"Current status: {self.user_statuses[user_id]}")
            logger.debug(f"AWAY_TIMEOUT: {self.AWAY_TIMEOUT}")
            
            if time_since_activity >= self.AWAY_TIMEOUT and self.user_statuses[user_id] == "online":
                logger.info(f"Setting user {user_id} to away status")
                self.user_statuses[user_id] = "away"
                await self.broadcast_status_change(user_id, "away")
                logger.info(f"User {user_id} status broadcast complete")

    def is_user_connected(self, user_id: int) -> bool:
        """Check if a user is still connected"""
        return user_id in self.user_connections and len(self.user_connections[user_id]) > 0

    def get_user_status(self, user_id: int) -> UserStatus:
        """Get the current status of a user"""
        if user_id not in self.user_connections:
            return "offline"
        return self.user_statuses.get(user_id, "offline")

    async def broadcast_status_change(self, user_id: int, status: UserStatus):
        """Broadcast a user's status change to relevant channels"""
        message = {
            "type": "user_status_change",
            "user_id": user_id,
            "status": status
        }
        # Broadcast to all channels the user is in
        if user_id in self.user_channels:
            for channel_id in self.user_channels[user_id]:
                await self.broadcast_to_channel(message, channel_id)

    def add_channel_for_user(self, user_id: int, channel_id: int):
        if user_id in self.user_channels:
            self.user_channels[user_id].add(channel_id)

    async def broadcast_to_channel(self, message: dict, channel_id: int):
        # Create a list of tuples (user_id, websocket) to iterate over
        connections_to_process = [
            (user_id, websocket)
            for user_id, channels in self.user_channels.items()
            if channel_id in channels
            for websocket in self.user_connections.get(user_id, [])
        ]
        
        disconnected_websockets = []
        for user_id, websocket in connections_to_process:
            try:
                await websocket.send_json(message)
            except RuntimeError:
                disconnected_websockets.append((websocket, user_id))
        
        # Handle disconnections after the broadcast is complete
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