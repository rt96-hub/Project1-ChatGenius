from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import logging

from .. import models, schemas
from ..llm_chat_service import ai_response

logger = logging.getLogger(__name__)





def get_conversation(db: Session, conversation_id: int, user_id: int) -> Optional[models.AIConversation]:
    """Get a single AI conversation by ID"""
    return (db.query(models.AIConversation)
            .filter(models.AIConversation.id == conversation_id,
                   models.AIConversation.user_id == user_id)
            .first())

def get_channel_conversations(
    db: Session, 
    channel_id: int, 
    user_id: int,
    skip: int = 0,
    limit: int = 50
) -> List[models.AIConversation]:
    """Get all AI conversations for a channel"""
    return (db.query(models.AIConversation)
            .filter(models.AIConversation.channel_id == channel_id,
                   models.AIConversation.user_id == user_id)
            .order_by(desc(models.AIConversation.last_message))
            .offset(skip)
            .limit(limit)
            .all())

def create_conversation(
    db: Session,
    channel_id: int,
    user_id: int,
    initial_message: str
) -> models.AIConversation:
    """Create a new AI conversation with initial message"""
    # Create conversation
    conversation = models.AIConversation(
        channel_id=channel_id,
        user_id=user_id
    )
    db.add(conversation)
    db.flush()  # Get the ID without committing

    # Add initial user message
    user_message = models.AIMessage(
        conversation_id=conversation.id,
        channel_id=channel_id,
        user_id=user_id,
        role='user',
        message=initial_message
    )
    db.add(user_message)
    db.flush()
    
    # TODO: later will pass search results to frontend
    ai_response_message, search_results_list = ai_response(initial_message, channel_id, user_id)
    ai_message = create_ai_message(
        db=db,
        conversation_id=conversation.id,
        channel_id=channel_id,
        user_id=user_id,
        message=ai_response_message,
        role='assistant'
    )

    db.commit()
    db.refresh(conversation)
    return conversation

def create_ai_message(
    db: Session,
    conversation_id: int,
    channel_id: int,
    user_id: int,
    message: str,
    role: str,
    parameters: Optional[dict] = None
) -> models.AIMessage:
    """Create a new AI message"""
    message = models.AIMessage(
        conversation_id=conversation_id,
        channel_id=channel_id,
        user_id=user_id,
        role=role,
        message=message,
        parameters=parameters
    )
    db.add(message)
    
    # Update conversation last_message timestamp
    conversation = get_conversation(db, conversation_id, user_id)
    if conversation:
        conversation.last_message = message.created_at
    
    db.commit()
    db.refresh(message)
    return message

def add_message_to_conversation(
    db: Session,
    conversation_id: int,
    channel_id: int,
    user_id: int,
    message: str
) -> models.AIConversation:
    """Add a new message to an existing conversation"""
    # Add user message
    user_message = create_ai_message(
        db=db,
        conversation_id=conversation_id,
        channel_id=channel_id,
        user_id=user_id,
        message=message,
        role='user'
    )

    # TODO: later will pass search results to frontend
    ai_response_message, search_results_list = ai_response(message, channel_id, user_id)
    ai_message = create_ai_message(
        db=db,
        conversation_id=conversation_id,
        channel_id=channel_id,
        user_id=user_id,
        message=ai_response_message,
        role='assistant'
    )

    conversation = get_conversation(db, conversation_id, user_id)
    return conversation 
