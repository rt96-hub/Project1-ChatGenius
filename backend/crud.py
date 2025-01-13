from sqlalchemy.orm import Session, joinedload
import models, schemas
from sqlalchemy.orm import joinedload
import logging
from sqlalchemy import func
from typing import List, Tuple, Optional

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
        user (models.User): The user to create the channel for
        
    Returns:
        models.Channel: The created personal channel
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

def get_channel_messages(db: Session, channel_id: int, skip: int = 0, limit: int = 50, include_reactions: bool = False, parent_only: bool = True):
    # Start with base query
    query = db.query(models.Message).filter(models.Message.channel_id == channel_id)
    
    # Add parent_only filter if requested
    if parent_only:
        query = query.filter(models.Message.parent_id.is_(None))
    
    # Add eager loading for user and parent
    query = query.options(
        joinedload(models.Message.user),
        joinedload(models.Message.parent).joinedload(models.Message.user)
    )
    
    if include_reactions:
        # Add eager loading for reactions and their related data
        query = query.options(
            joinedload(models.Message.reactions)
            .joinedload(models.MessageReaction.reaction),
            joinedload(models.Message.reactions)
            .joinedload(models.MessageReaction.user)
        )
    
    # Get messages with pagination
    messages = (query
               .order_by(models.Message.created_at.desc())
               .offset(skip)
               .limit(limit + 1)  # Get one extra to check if there are more
               .all())
    
    # Check if there are more messages
    has_more = len(messages) > limit
    messages = messages[:limit]  # Trim to requested limit
    
    # Get total count (respecting parent_only filter)
    total_query = db.query(models.Message).filter(models.Message.channel_id == channel_id)
    if parent_only:
        total_query = total_query.filter(models.Message.parent_id.is_(None))
    total = total_query.count()
    
    # Add has_replies information for each message
    message_ids = [m.id for m in messages]
    replies_exist = (
        db.query(models.Message.parent_id)
        .filter(models.Message.parent_id.in_(message_ids))
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

def update_message(db: Session, message_id: int, message_update: schemas.MessageCreate) -> models.Message:
    db_message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not db_message:
        return None
    
    db_message.content = message_update.content
    db.commit()
    db.refresh(db_message)
    return db_message

def delete_message(db: Session, message_id: int) -> models.Message:
    db_message = (db.query(models.Message)
                 .filter(models.Message.id == message_id)
                 .options(joinedload(models.Message.user))
                 .first())
    if not db_message:
        return None
    
    # Create a copy of the message with its relationships
    message_copy = schemas.Message.from_orm(db_message)
    
    db.delete(db_message)
    db.commit()
    return message_copy

def get_message(db: Session, message_id: int) -> models.Message:
    return db.query(models.Message).filter(models.Message.id == message_id).first()

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

def get_user_channel_role(db: Session, channel_id: int, user_id: int):
    return (db.query(models.ChannelRole)
            .filter(models.ChannelRole.channel_id == channel_id,
                   models.ChannelRole.user_id == user_id)
            .first())

def update_user_channel_role(db: Session, channel_id: int, user_id: int, role: str):
    db_role = get_user_channel_role(db, channel_id, user_id)
    if db_role:
        db_role.role = role
        db.commit()
        db.refresh(db_role)
    else:
        db_role = models.ChannelRole(
            channel_id=channel_id,
            user_id=user_id,
            role=role
        )
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
    return db_role

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

def get_all_reactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Reaction).offset(skip).limit(limit).all()

def get_reaction(db: Session, reaction_id: int) -> models.Reaction:
    return db.query(models.Reaction).filter(models.Reaction.id == reaction_id).first()

def add_reaction_to_message(db: Session, message_id: int, reaction_id: int, user_id: int) -> models.MessageReaction:
    # Check if the reaction already exists
    existing_reaction = (db.query(models.MessageReaction)
                        .filter(models.MessageReaction.message_id == message_id,
                               models.MessageReaction.reaction_id == reaction_id,
                               models.MessageReaction.user_id == user_id)
                        .first())
    if existing_reaction:
        return existing_reaction

    # Create new reaction
    db_message_reaction = models.MessageReaction(
        message_id=message_id,
        reaction_id=reaction_id,
        user_id=user_id
    )
    db.add(db_message_reaction)
    db.commit()
    db.refresh(db_message_reaction)
    return db_message_reaction

