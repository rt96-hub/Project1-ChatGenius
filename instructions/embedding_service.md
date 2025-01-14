## Plan of Action to Integrate Pinecone Vector Storage for Messages

### Overview
We will create a new Python file in the backend (e.g., `embedding_service.py`) to handle the following tasks related to message embeddings:
- Generate embeddings using OpenAI
- Insert the embeddings into Pinecone
- Store the vector ID (UUID) in the database for future reference

Below is our plan, along with code snippet placeholders.

---

### Tasks

- [x] Set up Pinecone client and environment variables (API Keys, Environment)
- [x] Implement function to generate embeddings using OpenAI
- [x] Implement function to save embeddings to Pinecone
- [ ] Integrate the logic into our message creation workflow
- [x] Add a UUID field to the Messages table (DB migration)

---

### Implementation Details

1. Add a new UUID field to messages table (e.g., `vector_id`) to store the Pinecone vector ID.
2. Create a Python file (e.g., `backend/embedding_service.py`) to encapsulate:
   - Pinecone client initialization
   - Embedding generation with OpenAI
   - Functions for inserting/updating/deleting embeddings in Pinecone

3. Update the message creation endpoint/service logic:
   - After a new message is created in the database, generate an embedding for the message content.
   - Obtain a new UUID for the message’s `vector_id`.
   - Store the new vector (embedding + metadata) in Pinecone.

4. For message editing and deletion, we’ll add logic in `embedding_service.py` to handle updating or removing from Pinecone.
    - When a message is edited, we'll regenerate the embedding and update the Pinecone vector.
    - When a message is deleted, we'll remove the Pinecone vector.

---

### Code Snippets

Below are snippet placeholders demonstrating a possible structure for `embedding_service.py`.  
Replace the placeholders with actual code.

[CODE START]
import pinecone
import openai
import uuid

PINECONE_API_KEY = "..."
PINECONE_ENVIRONMENT = "..."
INDEX_NAME = "my_app_messages"
# any other environment variables as needed, e.g. OPENAI_API_KEY

# Initialize pinecone
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

index = pinecone.Index(INDEX_NAME)

def generate_embedding(text: str) -> list:
    # Call OpenAI API to generate embedding
    # Return the embedding vector
    pass

def upsert_embedding_to_pinecone(vector_id: str, embedding: list, metadata: dict):
    # Upsert the vector to Pinecone with the embedding and metadata
    pass

def create_message_embedding(message_content: str, message_id: int, ...) -> str:
    # Generate a unique UUID
    vector_id = str(uuid.uuid4())
    
    # Generate the embedding
    embedding = generate_embedding(message_content)
    
    # Prepare metadata
    # get the fields as needed from the message object or related objects
    metadata = {
        "message_id": message_id,
        "content": message_content,
        "created_at": message_created_at,
        "updated_at": message_updated_at,
        "user_id": message_user_id,
        "channel_id": message_channel_id,
        "parent_id": message_parent_id,
        "has_file": message_has_file,
        "file_name": message_file_name # may be null
    }
    
    # Upsert to pinecone
    upsert_embedding_to_pinecone(vector_id, embedding, metadata)
    
    return vector_id

def update_message_embedding(message_id: int, new_content: str):
    # Update the Pinecone vector with the new content, metadata, and embedding
    pass

def delete_message_embedding(message_id: int):
    # Delete the Pinecone vector for the message
    pass
[CODE END]

---

### Next Steps
- Integrate this module into the main message creation flow (e.g., whenever we create a new message in `backend/crud.py`, call `create_message_embedding` and save the returned `vector_id` to the database).
- Integrate this module into the main message editing flow (e.g., whenever we edit a message in `backend/crud.py`, call `update_message_embedding`).
- Integrate this module into the main message deletion flow (e.g., whenever we delete a message in `backend/crud.py`, call `delete_message_embedding`).
- Perform DB migration to ensure `vector_id` is stored in the `messages` table.
- Create a process to do a mass update of all existing messages to generate embeddings and store them in Pinecone.
- Test thoroughly to ensure embeddings are generated and stored properly in Pinecone.
