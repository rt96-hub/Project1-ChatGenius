from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Request, APIRouter
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
from file_uploads import router as file_uploads_router
from search import router as search_router
from websocket_manager import manager
from middleware import SearchRateLimitMiddleware, CacheControlMiddleware

# Configure logging for errors only
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

load_dotenv()

MAX_CONNECTIONS_PER_USER = int(os.getenv('MAX_WEBSOCKET_CONNECTIONS_PER_USER', '5'))
MAX_TOTAL_CONNECTIONS = int(os.getenv('MAX_TOTAL_WEBSOCKET_CONNECTIONS', '1000'))
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
MAX_SEARCH_REQUESTS = int(os.getenv('MAX_SEARCH_REQUESTS_PER_MINUTE', '60'))
SEARCH_WINDOW_SIZE = int(os.getenv('SEARCH_RATE_LIMIT_WINDOW', '60'))

# Create the main app without root_path
app = FastAPI()

# Create an API router for all your routes
api_router = APIRouter()

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

# Add rate limiting and caching middleware
app.add_middleware(
    SearchRateLimitMiddleware,
    window_size=SEARCH_WINDOW_SIZE,
    max_requests=MAX_SEARCH_REQUESTS
)
app.add_middleware(CacheControlMiddleware)

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth endpoints
@api_router.post("/auth/sync", response_model=schemas.User)
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

@api_router.get("/auth/verify", response_model=dict)
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

@api_router.websocket("/ws")
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
        if not await manager.connect(websocket, user.id, channel_ids, MAX_CONNECTIONS_PER_USER, MAX_TOTAL_CONNECTIONS):
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
@api_router.get("/users/me", response_model=schemas.User)
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

@api_router.get("/users/by-last-dm", response_model=List[schemas.UserWithLastDM])
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

