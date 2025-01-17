import os
import sys
import argparse
import logging
from sqlalchemy.orm import Session
from sqlalchemy import or_

# Add the parent directory to the Python path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import User
from app.llm_chat_service import generate_user_persona_profile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_profiles(db: Session, all_users: bool = False):
    """
    Generate AI persona profiles for users.
    
    Args:
        db (Session): Database session
        all_users (bool): If True, generate profiles for all users. If False, only for users without profiles.
    """
    try:
        # Query users based on the all_users flag
        if all_users:
            users = db.query(User).all()
            logger.info(f"Found {len(users)} total users")
        else:
            users = db.query(User).filter(
                or_(
                    User.ai_persona_profile == None,
                    User.ai_persona_profile == ""
                )
            ).all()
            logger.info(f"Found {len(users)} users without profiles")

        # Generate profiles for each user
        success_count = 0
        error_count = 0
        
        for user in users:
            try:
                logger.info(f"Generating profile for user {user.id} ({user.name or user.email})")
                profile = generate_user_persona_profile(db, user.id)
                
                if profile:
                    success_count += 1
                    logger.info(f"Successfully generated profile for user {user.id}")
                else:
                    error_count += 1
                    logger.error(f"Failed to generate profile for user {user.id} - no messages found")
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error generating profile for user {user.id}: {str(e)}")
                continue

        logger.info(f"\nProfile Generation Summary:")
        logger.info(f"Total users processed: {len(users)}")
        logger.info(f"Successful generations: {success_count}")
        logger.info(f"Failed generations: {error_count}")

    except Exception as e:
        logger.error(f"Error during profile generation: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Generate AI persona profiles for users')
    parser.add_argument('--all', action='store_true', help='Generate profiles for all users, not just those without profiles')
    args = parser.parse_args()

    db = SessionLocal()
    try:
        generate_profiles(db, args.all)
    finally:
        db.close()

if __name__ == "__main__":
    main() 