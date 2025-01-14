# Reaction Endpoints

All endpoints in this router require authentication via Bearer token. They handle message reaction operations including listing available reactions, adding reactions to messages, and removing reactions.

## Endpoints

### GET /reactions/
Get all available reactions.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Query Parameters:
  - `skip`: integer (optional, default: 0)
  - `limit`: integer (optional, default: 100)

#### Response
- Status: 200 OK
- Body: Array of Reaction objects
  ```json
  [
    {
      "id": "integer",
      "code": "string",
      "unicode": "string",
      "description": "string"
    }
  ]
  ```

### POST /reactions/{message_id}
Add a reaction to a message.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer
  - `message_id`: integer
- Body (MessageReactionCreate schema):
  ```json
  {
    "reaction_id": "integer"
  }
  ```

#### Response
- Status: 200 OK
- Body (MessageReaction schema):
  ```json
  {
    "id": "integer",
    "message_id": "integer",
    "reaction_id": "integer",
    "user_id": "integer",
    "created_at": "datetime"
  }
  ```

### DELETE /reactions/{message_id}/{reaction_id}
Remove a reaction from a message.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer
  - `message_id`: integer
  - `reaction_id`: integer

#### Response
- Status: 200 OK
- Body:
  ```json
  {
    "message": "Reaction removed successfully"
  }
  ```

## WebSocket Events

The reactions router broadcasts several events through WebSocket connections:

1. `reaction_add`: When a reaction is added to a message
2. `reaction_remove`: When a reaction is removed from a message

## Error Responses
- 400 Bad Request: Message does not belong to specified channel
- 401 Unauthorized: Missing or invalid token
- 403 Forbidden: Not a member of the channel
- 404 Not Found: Message or reaction not found
- 500 Internal Server Error: Server-side error 