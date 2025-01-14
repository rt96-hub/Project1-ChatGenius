from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from .. import models, schemas
from ..database import get_db
from ..auth0 import get_current_user
from ..events_manager import events
from ..crud.reactions import (
    get_all_reactions,
    get_reaction,
    add_reaction_to_message,
    remove_reaction_from_message
)
from ..crud.messages import get_message
from ..crud.channels import get_channel

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[schemas.Reaction])
def list_reactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all available reactions"""
    return get_all_reactions(db, skip=skip, limit=limit)

# want to switch this endpoint to /reactions/{message_id}
@router.post("/{message_id}", response_model=schemas.MessageReaction)
async def add_reaction_endpoint(
    channel_id: int,
    message_id: int,
    reaction: schemas.MessageReactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Add a reaction to a message"""
    # Check if message exists and user has permission
    db_message = get_message(db, message_id=message_id)
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    if db_message.channel_id != channel_id:
        raise HTTPException(status_code=400, detail="Message does not belong to this channel")
    
    # Check if user is member of the channel
    db_channel = get_channel(db, channel_id=channel_id)
    if current_user.id not in [user.id for user in db_channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    # Add the reaction
    message_reaction = add_reaction_to_message(
        db=db,
        message_id=message_id,
        reaction_id=reaction.reaction_id,
        user_id=current_user.id
    )
    
    # Get the reaction object to include its code
    db_reaction = get_reaction(db, reaction_id=reaction.reaction_id)
    
    # Broadcast the reaction to all users in the channel
    await events.broadcast_reaction_add(channel_id, message_id, message_reaction, db_reaction, current_user)
    
    return message_reaction

# want to switch this endpoint to /reactions/{message_id}/{reaction_id}
@router.delete("/{message_id}/{reaction_id}")
async def remove_reaction_endpoint(
    channel_id: int,
    message_id: int,
    reaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Remove a reaction from a message"""
    # Check if message exists
    db_message = get_message(db, message_id=message_id)
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    if db_message.channel_id != channel_id:
        raise HTTPException(status_code=400, detail="Message does not belong to this channel")
    
    # Check if user is member of the channel
    db_channel = get_channel(db, channel_id=channel_id)
    if current_user.id not in [user.id for user in db_channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    # Remove the reaction
    if remove_reaction_from_message(db, message_id, reaction_id, current_user.id):
        # Broadcast the reaction removal to all users in the channel
        await events.broadcast_reaction_remove(channel_id, message_id, reaction_id, current_user.id)
        return {"message": "Reaction removed successfully"}
    
    raise HTTPException(status_code=404, detail="Reaction not found") 