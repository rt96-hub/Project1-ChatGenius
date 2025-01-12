import os
import boto3
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
import magic
import logging
from dotenv import load_dotenv

import models
import schemas
import crud
from database import get_db
from auth0 import get_current_user
from websocket_manager import manager  # Import from new location

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')
AWS_S3_REGION = os.getenv('AWS_S3_REGION', 'us-east-1')

# File upload configurations
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '50'))  # Default 50MB
ALLOWED_FILE_TYPES = os.getenv('ALLOWED_FILE_TYPES', 'image/*,application/pdf,text/*').split(',')

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_S3_REGION
)

router = APIRouter()

def validate_file_type(content_type: str) -> bool:
    """Validate if the file type is allowed"""
    for allowed_type in ALLOWED_FILE_TYPES:
        if allowed_type.endswith('/*'):
            # Check main type for wildcards (e.g., image/*)
            if content_type.split('/')[0] == allowed_type.split('/')[0]:
                return True
        elif content_type == allowed_type:
            return True
    return False

def generate_s3_key(filename: str, message_id: int) -> str:
    """Generate a unique S3 key for the file"""
    timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    extension = os.path.splitext(filename)[1]
    return f"messages/{message_id}/{timestamp}-{unique_id}{extension}"

@router.post("/files/upload", response_model=schemas.FileUpload)
async def upload_file(
    file: UploadFile = File(...),
    message_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Upload a file and attach it to a message"""
    try:
        # Verify message exists and user has access
        message = crud.get_message(db, message_id=message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        if not crud.user_in_channel(db, current_user.id, message.channel_id):
            raise HTTPException(status_code=403, detail="Not a member of this channel")
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        file_size = len(content)
        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE_MB}MB"
            )
        
        # Validate file type using python-magic
        mime = magic.Magic(mime=True)
        content_type = mime.from_buffer(content)
        if not validate_file_type(content_type):
            raise HTTPException(
                status_code=400,
                detail=f"File type {content_type} not allowed"
            )
        
        # Generate S3 key
        s3_key = generate_s3_key(file.filename, message_id)
        
        # Upload to S3
        try:
            s3_client.put_object(
                Bucket=AWS_S3_BUCKET_NAME,
                Key=s3_key,
                Body=content,
                ContentType=content_type
            )
        except Exception as e:
            logger.error(f"S3 upload error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to upload file to storage"
            )
        
        # Create file upload record
        file_upload = models.FileUpload(
            message_id=message_id,
            file_name=file.filename,
            s3_key=s3_key,
            content_type=content_type,
            file_size=file_size,
            uploaded_by=current_user.id
        )
        
        db.add(file_upload)
        db.commit()
        db.refresh(file_upload)
        
        # Broadcast file upload event
        await manager.broadcast_file_upload(message.channel_id, file_upload, message)
        
        return file_upload
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )

@router.get("/files/{file_id}/download-url")
async def get_download_url(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Generate a presigned URL for file download"""
    try:
        # Get file upload record
        file_upload = db.query(models.FileUpload).filter(
            models.FileUpload.id == file_id,
            models.FileUpload.is_deleted == False
        ).first()
        
        if not file_upload:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Verify user has access to the channel containing the message
        message = crud.get_message(db, message_id=file_upload.message_id)
        if not crud.user_in_channel(db, current_user.id, message.channel_id):
            raise HTTPException(status_code=403, detail="Not authorized to access this file")
        
        # Generate presigned URL
        try:
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': AWS_S3_BUCKET_NAME,
                    'Key': file_upload.s3_key,
                    'ResponseContentDisposition': f'attachment; filename="{file_upload.file_name}"'
                },
                ExpiresIn=3600  # URL expires in 1 hour
            )
            return {"download_url": url}
        except Exception as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate download URL"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download URL generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate download URL: {str(e)}"
        )

@router.delete("/files/{file_id}")
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Soft delete a file upload"""
    try:
        # Get file upload record
        file_upload = db.query(models.FileUpload).filter(
            models.FileUpload.id == file_id,
            models.FileUpload.is_deleted == False
        ).first()
        
        if not file_upload:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get message for channel ID
        message = crud.get_message(db, message_id=file_upload.message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Associated message not found")
        
        # Verify user is the uploader or has appropriate permissions
        if file_upload.uploaded_by != current_user.id:
            if message.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized to delete this file")
        
        # Soft delete the file
        file_upload.is_deleted = True
        db.commit()
        
        # Broadcast file deletion event
        await manager.broadcast_file_deleted(message.channel_id, file_id, file_upload.message_id)
        
        return {"message": "File deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File deletion error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        ) 