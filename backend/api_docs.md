# API Documentation

## Authentication

All endpoints (except authentication endpoints) require a valid Auth0 JWT token in the Authorization header:
```
Authorization: Bearer <your_auth0_token>
```

### Authentication Endpoints

#### 1. Sync Auth0 User
```http
POST /auth/sync
```

Syncs Auth0 user data with the local database.

**Request Body:**
```json
{
    "email": "user@example.com",
    "auth0_id": "auth0|123456789",
    "name": "User Name",
    "picture": "https://example.com/picture.jpg"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "email": "user@example.com",
    "name": "User Name",
    "picture": "https://example.com/picture.jpg",
    "auth0_id": "auth0|123456789",
    "is_active": true,
    "created_at": "2024-01-07T12:00:00Z"
}
```

#### 2. Verify Auth Token
```http
GET /auth/verify
```

Verifies Auth0 token and returns user data.

**Response (200 OK):**
```json
{
    "valid": true,
    "user": {
        "id": 1,
        "email": "user@example.com",
        "name": "User Name",
        "picture": "https://example.com/picture.jpg",
        "auth0_id": "auth0|123456789",
        "is_active": true,
        "created_at": "2024-01-07T12:00:00Z"
    }
}
```

## User Management

### 1. Get Current User
```http
GET /users/me
```

Returns the currently authenticated user's information.

**Response (200 OK):**
```json
{
    "id": 1,
    "email": "user@example.com",
    "name": "User Name",
    "picture": "https://example.com/picture.jpg",
    "auth0_id": "auth0|123456789",
    "is_active": true,
    "created_at": "2024-01-07T12:00:00Z"
}
```

### 2. List Users
```http
GET /users/?skip=0&limit=100
```

Returns a list of users with pagination.

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100)

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "email": "user1@example.com",
        "name": "User One",
        "picture": "https://example.com/picture1.jpg",
        "auth0_id": "auth0|123456789",
        "is_active": true,
        "created_at": "2024-01-07T12:00:00Z"
    },
    {
        "id": 2,
        "email": "user2@example.com",
        "name": "User Two",
        "picture": "https://example.com/picture2.jpg",
        "auth0_id": "auth0|987654321",
        "is_active": true,
        "created_at": "2024-01-07T12:00:00Z"
    }
]
```

### 3. Get User by ID
```http
GET /users/{user_id}
```

Returns information about a specific user.

**Response (200 OK):**
```json
{
    "id": 1,
    "email": "user@example.com",
    "name": "User Name",
    "picture": "https://example.com/picture.jpg",
    "auth0_id": "auth0|123456789",
    "is_active": true,
    "created_at": "2024-01-07T12:00:00Z"
}
```

## Channel Management

### 1. Create Channel
```http
POST /channels/
```

Creates a new channel.

**Request Body:**
```json
{
    "name": "general",
    "description": "General discussion channel"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "general",
    "description": "General discussion channel",
    "owner_id": 1,
    "created_at": "2024-01-07T12:00:00Z",
    "users": [
        {
            "id": 1,
            "email": "user@example.com",
            "name": "User Name"
        }
    ]
}
```

### 2. List User's Channels
```http
GET /channels/me?skip=0&limit=100
```

Returns all channels the current user is a member of.

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100)

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "general",
        "description": "General discussion channel",
        "owner_id": 1,
        "created_at": "2024-01-07T12:00:00Z",
        "users": [
            {
                "id": 1,
                "email": "user@example.com",
                "name": "User Name"
            }
        ]
    }
]
```

### 3. Get Channel
```http
GET /channels/{channel_id}
```

