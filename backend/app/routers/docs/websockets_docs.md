# WebSocket Events

The WebSocket connection requires authentication via a token query parameter. It handles real-time messaging and reactions.

## Configuration
- Maximum connections per user: 5 (configurable via `MAX_WEBSOCKET_CONNECTIONS_PER_USER` env var)
- Maximum total connections: 1000 (configurable via `MAX_TOTAL_WEBSOCKET_CONNECTIONS` env var)

## Connection

### WebSocket URL
```
ws://{base_url}/ws?token={auth_token}
```

### Connection Flow
1. Client connects with valid auth token
2. Server verifies token and retrieves user
3. Server gets user's channel memberships
4. Server adds connection to event manager
5. Connection is established if limits not exceeded

## Client Events (Sent to Server)

### New Message
Send a new message to a channel.
```json
{
  "type": "new_message",
  "channel_id": "integer",
  "content": "string"
}
```

### Message Reply
Send a reply to an existing message.
```json
{
  "type": "message_reply",
  "channel_id": "integer",
  "parent_id": "integer",
  "content": "string"
}
```

### Add Reaction
Add a reaction to a message.
```json
{
  "type": "add_reaction",
  "channel_id": "integer",
  "message_id": "integer",
  "reaction_id": "integer"
}
```

### Remove Reaction
Remove a reaction from a message.
```json
{
  "type": "remove_reaction",
  "channel_id": "integer",
  "message_id": "integer",
  "reaction_id": "integer"
}
```

## Server Events (Sent to Client)

### New Message
Broadcast when a new message is created.
```json
{
  "type": "new_message",
  "channel_id": "integer",
  "message": {
    "id": "integer",
    "content": "string",
    "created_at": "datetime",
    "user_id": "integer",
    "channel_id": "integer",
    "from_ai": "boolean",
    "user": {
      "id": "integer",
      "email": "string",
      "name": "string"
    }
  }
}
```

### Message Created (Reply)
Broadcast when a reply message is created.
```json
{
  "type": "message_created",
  "channel_id": "integer",
  "message": {
    "id": "integer",
    "content": "string",
    "created_at": "datetime",
    "updated_at": "datetime",
    "user_id": "integer",
    "channel_id": "integer",
    "parent_id": "integer",
    "parent": {
      "id": "integer",
      "content": "string",
      "created_at": "datetime",
      "user_id": "integer",
      "channel_id": "integer"
    },
    "user": {
      "id": "integer",
      "email": "string",
      "name": "string",
      "picture": "string"
    }
  }
}
```

### Message Update
Broadcast when a message is updated or gets replies.
```json
{
  "type": "message_update",
  "channel_id": "integer",
  "message": {
    "id": "integer",
    "content": "string",
    "created_at": "datetime",
    "updated_at": "datetime",
    "user_id": "integer",
    "channel_id": "integer",
    "parent_id": "integer",
    "has_replies": "boolean",
    "user": {
      "id": "integer",
      "email": "string",
      "name": "string",
      "picture": "string"
    }
  }
}
```

### Reaction Added
Broadcast when a reaction is added to a message.
```json
{
  "type": "message_reaction_add",
  "channel_id": "integer",
  "message_id": "integer",
  "reaction": {
    "id": "integer",
    "message_id": "integer",
    "reaction_id": "integer",
    "user_id": "integer",
    "created_at": "datetime",
    "reaction": {
      "id": "integer",
      "code": "string",
      "is_system": "boolean",
      "image_url": "string"
    },
    "user": {
      "id": "integer",
      "email": "string",
      "name": "string",
      "picture": "string"
    }
  }
}
```

### Reaction Removed
Broadcast when a reaction is removed from a message.
```json
{
  "type": "message_reaction_remove",
  "channel_id": "integer",
  "message_id": "integer",
  "reaction_id": "integer",
  "user_id": "integer"
}
```

## Error Handling

### Close Codes
- 1008 (Policy Violation): Invalid token or user not found
- 1011 (Internal Error): Server-side error

### Disconnection
- Client disconnects: Server removes connection from event manager
- Server error: Server removes connection and closes with appropriate code
- Rate limit exceeded: Server refuses connection 