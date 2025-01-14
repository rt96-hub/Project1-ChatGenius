from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from .. import models, schemas
from ..database import get_db
from ..auth0 import get_current_user
from ..crud.ai import (
    get_conversation,
    get_channel_conversations,
    create_conversation,
    add_message_to_conversation
)
from ..crud.channels import get_channel

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/channels/{channel_id}/conversations", response_model=schemas.AIConversationList)
async def get_channel_ai_conversations(
    channel_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all AI conversations for a channel"""
    # Verify user is member of channel
    channel = get_channel(db, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [u.id for u in channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")

    conversations = get_channel_conversations(
        db, channel_id, current_user.id, skip=skip, limit=limit
    )
    return schemas.AIConversationList(conversations=conversations)

@router.get("/channels/{channel_id}/conversations/{conversation_id}", response_model=schemas.AIConversation)
async def get_ai_conversation(
    channel_id: int,
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific AI conversation"""
    # Verify user is member of channel
    channel = get_channel(db, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [u.id for u in channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")

    conversation = get_conversation(db, conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.channel_id != channel_id:
        raise HTTPException(status_code=400, detail="Conversation does not belong to this channel")
    
    return conversation

@router.post("/channels/{channel_id}/query", response_model=schemas.AIQueryResponse)
async def create_ai_query(
    channel_id: int,
    query: schemas.AIQueryRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new AI conversation with initial query"""
    # Verify user is member of channel
    channel = get_channel(db, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [u.id for u in channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")

    # Create new conversation with initial message
    conversation = create_conversation(
        db=db,
        channel_id=channel_id,
        user_id=current_user.id,
        initial_message=query.query
    )

    # TODO: The AI response message should be created in the create_conversation function
    # For now, return the conversation with just the user message
    return schemas.AIQueryResponse(
        conversation=conversation,
        message=conversation.messages[-1]  # Last message in conversation
    )

@router.post("/channels/{channel_id}/conversations/{conversation_id}/messages", response_model=schemas.AIConversation)
async def add_message_to_conversation_endpoint(
    channel_id: int,
    conversation_id: int,
    message: schemas.AIMessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Add a new message to an existing conversation"""
    # Verify user is member of channel
    channel = get_channel(db, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [u.id for u in channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")

    # Verify conversation exists and belongs to user
    conversation = get_conversation(db, conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.channel_id != channel_id:
        raise HTTPException(status_code=400, detail="Conversation does not belong to this channel")

    # Add message to conversation
    updated_conversation = add_message_to_conversation(
        db=db,
        conversation_id=conversation_id,
        channel_id=channel_id,
        user_id=current_user.id,
        message=message.message
    )
    
    return updated_conversation