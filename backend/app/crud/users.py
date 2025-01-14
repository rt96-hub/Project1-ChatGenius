from sqlalchemy.orm import Session
from sqlalchemy import func
import logging
from typing import Optional

from .. import models, schemas

logger = logging.getLogger(__name__)

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_auth0_id(db: Session, auth0_id: str):
    return db.query(models.User).filter(models.User.auth0_id == auth0_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_personal_channel(db: Session, user: models.User) -> models.Channel:
    """
    Create a personal private channel for a user.
    
    Args:
        db (Session): SQLAlchemy database session
        user (User): The user to create the channel for
        
    Returns:
        Channel: The created personal channel
    """
    try:
        # Build channel name in the format "<UserName>-Personal"
        channel_name = f"{user.name}-Personal"

        # Create channel object
        personal_channel = models.Channel(
            name=channel_name,
            description=f"Personal channel for {user.name}. Search for other public channels in the sidebar",
            owner_id=user.id,
            is_private=True,
            is_dm=False  # treat it as a private channel, not a DM
        )

        db.add(personal_channel)
        db.commit()
        db.refresh(personal_channel)

        # Add user to channel membership
        user_channel = models.UserChannel(user_id=user.id, channel_id=personal_channel.id)
        db.add(user_channel)
        db.commit()
        db.refresh(personal_channel)

        logger.info(f"Created personal channel for user {user.name}")
        return personal_channel
    except Exception as e:
        logger.error(f"Error creating personal channel: {str(e)}", exc_info=True)
        db.rollback()
        raise

def sync_auth0_user(db: Session, user_data: schemas.UserCreate):
    try:
        # Check if user exists
        db_user = get_user_by_auth0_id(db, user_data.auth0_id)
        
        if db_user:
            # Update existing user
            db_user.email = user_data.email
            db_user.name = user_data.name
            db_user.picture = user_data.picture
            db.commit()
            db.refresh(db_user)
            return db_user
        
        # Create new user
        db_user = models.User(
            auth0_id=user_data.auth0_id,
            email=user_data.email,
            name=user_data.name,
            picture=user_data.picture
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Create personal channel for new user
        create_personal_channel(db, db_user)
        
        return db_user
    except Exception as e:
        logger.error(f"Error in sync_auth0_user: {str(e)}", exc_info=True)
        raise

def update_user_bio(db: Session, user_id: int, bio: str):
    db_user = get_user(db, user_id)
    if db_user:
        db_user.bio = bio
        db.commit()
        db.refresh(db_user)
    return db_user

def update_user_name(db: Session, user_id: int, name: str):
    db_user = get_user(db, user_id)
    if db_user:
        db_user.name = name
        db.commit()
        db.refresh(db_user)
    return db_user 

def get_users_by_last_dm(db: Session, current_user_id: int, skip: int = 0, limit: int = 100):
    """Get users ordered by their last one-on-one DM interaction with the current user.
    Users with no DM history appear first (NULL last_message_at),
    followed by users ordered by ascending last message date.
    Only includes one-on-one DMs (channels with exactly 2 users)."""
    
    # Subquery to get one-on-one DM channels shared between users
    shared_dms = (
        db.query(models.Channel.id.label('channel_id'))
        .join(models.UserChannel, models.Channel.id == models.UserChannel.channel_id)
        .filter(models.Channel.is_dm == True)
        .filter(models.UserChannel.user_id == current_user_id)
        .filter(
            db.query(func.count('*'))
            .select_from(models.UserChannel)
            .filter(models.UserChannel.channel_id == models.Channel.id)
            .correlate(models.Channel)  # Add this line
            .as_scalar() == 2
        )
        .subquery()
    )
    
    # Subquery to get the other user's ID and channel ID for each one-on-one DM
    user_channels = (
        db.query(
            models.UserChannel.user_id,
            models.UserChannel.channel_id
        )
        .filter(models.UserChannel.channel_id.in_(db.query(shared_dms.c.channel_id)))
        .filter(models.UserChannel.user_id != current_user_id)
        .subquery()
    )
    
    # Subquery to get the last message date for each channel
    last_message_dates = (
        db.query(
            models.Message.channel_id,
            func.max(models.Message.created_at).label('last_message_at')
        )
        .filter(models.Message.channel_id.in_(db.query(shared_dms.c.channel_id)))
        .group_by(models.Message.channel_id)
        .subquery()
    )
    
    # Query all users except current user, with their last DM interaction date and channel ID
    query = (
        db.query(
            models.User,
            last_message_dates.c.last_message_at,
            user_channels.c.channel_id
        )
        .outerjoin(user_channels, models.User.id == user_channels.c.user_id)
        .outerjoin(
            last_message_dates,
            user_channels.c.channel_id == last_message_dates.c.channel_id
        )
        .filter(models.User.id != current_user_id)
        .order_by(last_message_dates.c.last_message_at.asc().nullsfirst())
        .offset(skip)
        .limit(limit)
    )
    
    # Execute query and format results
    results = query.all()
    
    return [
        {
            "user": user,
            "last_dm_at": last_dm_at.isoformat() if last_dm_at else None,
            "channel_id": channel_id
        }
        for user, last_dm_at, channel_id in results
    ]
