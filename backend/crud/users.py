from sqlalchemy.orm import Session
import logging
from typing import Optional

from ..models import User, Channel, UserChannel
from .. import schemas

logger = logging.getLogger(__name__)

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_auth0_id(db: Session, auth0_id: str):
    return db.query(User).filter(User.auth0_id == auth0_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_personal_channel(db: Session, user: User) -> Channel:
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
        personal_channel = Channel(
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
        user_channel = UserChannel(user_id=user.id, channel_id=personal_channel.id)
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
        db_user = User(
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