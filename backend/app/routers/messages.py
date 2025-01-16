from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import magic
import uuid
from datetime import datetime
import boto3
from botocore.config import Config
import os

from .. import models, schemas
from ..database import get_db
from ..auth0 import get_current_user
from ..events_manager import events
from ..embedding_service import embedding_service
from ..crud.messages import (
    create_message,
    update_message,
    delete_message,
    get_channel_messages,
    get_message,
    create_reply,
    get_message_reply_chain
)
from ..crud.channels import get_channel, user_in_channel

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME', '')
AWS_S3_REGION = os.getenv('AWS_S3_REGION', 'us-east-2')
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '50'))
ALLOWED_FILE_TYPES = os.getenv('ALLOWED_FILE_TYPES', 'image/*,application/pdf,text/*').split(',')

s3_client = boto3.client(
    's3',
    region_name=AWS_S3_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    config=Config(s3={'addressing_style': 'virtual'}, signature_version='s3v4')
)

def validate_file_type(content_type: str) -> bool:
    """Validate if the file type is allowed based on ALLOWED_FILE_TYPES."""
    for allowed_type in ALLOWED_FILE_TYPES:
        if allowed_type.endswith('/*'):
            if content_type.split('/')[0] == allowed_type.split('/')[0]:
                return True
        elif content_type == allowed_type:
            return True
    return False

def generate_s3_key(filename: str, message_id: int) -> str:
    """Generate a unique S3 key for the file."""
    timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    extension = os.path.splitext(filename)[1]
    return f"messages/{message_id}/{timestamp}-{unique_id}{extension}"

