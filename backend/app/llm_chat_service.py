import os
import logging
from pinecone import Pinecone
from openai import OpenAI
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from .models import Message, User
from .crud.channels import get_common_channels
from .crud.messages import get_channel_messages


from dotenv import load_dotenv

load_dotenv()
# Environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX")
# Initialize OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)


# absolutely disgusting solution, but instead of fixing the circular import for the bulk generation script,
# im just going to leave this one function here, and use the new ai_service.py file for the rest of the app to use

def generate_user_persona_profile(db: Session, user_id: int) -> str:
    """
    Analyzes a user's last 100 messages to generate a detailed persona profile.
    This profile will be used to inform AI responses when mimicking the user's style.
    
    Args:
        db (Session): Database session
        user_id (int): ID of the user to generate profile for
        
    Returns:
        str: Generated profile text or None if generation fails
    """
    try:
        # Get the user's last 100 messages
        messages = db.query(Message).filter(
            Message.user_id == user_id,
            Message.from_ai == False  # Exclude AI messages
        ).order_by(Message.created_at.desc()).limit(100).all()
        
        if not messages:
            return None
            
        # Build context from messages
        context = ""
        for msg in messages:
            channel_name = msg.channel.name if msg.channel else "Unknown Channel"
            context += f"In {channel_name}: {msg.content}\n"

        system_prompt = """Analyze the provided message history and create a detailed profile of the user's communication style and personality.
        Focus on:
        1. Writing style and tone
        2. Common topics and interests
        3. Technical knowledge and expertise areas
        4. Communication patterns
        5. Personality traits evident in messages
        
        Format the response as a structured profile that can be used to inform AI responses mimicking this user's style.
        Keep the profile concise but comprehensive."""

        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here are the user's last messages:\n\n{context}"}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        profile = completion.choices[0].message.content

        # Update the user's profile in the database
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.ai_persona_profile = profile
            db.commit()
            
        return profile

    except Exception as e:
        logger.error(f"Error generating user persona profile: {e}")
        return None

    

