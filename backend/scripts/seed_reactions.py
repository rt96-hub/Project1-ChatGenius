from sqlalchemy.orm import Session
from database import SessionLocal
import backend.app.models as models

def seed_reactions():
    db = SessionLocal()
    try:
        # Define initial reactions
        initial_reactions = [
            {"code": "smile", "is_system": True},
            {"code": "heart", "is_system": True},
            {"code": "thumbs_up", "is_system": True},
            {"code": "laugh", "is_system": True},
            {"code": "sad", "is_system": True},
            {"code": "angry", "is_system": True},
            {"code": "clap", "is_system": True},
            {"code": "fire", "is_system": True},
            {"code": "poop", "is_system": True}
        ]
        
        # Check and insert each reaction if it doesn't exist
        for reaction_data in initial_reactions:
            existing_reaction = db.query(models.Reaction).filter_by(code=reaction_data["code"]).first()
            if not existing_reaction:
                reaction = models.Reaction(**reaction_data)
                db.add(reaction)
                print(f"Added reaction: {reaction_data['code']}")
            else:
                print(f"Reaction already exists: {reaction_data['code']}")
        
        db.commit()
        print("Successfully seeded reactions!")
    except Exception as e:
        print(f"Error seeding reactions: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_reactions() 