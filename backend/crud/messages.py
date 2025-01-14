from sqlalchemy.orm import Session, joinedload
import logging
from typing import List, Optional, Tuple

from ..models import Message, User, MessageReaction
from .. import schemas
from ..embedding_service import embedding_service

logger = logging.getLogger(__name__)

def create_message(db: Session, channel_id: int, user_id: int, message: schemas.MessageCreate):
    """Create a new message and generate its embedding"""
    db_message = Message(
        content=message.content,
        channel_id=channel_id,
        user_id=user_id
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    try:
        # Generate embedding and get vector_id
        vector_id = embedding_service.create_message_embedding(
            message_content=db_message.content,
            message_id=db_message.id,
            user_id=user_id,
            channel_id=channel_id,
            parent_id=None,  # This is a parent message
            file_name=None  # Add file handling later if needed
        )
        
        # Update message with vector_id
        db_message.vector_id = vector_id
        db.commit()
        db.refresh(db_message)
        logger.info(f"Created message {db_message.id} with vector_id {vector_id}")
    except Exception as e:
        logger.error(f"Error creating message embedding: {e}")
        # Don't fail the message creation if embedding fails
        # We can add a background task to retry later if needed
    
    return db_message

def update_message(db: Session, message_id: int, message_update: schemas.MessageCreate) -> Message:
    """Update a message and its embedding"""
    db_message = db.query(Message).filter(Message.id == message_id).first()
    if not db_message:
        return None
    
    # Store old content in case we need to rollback
    old_content = db_message.content
    
    try:
        # Update message content
        db_message.content = message_update.content
        db.commit()
        db.refresh(db_message)

        # Only update embedding if we have a vector_id
        if db_message.vector_id:            
            # Update the embedding
            embedding_service.update_message_embedding(
                vector_id=db_message.vector_id,
                new_content=message_update.content,
                message_id=message_id,
                has_file=bool(db_message.files),
                file_name=db_message.files[0].file_name if db_message.files else None,
                parent_id=db_message.parent_id
            )
            logger.info(f"Updated message {message_id} embedding")
    except Exception as e:
        logger.error(f"Error updating message embedding: {e}")
        # Rollback content update if embedding update fails
        db_message.content = old_content
        db.commit()
        db.refresh(db_message)
        raise
    
    return db_message

def delete_message(db: Session, message_id: int) -> Message:
    """Delete a message and its embedding"""
    db_message = (db.query(Message)
                 .filter(Message.id == message_id)
                 .options(joinedload(Message.user))
                 .first())
    if not db_message:
        return None
    
    # Create a copy of the message with its relationships
    message_copy = schemas.Message.from_orm(db_message)
    
    try:
        # Delete embedding first if it exists
        if db_message.vector_id:
            embedding_service.delete_message_embedding(db_message.vector_id)
            logger.info(f"Deleted embedding for message {message_id}")
        
        # Then delete the message
        db.delete(db_message)
        db.commit()
    except Exception as e:
        logger.error(f"Error deleting message embedding: {e}")
        # Continue with message deletion even if embedding deletion fails
        db.delete(db_message)
        db.commit()
    
    return message_copy

def get_channel_messages(db: Session, channel_id: int, skip: int = 0, limit: int = 50, include_reactions: bool = False, parent_only: bool = True):
    # Start with base query
    query = db.query(Message).filter(Message.channel_id == channel_id)
    
    # Add parent_only filter if requested
    if parent_only:
        query = query.filter(Message.parent_id.is_(None))
    
    # Add eager loading for user and parent
    query = query.options(
        joinedload(Message.user),
        joinedload(Message.parent).joinedload(Message.user)
    )
    
    if include_reactions:
        # Add eager loading for reactions and their related data
        query = query.options(
            joinedload(Message.reactions)
            .joinedload(MessageReaction.reaction),
            joinedload(Message.reactions)
            .joinedload(MessageReaction.user)
        )
    
    # Get messages with pagination
    messages = (query
               .order_by(Message.created_at.desc())
               .offset(skip)
               .limit(limit + 1)  # Get one extra to check if there are more
               .all())
    
    # Check if there are more messages
    has_more = len(messages) > limit
    messages = messages[:limit]  # Trim to requested limit
    
    # Get total count (respecting parent_only filter)
    total_query = db.query(Message).filter(Message.channel_id == channel_id)
    if parent_only:
        total_query = total_query.filter(Message.parent_id.is_(None))
    total = total_query.count()
    
    # Add has_replies information for each message
    message_ids = [m.id for m in messages]
    replies_exist = (
        db.query(Message.parent_id)
        .filter(Message.parent_id.in_(message_ids))
        .distinct()
        .all()
    )
    messages_with_replies = {r[0] for r in replies_exist}
    
    # Set has_replies flag for each message
    for message in messages:
        message.has_replies = message.id in messages_with_replies
    
    return schemas.MessageList(
        messages=messages,
        total=total,
        has_more=has_more
    )

def get_message(db: Session, message_id: int) -> Message:
    return db.query(Message).filter(Message.id == message_id).first()

def find_last_reply_in_chain(db: Session, message_id: int) -> Message:
    """
    Recursively find the last message in a reply chain.
    Returns the last message that doesn't have a reply.
    """
    current_message = db.query(Message).filter(Message.id == message_id).first()
    if not current_message:
        return None
    
    # Follow the reply chain until we find a message with no reply
    while True:
        reply = db.query(Message).filter(Message.parent_id == current_message.id).first()
        if not reply:
            return current_message
        current_message = reply

def create_reply(db: Session, parent_id: int, user_id: int, message: schemas.MessageReplyCreate) -> Tuple[Message, Message]:
    """
    Create a reply to a message. If the parent message already has a reply,
    the new message will be attached to the last message in the chain.
    Returns a tuple of (reply_message, root_message).
    Create a reply message with embedding
    """
    # First check if parent message exists
    parent_message = db.query(Message).filter(Message.id == parent_id).first()
    if not parent_message:
        return None, None
    
    # Find the last message in the reply chain
    last_message = find_last_reply_in_chain(db, parent_id)
    
    # Create the new reply message
    db_message = Message(
        content=message.content,
        channel_id=parent_message.channel_id,
        user_id=user_id,
        parent_id=last_message.id
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    try:
        # Generate embedding for the reply
        vector_id = embedding_service.create_message_embedding(
            message_content=db_message.content,
            message_id=db_message.id,
            user_id=user_id,
            channel_id=parent_message.channel_id,
            parent_id=last_message.id,
            file_name=None
        )
        
        # Update message with vector_id
        db_message.vector_id = vector_id
        db.commit()
        db.refresh(db_message)
        logger.info(f"Created reply message {db_message.id} with vector_id {vector_id}")
    except Exception as e:
        logger.error(f"Error creating reply message embedding: {e}")
        # Don't fail the reply creation if embedding fails
    
    # Get the root message (the one with no parent)
    root_message = parent_message
    while root_message.parent_id is not None:
        root_message = db.query(Message).filter(Message.id == root_message.parent_id).first()
    
    # Refresh root message to ensure we have the latest data
    db.refresh(root_message)
    
    return db_message, root_message

def get_message_reply_chain(db: Session, message_id: int) -> List[Message]:
    """
    Get all messages in a reply chain, including:
    1. The original message
    2. All parent messages (if the given message is a reply)
    3. All reply messages (if any message has replies)
    Returns messages ordered by created_at date.
    """
    # First, get the original message
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        return []
    
    # Get all messages in the chain
    chain_messages = []
    
    # If this message has a parent, traverse up to find the root
    current = message
    while current.parent_id is not None:
        parent = db.query(Message).filter(Message.id == current.parent_id).first()
        if not parent:
            break
        chain_messages.append(parent)
        current = parent
    
    # Add the original message
    chain_messages.append(message)
    
    # Find all replies in the chain
    current = message
    while True:
        reply = db.query(Message).filter(Message.parent_id == current.id).first()
        if not reply:
            break
        chain_messages.append(reply)
        current = reply
    
    # Sort all messages by created_at
    chain_messages.sort(key=lambda x: x.created_at)
    
    # Eager load user data for each message
    message_ids = [m.id for m in chain_messages]
    return (db.query(Message)
            .filter(Message.id.in_(message_ids))
            .options(joinedload(Message.user))
            .order_by(Message.created_at)
            .all()) 