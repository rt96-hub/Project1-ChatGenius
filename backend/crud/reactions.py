from sqlalchemy.orm import Session
import logging

from ..models import Reaction, MessageReaction
from .. import schemas

logger = logging.getLogger(__name__)

def get_all_reactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Reaction).offset(skip).limit(limit).all()

def get_reaction(db: Session, reaction_id: int) -> Reaction:
    return db.query(Reaction).filter(Reaction.id == reaction_id).first()

def add_reaction_to_message(db: Session, message_id: int, reaction_id: int, user_id: int) -> MessageReaction:
    # Check if the reaction already exists
    existing_reaction = (db.query(MessageReaction)
                        .filter(MessageReaction.message_id == message_id,
                               MessageReaction.reaction_id == reaction_id,
                               MessageReaction.user_id == user_id)
                        .first())
    if existing_reaction:
        return existing_reaction

    # Create new reaction
    db_message_reaction = MessageReaction(
        message_id=message_id,
        reaction_id=reaction_id,
        user_id=user_id
    )
    db.add(db_message_reaction)
    db.commit()
    db.refresh(db_message_reaction)
    return db_message_reaction

def remove_reaction_from_message(db: Session, message_id: int, reaction_id: int, user_id: int) -> bool:
    db_message_reaction = (db.query(MessageReaction)
                          .filter(MessageReaction.message_id == message_id,
                                 MessageReaction.reaction_id == reaction_id,
                                 MessageReaction.user_id == user_id)
                          .first())
    if db_message_reaction:
        db.delete(db_message_reaction)
        db.commit()
        return True
    return False 