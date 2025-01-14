# Message Endpoints

All endpoints in this router require authentication via Bearer token. They handle message-related operations including creation, updates, deletion, and file attachments.

## File Upload Configuration
- Maximum file size: 50MB (configurable via `MAX_FILE_SIZE_MB` env var)
- Allowed file types (configurable via `ALLOWED_FILE_TYPES` env var):
  - Images (`image/*`)
  - PDFs (`application/pdf`)
  - Text files (`text/*`)

## Endpoints

### POST /messages/{channel_id}/messages
Create a new message in a channel.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer
- Body (MessageCreate schema):
  ```json
  {
    "content": "string",
    "metadata": {
      "key": "value"
    }
  }
  ```

#### Response
- Status: 200 OK
- Body (Message schema):
  ```json
  {
    "id": "integer",
    "channel_id": "integer",
    "user_id": "integer",
    "content": "string",
    "metadata": "object",
    "parent_id": "integer",
    "has_replies": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
  ```

### GET /messages/{channel_id}/messages
Get messages from a channel.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer
- Query Parameters:
  - `skip`: integer (optional, default: 0)
  - `limit`: integer (optional, default: 50)
  - `include_reactions`: boolean (optional, default: false)
  - `parent_only`: boolean (optional, default: true)

#### Response
- Status: 200 OK
- Body (MessageList schema):
  ```json
  {
    "total": "integer",
    "messages": [Message]
  }
  ```

### PUT /messages/{channel_id}/messages/{message_id}
Update a message (author only).

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer
  - `message_id`: integer
- Body (MessageCreate schema):
  ```json
  {
    "content": "string",
    "metadata": {
      "key": "value"
    }
  }
  ```

#### Response
- Status: 200 OK
- Body: Updated Message object

### DELETE /messages/{channel_id}/messages/{message_id}
Delete a message (author only).

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer
  - `message_id`: integer

#### Response
- Status: 200 OK
- Body: Deleted Message object

### POST /messages/{channel_id}/messages/{parent_id}/reply
Create a reply to a message.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer
  - `parent_id`: integer
- Body (MessageReplyCreate schema):
  ```json
  {
    "content": "string",
    "metadata": {
      "key": "value"
    }
  }
  ```

#### Response
- Status: 200 OK
- Body: Message object

### GET /messages/{message_id}/reply-chain
Get all messages in a reply chain.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `message_id`: integer

#### Response
- Status: 200 OK
- Body: Array of Message objects

### POST /messages/{channel_id}/messages/with-file
Create a message with a file attachment.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer
- Form Data:
  - `file`: File (optional)
  - `content`: string (optional)
  - `parent_id`: integer (optional)

#### Response
- Status: 200 OK
- Body: Message object with file metadata

### POST /messages/{channel_id}/messages/{parent_id}/reply-with-file
Create a reply message with a file attachment.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer
  - `parent_id`: integer
- Form Data:
  - `file`: File (optional)
  - `content`: string (optional)

#### Response
- Status: 200 OK
- Body: Message object with file metadata

## WebSocket Events

The messages router broadcasts several events through WebSocket connections:

1. `message_created`: When a new message is created
2. `message_updated`: When a message is edited
3. `message_deleted`: When a message is deleted
4. `root_message_update`: When a message gets replies

## Error Responses
- 400 Bad Request: Invalid request data or file type
- 401 Unauthorized: Missing or invalid token
- 403 Forbidden: Not a member of the channel or not the message author
- 404 Not Found: Channel or message not found
- 413 Request Entity Too Large: File size exceeds limit
- 500 Internal Server Error: Server-side error 