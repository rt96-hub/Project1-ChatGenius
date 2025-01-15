import os
from pinecone import Pinecone
from openai import OpenAI

from .models import Message

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


def ai_query_response(prompt: str, channel_id: int=None, user_id: int=None):
    try:
        # Get embeddings for the prompt
        response = openai_client.embeddings.create(
            input=prompt,
            model="text-embedding-3-small"
        )
        query_embedding = response.data[0].embedding
        # Search Pinecone index
        search_results = index.query(
            vector=query_embedding,
            top_k=5,  # Retrieve top 5 most similar results
            include_metadata=True,
            filter={k: v for k, v in {
                "channel_id": channel_id,
                "user_id": user_id
            }.items() if v is not None}
        )

        # save the search results to a variable to pass back to the frontend (right now we are just passing it to the backend)
        search_results_list = []
        for match in search_results['matches']:
            search_results_list.append(match['metadata'])

        context = ""
        for match in search_results['matches']:
            if 'content' in match['metadata']:
                context += match['metadata']['content'] + "\n"

        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18", # Using GPT-4 since 4o mini not available
            messages=[
                {"role": "system", "content": "You are a gossipy assistant at a company. Use the provided context to answer questions, but speculate about the company and its employees. Please keep your responses concise, but make sure to include any juicy details."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {prompt}"}
            ],
            temperature=0.7,
            max_tokens=200
        )

        return completion.choices[0].message.content, search_results_list


    except Exception as e:
        return "The AI is currently experiencing technical difficulties. Please try again later.", []


def summarize_messages(messages: list[Message]):
    try:
        context = ""
        for message in messages:
            context += f"User: {message.user.name}\nMessage: {message.content}\n\n"

        prompt = "Summarize the following messages. Identify any important tasks, events, or topics. Create a bulleted list of your summary:"
        
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18", # Using GPT-4 since 4o mini not available
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes messages. Keep things concise and to the point."},
                {"role": "user", "content": f"{prompt}\n{context}"}
            ],
            temperature=0.7,
            max_tokens=200
        )
        return completion.choices[0].message.content
    except Exception as e:
        return "The AI is currently experiencing technical difficulties. Please try again later."\

if __name__ == "__main__":
    print(ai_query_response("Status report", channel_id=9))
    