@api_router.get("/users/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_users(db, skip=skip, limit=limit)

@api_router.get("/users/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@api_router.put("/users/me/bio", response_model=schemas.User)
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

@api_router.put("/users/me/name", response_model=schemas.User)
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
@api_router.post("/channels/", response_model=schemas.Channel)
async def create_channel_endpoint(
    channel: schemas.ChannelCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = crud.create_channel(db=db, channel=channel, creator_id=current_user.id)
    
    # Add the new channel to the user's WebSocket connection
    manager.add_channel_for_user(current_user.id, db_channel.id)
    
    return db_channel

@api_router.get("/channels/me", response_model=List[schemas.Channel])
def read_user_channels(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    channels = crud.get_user_channels(db, user_id=current_user.id, skip=skip, limit=limit)
    return channels

@api_router.get("/channels/available", response_model=List[schemas.Channel])
def get_available_channels_endpoint(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all public channels that the user can join."""
    return crud.get_available_channels(db, user_id=current_user.id, skip=skip, limit=limit)

@api_router.get("/channels/{channel_id}", response_model=schemas.Channel)
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

@api_router.put("/channels/{channel_id}", response_model=schemas.Channel)
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

@api_router.delete("/channels/{channel_id}", response_model=schemas.Channel)
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

@api_router.post("/channels/{channel_id}/messages", response_model=schemas.Message)
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

@api_router.get("/channels/{channel_id}/messages", response_model=schemas.MessageList)
def get_channel_messages(
    channel_id: int,
    skip: int = 0,
    limit: int = 50,
    include_reactions: bool = False,
    parent_only: bool = True,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    # Verify channel access
    channel = crud.get_channel(db, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    if not crud.user_in_channel(db, current_user.id, channel_id):
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    return crud.get_channel_messages(
        db=db,
        channel_id=channel_id,
        skip=skip,
        limit=limit,
        include_reactions=include_reactions,
        parent_only=parent_only
    )

@api_router.put("/channels/{channel_id}/messages/{message_id}", response_model=schemas.Message)
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

@api_router.delete("/channels/{channel_id}/messages/{message_id}", response_model=schemas.Message)
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

@api_router.get("/channels/{channel_id}/members", response_model=List[schemas.UserInChannel])
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

@api_router.delete("/channels/{channel_id}/members/{user_id}")
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

@api_router.put("/channels/{channel_id}/privacy", response_model=schemas.Channel)
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

@api_router.get("/channels/{channel_id}/role", response_model=schemas.ChannelRole)
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

@api_router.put("/channels/{channel_id}/roles/{user_id}", response_model=schemas.ChannelRole)
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

@api_router.post("/channels/{channel_id}/leave")
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
@api_router.get("/reactions/", response_model=List[schemas.Reaction])
def list_reactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all available reactions"""
    return crud.get_all_reactions(db, skip=skip, limit=limit)

@api_router.post("/channels/{channel_id}/messages/{message_id}/reactions", response_model=schemas.MessageReaction)
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

@api_router.delete("/channels/{channel_id}/messages/{message_id}/reactions/{reaction_id}")
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

@api_router.post("/channels/dm", response_model=schemas.Channel)
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

@api_router.get("/channels/me/dms", response_model=List[schemas.Channel])
def read_user_dms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all DM channels for the current user, ordered by most recent message."""
    return crud.get_user_dms(db, user_id=current_user.id, skip=skip, limit=limit)

@api_router.get("/channels/dm/check/{other_user_id}", response_model=schemas.DMCheckResponse)
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

@api_router.post("/channels/{channel_id}/messages/{parent_id}/reply", response_model=schemas.Message)
async def create_message_reply_endpoint(
    channel_id: int,
    parent_id: int,
    message: schemas.MessageReplyCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Creates a reply to a message. If the parent message already has a reply,
    the new message will be attached to the last message in the reply chain."""
    
    # Verify channel access and message existence
    channel = crud.get_channel(db, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    if not crud.user_in_channel(db, current_user.id, channel_id):
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    # Verify parent message exists and belongs to this channel
    parent_message = crud.get_message(db, message_id=parent_id)
    if not parent_message:
        raise HTTPException(status_code=404, detail="Parent message not found")
    if parent_message.channel_id != channel_id:
        raise HTTPException(status_code=400, detail="Parent message does not belong to this channel")
    
    # Create the reply
    reply, root_message = crud.create_reply(
        db=db,
        parent_id=parent_id,
        user_id=current_user.id,
        message=message
    )
    
    if not reply or not root_message:
        raise HTTPException(status_code=400, detail="Could not create reply")
    
    # Broadcast the new reply message to all users in the channel
    message_data = {
        "type": "message_created",
        "message": {
            "id": reply.id,
            "content": reply.content,
            "created_at": reply.created_at.isoformat(),
            "updated_at": reply.updated_at.isoformat(),
            "user_id": reply.user_id,
            "channel_id": reply.channel_id,
            "parent_id": reply.parent_id,
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "name": current_user.name,
                "picture": current_user.picture
            }
        }
    }
    await manager.broadcast_to_channel(message_data, channel_id)
    
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
    await manager.broadcast_to_channel(root_message_data, channel_id)
    
    return reply

@api_router.get("/messages/{message_id}/reply-chain", response_model=List[schemas.Message])
async def get_message_reply_chain_endpoint(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Returns all messages in a reply chain for a given message ID.
    This includes:
    1. All parent messages (if the given message is a reply)
    2. The message itself
    3. All replies in the chain
    Messages are ordered by created_at date (ascending)."""
    
    # Get the message to verify it exists and get its channel
    message = crud.get_message(db, message_id=message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Verify user has access to the channel
    if not crud.user_in_channel(db, current_user.id, message.channel_id):
        raise HTTPException(status_code=403, detail="Not a member of the channel containing this message")
    
    # Get the reply chain
    reply_chain = crud.get_message_reply_chain(db, message_id=message_id)
    
    return reply_chain

@api_router.post("/channels/{channel_id}/join", response_model=schemas.Channel)
async def join_channel_endpoint(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Join a channel."""
    # Get the channel first to check if it exists and is joinable
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if db_channel.is_private:
        raise HTTPException(status_code=403, detail="Cannot join private channels directly")
    if db_channel.is_dm:
        raise HTTPException(status_code=403, detail="Cannot join DM channels directly")
    
    # Try to join the channel
    updated_channel = crud.join_channel(db, channel_id=channel_id, user_id=current_user.id)
    if not updated_channel:
        raise HTTPException(status_code=400, detail="Failed to join channel")
    
    # Add the channel to the user's WebSocket connection
    manager.add_channel_for_user(current_user.id, channel_id)
    
    # Broadcast member joined event
    await manager.broadcast_member_joined(channel_id, current_user)
    
    return updated_channel

# Include the router with the prefix
app.include_router(api_router, prefix=os.getenv('ROOT_PATH', ''))
app.include_router(file_uploads_router, prefix=os.getenv('ROOT_PATH', ''), tags=["files"])
app.include_router(search_router, prefix=os.getenv('ROOT_PATH', ''), tags=["search"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

