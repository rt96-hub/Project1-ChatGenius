from sqlalchemy.orm import Session
import models, schemas
from security import get_password_hash, verify_password
from sqlalchemy.orm import joinedload

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

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

# Message operations
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
    # First get total count
    total_count = db.query(models.Message)\
        .filter(models.Message.channel_id == channel_id)\
        .count()

    # Get messages ordered by created_at descending (newest first)
    messages = db.query(models.Message)\
        .filter(models.Message.channel_id == channel_id)\
        .options(joinedload(models.Message.user))\
        .order_by(models.Message.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    # Reverse the messages so oldest appears first in the list
    messages.reverse()
    
    return {
        "messages": messages,
        "total": total_count,
        "has_more": (skip + limit) < total_count
    }

# TODO: Add more CRUD operations for channels, messages, etc.