@router.post("/{channel_id}/messages", response_model=schemas.Message)
async def create_message_endpoint(
    channel_id: int,
    message: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_channel = get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [user.id for user in db_channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    # Update user activity when sending a message
    await events.update_user_activity(current_user.id)
    
    db_message = create_message(
        db=db,
        channel_id=channel_id,
        user_id=current_user.id,
        message=message
    )

    # Broadcast the new message to all users in the channel
    await events.broadcast_message_created(channel_id, db_message, current_user)
    
    return db_message

@router.get("/{channel_id}/messages", response_model=schemas.MessageList)
async def get_channel_messages_endpoint(
    channel_id: int,
    skip: int = 0,
    limit: int = 50,
    include_reactions: bool = False,
    parent_only: bool = True,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify channel access
    channel = get_channel(db, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    if not user_in_channel(db, current_user.id, channel_id):
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    # Update user activity when fetching messages
    await events.update_user_activity(current_user.id)
    
    return get_channel_messages(
        db=db,
        channel_id=channel_id,
        skip=skip,
        limit=limit,
        include_reactions=include_reactions,
        parent_only=parent_only
    )

@router.put("/{channel_id}/messages/{message_id}", response_model=schemas.Message)
async def update_message_endpoint(
    channel_id: int,
    message_id: int,
    message: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if message exists and user has permission
    db_message = get_message(db, message_id=message_id)
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    if db_message.channel_id != channel_id:
        raise HTTPException(status_code=400, detail="Message does not belong to this channel")
    if db_message.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the message author can edit the message")
    
    # Update user activity when editing a message
    await events.update_user_activity(current_user.id)
    
    # Update the message
    updated_message = update_message(db=db, message_id=message_id, message_update=message)
    
    # Broadcast the update to all users in the channel
    await events.broadcast_message_update(channel_id, updated_message, current_user)
    
    return updated_message

@router.delete("/{channel_id}/messages/{message_id}", response_model=schemas.Message)
async def delete_message_endpoint(
    channel_id: int,
    message_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if message exists and user has permission
    db_message = get_message(db, message_id=message_id)
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    if db_message.channel_id != channel_id:
        raise HTTPException(status_code=400, detail="Message does not belong to this channel")
    if db_message.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the message author can delete the message")
    
    # Update user activity when deleting a message
    await events.update_user_activity(current_user.id)
    
    # Delete the message
    deleted_message = delete_message(db=db, message_id=message_id)
    
    # Broadcast the deletion to all users in the channel
    await events.broadcast_message_delete(channel_id, message_id)
    
    return deleted_message

@router.post("/{channel_id}/messages/{parent_id}/reply", response_model=schemas.Message)
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
    channel = get_channel(db, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    if not user_in_channel(db, current_user.id, channel_id):
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    # Update user activity when replying to a message
    await events.update_user_activity(current_user.id)
    
    # Verify parent message exists and belongs to this channel
    parent_message = get_message(db, message_id=parent_id)
    if not parent_message:
        raise HTTPException(status_code=404, detail="Parent message not found")
    if parent_message.channel_id != channel_id:
        raise HTTPException(status_code=400, detail="Parent message does not belong to this channel")
    
    # Create the reply
    reply, root_message = create_reply(
        db=db,
        parent_id=parent_id,
        user_id=current_user.id,
        message=message
    )
    
    if not reply or not root_message:
        raise HTTPException(status_code=400, detail="Could not create reply")
    
    # Broadcast the new reply message to all users in the channel
    await events.broadcast_message_created(channel_id, reply, current_user)
    
    # Also broadcast an update to the root message to show it has replies
    await events.broadcast_root_message_update(channel_id, root_message)
    
    return reply

@router.get("/{message_id}/reply-chain", response_model=List[schemas.Message])
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
    message = get_message(db, message_id=message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Verify user has access to the channel
    if not user_in_channel(db, current_user.id, message.channel_id):
        raise HTTPException(status_code=403, detail="Not a member of the channel containing this message")
    
    # Update user activity when fetching reply chain
    await events.update_user_activity(current_user.id)
    
    # Get the reply chain
    reply_chain = get_message_reply_chain(db, message_id=message_id)
    
    return reply_chain

@router.post("/{channel_id}/messages/with-file", response_model=schemas.Message)
async def create_message_with_file(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    file: Optional[UploadFile] = File(None),
    content: Optional[str] = Form(None),
    parent_id: Optional[int] = Form(None),
):
    """
    Creates a message (optionally a reply, if parent_id provided) and an optional file 
    in one request, attaching the file to the newly created message.
    """
    # Validate channel membership
    db_channel = get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [u.id for u in db_channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    # Update user activity when sending a message with file
    await events.update_user_activity(current_user.id)
    
    # If there's no text content and no file, cannot create an empty message
    if (not content or not content.strip()) and not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create an empty message with no file and no text."
        )

    # If parent_id is provided, treat it as a reply flow
    if parent_id:
        parent_msg = get_message(db, message_id=parent_id)
        if not parent_msg:
            raise HTTPException(status_code=404, detail="Parent message not found")
        if parent_msg.channel_id != channel_id:
            raise HTTPException(status_code=400, detail="Parent message not in this channel")
        # Use the existing create_reply logic
        db_message, root_message = create_reply(
            db=db,
            parent_id=parent_id,
            user_id=current_user.id,
            message=schemas.MessageReplyCreate(content=content or "")
        )
    else:
        # Create a brand-new message
        message_data = schemas.MessageCreate(content=content or "")
        db_message = create_message(
            db=db,
            channel_id=channel_id,
            user_id=current_user.id,
            message=message_data
        )
        
        logger.info(f"Created message (ID: {db_message.id}) for channel {channel_id} by user {current_user.id}")

        # Broadcast the new message to all users in the channel
        await events.broadcast_message_created(channel_id, db_message, current_user)

    # Handle file if present
    if file:
        # Read file
        file_bytes = await file.read()

        # Validate file size
        if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE_MB}MB"
            )

        # Validate file type
        mime = magic.Magic(mime=True)
        content_type = mime.from_buffer(file_bytes)
        if not validate_file_type(content_type):
            raise HTTPException(status_code=400, detail=f"File type {content_type} not allowed")

        # Generate S3 key (includes the newly created message id)
        s3_key = generate_s3_key(file.filename, db_message.id)

        # Upload to S3
        try:
            s3_client.put_object(
                Bucket=AWS_S3_BUCKET_NAME,
                Key=s3_key,
                Body=file_bytes,
                ContentType=content_type
            )
        except Exception as e:
            logger.error(f"S3 upload error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to upload file to storage"
            )
        
        # Create file record (FileUpload model)
        file_upload = models.FileUpload(
            message_id=db_message.id,
            file_name=file.filename,
            s3_key=s3_key,
            content_type=content_type,
            file_size=len(file_bytes),
            uploaded_by=current_user.id
        )
        db.add(file_upload)
        db.commit()
        db.refresh(file_upload)

        embed_metadata = {
            "file_name": file.filename,
            "has_file": True
        }
        embedding_service.update_metadata(db_message.vector_id, embed_metadata)
        
        logger.info(f"Attached file (ID: {file_upload.id}) to message {db_message.id}")

    # Now refresh the message to include files in the response
    db.refresh(db_message)
    return db_message

@router.post("/{channel_id}/messages/{parent_id}/reply-with-file", response_model=schemas.Message)
async def create_reply_message_with_file(
    channel_id: int,
    parent_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    file: Optional[UploadFile] = File(None),
    content: Optional[str] = Form(None),
):
    """
    Creates a reply to the given parent message in the specified channel 
    and optionally attaches a file, all in one request.
    """
    # Validate channel membership
    db_channel = get_channel(db, channel_id=channel_id)
    if not db_channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    if current_user.id not in [u.id for u in db_channel.users]:
        raise HTTPException(status_code=403, detail="Not a member of this channel")

    # Update user activity when replying with file
    await events.update_user_activity(current_user.id)

    # Check parent message
    parent_msg = get_message(db, message_id=parent_id)
    if not parent_msg:
        raise HTTPException(status_code=404, detail="Parent message not found")
    if parent_msg.channel_id != channel_id:
        raise HTTPException(status_code=400, detail="Parent message not in this channel")

    # If there's no text content and no file, cannot create an empty message
    if (not content or not content.strip()) and not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create an empty reply with no file and no text."
        )

    # Use existing create_reply logic
    db_message, root_message = create_reply(
        db=db,
        parent_id=parent_id,
        user_id=current_user.id,
        message=schemas.MessageReplyCreate(content=content or "")
    )

    logger.info(
        f"Created reply message (ID: {db_message.id}) "
        f"to parent (ID: {parent_id}) in channel {channel_id} by user {current_user.id}"
    )

    # Handle file if present
    if file:
        # Read file
        file_bytes = await file.read()

        # Validate file size
        if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE_MB}MB"
            )

        # Validate file type
        mime = magic.Magic(mime=True)
        content_type = mime.from_buffer(file_bytes)
        if not validate_file_type(content_type):
            raise HTTPException(status_code=400, detail=f"File type {content_type} not allowed")

        # Generate S3 key (includes the newly created message id)
        s3_key = generate_s3_key(file.filename, db_message.id)

        # Upload to S3
        try:
            s3_client.put_object(
                Bucket=AWS_S3_BUCKET_NAME,
                Key=s3_key,
                Body=file_bytes,
                ContentType=content_type
            )
        except Exception as e:
            logger.error(f"S3 upload error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to upload file to storage"
            )
        
        # Create file record
        file_upload = models.FileUpload(
            message_id=db_message.id,
            file_name=file.filename,
            s3_key=s3_key,
            content_type=content_type,
            file_size=len(file_bytes),
            uploaded_by=current_user.id
        )
        db.add(file_upload)
        db.commit()
        db.refresh(file_upload)

        embed_metadata = {
            "file_name": file.filename,
            "has_file": True
        }
        embedding_service.update_metadata(db_message.vector_id, embed_metadata)

        logger.info(f"Attached file (ID: {file_upload.id}) to reply (message {db_message.id})")

    # Broadcast the new reply message to all users in the channel
    await events.broadcast_message_created(channel_id, db_message, current_user)
    
    # Also broadcast an update to the root message to show it has replies
    await events.broadcast_root_message_update(channel_id, root_message)

    # Refresh to include attached files in the response
    db.refresh(db_message)
    return db_message 