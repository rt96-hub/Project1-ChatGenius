from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from .. import models, schemas
from ..database import get_db
from ..auth0 import get_current_user
from ..events_manager import events
from ..crud.channels import (
    create_channel,
    get_channel,
    get_user_channels,
    update_channel,
    delete_channel,
    get_channel_members,
    remove_channel_member,
    update_channel_privacy,
    join_channel,
    leave_channel,
    get_available_channels,
    user_in_channel,
    create_dm,
    get_user_dms,
    get_existing_dm_channel
)
from ..crud.users import get_user

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=schemas.Channel)
async def create_channel_endpoint(
    channel: schemas.ChannelCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = create_channel(db=db, channel=channel, creator_id=current_user.id)
    
    # Add the new channel to the user's WebSocket connection
    events.add_channel_for_user(current_user.id, db_channel.id)
    
    return db_channel

@router.get("/me", response_model=List[schemas.Channel])
def read_user_channels(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    channels = get_user_channels(db, user_id=current_user.id, skip=skip, limit=limit)
    return channels

@router.get("/available", response_model=List[schemas.Channel])
def get_available_channels_endpoint(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all public channels that the user can join."""
    return get_available_channels(db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{channel_id}", response_model=schemas.Channel)
def read_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [user.id for user in db_channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    return db_channel

@router.put("/{channel_id}", response_model=schemas.Channel)
async def update_channel_endpoint(
    channel_id: int,
    channel_update: schemas.ChannelCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [user.id for user in db_channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    if db_channel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the channel owner can update the channel")
    
    updated_channel = update_channel(db=db, channel_id=channel_id, channel_update=channel_update)
    
    # Use events manager instead of direct WebSocket manager
    await events.broadcast_channel_update(channel_id, {
        "id": updated_channel.id,
        "name": updated_channel.name,
        "description": updated_channel.description,
        "owner_id": updated_channel.owner_id
    })
    
    return updated_channel

@router.delete("/{channel_id}", response_model=schemas.Channel)
def delete_channel_endpoint(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if db_channel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the channel owner can delete the channel")
    return delete_channel(db=db, channel_id=channel_id)

@router.get("/{channel_id}/members", response_model=List[schemas.UserInChannel])
def get_channel_members_endpoint(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [user.id for user in db_channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    return get_channel_members(db, channel_id=channel_id)

@router.delete("/{channel_id}/members/{user_id}")
async def remove_channel_member_endpoint(
    channel_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if db_channel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only channel owner can remove members")
    
    if remove_channel_member(db, channel_id=channel_id, user_id=user_id):
        await events.broadcast_member_left(channel_id, user_id)
        return {"message": "Member removed successfully"}
    raise HTTPException(status_code=404, detail="Member not found")

@router.put("/{channel_id}/privacy", response_model=schemas.Channel)
async def update_channel_privacy_endpoint(
    channel_id: int,
    privacy_update: schemas.ChannelPrivacyUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if db_channel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only channel owner can update privacy settings")
    
    updated_channel = update_channel_privacy(db, channel_id=channel_id, privacy_update=privacy_update)
    await events.broadcast_privacy_updated(channel_id, privacy_update.is_private)
    return updated_channel

@router.post("/{channel_id}/join", response_model=schemas.Channel)
async def join_channel_endpoint(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Join a channel."""
    # Get the channel first to check if it exists and is joinable
    db_channel = get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if db_channel.is_private:
        raise HTTPException(status_code=403, detail="Cannot join private channels directly")
    if db_channel.is_dm:
        raise HTTPException(status_code=403, detail="Cannot join DM channels directly")
    
    # Try to join the channel
    updated_channel = join_channel(db, channel_id=channel_id, user_id=current_user.id)
    if not updated_channel:
        raise HTTPException(status_code=400, detail="Failed to join channel")
    
    # Add the channel to the user's WebSocket connection
    events.add_channel_for_user(current_user.id, channel_id)
    
    # Broadcast member joined event
    await events.broadcast_member_joined(channel_id, current_user)
    
    return updated_channel

@router.post("/{channel_id}/leave")
async def leave_channel_endpoint(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    if leave_channel(db, channel_id=channel_id, user_id=current_user.id):
        await events.broadcast_member_left(channel_id, current_user.id)
        return {"message": "Successfully left the channel"}
    raise HTTPException(status_code=500, detail="Failed to leave channel")

@router.post("/dm", response_model=schemas.Channel)
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
    
    db_channel = create_dm(db=db, creator_id=current_user.id, dm=dm)
    if db_channel is None:
        raise HTTPException(
            status_code=400,
            detail="Could not create DM channel. Make sure all user IDs are valid."
        )
    
    # Add the new channel to the WebSocket connections for all users
    events.add_channel_for_user(current_user.id, db_channel.id)
    for user_id in dm.user_ids:
        events.add_channel_for_user(user_id, db_channel.id)
    
    # Broadcast events
    await events.broadcast_channel_created(db_channel)
    
    # Broadcast to all users that they've been added to the DM
    for user in db_channel.users:
        await events.broadcast_member_joined(db_channel.id, user)
    
    return db_channel

@router.get("/me/dms", response_model=List[schemas.Channel])
def read_user_dms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all DM channels for the current user, ordered by most recent message."""
    return get_user_dms(db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/dm/check/{other_user_id}", response_model=schemas.DMCheckResponse)
def check_existing_dm_endpoint(
    other_user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Check if there's an existing one-on-one DM channel between the current user and another user."""
    try:
        # Check if other user exists
        other_user = get_user(db, user_id=other_user_id)
        if not other_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check for existing DM channel
        channel_id = get_existing_dm_channel(db, current_user.id, other_user_id)
        
        return {"channel_id": channel_id}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error checking DM channel: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking DM channel: {str(e)}"
        ) 