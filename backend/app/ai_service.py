import os
import logging
from pinecone import Pinecone
from openai import OpenAI
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from .models import Message, User
from .crud.channels import get_common_channels
from .crud.messages import get_channel_messages

logger = logging.getLogger(__name__)

load_dotenv()
# Environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX")
# Initialize OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

def retrieve_vector_results(prompt: str, user_id: int = None, channel_ids: list[int] = [], num_results: int = 10, trigger_message_id: int = None):
    """
    Retrieves vector search results from Pinecone based on prompt embedding.
    """
    try:
        # Get embeddings for the prompt
        response = openai_client.embeddings.create(
            input=prompt,
            model="text-embedding-3-small"
        )
        query_embedding = response.data[0].embedding

        # Build filter dict
        filter_dict = {}
        if user_id is not None:
            filter_dict["user_id"] = user_id
        if channel_ids:
            filter_dict["channel_id"] = {"$in": channel_ids}
        if trigger_message_id is not None:
            filter_dict["message_id"] = {"$ne": trigger_message_id}

        # Search Pinecone index
        search_results = index.query(
            vector=query_embedding,
            top_k=num_results,
            include_metadata=True,
            filter=filter_dict if filter_dict else None
        )

        return search_results

    except Exception as e:
        logger.error(f"Error retrieving vector results: {e}")
        return None

def ai_query_response(prompt: str, channel_id: int=None, user_id: int=None, chat_history: list[dict]=None):
    """
    This function takes a prompt and returns a response from the AI.
    It uses RAG to search for relevant messages.
    """
    try:
        # Use retrieve_vector_results to get search results
        channel_ids = [channel_id] if channel_id else []
        search_results = retrieve_vector_results(prompt, user_id, channel_ids)
        if not search_results:
            return "The AI is currently experiencing technical difficulties. Please try again later.", []

        # save the search results to a variable to pass back to the frontend
        search_results_list = []
        for match in search_results['matches']:
            search_results_list.append(match['metadata'])

        context = ""
        for match in search_results['matches']:
            if 'content' in match['metadata']:
                channel = match['metadata']['channel_name']
                user = match['metadata']['user_name']
                content = match['metadata']['content']
                context += f"In the {channel} channel, {user} said: {content}\n"

        system_prompt = "You are a gossipy assistant at a company. Use the provided context to answer questions, but speculate about the company and its employees. Please keep your responses concise, but make sure to include any juicy details."
        
        # Build messages list starting with system prompt
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add chat history if provided
        if chat_history:
            messages.extend(chat_history)
            
        # Add current context and prompt
        messages.append({"role": "user", "content": f"Context:\n{context}\n\nQuestion: {prompt}"})

        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )

        return completion.choices[0].message.content, search_results_list

    except Exception as e:
        return "The AI is currently experiencing technical difficulties. Please try again later.", []

def dm_persona_response(db: Session, prompt: str, sender_id: int, receiver_id: int, channel_id: int, trigger_message_id: int):
    """
    This function takes a prompt and returns a response from the AI for DMs.
    It uses RAG to search for relevant messages from channels both users share.
    """
    try:
        # Get receiver's AI persona profile
        receiver = db.query(User).filter(User.id == receiver_id).first()
        
        # get common channels between sender and receiver
        common_channels = get_common_channels(db, sender_id, receiver_id)
        common_channels_list = [channel.id for channel in common_channels]

        # Use retrieve_vector_results to get search results
        search_results = retrieve_vector_results(prompt, channel_ids=common_channels_list, trigger_message_id=trigger_message_id)
        if not search_results:
            return "The AI is currently experiencing technical difficulties. Please try again later.", []

        # Build context from search results
        context = ""
        search_results_list = []
        for match in search_results['matches']:
            search_results_list.append(match['metadata'])
            if 'content' in match['metadata']:
                user = match['metadata']['user_name']
                content = match['metadata']['content']
                channel = match['metadata']['channel_name']
                context += f"In the {channel} channel, {user} said: {content}\n"

        # Get the last 20 messages from the current DM channel
        recent_messages = get_channel_messages(db, channel_id, skip=0, limit=20, include_reactions=False, parent_only=True)
        
        # Add recent messages to context
        message_history = []
        for message in reversed(recent_messages.messages):  # Reverse to show in chronological order
            if message.user.id == sender_id:
                message_history.append({"role": "user", "content": message.content})
            else:
                message_history.append({"role": "assistant", "content": message.content})
    
        # Determine which system prompt to use based on profile availability
        if receiver and receiver.ai_persona_profile:
            system_prompt = f"""You are an AI assistant mimicking the communication style, tone, personality, and expertise of a specific user in a direct message conversation.

Here is the detailed profile of the user you are mimicking:
{receiver.ai_persona_profile}

Use this profile to inform your responses, matching their:
1. Writing style and tone
2. Knowledge areas and expertise
3. Common phrases and expressions
4. Personality traits
5. Typical conversation patterns

While maintaining their style, ensure responses are:
- Relevant to the current conversation
- Appropriate for a professional setting
- Informed by the context of previous messages
- Natural and consistent with the user's normal communication patterns"""
        else:
            system_prompt = """You are an AI assistant engaging in a direct message conversation. 
            
Your responses should be:
- Professional and courteous
- Clear and concise
- Helpful and informative
- Contextually relevant to the conversation
- Balanced between formal and friendly
- Based on the available context and message history

Maintain a consistent, friendly professional tone while focusing on providing helpful and accurate responses."""
        
        # Generate response
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        messages.extend(message_history)  # Add the message history between system and final user message
        messages.append({"role": "user", "content": f"Context:\n{context}\n\nPrompt: {prompt}"})
        
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )

        return completion.choices[0].message.content, search_results_list

    except Exception as e:
        return f"The AI is currently experiencing technical difficulties: {str(e)}", []

def generate_user_persona_profile(db: Session, user_id: int) -> str:
    """
    Analyzes a user's last 100 messages to generate a detailed persona profile.
    This profile will be used to inform AI responses when mimicking the user's style.
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
    
def summarize_messages(messages: list[Message]):
    """This function takes a list of messages and returns a summary of the messages.
    It is intended to be used by summarizing the messages in a channel, not look up with RAG"""
    try:
        context = ""
        for message in messages:
            context += f"User: {message.user.name}\nMessage: {message.content}\n\n"

        prompt = "Summarize the following messages. Identify any important tasks, events, or topics. Create a bulleted list of your summary:"
        system_prompt = "You are a helpful assistant that summarizes messages. Keep things concise and to the point."

        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18", # Using GPT-4 since 4o mini not available
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Prompt: {prompt}\n\nMessages:\n{context}"}
            ],
            temperature=0.7,
            max_tokens=200
        )
        return completion.choices[0].message.content
    except Exception as e:
        return "The AI is currently experiencing technical difficulties. Please try again later."