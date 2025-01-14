from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
import os
from typing import Optional

from .. import models, schemas
from ..database import get_db
from ..auth0 import verify_token
from ..events_manager import events
from ..crud.users import get_user_by_auth0_id
from ..crud.channels import get_user_channels, get_channel
from ..crud.messages import (
    create_message,
    get_message,
    create_reply
)
from ..crud.reactions import (
    add_reaction_to_message,
    get_reaction,
    remove_reaction_from_message
)

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
MAX_CONNECTIONS_PER_USER = int(os.getenv('MAX_WEBSOCKET_CONNECTIONS_PER_USER', '5'))
MAX_TOTAL_CONNECTIONS = int(os.getenv('MAX_TOTAL_WEBSOCKET_CONNECTIONS', '1000'))

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    user_id = None
    try:
        # Verify token and get user
        payload = await verify_token(token)
        user = get_user_by_auth0_id(db, payload["sub"])
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        user_id = user.id
        
        # Get all channels the user is a member of
        channels = get_user_channels(db, user_id=user.id)
        channel_ids = [channel.id for channel in channels]
        
        # Attempt to connect
        if not await events.connect(websocket, user.id, channel_ids, MAX_CONNECTIONS_PER_USER, MAX_TOTAL_CONNECTIONS):
            return
        
        try:
            while True:
                data = await websocket.receive_json()
                event_type = data.get('type')
                channel_id = data.get('channel_id')
                
                if not channel_id or channel_id not in events.get_user_channels(user.id):
                    continue
                
                if event_type == "new_message":
                    content = data.get('content')
                    if not content:
                        continue
                    
                    # Create and save the message
                    message = create_message(
                        db=db,
                        channel_id=channel_id,
                        user_id=user.id,
                        message=schemas.MessageCreate(content=content)
                    )
                    
                    # Prepare message data for broadcast
                    message_data = {
                        "type": "new_message",
                        "channel_id": channel_id,
                        "message": {
                            "id": message.id,
                            "content": message.content,
                            "created_at": message.created_at.isoformat(),
                            "user_id": message.user_id,
                            "channel_id": message.channel_id,
                            "user": {
                                "id": user.id,
                                "email": user.email,
                                "name": user.name
                            }
                        }
                    }
                    await events.broadcast_to_channel(message_data, channel_id)
                
                elif event_type == "message_reply":
                    content = data.get('content')
                    parent_id = data.get('parent_id')
                    if not content or not parent_id:
                        continue
                    
                    # Create the reply
                    reply, root_message = create_reply(
                        db=db,
                        parent_id=parent_id,
                        user_id=user.id,
                        message=schemas.MessageReplyCreate(content=content)
                    )
                    
                    if not reply or not root_message:
                        continue
                    
                    # Broadcast the new reply message
                    message_data = {
                        "type": "message_created",
                        "channel_id": channel_id,
                        "message": {
                            "id": reply.id,
                            "content": reply.content,
                            "created_at": reply.created_at.isoformat(),
                            "updated_at": reply.updated_at.isoformat(),
                            "user_id": reply.user_id,
                            "channel_id": reply.channel_id,
                            "parent_id": reply.parent_id,
                            "parent": {
                                "id": root_message.id,
                                "content": root_message.content,
                                "created_at": root_message.created_at.isoformat(),
                                "user_id": root_message.user_id,
                                "channel_id": root_message.channel_id
                            },
                            "user": {
                                "id": user.id,
                                "email": user.email,
                                "name": user.name,
                                "picture": user.picture
                            }
                        }
                    }
                    await events.broadcast_to_channel(message_data, channel_id)
                    
                    # Also broadcast an update to the root message to show it has replies
                    root_message_data = {
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
                    }
                    await events.broadcast_to_channel(root_message_data, channel_id)
                
                elif event_type == "add_reaction":
                    message_id = data.get('message_id')
                    reaction_id = data.get('reaction_id')
                    if not message_id or not reaction_id:
                        continue
                    
                    # Verify message belongs to channel
                    db_message = get_message(db, message_id=message_id)
                    if not db_message or db_message.channel_id != channel_id:
                        continue
                    
                    # Add the reaction
                    message_reaction = add_reaction_to_message(
                        db=db,
                        message_id=message_id,
                        reaction_id=reaction_id,
                        user_id=user.id
                    )
                    
                    # Get the reaction object
                    db_reaction = get_reaction(db, reaction_id=reaction_id)
                    
                    # Broadcast the reaction
                    reaction_data = {
                        "type": "message_reaction_add",
                        "channel_id": channel_id,
                        "message_id": message_id,
                        "reaction": {
                            "id": message_reaction.id,
                            "message_id": message_reaction.message_id,
                            "reaction_id": message_reaction.reaction_id,
                            "user_id": message_reaction.user_id,
                            "created_at": message_reaction.created_at.isoformat(),
                            "reaction": {
                                "id": db_reaction.id,
                                "code": db_reaction.code,
                                "is_system": db_reaction.is_system,
                                "image_url": db_reaction.image_url
                            },
                            "user": {
                                "id": user.id,
                                "email": user.email,
                                "name": user.name,
                                "picture": user.picture
                            }
                        }
                    }
                    await events.broadcast_to_channel(reaction_data, channel_id)
                
                elif event_type == "remove_reaction":
                    message_id = data.get('message_id')
                    reaction_id = data.get('reaction_id')
                    if not message_id or not reaction_id:
                        continue
                    
                    # Verify message belongs to channel
                    db_message = get_message(db, message_id=message_id)
                    if not db_message or db_message.channel_id != channel_id:
                        continue
                    
                    # Remove the reaction
                    if remove_reaction_from_message(db, message_id, reaction_id, user.id):
                        # Broadcast the removal
                        reaction_data = {
                            "type": "message_reaction_remove",
                            "channel_id": channel_id,
                            "message_id": message_id,
                            "reaction_id": reaction_id,
                            "user_id": user.id
                        }
                        await events.broadcast_to_channel(reaction_data, channel_id)
                
        except WebSocketDisconnect:
            if user_id is not None:
                events.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if user_id is not None:
            events.disconnect(websocket, user_id)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR) 