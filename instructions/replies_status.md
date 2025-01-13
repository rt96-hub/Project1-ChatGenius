# Message Replies Status

## Database Structure

### Message Model
The message reply system is built into the `Message` model with the following key components:
- `parent_id`: Foreign key to the parent message (nullable)
- `parent`: Relationship to parent message
- `reply`: Back reference to child message
- Unique constraint on `parent_id` to ensure one reply per message

### Migration Status
- Migration file exists: `9fc612a29cc9_chat_replies.py`
- Adds `parent_id` column to messages table
- Creates unique constraint `unique_reply_message`

## Core Functionality

### Reply Chain Design
1. Messages form a linked list structure where:
   - Root messages have `parent_id = null`
   - Reply messages have `parent_id` pointing to their parent
   - Each message can have at most one reply (enforced by unique constraint)
   - New replies are automatically attached to the last message in the chain

### CRUD Operations

#### 1. Create Reply
Function: `create_reply` in `crud.py`
- Creates a reply to a message
- Automatically finds the last message in the reply chain
- Attaches new reply to the last message
- Returns the created message

#### 2. Find Last Reply
Function: `find_last_reply_in_chain` in `crud.py`
- Recursively finds the last message in a reply chain
- Returns the last message that doesn't have a reply

#### 3. Get Reply Chain
Function: `get_message_reply_chain` in `crud.py`
- Gets all messages in a reply chain
- Includes:
  - Original message
  - Parent messages (if given message is a reply)
  - All reply messages
- Returns messages ordered by creation date
- Eager loads user data for each message

#### 4. List Channel Messages
Function: `get_channel_messages` in `crud.py`
- Supports filtering for parent messages only
- Includes parent message data for replies
- Adds `has_replies` flag to indicate if a message has replies
- Supports pagination and reaction inclusion

## API Endpoints

### 1. Create Reply
```http
POST /channels/{channel_id}/messages/{parent_id}/reply
```
- Creates a reply to a message
- Documented in API docs but **NOT IMPLEMENTED** in main.py

### 2. List Messages
```http
GET /channels/{channel_id}/messages
```
- Implemented and working
- Supports query parameters:
  - `skip`: Pagination offset
  - `limit`: Page size
  - `include_reactions`: Include reaction data
  - `parent_only`: Show only root messages

### 3. Get Reply Chain
```http
GET /messages/{message_id}/reply-chain
```
- Documented in API docs but **NOT IMPLEMENTED** in main.py

## WebSocket Events

### Message Events
1. New Message Event:
```json
{
    "type": "message_created",
    "message": {
        "id": 2,
        "content": "Reply content",
        "parent_id": 1,
        ...
    }
}
```

2. Message Update Event:
```json
{
    "type": "message_update",
    "channel_id": 1,
    "message": {
        "id": 1,
        "content": "Updated content",
        "parent_id": null,
        ...
    }
}
```

## Missing Components

1. **API Endpoints**:
   - Reply creation endpoint not implemented
   - Reply chain retrieval endpoint not implemented

2. **Frontend Integration**:
   - No documentation on frontend components for reply UI
   - No documentation on reply chain visualization

## Recommendations

1. **Implementation Needed**:
   - Implement missing API endpoints for reply creation and chain retrieval
   - Add proper error handling for reply operations
   - Add validation for reply chain depth limits

2. **Documentation Updates**:
   - Add frontend integration guidelines
   - Document reply chain visualization patterns
   - Add examples of reply chain reconstruction

3. **Testing**:
   - Add unit tests for reply chain operations
   - Add integration tests for reply endpoints
   - Test edge cases in reply chain handling 