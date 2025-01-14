import os
from pinecone import Pinecone
from openai import OpenAI
import uuid
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

load_dotenv()
# Environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX")

# Initialize OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)

class EmbeddingService:
    def __init__(self):
        if not all([PINECONE_API_KEY, OPENAI_API_KEY, INDEX_NAME]):
            raise ValueError("Missing required environment variables for EmbeddingService")
        
        # Initialize pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index = pc.Index(INDEX_NAME)
        logger.info(f"Initialized Pinecone index: {INDEX_NAME}")

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI's text-embedding-3-small model"""
        try:
            response = openai_client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def upsert_embedding(self, vector_id: str, embedding: List[float], metadata: Dict) -> bool:
        """Upsert embedding to Pinecone"""
        try:
            self.index.upsert(vectors=[(vector_id, embedding, metadata)])
            return True
        except Exception as e:
            logger.error(f"Error upserting embedding: {e}")
            raise

    def update_embedding(self, vector_id: str, embedding: List[float], metadata: Dict) -> bool:
        """Upsert embedding to Pinecone"""
        try:
            self.index.update(id=vector_id, set_metadata=metadata, values=embedding)
            return True
        except Exception as e:
            logger.error(f"Error updating embedding: {e}")
            raise

    def update_metadata(self, vector_id: str, metadata: Dict) -> bool:
        """Update metadata for an existing embedding"""
        try:
            self.index.update(id=vector_id, set_metadata=metadata)
            return True
        except Exception as e:
            logger.error(f"Error updating metadata: {e}")
            raise

    def create_message_embedding(
        self,
        message_content: str,
        message_id: int,
        user_id: int,
        channel_id: int,
        parent_id: Optional[int] = None,
        file_name: Optional[str] = None
    ) -> str:
        """Create embedding for a new message"""
        # Generate a unique UUID for the vector
        vector_id = str(uuid.uuid4())
        
        # Generate the embedding
        embedding = self.generate_embedding(message_content)
        
        # Prepare metadata
        metadata = {
            "message_id": message_id,
            "content": message_content,
            "user_id": user_id,
            "channel_id": channel_id,
            "parent_id": parent_id if parent_id else "",
            "has_file": bool(file_name),
            "file_name": file_name if file_name else ""
        }
        
        # Upsert to pinecone
        self.upsert_embedding(vector_id, embedding, metadata)
        logger.info(f"Created embedding for message {message_id} with vector_id {vector_id}")
        
        return vector_id

    def update_message_embedding(
        self,
        vector_id: str,
        new_content: str,
        message_id: int,
        has_file: bool,
        file_name: Optional[str] = None,
        parent_id: Optional[int] = None
    ) -> bool:
        """Update existing message embedding"""
        # Generate new embedding for updated content
        new_embedding = self.generate_embedding(new_content)
        
        # Update metadata with new content
        metadata = {
            "content": new_content,
            "has_file": has_file,
            "file_name": file_name if file_name else "",
            "parent_id": parent_id if parent_id else ""
        }


        # Upsert to pinecone (this will overwrite the existing vector)
        self.update_embedding(vector_id, new_embedding, metadata)
        logger.info(f"Updated embedding for message {message_id}")
        return True

    def delete_message_embedding(self, vector_id: str) -> bool:
        """Delete message embedding from Pinecone"""
        try:
            self.index.delete(ids=[vector_id])
            logger.info(f"Deleted embedding with vector_id {vector_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting embedding: {e}")
            raise

# Create a singleton instance
embedding_service = EmbeddingService() 