Returns information about a specific channel.

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "general",
    "description": "General discussion channel",
    "owner_id": 1,
    "created_at": "2024-01-07T12:00:00Z",
    "users": [
        {
            "id": 1,
            "email": "user@example.com",
            "name": "User Name"
        }
    ]
}
```

### 4. Update Channel
```http
PUT /channels/{channel_id}
```

Updates a channel's information. Only the channel owner can perform this action.

**Request Body:**
```json
{
    "name": "updated-general",
    "description": "Updated general discussion channel"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "updated-general",
    "description": "Updated general discussion channel",
    "owner_id": 1,
    "created_at": "2024-01-07T12:00:00Z",
    "users": [
        {
            "id": 1,
            "email": "user@example.com",
            "name": "User Name"
        }
    ]
}
```

### 5. Delete Channel
```http
DELETE /channels/{channel_id}
```

Deletes a channel. Only the channel owner can perform this action.

**Response (200 OK):**
Returns the deleted channel object.

## Message Management

### 1. Create Message
```http
POST /channels/{channel_id}/messages
```

Creates a new message in a channel.

**Request Body:**
```json
{
    "content": "Hello, world!"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "content": "Hello, world!",
    "created_at": "2024-01-07T12:00:00Z",
    "updated_at": "2024-01-07T12:00:00Z",
    "user_id": 1,
    "channel_id": 1,
    "user": {
        "id": 1,
        "email": "user@example.com",
        "name": "User Name"
    }
}
```

### 2. List Channel Messages
```http
GET /channels/{channel_id}/messages?skip=0&limit=50
```

Returns messages from a channel with pagination.

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 50)

**Response (200 OK):**
```json
{
    "messages": [
        {
            "id": 1,
            "content": "Hello, world!",
            "created_at": "2024-01-07T12:00:00Z",
            "updated_at": "2024-01-07T12:00:00Z",
            "user_id": 1,
            "channel_id": 1,
            "user": {
                "id": 1,
                "email": "user@example.com",
                "name": "User Name"
            }
        }
    ],
    "total": 1,
    "has_more": false
}
```

### 3. Update Message
```http
PUT /channels/{channel_id}/messages/{message_id}
```

Updates a message's content. Only the message author can perform this action.

**Request Body:**
```json
{
    "content": "Updated message content"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "content": "Updated message content",
    "created_at": "2024-01-07T12:00:00Z",
    "updated_at": "2024-01-07T12:30:00Z",
    "user_id": 1,
    "channel_id": 1,
    "user": {
        "id": 1,
        "email": "user@example.com",
        "name": "User Name"
    }
}
```

### 4. Delete Message
```http
DELETE /channels/{channel_id}/messages/{message_id}
```

Deletes a message. Only the message author can perform this action.

**Response (200 OK):**
Returns the deleted message object.

## WebSocket Connection

### Connect to WebSocket
```http
WS /ws?token=<auth0_token>
```

Establishes a WebSocket connection for real-time updates.

**Query Parameters:**
- `token`: Valid Auth0 JWT token

### WebSocket Events

1. **New Message**
```json
{
    "type": "new_message",
    "channel_id": 1,
    "message": {
        "id": 1,
        "content": "Hello, world!",
        "created_at": "2024-01-07T12:00:00Z",
        "user_id": 1,
        "channel_id": 1,
        "user": {
            "id": 1,
            "email": "user@example.com",
            "name": "User Name"
        }
    }
}
```

2. **Message Update**
```json
{
    "type": "message_update",
    "channel_id": 1,
    "message": {
        "id": 1,
        "content": "Updated content",
        "created_at": "2024-01-07T12:00:00Z",
        "updated_at": "2024-01-07T12:30:00Z",
        "user_id": 1,
        "channel_id": 1,
        "user": {
            "id": 1,
            "email": "user@example.com",
            "name": "User Name"
        }
    }
}
```

3. **Message Delete**
```json
{
    "type": "message_delete",
    "channel_id": 1,
    "message_id": 1
}
```

4. **Channel Update**
```json
{
    "type": "channel_update",
    "channel_id": 1,
    "channel": {
        "id": 1,
        "name": "updated-name",
        "description": "Updated description",
        "owner_id": 1
    }
}
```

## Error Responses

### 1. Unauthorized (401)
```json
{
    "detail": "Invalid or missing token"
}
```

### 2. Forbidden (403)
```json
{
    "detail": "Not enough permissions"
}
```

### 3. Not Found (404)
```json
{
    "detail": "Resource not found"
}
```

### 4. Bad Request (400)
```json
{
    "detail": "Invalid request"
}
```

### 5. Internal Server Error (500)
```json
{
    "detail": "Internal server error"
}
``` 