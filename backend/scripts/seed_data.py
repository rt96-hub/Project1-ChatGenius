"""
Data seeding script to populate the database with realistic test data.
"""

import os
import sys
# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from faker import Faker
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from typing import List, Dict
import logging
import uuid
import string

from models import User, Channel, Message, UserChannel, MessageReaction, Reaction
from database import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Faker
fake = Faker()

def create_fake_users(db: Session, count: int = 50) -> List[User]:
    """
    Create fake users with realistic data.
    
    Args:
        db (Session): SQLAlchemy database session
        count (int): Number of users to create (default: 10)
        
    Returns:
        List[User]: List of created user objects
    """
    logger.info(f"Creating {count} fake users...")
    users = []
    
    try:
        for _ in range(count):
            # Generate a fake auth0 id using UUID
            auth0_id = f"auth0|{str(uuid.uuid4())}"
            
            # Create user with fake data
            user = User(
                auth0_id=auth0_id,
                email=fake.unique.email(),
                is_active=True,  # Most users are active by default
                created_at=fake.date_time_this_year(tzinfo=None),
                name=fake.name(),
                # picture may be updated to null
                picture=None,
                #picture=fake.image_url(),  # Generate a random avatar URL
                bio=fake.text(max_nb_chars=200)  # Generate a bio with max 200 chars
            )
            
            db.add(user)
            users.append(user)
        
        # Commit all users at once
        db.commit()
        logger.info(f"Successfully created {len(users)} users")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating users: {str(e)}")
        raise
    
    return users

def create_fake_channels(db: Session, users: List[User], count: int = 10) -> List[Channel]:
    """
    Create fake channels with a mix of regular and DM channels.
    
    Args:
        db (Session): SQLAlchemy database session
        users (List[User]): List of available users
        count (int): Number of channels to create (default: 5)
        
    Returns:
        List[Channel]: List of created channel objects
    """
    logger.info(f"Creating {count} fake channels...")
    channels = []
    
    try:
        for _ in range(count):
            # Determine channel type (30% chance of being a DM)
            is_dm = random.random() < 0.3
            
            # For regular channels, 40% chance of being private
            is_private = True if is_dm else random.random() < 0.4
            
            # Select a random owner
            owner = random.choice(users)
            
            channel = Channel(
                name=f'{owner.name} DM' if is_dm else fake.unique.company(),
                description=None if is_dm else fake.text(max_nb_chars=100),
                owner_id=owner.id,
                created_at=fake.date_time_this_year(tzinfo=None),
                is_private=is_private,
                is_dm=is_dm
            )
            
            db.add(channel)
            channels.append(channel)
        
        # Commit all channels at once
        db.commit()
        logger.info(f"Successfully created {len(channels)} channels")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating channels: {str(e)}")
        raise
    
    return channels

def add_users_to_channels(db: Session, users: List[User], channels: List[Channel]) -> None:
    """
    Add users to channels following specific rules for DMs and regular channels.
    
    Args:
        db (Session): SQLAlchemy database session
        users (List[User]): List of available users
        channels (List[Channel]): List of channels to add users to
    """
    logger.info("Adding users to channels...")
    
    try:
        for channel in channels:
            if channel.is_dm:
                # For DM channels: exactly 2 users (owner + one other)
                owner = next(user for user in users if user.id == channel.owner_id)
                available_users = [u for u in users if u.id != owner.id]
                
                if not available_users:
                    logger.warning(f"No available users for DM channel {channel.id}")
                    continue
                
                other_user = random.choice(available_users)
                
                # Add owner and other user
                user_channels = [
                    UserChannel(user_id=owner.id, channel_id=channel.id),
                    UserChannel(user_id=other_user.id, channel_id=channel.id)
                ]
                
            else:
                # For regular channels: random number of users (min 2, max all users)
                owner = next(user for user in users if user.id == channel.owner_id)
                other_users = [u for u in users if u.id != owner.id]
                
                # Random number of additional users (at least 1, could be all remaining users)
                num_additional_users = random.randint(1, len(other_users))
                selected_users = random.sample(other_users, num_additional_users)
                
                # Create UserChannel entries for owner and selected users
                user_channels = [UserChannel(user_id=owner.id, channel_id=channel.id)]
                user_channels.extend([
                    UserChannel(user_id=user.id, channel_id=channel.id)
                    for user in selected_users
                ])
            
            # Add all user-channel relationships
            for uc in user_channels:
                db.add(uc)
        
        # Commit all changes at once
        db.commit()
        logger.info("Successfully added users to channels")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding users to channels: {str(e)}")
        raise

