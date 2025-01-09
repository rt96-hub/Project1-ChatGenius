from sqlalchemy.orm import Session, joinedload
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

def get_channel_messages(db: Session, channel_id: int, skip: int = 0, limit: int = 50, include_reactions: bool = False):
    query = (db.query(models.Message)
             .filter(models.Message.channel_id == channel_id)
             .options(joinedload(models.Message.user)))
    
    if include_reactions:
        # Add eager loading for reactions and their related data
        query = query.options(
            joinedload(models.Message.reactions)
            .joinedload(models.MessageReaction.reaction),
            joinedload(models.Message.reactions)
            .joinedload(models.MessageReaction.user)
        )
    
    messages = (query
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
        db_channel.join_code = privacy_update.join_code
        db.commit()
        db.refresh(db_channel)
    return db_channel

def create_channel_invite(db: Session, channel_id: int) -> str:
    import secrets
    import string

    # Generate a random join code
    alphabet = string.ascii_letters + string.digits
    join_code = ''.join(secrets.choice(alphabet) for _ in range(10))

    db_channel = get_channel(db, channel_id)
    if db_channel:
        db_channel.join_code = join_code
        db.commit()
        db.refresh(db_channel)
        return join_code
    return None

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

# TODO: Add more CRUD operations for channels, messages, etc.

