# Message Edit and Delete Endpoints

This document outlines the requirements and specifications for the message editing and deletion endpoints in the ChatGenius API.

## Edit Message

**Endpoint:** `PUT /channels/{channel_id}/messages/{message_id}`

Updates the content of an existing message. Only the original author of the message can edit it.

### Request Parameters
- `channel_id` (path parameter, integer): The ID of the channel containing the message
- `message_id` (path parameter, integer): The ID of the message to edit

### Request Body
```json
{
    "content": "Updated message content"
}
```

### Response
```json
{
    "id": 123,
    "content": "Updated message content",
    "created_at": "2024-01-07T12:00:00Z",
    "updated_at": "2024-01-07T12:30:00Z",
    "user_id": 456,
    "channel_id": 789,
    "user": {
        "id": 456,
        "email": "user@example.com",
        "name": "User Name"
    }
}
```

### WebSocket Event
When a message is edited, all users in the channel will receive a WebSocket event:
```json
{
    "type": "message_update",
    "channel_id": 789,
    "message": {
        "id": 123,
        "content": "Updated message content",
        "created_at": "2024-01-07T12:00:00Z",
        "updated_at": "2024-01-07T12:30:00Z",
        "user_id": 456,
        "channel_id": 789,
        "user": {
            "id": 456,
            "email": "user@example.com",
            "name": "User Name"
        }
    }
}
```

### Error Responses
- 404: Message not found
- 400: Message does not belong to the specified channel
- 403: User is not the message author
- 401: Unauthorized (invalid or missing token)

## Delete Message

**Endpoint:** `DELETE /channels/{channel_id}/messages/{message_id}`

Deletes an existing message. Only the original author of the message can delete it.

### Request Parameters
- `channel_id` (path parameter, integer): The ID of the channel containing the message
- `message_id` (path parameter, integer): The ID of the message to delete

### Response
Returns the deleted message object before deletion:
```json
{
    "id": 123,
    "content": "Message content",
    "created_at": "2024-01-07T12:00:00Z",
    "updated_at": "2024-01-07T12:00:00Z",
    "user_id": 456,
    "channel_id": 789,
    "user": {
        "id": 456,
        "email": "user@example.com",
        "name": "User Name"
    }
}
```

### WebSocket Event
When a message is deleted, all users in the channel will receive a WebSocket event:
```json
{
    "type": "message_delete",
    "channel_id": 789,
    "message_id": 123
}
```

### Error Responses
- 404: Message not found
- 400: Message does not belong to the specified channel
- 403: User is not the message author
- 401: Unauthorized (invalid or missing token)

## Authentication

Both endpoints require authentication using a Bearer token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## Frontend Implementation Notes

1. The frontend should update its local message cache when receiving WebSocket events for message updates or deletions.
2. The UI should only show edit/delete options for messages authored by the current user.
3. The `updated_at` timestamp should be displayed when a message has been edited (when `updated_at` differs from `created_at`).
4. Handle error cases appropriately by showing user-friendly error messages.
5. Consider implementing optimistic updates for better UX while waiting for the server response. 