from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Set
import models, schemas, crud
from database import SessionLocal, engine
from auth0 import get_current_user, verify_token
import asyncio
import os
from dotenv import load_dotenv
import logging

# Configure logging for errors only
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

load_dotenv()

MAX_CONNECTIONS_PER_USER = int(os.getenv('MAX_WEBSOCKET_CONNECTIONS_PER_USER', '5'))
MAX_TOTAL_CONNECTIONS = int(os.getenv('MAX_TOTAL_WEBSOCKET_CONNECTIONS', '1000'))
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')

ROOT_PATH = os.getenv('ROOT_PATH', '')  # Empty string for local dev, '/api' for production

app = FastAPI(
    root_path=ROOT_PATH
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        f"http://{os.getenv('EC2_PUBLIC_DNS')}:3000",
        f"https://{os.getenv('EC2_PUBLIC_DNS')}:3000",
        f"http://{os.getenv('EC2_PUBLIC_DNS')}",
        f"https://{os.getenv('EC2_PUBLIC_DNS')}"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[WebSocket, int] = {}
        self.user_connections: Dict[int, List[WebSocket]] = {}
        self.user_channels: Dict[int, Set[int]] = {}
        self.total_connections = 0

    async def connect(self, websocket: WebSocket, user_id: int, channels: list[int]):
        if self.total_connections >= MAX_TOTAL_CONNECTIONS:
            await websocket.close(code=status.WS_1013_TRY_AGAIN_LATER)
            return False

        if user_id in self.user_connections and len(self.user_connections[user_id]) >= MAX_CONNECTIONS_PER_USER:
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
                "join_code": channel.join_code,
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

manager = ConnectionManager()

# Auth endpoints
@app.post("/auth/sync", response_model=schemas.User)
async def sync_auth0_user_endpoint(
    request: Request,
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """Sync Auth0 user data with local database"""
    try:
        # Verify the token first
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header"
            )
        if not auth_header.startswith('Bearer '):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Must start with 'Bearer '"
            )
        
        token = auth_header.split(' ')[1]
        payload = await verify_token(token)
        
        # Ensure the Auth0 ID matches
        if payload['sub'] != user_data.auth0_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token subject does not match provided Auth0 ID"
            )
        
        return crud.sync_auth0_user(db, user_data)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error syncing user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing user: {str(e)}"
        )

@app.get("/auth/verify", response_model=dict)
async def verify_auth(
    request: Request,
    db: Session = Depends(get_db)
):
    """Verify Auth0 token and return user data"""
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header"
            )
        if not auth_header.startswith('Bearer '):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Must start with 'Bearer '"
            )
        
        token = auth_header.split(' ')[1]
        payload = await verify_token(token)
        
        # Get user from database
        user = crud.get_user_by_auth0_id(db, payload['sub'])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "valid": True,
            "user": user
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error verifying user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying user: {str(e)}"
        )

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    user_id = None
    try:
        # Verify token and get user
        payload = await verify_token(token)
        user = crud.get_user_by_auth0_id(db, payload["sub"])
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        user_id = user.id
        
        # Get all channels the user is a member of
        channels = crud.get_user_channels(db, user_id=user.id)
        channel_ids = [channel.id for channel in channels]
        
        # Attempt to connect
        if not await manager.connect(websocket, user.id, channel_ids):
            return
        
        try:
            while True:
                data = await websocket.receive_json()
                event_type = data.get('type')
                channel_id = data.get('channel_id')
                
                if not channel_id or channel_id not in manager.user_channels[user.id]:
                    continue
                
                if event_type == "new_message":
                    content = data.get('content')
                    if not content:
                        continue
                    
                    # Create and save the message
                    message = crud.create_message(
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
                    await manager.broadcast_to_channel(message_data, channel_id)
                
                elif event_type == "add_reaction":
                    message_id = data.get('message_id')
                    reaction_id = data.get('reaction_id')
                    if not message_id or not reaction_id:
                        continue
                    
                    # Verify message belongs to channel
                    db_message = crud.get_message(db, message_id=message_id)
                    if not db_message or db_message.channel_id != channel_id:
                        continue
                    
                    # Add the reaction
                    message_reaction = crud.add_reaction_to_message(
                        db=db,
                        message_id=message_id,
                        reaction_id=reaction_id,
                        user_id=user.id
                    )
                    
                    # Get the reaction object
                    db_reaction = crud.get_reaction(db, reaction_id=reaction_id)
                    
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
                    await manager.broadcast_to_channel(reaction_data, channel_id)
                
                elif event_type == "remove_reaction":
                    message_id = data.get('message_id')
                    reaction_id = data.get('reaction_id')
                    if not message_id or not reaction_id:
                        continue
                    
                    # Verify message belongs to channel
                    db_message = crud.get_message(db, message_id=message_id)
                    if not db_message or db_message.channel_id != channel_id:
                        continue
                    
                    # Remove the reaction
                    if crud.remove_reaction_from_message(db, message_id, reaction_id, user.id):
                        # Broadcast the removal
                        reaction_data = {
                            "type": "message_reaction_remove",
                            "channel_id": channel_id,
                            "message_id": message_id,
                            "reaction_id": reaction_id,
                            "user_id": user.id
                        }
                        await manager.broadcast_to_channel(reaction_data, channel_id)
                
        except WebSocketDisconnect:
            if user_id is not None:
                manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if user_id is not None:
            manager.disconnect(websocket, user_id)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

# User endpoints
@app.get("/users/me", response_model=schemas.User)
async def read_users_me(
    request: Request,
    current_user: models.User = Depends(get_current_user)
):
    """Get the current authenticated user's information"""
    try:
        return current_user
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting current user: {str(e)}"
        )