def get_channel_members(db: Session, channel_id: int) -> List[User]:
    """Helper function to get all members of a channel."""
    user_channels = db.query(UserChannel).filter(UserChannel.channel_id == channel_id).all()
    return [uc.user_id for uc in user_channels]

def create_fake_messages(db: Session, channels: List[Channel], users: List[User], messages_per_channel: int = 100) -> List[Message]:
    """
    Create fake messages in channels with replies.
    
    Args:
        db (Session): SQLAlchemy database session
        channels (List[Channel]): List of channels to create messages in
        users (List[User]): List of available users
        messages_per_channel (int): Number of messages to create per channel (default: 20)
        
    Returns:
        List[Message]: List of created message objects
    """
    logger.info(f"Creating messages in {len(channels)} channels...")
    messages = []
    
    try:
        for channel in channels:
            # Get members of this channel
            channel_member_ids = get_channel_members(db, channel.id)
            if not channel_member_ids:
                logger.warning(f"No members found for channel {channel.id}, skipping message creation")
                continue
            
            # Track messages in this channel for reply creation
            channel_messages = []
            
            # Create messages for this channel
            for _ in range(messages_per_channel):
                # Select random member as message author
                author_id = random.choice(channel_member_ids)
                
                # Determine message content type (60% sentence, 40% paragraph)
                content = fake.paragraph() if random.random() < 0.4 else fake.sentence()
                
                # Create message with a timestamp within the last year
                created_at = fake.date_time_this_year(tzinfo=None)
                
                message = Message(
                    content=content,
                    created_at=created_at,
                    updated_at=created_at,
                    user_id=author_id,
                    channel_id=channel.id,
                    parent_id=None  # Will be set later for replies
                )
                
                db.add(message)
                db.flush()  # Flush to get message ID for replies
                
                channel_messages.append(message)
                messages.append(message)
                
                # 20% chance to generate a reply to this message
                if random.random() < 0.2 and len(channel_member_ids) > 1:
                    # Select different user for reply
                    reply_author_id = random.choice([uid for uid in channel_member_ids if uid != author_id])
                    
                    # Create reply with a later timestamp
                    reply_created_at = created_at + timedelta(minutes=random.randint(1, 60))
                    
                    reply = Message(
                        content=fake.sentence(),  # Replies are usually shorter
                        created_at=reply_created_at,
                        updated_at=reply_created_at,
                        user_id=reply_author_id,
                        channel_id=channel.id,
                        parent_id=message.id
                    )
                    
                    db.add(reply)
                    messages.append(reply)
            
        # Commit all messages at once
        db.commit()
        logger.info(f"Successfully created {len(messages)} messages")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating messages: {str(e)}")
        raise
    
    return messages

def get_available_reactions(db: Session) -> List[Reaction]:
    """Helper function to get all available system reactions."""
    return db.query(Reaction).filter(Reaction.is_system == True).all()

