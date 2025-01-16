import os
import logging
from pinecone import Pinecone
from openai import OpenAI
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from .models import Message
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


def retrieve_vector_results(prompt: str, user_id: int = None, channel_ids: list[int] = [], num_results: int = 5, trigger_message_id: int = None):
    """
    Retrieves vector search results from Pinecone based on prompt embedding.
    
    Args:
        prompt (str): The text prompt to search with
        user_id (int, optional): User ID to filter results by. Defaults to None.
        channel_ids (list[int], optional): Channel IDs to filter results by. Defaults to empty list.
        num_results (int, optional): Number of results to return. Defaults to 5.
        trigger_message_id (int, optional): Message ID to exclude from results. Defaults to None.
        
    Returns:
        dict: Pinecone query results
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



def ai_query_response(prompt: str, channel_id: int=None, user_id: int=None):
    """This function takes a prompt and returns a response from the AI.
    It uses RAG to search for relevant messages. It can be filtered by channel or user."""
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
        
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18", # Using GPT-4 since 4o mini not available
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {prompt}"}
            ],
            temperature=0.7,
            max_tokens=200
        )

        return completion.choices[0].message.content, search_results_list

    except Exception as e:
        return "The AI is currently experiencing technical difficulties. Please try again later.", []


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
    
def dm_persona_response(db: Session, prompt: str, sender_id: int, receiver_id: int, channel_id: int, trigger_message_id: int):
    """This function takes a prompt and returns a response from the AI for DMs.
    It uses RAG to search for relevant messages from channels both users share."""
    try:
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

        # Get the last 10 messages from the current DM channel
        recent_messages = get_channel_messages(db, channel_id, skip=0, limit=10, include_reactions=False, parent_only=True)
        
        # Add recent messages to context
        message_history = []
        for message in reversed(recent_messages.messages):  # Reverse to show in chronological order
            if message.user.id == sender_id:
                message_history.append({"role": "user", "content": message.content})
            else:
                message_history.append({"role": "assistant", "content": message.content})
    
        # System prompt for DM persona
        system_prompt = """You are a helpful AI assistant in a direct message conversation. 
        Use the provided context about the users' previous messages to inform your response.
        Keep responses friendly and conversational while staying relevant to the topic."""
        
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

        return completion.choices[0].message.content

    except Exception as e:
        return f"The AI is currently experiencing technical difficulties: {str(e)}", []

def prompt_message_set(prompt: str, messages: list[Message]):
    try:
        return "The AI is currently experiencing technical difficulties. Please try again later."
    except Exception as e:
        return "The AI is currently experiencing technical difficulties. Please try again later."

if __name__ == "__main__":
    print(ai_query_response("Status report", channel_id=9))
    

