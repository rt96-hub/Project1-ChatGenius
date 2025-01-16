from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
import logging
from typing import List, Optional

from .. import models, schemas
from .users import get_user

logger = logging.getLogger(__name__)

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

def get_channel_members(db: Session, channel_id: int):
    channel = db.query(models.Channel).filter(models.Channel.id == channel_id).first()
    if not channel:
        return None
    return channel.users

def remove_channel_member(db: Session, channel_id: int, user_id: int):
    db_user_channel = (db.query(models.UserChannel)
                      .filter(models.UserChannel.channel_id == channel_id,
                             models.UserChannel.user_id == user_id)
                      .first())
    if db_user_channel:
        # Delete any roles the user has in the channel
        db.query(models.ChannelRole).filter(
            models.ChannelRole.channel_id == channel_id,
            models.ChannelRole.user_id == user_id
        ).delete()
        
        # Delete the user-channel association
        db.delete(db_user_channel)
        db.commit()
        return True
    return False

def update_channel_privacy(db: Session, channel_id: int, privacy_update: schemas.ChannelPrivacyUpdate):
    db_channel = get_channel(db, channel_id)
    if db_channel:
        db_channel.is_private = privacy_update.is_private
        db.commit()
        db.refresh(db_channel)
    return db_channel

def join_channel(db: Session, channel_id: int, user_id: int) -> Optional[models.Channel]:
    """Add a user to a channel."""
    # Get the channel
    channel = get_channel(db, channel_id=channel_id)
    if not channel:
        return None
    
    # Check if user is already a member
    if any(user.id == user_id for user in channel.users):
        return channel
    
    # Add user to channel
    db_user_channel = models.UserChannel(user_id=user_id, channel_id=channel_id)
    db.add(db_user_channel)
    db.commit()
    
    # Refresh the channel to get updated users list
    db.refresh(channel)
    return channel

def leave_channel(db: Session, channel_id: int, user_id: int):
    db_channel = get_channel(db, channel_id)
    if not db_channel:
        return None
    
    # Check if user is the owner
    if db_channel.owner_id == user_id:
        # Find another user to transfer ownership to
        other_user = (db.query(models.UserChannel)
                     .filter(models.UserChannel.channel_id == channel_id,
                            models.UserChannel.user_id != user_id)
                     .first())
        if other_user:
            db_channel.owner_id = other_user.user_id
        else:
            # If no other users, delete the channel
            return delete_channel(db, channel_id)
    
    # Remove user from channel
    return remove_channel_member(db, channel_id, user_id)

