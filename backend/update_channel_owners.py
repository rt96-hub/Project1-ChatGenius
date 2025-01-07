from sqlalchemy.orm import Session
from database import SessionLocal
import models

def update_channel_owners():
    db = SessionLocal()
    try:
        # Get all channels
        channels = db.query(models.Channel).all()
        
        for channel in channels:
            if channel.owner_id is None:
                # Get the first user in the channel as the owner
                user_channel = db.query(models.UserChannel)\
                    .filter(models.UserChannel.channel_id == channel.id)\
                    .first()
                
                if user_channel:
                    channel.owner_id = user_channel.user_id
        
        db.commit()
        print("Successfully updated channel owners!")
    except Exception as e:
        print(f"Error updating channel owners: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_channel_owners() 