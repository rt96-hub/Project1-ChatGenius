import os
import sys
from pathlib import Path

# Add the parent directory to the Python path so we can import our app modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
import app.models as models
from app.embedding_service import embedding_service
import logging
from time import sleep

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_messages_with_vectors(db: Session, batch_size: int = 100, offset: int = 0):
    """Get all messages that have vector IDs"""
    return (db.query(models.Message)
            .filter(models.Message.vector_id.isnot(None))
            .offset(offset)
            .limit(batch_size)
            .all())

def process_message_batch(db: Session, messages: list[models.Message]):
    """Process a batch of messages to update their embeddings"""
    for message in messages:
        try:
            # Get channel and user information
            channel = db.query(models.Channel).filter(models.Channel.id == message.channel_id).first()
            user = db.query(models.User).filter(models.User.id == message.user_id).first()
            
            # Update embedding
            embedding_service.update_message_embedding(
                vector_id=message.vector_id,
                new_content=message.content,
                channel_name=channel.name,
                user_name=user.name,
                message_id=message.id,
                has_file=bool(message.files),
                file_name=message.files[0].file_name if message.files else None,
                parent_id=message.parent_id
            )
            
            logger.info(f"Updated embedding for message {message.id} with vector_id {message.vector_id}")
            
            # Small delay to avoid rate limits
            sleep(0.1)
            
        except Exception as e:
            logger.error(f"Error updating embedding for message {message.id}: {e}")
            continue

def main():
    """Main function to process all messages with vectors"""
    print("Starting bulk embedding update process...")
    db = SessionLocal()
    try:
        # Get total count of messages with vectors
        total_messages = db.query(models.Message).filter(models.Message.vector_id.isnot(None)).count()
        print(f"Found {total_messages} messages with vector embeddings to update")
        
        if total_messages == 0:
            print("No messages need processing. Exiting.")
            return
        
        # Process messages in batches
        batch_size = 100
        offset = 0
        
        while offset < total_messages:
            # Get next batch of messages
            messages = get_messages_with_vectors(db, batch_size, offset)
            if not messages:
                break
                
            # Process the batch
            process_message_batch(db, messages)
            
            # Update offset
            offset += batch_size
            print(f"Processed {min(offset, total_messages)}/{total_messages} messages")
        
        print("Bulk embedding update complete.")
        
    except Exception as e:
        logger.error(f"Error during bulk embedding update: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()