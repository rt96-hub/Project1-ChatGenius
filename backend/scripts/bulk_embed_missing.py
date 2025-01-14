import os
import sys
from pathlib import Path

# Add the parent directory to the Python path so we can import our app modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
import backend.app.models as models
from app.embedding_service import embedding_service
import logging
from time import sleep

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_messages_without_vectors(db: Session, batch_size: int = 100):
    """Get all messages that don't have vector IDs"""
    return (db.query(models.Message)
            .filter(models.Message.vector_id.is_(None))
            .limit(batch_size)
            .all())

def process_message_batch(db: Session, messages: list[models.Message]):
    """Process a batch of messages to create their embeddings"""
    for message in messages:
        try:
            # Generate embedding and get vector_id
            vector_id = embedding_service.create_message_embedding(
                message_content=message.content,
                message_id=message.id,
                user_id=message.user_id,
                channel_id=message.channel_id,
                parent_id=message.parent_id,
                file_name=message.files[0].file_name if message.files else None
            )
            
            # Update message with vector_id
            message.vector_id = vector_id
            db.commit()
            logger.info(f"Created embedding for message {message.id} with vector_id {vector_id}")
            
            # Small delay to avoid rate limits
            sleep(0.1)
            
        except Exception as e:
            logger.error(f"Error creating embedding for message {message.id}: {e}")
            db.rollback()
            continue

def main():
    """Main function to process all messages without vectors"""
    logger.info("Starting bulk embedding process...")
    
    db = SessionLocal()
    try:
        # Get initial count of messages without vectors
        total_messages = db.query(models.Message).filter(models.Message.vector_id.is_(None)).count()
        logger.info(f"Found {total_messages} messages without vector embeddings")
        
        if total_messages == 0:
            logger.info("No messages need processing. Exiting.")
            return
        
        # Process messages in batches
        batch_size = 100
        
        while True:
            # Get next batch of messages
            messages = get_messages_without_vectors(db, batch_size)
            if not messages:
                break
                
            # Process the batch
            process_message_batch(db, messages)
            
        
        # Final count check
        remaining = db.query(models.Message).filter(models.Message.vector_id.is_(None)).count()
        logger.info(f"Bulk embedding complete. {remaining} messages remaining without vectors.")
        
    except Exception as e:
        logger.error(f"Error during bulk embedding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main() 