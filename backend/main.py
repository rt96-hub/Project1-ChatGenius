from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
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

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
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
        self.user_connections: dict[int, list[WebSocket]] = {}
        self.user_channels: dict[int, set[int]] = {}
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
                channel_id = data.get('channel_id')
                content = data.get('content')
                
                if not channel_id or not content:
                    continue
                
                # Verify channel membership
                if channel_id not in manager.user_channels[user.id]:
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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [user.id for user in db_channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    return crud.get_channel_messages(db, channel_id=channel_id, skip=skip, limit=limit)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

