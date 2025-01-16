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
async def list_reactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all available reactions"""
    # Update user activity when fetching reactions list
    await events.update_user_activity(current_user.id)
    
    return get_all_reactions(db, skip=skip, limit=limit)

# want to switch this endpoint to /reactions/{message_id}
@router.post("/{message_id}", response_model=schemas.MessageReaction)
async def add_reaction(
    message_id: int,
    reaction: schemas.MessageReactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Add a reaction to a message"""
    # Update user activity when adding a reaction
    await events.update_user_activity(current_user.id)
    
    message = get_message(db, message_id=message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Verify user has access to the channel
    channel = get_channel(db, channel_id=message.channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [u.id for u in channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    message_reaction = add_reaction_to_message(
        db=db,
        message_id=message_id,
        user_id=current_user.id,
        reaction_id=reaction.reaction_id
    )

    db_reaction = get_reaction(db, reaction_id=reaction.reaction_id)
    
    # Broadcast the reaction addition
    await events.broadcast_reaction_add(message.channel_id, message_id, message_reaction, db_reaction, current_user)
    
    return message_reaction

# want to switch this endpoint to /reactions/{message_id}/{reaction_id}
@router.delete("/{message_id}/{reaction_id}", response_model=dict)
async def remove_reaction(
    message_id: int,
    reaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Remove a reaction from a message"""
    # Update user activity when removing a reaction
    await events.update_user_activity(current_user.id)
    
    message = get_message(db, message_id=message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Verify user has access to the channel
    channel = get_channel(db, channel_id=message.channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [u.id for u in channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    # Remove the reaction
    removed = remove_reaction_from_message(
        db=db,
        message_id=message_id,
        user_id=current_user.id,
        reaction_id=reaction_id
    )
    
    if removed:
        # Broadcast the reaction removal
        await events.broadcast_reaction_remove(message.channel_id, message_id, reaction_id, current_user.id)
        return {"message": "Reaction removed successfully"}
    else:
        raise HTTPException(status_code=404, detail="Reaction not found") 