def remove_reaction_from_message(db: Session, message_id: int, reaction_id: int, user_id: int) -> bool:
    db_message_reaction = (db.query(models.MessageReaction)
                          .filter(models.MessageReaction.message_id == message_id,
                                 models.MessageReaction.reaction_id == reaction_id,
                                 models.MessageReaction.user_id == user_id)
                          .first())
    if db_message_reaction:
        db.delete(db_message_reaction)
        db.commit()
        return True
    return False

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
             .options(joinedload(models.Channel.users))
             .outerjoin(latest_messages, models.Channel.id == latest_messages.c.channel_id)
             .order_by(latest_messages.c.latest_message_at.desc().nullslast())
             .offset(skip)
             .limit(limit))
    
    return query.all()

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

def find_last_reply_in_chain(db: Session, message_id: int) -> models.Message:
    """
    Recursively find the last message in a reply chain.
    Returns the last message that doesn't have a reply.
    """
    current_message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not current_message:
        return None
    
    # Follow the reply chain until we find a message with no reply
    while True:
        reply = db.query(models.Message).filter(models.Message.parent_id == current_message.id).first()
        if not reply:
            return current_message
        current_message = reply

def create_reply(db: Session, parent_id: int, user_id: int, message: schemas.MessageReplyCreate) -> Tuple[models.Message, models.Message]:
    """
    Create a reply to a message. If the parent message already has a reply,
    the new message will be attached to the last message in the chain.
    Returns a tuple of (reply_message, root_message).
    """
    # First check if parent message exists
    parent_message = db.query(models.Message).filter(models.Message.id == parent_id).first()
    if not parent_message:
        return None, None
    
    # Find the last message in the reply chain
    last_message = find_last_reply_in_chain(db, parent_id)
    
    # Create the new reply message
    db_message = models.Message(
        content=message.content,
        channel_id=parent_message.channel_id,  # Use the same channel as parent
        user_id=user_id,
        parent_id=last_message.id  # Set parent_id to the last message in chain
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Get the root message (the one with no parent)
    root_message = parent_message
    while root_message.parent_id is not None:
        root_message = db.query(models.Message).filter(models.Message.id == root_message.parent_id).first()
    
    # Refresh root message to ensure we have the latest data
    db.refresh(root_message)
    
    return db_message, root_message

def user_in_channel(db: Session, user_id: int, channel_id: int) -> bool:
    """Check if a user is a member of a channel."""
    return db.query(models.UserChannel).filter(
        models.UserChannel.user_id == user_id,
        models.UserChannel.channel_id == channel_id
    ).first() is not None

def get_message_reply_chain(db: Session, message_id: int) -> List[models.Message]:
    """
    Get all messages in a reply chain, including:
    1. The original message
    2. All parent messages (if the given message is a reply)
    3. All reply messages (if any message has replies)
    Returns messages ordered by created_at date.
    """
    # First, get the original message
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not message:
        return []
    
    # Get all messages in the chain
    chain_messages = []
    
    # If this message has a parent, traverse up to find the root
    current = message
    while current.parent_id is not None:
        parent = db.query(models.Message).filter(models.Message.id == current.parent_id).first()
        if not parent:
            break
        chain_messages.append(parent)
        current = parent
    
    # Add the original message
    chain_messages.append(message)
    
    # Find all replies in the chain
    current = message
    while True:
        reply = db.query(models.Message).filter(models.Message.parent_id == current.id).first()
        if not reply:
            break
        chain_messages.append(reply)
        current = reply
    
    # Sort all messages by created_at
    chain_messages.sort(key=lambda x: x.created_at)
    
    # Eager load user data for each message
    message_ids = [m.id for m in chain_messages]
    return (db.query(models.Message)
            .filter(models.Message.id.in_(message_ids))
            .options(joinedload(models.Message.user))
            .order_by(models.Message.created_at)
            .all())

def get_available_channels(db: Session, user_id: int, skip: int = 0, limit: int = 50):
    """Get all public channels that the user is not a member of."""
    # Get all channels that are:
    # 1. Not private
    # 2. Not DMs
    # 3. User is not a member of
    return (db.query(models.Channel)
            .filter(models.Channel.is_private == False)
            .filter(models.Channel.is_dm == False)
            .filter(~models.Channel.users.any(models.User.id == user_id))
            .options(joinedload(models.Channel.users))
            .order_by(models.Channel.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all())

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

# TODO: Add more CRUD operations for channels, messages, etc.

