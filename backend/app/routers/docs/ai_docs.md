# AI Assistant Endpoints

All endpoints in this router require authentication via Bearer token. They handle AI conversation operations including creating new conversations, adding messages, and retrieving conversation history.

## Endpoints

### GET /ai/channels/{channel_id}/conversations
Returns all AI conversations for a specific channel that belong to the authenticated user.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer
- Query Parameters:
  - `skip`: integer (optional, default: 0)
  - `limit`: integer (optional, default: 50)

#### Response
- Status: 200 OK
- Body:
  ```json
  {
    "conversations": [
      {
        "id": "string",
        "channelId": "integer",
        "userId": "integer",
        "messages": [
          {
            "id": "string",
            "content": "string",
            "role": "user | assistant",
            "timestamp": "datetime",
            "parameters": "object | null"
          }
        ],
        "createdAt": "datetime",
        "updatedAt": "datetime"
      }
    ]
  }
  ```

### GET /ai/channels/{channel_id}/conversations/{conversation_id}
Get a specific AI conversation with all its messages.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer
  - `conversation_id`: string

#### Response
- Status: 200 OK
- Body:
  ```json
  {
    "id": "string",
    "channelId": "integer",
    "userId": "integer",
    "messages": [
      {
        "id": "string",
        "content": "string",
        "role": "user | assistant",
        "timestamp": "datetime",
        "parameters": "object | null"
      }
    ],
    "createdAt": "datetime",
    "updatedAt": "datetime"
  }
  ```

### DELETE /ai/channels/{channel_id}/conversations/{conversation_id}
Delete a specific AI conversation and all its messages.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer
  - `conversation_id`: string

#### Response
- Status: 204 No Content

#### Error Responses
- 400: Conversation does not belong to this channel
- 403: Not a member of this channel
- 404: Channel or conversation not found
- 500: Failed to delete conversation

### POST /ai/channels/{channel_id}/query
Submit a new query to the AI assistant and start a new conversation.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer
- Body:
  ```json
  {
    "query": "string"
  }
  ```

#### Response
- Status: 200 OK
- Body:
  ```json
  {
    "conversation": {
      "id": "string",
      "channelId": "integer",
      "userId": "integer",
      "messages": [
        {
          "id": "string",
          "content": "string",
          "role": "user | assistant",
          "timestamp": "datetime",
          "parameters": "object | null"
        }
      ],
      "createdAt": "datetime",
      "updatedAt": "datetime"
    },
    "message": {
      "id": "string",
      "content": "string",
      "role": "assistant",
      "timestamp": "datetime",
      "parameters": "object | null"
    }
  }
  ```

### POST /ai/channels/{channel_id}/conversations/{conversation_id}/messages
Add a new message to an existing AI conversation.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer
  - `conversation_id`: string
- Body:
  ```json
  {
    "content": "string",
    "role": "user"
  }
  ```

#### Response
- Status: 200 OK
- Body:
  ```json
  {
    "id": "string",
    "channelId": "integer",
    "userId": "integer",
    "messages": [
      {
        "id": "string",
        "content": "string",
        "role": "user | assistant",
        "timestamp": "datetime",
        "parameters": "object | null"
      }
    ],
    "createdAt": "datetime",
    "updatedAt": "datetime"
  }
  ```

### GET /ai/channels/{channel_id}/summarize
Get a summary of channel messages for a specified time period.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer
- Query Parameters:
  - `quantity`: integer (required) - The number of time units to look back
  - `time_unit`: string (required) - One of: "hours", "days", "weeks"

#### Response
- Status: 200 OK
- Body:
  ```json
  {
    "summary": "string"
  }
  ```

#### Error Responses
- 404: Channel not found
- 403: Not a member of this channel
- 500: Internal server error


## Access Control
- All endpoints require authentication via Bearer token
- Users can only access conversations they created
- Users must be members of the channel to use any AI features
- Each conversation is tied to a specific channel

## Error Responses

### 400 Bad Request
```json
{
  "error": "string",
  "message": "string"
}
```

### 401 Unauthorized
```json
{
  "error": "string",
  "message": "Unauthorized access"
}
```

### 403 Forbidden
```json
{
  "error": "string",
  "message": "Not a member of this channel"
}
```

### 404 Not Found
```json
{
  "error": "string",
  "message": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "string",
  "message": "Internal server error"
}
```

## Notes
- The `role` field in messages can only be either "user" or "assistant"
- The `parameters` field is a JSON object that can contain additional metadata about the message
- All timestamps are in ISO 8601 format
- Conversation and message IDs are UUIDs stored as strings
- The most recent conversations are returned first when listing conversations
- Each conversation maintains a `last_message` timestamp that's updated whenever a new message is added 