from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
import models, schemas, crud
from database import SessionLocal, engine
from security import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

MAX_CONNECTIONS_PER_USER = int(os.getenv('MAX_WEBSOCKET_CONNECTIONS_PER_USER', '5'))
MAX_TOTAL_CONNECTIONS = int(os.getenv('MAX_TOTAL_WEBSOCKET_CONNECTIONS', '1000'))

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost:3001"],
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
        # Store multiple connections per user and their channel memberships
        self.user_connections: dict[int, list[WebSocket]] = {}  # user_id -> list of websockets
        self.user_channels: dict[int, set[int]] = {}  # user_id -> set of channel_ids
        self.total_connections = 0

    async def connect(self, websocket: WebSocket, user_id: int, channels: list[int]):
        # Check total connection limit
        if self.total_connections >= MAX_TOTAL_CONNECTIONS:
            await websocket.close(code=status.WS_1013_TRY_AGAIN_LATER)
            return False

        # Check user connection limit
        if user_id in self.user_connections and len(self.user_connections[user_id]) >= MAX_CONNECTIONS_PER_USER:
            await websocket.close(code=status.WS_1013_TRY_AGAIN_LATER)
            return False

        await websocket.accept()
        
        # Initialize user connections if not exists
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
                
                # Clean up user entry if no more connections
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
                    del self.user_channels[user_id]

    async def broadcast_to_channel(self, message: dict, channel_id: int):
        # Find all users who are members of this channel and send them the message
        disconnected_websockets = []
        for user_id, channels in self.user_channels.items():
            if channel_id in channels:
                if user_id in self.user_connections:
                    for websocket in self.user_connections[user_id]:
                        try:
                            await websocket.send_json(message)
                        except RuntimeError:
                            # Connection is closed or invalid
                            disconnected_websockets.append((websocket, user_id))
        
        # Clean up any disconnected websockets
        for websocket, user_id in disconnected_websockets:
            self.disconnect(websocket, user_id)

manager = ConnectionManager()

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=schemas.User)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    user_id = None
    try:
        # Verify token
        user = await get_current_user(token, db)
        user_id = user.id
        
        # Get all channels the user is a member of
        channels = crud.get_user_channels(db, user_id=user.id)
        channel_ids = [channel.id for channel in channels]
        
        # Attempt to connect
        if not await manager.connect(websocket, user.id, channel_ids):
            return  # Connection was rejected due to limits
        
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
                            "email": user.email
                        }
                    }
                }
                await manager.broadcast_to_channel(message_data, channel_id)
        except WebSocketDisconnect:
            if user_id is not None:
                manager.disconnect(websocket, user_id)
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        if user_id is not None:
            manager.disconnect(websocket, user_id)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

@app.get("/users/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

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
def create_channel_endpoint(
    channel: schemas.ChannelCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_channel(db=db, channel=channel, creator_id=current_user.id)

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
    # Check if user is member of channel
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
    
    # Broadcast channel update to all connected clients in this channel
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
    # Check if user is the owner
    if db_channel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the channel owner can delete the channel")
    return crud.delete_channel(db=db, channel_id=channel_id)

# Message endpoints
@app.post("/channels/{channel_id}/messages", response_model=schemas.Message)
def create_message_endpoint(
    channel_id: int,
    message: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if user is member of channel
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
    # Check if user is member of channel
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [user.id for user in db_channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    return crud.get_channel_messages(db, channel_id=channel_id, skip=skip, limit=limit)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