@app.get("/users/by-last-dm", response_model=List[schemas.UserWithLastDM])
def read_users_by_last_dm(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all users ordered by their last DM interaction with the current user.
    Users with no DM history appear first, followed by users with DMs ordered by ascending date
    (most recent DM appears last)."""
    return crud.get_users_by_last_dm(
        db,
        current_user_id=current_user.id,
        skip=skip,
        limit=limit
    )

@app.get("/users/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_users(db, skip=skip, limit=limit)

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/me/bio", response_model=schemas.User)
async def update_user_bio(
    bio_update: schemas.UserBioUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update the current user's bio"""
    try:
        updated_user = crud.update_user_bio(db, user_id=current_user.id, bio=bio_update.bio)
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except Exception as e:
        logger.error(f"Error updating user bio: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user bio: {str(e)}"
        )

@app.put("/users/me/name", response_model=schemas.User)
async def update_user_name(
    name_update: schemas.UserNameUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update the current user's name"""
    try:
        updated_user = crud.update_user_name(db, user_id=current_user.id, name=name_update.name)
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except Exception as e:
        logger.error(f"Error updating user name: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user name: {str(e)}"
        )

# Channel endpoints
@app.post("/channels/", response_model=schemas.Channel)
async def create_channel_endpoint(
    channel: schemas.ChannelCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = crud.create_channel(db=db, channel=channel, creator_id=current_user.id)
    
    # Add the new channel to the user's WebSocket connection
    manager.add_channel_for_user(current_user.id, db_channel.id)
    
    return db_channel

@app.get("/channels/me", response_model=List[schemas.Channel])
def read_user_channels(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    channels = crud.get_user_channels(db, user_id=current_user.id, skip=skip, limit=limit)
    return channels

@app.get("/channels/{channel_id}", response_model=schemas.Channel)
def read_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [user.id for user in db_channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    return db_channel

@app.put("/channels/{channel_id}", response_model=schemas.Channel)
async def update_channel_endpoint(
    channel_id: int,
    channel_update: schemas.ChannelCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [user.id for user in db_channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    if db_channel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the channel owner can update the channel")
    
    updated_channel = crud.update_channel(db=db, channel_id=channel_id, channel_update=channel_update)
    
    channel_update_data = {
        "type": "channel_update",
        "channel_id": channel_id,
        "channel": {
            "id": updated_channel.id,
            "name": updated_channel.name,
            "description": updated_channel.description,
            "owner_id": updated_channel.owner_id
        }
    }
    await manager.broadcast_to_channel(channel_update_data, channel_id)
    
    return updated_channel

@app.delete("/channels/{channel_id}", response_model=schemas.Channel)
def delete_channel_endpoint(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if db_channel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the channel owner can delete the channel")
    return crud.delete_channel(db=db, channel_id=channel_id)

@app.post("/channels/{channel_id}/messages", response_model=schemas.Message)
def create_message_endpoint(
    channel_id: int,
    message: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [user.id for user in db_channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    return crud.create_message(
        db=db,
        channel_id=channel_id,
        user_id=current_user.id,
        message=message
    )

@app.get("/channels/{channel_id}/messages", response_model=schemas.MessageList)
def read_channel_messages(
    channel_id: int,
    skip: int = 0,
    limit: int = 50,
    include_reactions: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [user.id for user in db_channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    return crud.get_channel_messages(
        db, 
        channel_id=channel_id, 
        skip=skip, 
        limit=limit,
        include_reactions=include_reactions
    )

@app.put("/channels/{channel_id}/messages/{message_id}", response_model=schemas.Message)
async def update_message_endpoint(
    channel_id: int,
    message_id: int,
    message: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if message exists and user has permission
    db_message = crud.get_message(db, message_id=message_id)
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    if db_message.channel_id != channel_id:
        raise HTTPException(status_code=400, detail="Message does not belong to this channel")
    if db_message.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the message author can edit the message")
    
    # Update the message
    updated_message = crud.update_message(db=db, message_id=message_id, message_update=message)
    
    # Broadcast the update to all users in the channel
    message_update_data = {
        "type": "message_update",
        "channel_id": channel_id,
        "message": {
            "id": updated_message.id,
            "content": updated_message.content,
            "created_at": updated_message.created_at.isoformat(),
            "updated_at": updated_message.updated_at.isoformat(),
            "user_id": updated_message.user_id,
            "channel_id": updated_message.channel_id,
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "name": current_user.name
            }
        }
    }
    await manager.broadcast_to_channel(message_update_data, channel_id)
    
    return updated_message

@app.delete("/channels/{channel_id}/messages/{message_id}", response_model=schemas.Message)
async def delete_message_endpoint(
    channel_id: int,
    message_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if message exists and user has permission
    db_message = crud.get_message(db, message_id=message_id)
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    if db_message.channel_id != channel_id:
        raise HTTPException(status_code=400, detail="Message does not belong to this channel")
    if db_message.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the message author can delete the message")
    
    # Delete the message
    deleted_message = crud.delete_message(db=db, message_id=message_id)
    
    # Broadcast the deletion to all users in the channel
    message_delete_data = {
        "type": "message_delete",
        "channel_id": channel_id,
        "message_id": message_id
    }
    await manager.broadcast_to_channel(message_delete_data, channel_id)
    
    return deleted_message

@app.get("/channels/{channel_id}/members", response_model=List[schemas.UserInChannel])
def get_channel_members_endpoint(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [user.id for user in db_channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    return crud.get_channel_members(db, channel_id=channel_id)

@app.delete("/channels/{channel_id}/members/{user_id}")
async def remove_channel_member_endpoint(
    channel_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if db_channel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only channel owner can remove members")
    
    if crud.remove_channel_member(db, channel_id=channel_id, user_id=user_id):
        await manager.broadcast_member_left(channel_id, user_id)
        return {"message": "Member removed successfully"}
    raise HTTPException(status_code=404, detail="Member not found")

@app.put("/channels/{channel_id}/privacy", response_model=schemas.Channel)
async def update_channel_privacy_endpoint(
    channel_id: int,
    privacy_update: schemas.ChannelPrivacyUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if db_channel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only channel owner can update privacy settings")
    
    updated_channel = crud.update_channel_privacy(db, channel_id=channel_id, privacy_update=privacy_update)
    await manager.broadcast_privacy_updated(channel_id, privacy_update.is_private)
    return updated_channel

@app.post("/channels/{channel_id}/invite", response_model=schemas.ChannelInvite)
def create_channel_invite_endpoint(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [user.id for user in db_channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    join_code = crud.create_channel_invite(db, channel_id=channel_id)
    if join_code:
        return schemas.ChannelInvite(join_code=join_code, channel_id=channel_id)
    raise HTTPException(status_code=500, detail="Failed to create invite")

@app.get("/channels/{channel_id}/role", response_model=schemas.ChannelRole)
def get_channel_role_endpoint(
    channel_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [user.id for user in db_channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    role = crud.get_user_channel_role(db, channel_id=channel_id, user_id=user_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@app.put("/channels/{channel_id}/roles/{user_id}", response_model=schemas.ChannelRole)
async def update_channel_role_endpoint(
    channel_id: int,
    user_id: int,
    role_update: schemas.ChannelRoleBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if db_channel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only channel owner can update roles")
    
    updated_role = crud.update_user_channel_role(
        db, channel_id=channel_id, user_id=user_id, role=role_update.role
    )
    await manager.broadcast_role_updated(channel_id, user_id, role_update.role)
    return updated_role

@app.post("/channels/{channel_id}/leave")
async def leave_channel_endpoint(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    if crud.leave_channel(db, channel_id=channel_id, user_id=current_user.id):
        await manager.broadcast_member_left(channel_id, current_user.id)
        return {"message": "Successfully left the channel"}
    raise HTTPException(status_code=500, detail="Failed to leave channel")

# Reaction endpoints
@app.get("/reactions/", response_model=List[schemas.Reaction])
def list_reactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all available reactions"""
    return crud.get_all_reactions(db, skip=skip, limit=limit)

@app.post("/channels/{channel_id}/messages/{message_id}/reactions", response_model=schemas.MessageReaction)
async def add_reaction_endpoint(
    channel_id: int,
    message_id: int,
    reaction: schemas.MessageReactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Add a reaction to a message"""
    # Check if message exists and user has permission
    db_message = crud.get_message(db, message_id=message_id)
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    if db_message.channel_id != channel_id:
        raise HTTPException(status_code=400, detail="Message does not belong to this channel")
    
    # Check if user is member of the channel
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if current_user.id not in [user.id for user in db_channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    # Add the reaction
    message_reaction = crud.add_reaction_to_message(
        db=db,
        message_id=message_id,
        reaction_id=reaction.reaction_id,
        user_id=current_user.id
    )
    
    # Get the reaction object to include its code
    db_reaction = crud.get_reaction(db, reaction_id=reaction.reaction_id)
    
    # Broadcast the reaction to all users in the channel
    reaction_data = {
        "type": "message_reaction_add",
        "channel_id": channel_id,
        "message_id": message_id,
        "reaction": {
            "id": message_reaction.id,
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
                "id": current_user.id,
                "email": current_user.email,
                "name": current_user.name,
                "picture": current_user.picture
            }
        }
    }
    await manager.broadcast_to_channel(reaction_data, channel_id)
    
    return message_reaction

@app.delete("/channels/{channel_id}/messages/{message_id}/reactions/{reaction_id}")
async def remove_reaction_endpoint(
    channel_id: int,
    message_id: int,
    reaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Remove a reaction from a message"""
    # Check if message exists
    db_message = crud.get_message(db, message_id=message_id)
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    if db_message.channel_id != channel_id:
        raise HTTPException(status_code=400, detail="Message does not belong to this channel")
    
    # Check if user is member of the channel
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if current_user.id not in [user.id for user in db_channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    # Remove the reaction
    if crud.remove_reaction_from_message(db, message_id, reaction_id, current_user.id):
        # Broadcast the reaction removal to all users in the channel
        reaction_data = {
            "type": "message_reaction_remove",
            "channel_id": channel_id,
            "message_id": message_id,
            "reaction_id": reaction_id,
            "user_id": current_user.id
        }
        await manager.broadcast_to_channel(reaction_data, channel_id)
        return {"message": "Reaction removed successfully"}
    
    raise HTTPException(status_code=404, detail="Reaction not found")

@app.post("/channels/dm", response_model=schemas.Channel)
async def create_dm_endpoint(
    dm: schemas.DMCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new DM channel with multiple users."""
    # Validate that the creator is not in the user_ids list
    if current_user.id in dm.user_ids:
        raise HTTPException(
            status_code=400,
            detail="Creator should not be included in the user_ids list"
        )
    
    db_channel = crud.create_dm(db=db, creator_id=current_user.id, dm=dm)
    if db_channel is None:
        raise HTTPException(
            status_code=400,
            detail="Could not create DM channel. Make sure all user IDs are valid."
        )
    
    # Add the new channel to the WebSocket connections for all users
    manager.add_channel_for_user(current_user.id, db_channel.id)
    for user_id in dm.user_ids:
        manager.add_channel_for_user(user_id, db_channel.id)
    
    # Broadcast channel creation event
    await manager.broadcast_channel_created(db_channel)
    
    # Broadcast to all users that they've been added to the DM
    for user in db_channel.users:
        await manager.broadcast_member_joined(db_channel.id, user)
    
    return db_channel

@app.get("/channels/me/dms", response_model=List[schemas.Channel])
def read_user_dms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all DM channels for the current user, ordered by most recent message."""
    return crud.get_user_dms(db, user_id=current_user.id, skip=skip, limit=limit)

@app.get("/channels/dm/check/{other_user_id}", response_model=schemas.DMCheckResponse)
def check_existing_dm_endpoint(
    other_user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Check if there's an existing one-on-one DM channel between the current user and another user."""
    try:
        # Check if other user exists
        other_user = crud.get_user(db, user_id=other_user_id)
        if not other_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check for existing DM channel
        channel_id = crud.get_existing_dm_channel(db, current_user.id, other_user_id)
        
        return {"channel_id": channel_id}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error checking DM channel: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking DM channel: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