def add_reactions_to_messages(db: Session, messages: List[Message], users: List[User]) -> None:
    """
    Add reactions to messages with proper distribution and constraints.
    
    Args:
        db (Session): SQLAlchemy database session
        messages (List[Message]): List of messages to add reactions to
        users (List[User]): List of available users
    """
    logger.info("Adding reactions to messages...")
    
    try:
        # Get available reactions
        available_reactions = get_available_reactions(db)
        if not available_reactions:
            logger.error("No system reactions found. Please run seed_reactions.py first.")
            return
        
        for message in messages:
            # 40% chance to add reactions to this message
            if random.random() < 0.4:
                # Get channel members who can react
                channel_member_ids = get_channel_members(db, message.channel_id)
                if not channel_member_ids:
                    continue
                
                # Determine number of reactions (1-3)
                num_reactions = random.randint(1, 3)
                
                # Track used reactions per user to prevent duplicates
                user_reactions = {}  # user_id -> set of reaction_ids
                
                # Try to add reactions
                for _ in range(num_reactions):
                    # Select a random user and reaction
                    user_id = random.choice(channel_member_ids)
                    reaction = random.choice(available_reactions)
                    
                    # Skip if user already used this reaction
                    if user_id not in user_reactions:
                        user_reactions[user_id] = set()
                    
                    if reaction.id in user_reactions[user_id]:
                        continue
                    
                    # Create the message reaction
                    message_reaction = MessageReaction(
                        message_id=message.id,
                        reaction_id=reaction.id,
                        user_id=user_id,
                        created_at=fake.date_time_between(
                            start_date=message.created_at,
                            end_date=datetime.now()
                        )
                    )
                    
                    db.add(message_reaction)
                    user_reactions[user_id].add(reaction.id)
        
        # Commit all reactions at once
        db.commit()
        logger.info("Successfully added reactions to messages")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding reactions to messages: {str(e)}")
        raise

def verify_reactions_exist(db: Session) -> bool:
    """
    Verify that system reactions are present in the database.
    
    Args:
        db (Session): SQLAlchemy database session
        
    Returns:
        bool: True if reactions exist, False otherwise
    """
    reactions = get_available_reactions(db)
    if not reactions:
        logger.error("No system reactions found in database!")
        logger.error("Please run 'python backend/scripts/seed_reactions.py' first")
        return False
    logger.info(f"Found {len(reactions)} system reactions")
    return True

def main():
    """Main function to orchestrate the data seeding process."""
    logger.info("Starting data seeding process...")
    logger.info("Step 1/6: Initializing database connection")
    db = SessionLocal()
    
    try:
        # Verify reactions exist
        logger.info("Step 2/6: Verifying system reactions")
        if not verify_reactions_exist(db):
            return
        
        # Create fake users
        logger.info("Step 3/6: Creating fake users")
        users = create_fake_users(db)
        if not users:
            logger.error("Failed to create users")
            return
        logger.info(f"Created {len(users)} users successfully")
        
        # Create fake channels
        logger.info("Step 4/6: Creating channels and setting up memberships")
        channels = create_fake_channels(db, users)
        if not channels:
            logger.error("Failed to create channels")
            return
        logger.info(f"Created {len(channels)} channels successfully")
        
        # Add users to channels
        add_users_to_channels(db, users, channels)
        logger.info("Channel memberships established successfully")
        
        # Create messages in channels
        logger.info("Step 5/6: Creating messages and replies")
        messages = create_fake_messages(db, channels, users)
        if not messages:
            logger.error("Failed to create messages")
            return
        logger.info(f"Created {len(messages)} messages successfully")
        
        # Add reactions to messages
        logger.info("Step 6/6: Adding reactions to messages")
        add_reactions_to_messages(db, messages, users)
        
        logger.info("Data seeding completed successfully!")
        logger.info(f"""
Summary of seeded data:
- Users created: {len(users)}
- Channels created: {len(channels)}
- Messages created: {len(messages)}
""")
        
    except Exception as e:
        logger.error(f"Error during data seeding: {str(e)}")
        db.rollback()
        raise
    finally:
        logger.info("Closing database connection...")
        db.close()

if __name__ == "__main__":
    main() 