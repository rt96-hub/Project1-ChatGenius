from typing import Any, Dict, List
from websocket_manager import manager

class EventsManager:
    @staticmethod
    async def connect(websocket: Any, user_id: int, channel_ids: List[int], max_connections_per_user: int, max_total_connections: int) -> bool:
        """Connect a WebSocket and initialize its channels"""
        return await manager.connect(websocket, user_id, channel_ids, max_connections_per_user, max_total_connections)
    
    @staticmethod
    def disconnect(websocket: Any, user_id: int):
        """Disconnect a WebSocket"""
        manager.disconnect(websocket, user_id)
    
    @staticmethod
    def get_user_channels(user_id: int) -> List[int]:
        """Get all channel IDs for a user"""
        return manager.user_channels.get(user_id, [])
    
    @staticmethod
    def add_channel_for_user(user_id: int, channel_id: int):
        """Add a channel to a user's WebSocket connection"""
        manager.add_channel_for_user(user_id, channel_id)
    
    @staticmethod
    def remove_channel_for_user(user_id: int, channel_id: int):
        """Remove a channel from a user's WebSocket connection"""
        manager.remove_channel_for_user(user_id, channel_id)
    
    @staticmethod
    async def broadcast_channel_update(channel_id: int, channel_data: Dict[str, Any]):
        """Broadcast channel update event to all members"""
        await manager.broadcast_to_channel({
            "type": "channel_update",
            "channel_id": channel_id,
            "channel": channel_data
        }, channel_id)
    
    @staticmethod
    async def broadcast_member_left(channel_id: int, user_id: int):
        """Broadcast member left event"""
        await manager.broadcast_member_left(channel_id, user_id)
    
    @staticmethod
    async def broadcast_privacy_updated(channel_id: int, is_private: bool):
        """Broadcast privacy update event"""
        await manager.broadcast_privacy_updated(channel_id, is_private)
    
    @staticmethod
    async def broadcast_member_joined(channel_id: int, user: Any):
        """Broadcast member joined event"""
        await manager.broadcast_member_joined(channel_id, user)
    
    @staticmethod
    async def broadcast_channel_created(channel: Any):
        """Broadcast channel creation event"""
        await manager.broadcast_channel_created(channel)

    @staticmethod
    async def broadcast_file_upload(channel_id: int, file_upload: Any, message: Any):
        """Broadcast file upload event"""
        await manager.broadcast_file_upload(channel_id, file_upload, message)
    
    @staticmethod
    async def broadcast_file_deleted(channel_id: int, file_id: int, message_id: int):
        """Broadcast file deletion event"""
        await manager.broadcast_file_deleted(channel_id, file_id, message_id)

    @staticmethod
    async def broadcast_message_update(channel_id: int, message: Any, user: Any):
        """Broadcast message update event"""
        await manager.broadcast_to_channel({
            "type": "message_update",
            "channel_id": channel_id,
            "message": {
                "id": message.id,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
                "updated_at": message.updated_at.isoformat(),
                "user_id": message.user_id,
                "channel_id": message.channel_id,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name
                }
            }
        }, channel_id)
    
    @staticmethod
    async def broadcast_message_delete(channel_id: int, message_id: int):
        """Broadcast message deletion event"""
        await manager.broadcast_to_channel({
            "type": "message_delete",
            "channel_id": channel_id,
            "message_id": message_id
        }, channel_id)
    
    @staticmethod
    async def broadcast_message_created(channel_id: int, message: Any, user: Any):
        """Broadcast new message event"""
        await manager.broadcast_to_channel({
            "type": "message_created",
            "message": {
                "id": message.id,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
                "updated_at": message.updated_at.isoformat(),
                "user_id": message.user_id,
                "channel_id": message.channel_id,
                "parent_id": message.parent_id,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "picture": user.picture
                }
            }
        }, channel_id)
    
    @staticmethod
    async def broadcast_root_message_update(channel_id: int, root_message: Any):
        """Broadcast root message update event (for replies)"""
        await manager.broadcast_to_channel({
            "type": "message_update",
            "channel_id": channel_id,
            "message": {
                "id": root_message.id,
                "content": root_message.content,
                "created_at": root_message.created_at.isoformat(),
                "updated_at": root_message.updated_at.isoformat(),
                "user_id": root_message.user_id,
                "channel_id": root_message.channel_id,
                "parent_id": root_message.parent_id,
                "has_replies": True,
                "user": {
                    "id": root_message.user.id,
                    "email": root_message.user.email,
                    "name": root_message.user.name,
                    "picture": root_message.user.picture
                }
            }
        }, channel_id)
    
    @staticmethod
    async def broadcast_reaction_add(channel_id: int, message_id: int, message_reaction: Any, reaction: Any, user: Any):
        """Broadcast reaction add event"""
        await manager.broadcast_to_channel({
            "type": "message_reaction_add",
            "channel_id": channel_id,
            "message_id": message_id,
            "reaction": {
                "id": message_reaction.id,
                "reaction_id": message_reaction.reaction_id,
                "user_id": message_reaction.user_id,
                "created_at": message_reaction.created_at.isoformat(),
                "reaction": {
                    "id": reaction.id,
                    "code": reaction.code,
                    "is_system": reaction.is_system,
                    "image_url": reaction.image_url
                },
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "picture": user.picture
                }
            }
        }, channel_id)
    
    @staticmethod
    async def broadcast_reaction_remove(channel_id: int, message_id: int, reaction_id: int, user_id: int):
        """Broadcast reaction remove event"""
        await manager.broadcast_to_channel({
            "type": "message_reaction_remove",
            "channel_id": channel_id,
            "message_id": message_id,
            "reaction_id": reaction_id,
            "user_id": user_id
        }, channel_id)

# Create a singleton instance
events = EventsManager() 