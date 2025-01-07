from sqlalchemy.orm import Session
import models, schemas
from sqlalchemy.orm import joinedload
import logging

logger = logging.getLogger(__name__)

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_auth0_id(db: Session, auth0_id: str):
    return db.query(models.User).filter(models.User.auth0_id == auth0_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

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
        return db_user
    except Exception as e:
        logger.error(f"Error in sync_auth0_user: {str(e)}", exc_info=True)
        raise

# Channel operations
def create_channel(db: Session, channel: schemas.ChannelCreate, creator_id: int):
    db_channel = models.Channel(
        name=channel.name,
        description=channel.description,
        owner_id=creator_id
    )
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    
    # Add creator as first member
    db_user_channel = models.UserChannel(user_id=creator_id, channel_id=db_channel.id)
    db.add(db_user_channel)
    db.commit()
    
    return db_channel

def get_channel(db: Session, channel_id: int):
    return db.query(models.Channel).filter(models.Channel.id == channel_id).first()

def get_user_channels(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return (db.query(models.Channel)
            .join(models.UserChannel)
            .filter(models.UserChannel.user_id == user_id)
            .options(joinedload(models.Channel.users))
            .offset(skip)
            .limit(limit)
            .all())

def update_channel(db: Session, channel_id: int, channel_update: schemas.ChannelCreate):
    db_channel = get_channel(db, channel_id)
    if db_channel:
        db_channel.name = channel_update.name
        db_channel.description = channel_update.description
        db.commit()
        db.refresh(db_channel)
    return db_channel

def delete_channel(db: Session, channel_id: int):
    db_channel = get_channel(db, channel_id)
    if db_channel:
        # Delete all user_channel associations first
        db.query(models.UserChannel).filter(models.UserChannel.channel_id == channel_id).delete()
        # Delete all messages in the channel
        db.query(models.Message).filter(models.Message.channel_id == channel_id).delete()
        # Delete the channel
        db.delete(db_channel)
        db.commit()
    return db_channel

def create_message(db: Session, channel_id: int, user_id: int, message: schemas.MessageCreate):
    db_message = models.Message(
        content=message.content,
        channel_id=channel_id,
        user_id=user_id
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_channel_messages(db: Session, channel_id: int, skip: int = 0, limit: int = 50):
    messages = (db.query(models.Message)
               .filter(models.Message.channel_id == channel_id)
               .order_by(models.Message.created_at.desc())
               .offset(skip)
               .limit(limit + 1)  # Get one extra to check if there are more
               .all())
    
    has_more = len(messages) > limit
    messages = messages[:limit]  # Trim to requested limit
    
    total = db.query(models.Message).filter(models.Message.channel_id == channel_id).count()
    
    return schemas.MessageList(
        messages=messages,
        total=total,
        has_more=has_more
    )

# TODO: Add more CRUD operations for channels, messages, etc.