def get_available_channels(db: Session, user_id: int, skip: int = 0, limit: int = 50):
    """Get all public channels that the user is not a member of."""
    return (db.query(models.Channel)
            .filter(models.Channel.is_private == False)
            .filter(models.Channel.is_dm == False)
            .filter(~models.Channel.users.any(models.User.id == user_id))
            .options(joinedload(models.Channel.users))
            .order_by(models.Channel.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all())

def user_in_channel(db: Session, user_id: int, channel_id: int) -> bool:
    """Check if a user is a member of a channel."""
    return db.query(models.UserChannel).filter(
        models.UserChannel.user_id == user_id,
        models.UserChannel.channel_id == channel_id
    ).first() is not None

def create_dm(db: Session, creator_id: int, dm: schemas.DMCreate) -> models.Channel:
    """Create a new DM channel with multiple users."""
    # Generate DM name (can be customized for group DMs)
    users = [get_user(db, user_id) for user_id in dm.user_ids]
    users.append(get_user(db, creator_id))  # Add creator to the list
    
    # Filter out None values and create a sorted list of valid users
    valid_users = [u for u in users if u is not None]
    if len(valid_users) < 2:
        return None
        
    # Create channel name from user names for 2-person DMs, or use provided name for group DMs
    if len(valid_users) == 2:
        channel_name = f"dm-{valid_users[0].name}-{valid_users[1].name}".lower().replace(" ", "-")
    else:
        channel_name = dm.name if dm.name else f"group-dm-{creator_id}-{'-'.join(str(uid) for uid in dm.user_ids)}"

    # Create the DM channel
    db_channel = models.Channel(
        name=channel_name,
        description="Direct Message Channel",
        owner_id=creator_id,
        is_private=True,
        is_dm=True
    )
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    
    # Add all users to the channel
    for user in valid_users:
        db_user_channel = models.UserChannel(user_id=user.id, channel_id=db_channel.id)
        db.add(db_user_channel)
    
    db.commit()
    db.refresh(db_channel)
    return db_channel

def get_user_dms(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get user's DM channels ordered by most recent message."""
    # Subquery to get the latest message timestamp for each channel
    latest_messages = (db.query(models.Message.channel_id,
                              func.max(models.Message.created_at).label('latest_message_at'))
                      .group_by(models.Message.channel_id)
                      .subquery())
    
    # Query for DM channels with latest message timestamp
    query = (db.query(models.Channel)
             .join(models.UserChannel)
             .filter(models.UserChannel.user_id == user_id)
             .filter(models.Channel.is_dm == True)
             .filter(models.Channel.ai_channel == False)  # Exclude AI channels
             .options(joinedload(models.Channel.users))
             .outerjoin(latest_messages, models.Channel.id == latest_messages.c.channel_id)
             .order_by(latest_messages.c.latest_message_at.desc().nullslast())
             .offset(skip)
             .limit(limit))
    
    return query.all()

def get_existing_dm_channel(db: Session, user1_id: int, user2_id: int) -> int:
    """Check if there's an existing one-on-one DM channel between two users.
    Returns the channel_id if found, None otherwise."""
    
    # Find channels that both users are members of
    shared_channels = (
        db.query(models.Channel.id)
        .join(models.UserChannel, models.Channel.id == models.UserChannel.channel_id)
        .filter(models.Channel.is_dm == True)  # Must be a DM channel
        .filter(models.UserChannel.user_id.in_([user1_id, user2_id]))
        .group_by(models.Channel.id)
        .having(func.count(models.UserChannel.user_id) == 2)  # Must have exactly 2 members
    )
    
    # From these channels, find one where these are the only two members
    dm_channel = (
        db.query(models.Channel.id)
        .filter(models.Channel.id.in_(shared_channels))
        .filter(~models.Channel.users.any(~models.User.id.in_([user1_id, user2_id])))  # No other members
        .first()
    )
    
    return dm_channel[0] if dm_channel else None 

def get_common_channels(db: Session, user1_id: int, user2_id: int):
    """Get all channels that both users are members of."""
    return (db.query(models.Channel.id)
            .join(models.UserChannel, models.Channel.id == models.UserChannel.channel_id)
            .filter(models.UserChannel.user_id.in_([user1_id, user2_id]))
            .group_by(models.Channel.id)
            .having(func.count(models.UserChannel.user_id) == 2)
            .all())

def get_or_create_ai_dm(db: Session, user_id: int) -> models.Channel:
    """Get or create an AI DM channel for a user."""
    user = get_user(db, user_id)
    if not user:
        return None
        
    channel_name = f"{user.name}-ai-dm".lower().replace(" ", "-")
    
    # Check if channel already exists
    existing_channel = (db.query(models.Channel)
                       .filter(models.Channel.name == channel_name)
                       .filter(models.Channel.is_dm == True)
                       .first())
    
    if existing_channel:
        return existing_channel
        
    # Create new AI DM channel
    db_channel = models.Channel(
        name=channel_name,
        description=f"AI Assistant for {user.name}",
        owner_id=user_id,
        is_private=True,
        is_dm=True,
        ai_channel=True
    )
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    
    # Add user to the channel
    db_user_channel = models.UserChannel(user_id=user_id, channel_id=db_channel.id)
    db.add(db_user_channel)
    db.commit()
    db.refresh(db_channel)
    
    return db_channel
