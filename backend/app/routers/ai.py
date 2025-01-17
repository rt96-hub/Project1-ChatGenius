from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import logging
from datetime import datetime, timedelta, timezone

from .. import models, schemas
from ..database import get_db
from ..auth0 import get_current_user
from ..llm_chat_service import summarize_messages
from ..crud.ai import (
    get_conversation,
    get_channel_conversations,
    create_conversation,
    add_message_to_conversation,
    delete_conversation
)
from ..crud.channels import get_channel
from ..crud.messages import get_channel_messages, create_message
from ..events_manager import events

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

    # Update user activity when fetching AI conversations
    await events.update_user_activity(current_user.id)

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

@router.delete("/channels/{channel_id}/conversations/{conversation_id}", status_code=204)
async def delete_ai_conversation(
    channel_id: int,
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete a specific AI conversation and all its messages"""
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

    # Delete the conversation
    success = delete_conversation(db, conversation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete conversation")

    return None

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

@router.get("/channels/{channel_id}/summarize", response_model=schemas.ChannelSummaryResponse)
async def summarize_channel(
    channel_id: int,
    quantity: int = Query(..., description="The number of time units to look back"),
    time_unit: str = Query(..., description="The time unit to look back", regex="^(hours|days|weeks)$"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Summarize channel messages for a specified time period"""
    # Verify user is member of channel
    channel = get_channel(db, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [u.id for u in channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")

    # Calculate the start date based on quantity and time_unit
    now = datetime.now(timezone.utc)
    if time_unit == "hours":
        start_date = now - timedelta(hours=quantity)
    elif time_unit == "days":
        start_date = now - timedelta(days=quantity)
    else:  # weeks
        start_date = now - timedelta(weeks=quantity)

    # Get messages from the specified time period
    messages = get_channel_messages(
        db=db,
        channel_id=channel_id,
        skip=0,
        limit=1000,  # Get a reasonable number of messages to summarize
        include_reactions=False,
        parent_only=False  # Include all messages for better context
    ).messages

    # Filter messages by date
    messages = [m for m in messages if m.created_at >= start_date]

    if not messages:
        return schemas.ChannelSummaryResponse(summary="No messages found in the specified time period.")

    # TODO: Implement actual summarization logic using LLM
    # For now, return a placeholder
    summary = summarize_messages(messages)
    
    return schemas.ChannelSummaryResponse(summary=summary)

# @router.post("/ai/persona/{receiver_id}", response_model=List[schemas.Message])
# async def create_ai_persona_message(
#     receiver_id: int,
#     message: schemas.MessageCreate,
#     channel_id: int,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     """Create a message from the sender and an AI-generated response that appears to be from the receiver"""
#     # Verify channel exists and sender has access
#     db_channel = get_channel(db, channel_id=channel_id)
#     if db_channel is None:
#         raise HTTPException(status_code=404, detail="Channel not found")
#     if current_user.id not in [user.id for user in db_channel.users]:
#         raise HTTPException(status_code=403, detail="Not a member of this channel")

#     # Verify receiver exists and is in the channel
#     if receiver_id not in [user.id for user in db_channel.users]:
#         raise HTTPException(status_code=404, detail="Receiver not found in channel")

#     # Update user activity
#     await events.update_user_activity(current_user.id)

#     # Create the sender's message
#     sender_message = create_message(
#         db=db,
#         channel_id=channel_id,
#         user_id=current_user.id,
#         message=message
#     )

#     # Broadcast the sender's message
#     await events.broadcast_message_created(channel_id, sender_message, current_user)

#     # TODO: Generate AI response based on the input message
#     # ai_response = generate_ai_response(message.content, receiver_id, current_user.id)
#     # For now, use a generic response
#     ai_response = "This response message is from an AI!"

#     # Create the AI response message as if it's from the receiver
#     ai_db_message = create_message(
#         db=db,
#         channel_id=channel_id,
#         user_id=receiver_id,  # Use receiver's ID as the message author
#         message=ai_response,
#         from_ai=True
#     )

#     # Broadcast the AI response message
#     await events.broadcast_message_created(channel_id, ai_db_message, receiver_id)
    
#     # Return both messages in order
#     return [sender_message, ai_db_message]