import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
import os

from .. import models, schemas
from ..database import get_db
from ..auth0 import get_current_user
from ..crud.channels import get_user_channels
from ..crud.messages import get_message

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Search rate limiting configurations
MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_SEARCH_REQUESTS_PER_MINUTE', '60'))
CACHE_EXPIRATION_SECONDS = int(os.getenv('SEARCH_CACHE_EXPIRATION_SECONDS', '300'))  # 5 minutes

def validate_date_params(from_date: Optional[datetime], to_date: Optional[datetime]):
    """Validate date range parameters"""
    if from_date and to_date and from_date > to_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="from_date must be before to_date"
        )

@router.get("/search/messages", response_model=schemas.MessageList)
async def search_messages(
    query: str,
    channel_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    from_user: Optional[int] = None,
    limit: int = Query(default=50, le=100),
    skip: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Search through message content across all accessible channels"""
    try:
        validate_date_params(from_date, to_date)
        
        # Get user's accessible channels
        accessible_channels = get_user_channels(db, user_id=current_user.id)
        channel_ids = [channel.id for channel in accessible_channels]
        
        if not channel_ids:
            return {"messages": [], "total": 0, "has_more": False}
        
        # Build base query
        query_filters = [
            models.Message.channel_id.in_(channel_ids),
            models.Message.is_deleted == False
        ]
        
        # Add optional filters
        if channel_id:
            if channel_id not in channel_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to search in this channel"
                )
            query_filters.append(models.Message.channel_id == channel_id)
        
        if from_date:
            query_filters.append(models.Message.created_at >= from_date)
        if to_date:
            query_filters.append(models.Message.created_at <= to_date)
        if from_user:
            query_filters.append(models.Message.user_id == from_user)
        
        # Execute search query
        messages = db.query(models.Message).filter(
            and_(*query_filters),
            models.Message.content.match(query)  # Using PostgreSQL full-text search
        ).order_by(
            getattr(models.Message, sort_by).desc() if sort_order == "desc"
            else getattr(models.Message, sort_by)
        ).offset(skip).limit(limit + 1).all()  # Get one extra to check has_more
        
        has_more = len(messages) > limit
        if has_more:
            messages = messages[:-1]  # Remove the extra item
        
        # Get total count
        total = db.query(func.count(models.Message.id)).filter(
            and_(*query_filters),
            models.Message.content.match(query)
        ).scalar()
        
        return {"messages": messages, "total": total, "has_more": has_more}
    
    except Exception as e:
        logger.error(f"Message search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/search/users")
async def search_users(
    query: str,
    exclude_channel: Optional[int] = None,
    only_channel: Optional[int] = None,
    limit: int = Query(default=50, le=100),
    skip: int = 0,
    sort_by: str = "name",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Search for users by name or email"""
    try:
        # Build base query
        base_query = db.query(models.User).filter(
            models.User.is_active == True,
            or_(
                models.User.name.ilike(f"%{query}%"),
                models.User.email.ilike(f"%{query}%")
            )
        )
        
        # Add channel filters
        if exclude_channel:
            base_query = base_query.filter(
                ~models.User.channels.any(models.Channel.id == exclude_channel)
            )
        if only_channel:
            base_query = base_query.filter(
                models.User.channels.any(models.Channel.id == only_channel)
            )
        
        # Execute query with one extra to check has_more
        users = base_query.order_by(
            getattr(models.User, sort_by).desc() if sort_order == "desc"
            else getattr(models.User, sort_by)
        ).offset(skip).limit(limit + 1).all()
        
        has_more = len(users) > limit
        if has_more:
            users = users[:-1]  # Remove the extra item
        
        # Get total count
        total = base_query.count()
        
        return {"users": users, "total": total, "has_more": has_more}
    
    except Exception as e:
        logger.error(f"User search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/search/channels")
async def search_channels(
    query: str,
    include_private: bool = False,
    is_dm: Optional[bool] = None,
    member_id: Optional[int] = None,
    limit: int = Query(default=50, le=100),
    skip: int = 0,
    sort_by: str = "name",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Search for channels by name or description"""
    try:
        # Build base query
        query_filters = [
            or_(
                models.Channel.name.ilike(f"%{query}%"),
                models.Channel.description.ilike(f"%{query}%")
            ),
        ]
        
        # Add DM filter if specified
        if is_dm is not None:
            query_filters.append(models.Channel.is_dm == is_dm)
        
        if not include_private:
            query_filters.append(models.Channel.is_private == False)
        
        base_query = db.query(models.Channel).filter(and_(*query_filters))
        
        if member_id:
            base_query = base_query.filter(
                models.Channel.users.any(models.User.id == member_id)
            )
        
        # Execute query with one extra to check has_more
        channels = base_query.order_by(
            getattr(models.Channel, sort_by).desc() if sort_order == "desc"
            else getattr(models.Channel, sort_by)
        ).offset(skip).limit(limit + 1).all()
        
        has_more = len(channels) > limit
        if has_more:
            channels = channels[:-1]  # Remove the extra item
        
        # Get total count
        total = base_query.count()
        
        # Add member count to each channel
        for channel in channels:
            channel.member_count = len(channel.users)
        
        return {"channels": channels, "total": total, "has_more": has_more}
    
    except Exception as e:
        logger.error(f"Channel search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/search/files")
async def search_files(
    query: str,
    channel_id: Optional[int] = None,
    file_type: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    uploaded_by: Optional[int] = None,
    limit: int = Query(default=50, le=100),
    skip: int = 0,
    sort_by: str = "uploaded_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Search for files by name or associated message content"""
    try:
        validate_date_params(from_date, to_date)
        
        # Get user's accessible channels
        accessible_channels = get_user_channels(db, user_id=current_user.id)
        channel_ids = [channel.id for channel in accessible_channels]
        
        if not channel_ids:
            return {"files": [], "total": 0, "has_more": False}
        
        # Build base query
        query_filters = [
            models.FileUpload.is_deleted == False,
            models.Message.channel_id.in_(channel_ids)
        ]
        
        # Add search conditions
        query_filters.append(
            or_(
                models.FileUpload.file_name.ilike(f"%{query}%"),
                models.Message.content.match(query)
            )
        )
        
        # Add optional filters
        if channel_id:
            if channel_id not in channel_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to search in this channel"
                )
            query_filters.append(models.Message.channel_id == channel_id)
        
        if file_type:
            query_filters.append(models.FileUpload.content_type.ilike(f"%{file_type}%"))
        
        if from_date:
            query_filters.append(models.FileUpload.uploaded_at >= from_date)
        if to_date:
            query_filters.append(models.FileUpload.uploaded_at <= to_date)
        if uploaded_by:
            query_filters.append(models.FileUpload.uploaded_by == uploaded_by)
        
        # Execute query with one extra to check has_more
        files = db.query(models.FileUpload).join(
            models.Message,
            models.FileUpload.message_id == models.Message.id
        ).filter(
            and_(*query_filters)
        ).order_by(
            getattr(models.FileUpload, sort_by).desc() if sort_order == "desc"
            else getattr(models.FileUpload, sort_by)
        ).offset(skip).limit(limit + 1).all()
        
        has_more = len(files) > limit
        if has_more:
            files = files[:-1]  # Remove the extra item
        
        # Get total count
        total = db.query(func.count(models.FileUpload.id)).join(
            models.Message,
            models.FileUpload.message_id == models.Message.id
        ).filter(
            and_(*query_filters)
        ).scalar()
        
        # Add message content to each file
        for file in files:
            message = db.query(models.Message).filter(models.Message.id == file.message_id).first()
            file.message_content = message.content if message else None
            file.channel_id = message.channel_id if message else None
        
        return {"files": files, "total": total, "has_more": has_more}
    
    except Exception as e:
        logger.error(f"File search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        ) 