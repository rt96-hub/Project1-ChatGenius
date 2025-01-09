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

**Request Headers:**
```
Authorization: Bearer <your_auth0_token>
```

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
    "created_at": "2024-01-07T12:00:00Z",
    "bio": null
}
```

#### 2. Verify Auth Token
```http
GET /auth/verify
```

Verifies Auth0 token and returns user data.

**Request Headers:**
```
Authorization: Bearer <your_auth0_token>
```

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
        "created_at": "2024-01-07T12:00:00Z",
        "bio": null
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
    "created_at": "2024-01-07T12:00:00Z",
    "bio": "User's bio text",
    "channels": [],
    "messages": []
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
        "created_at": "2024-01-07T12:00:00Z",
        "bio": "User's bio text",
        "channels": [],
        "messages": []
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
    "created_at": "2024-01-07T12:00:00Z",
    "bio": "User's bio text",
    "channels": [],
    "messages": []
}
```

### 4. Update User Bio
```http
PUT /users/me/bio
```

Updates the bio of the currently authenticated user.

**Request Body:**
```json
{
    "bio": "New bio text"
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
    "created_at": "2024-01-07T12:00:00Z",
    "bio": "New bio text",
    "channels": [],
    "messages": []
}
```

### 5. Update User Name
```http
PUT /users/me/name
```

Updates the name of the currently authenticated user.

**Request Body:**
```json
{
    "name": "New User Name"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "email": "user@example.com",
    "name": "New User Name",
    "picture": "https://example.com/picture.jpg",
    "auth0_id": "auth0|123456789",
    "is_active": true,
    "created_at": "2024-01-07T12:00:00Z",
    "bio": "User's bio text",
    "channels": [],
    "messages": []
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
    "description": "General discussion channel",
    "is_private": false,
    "join_code": null
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
    "is_private": false,
    "join_code": null,
    "users": [
        {
            "id": 1,
            "email": "user@example.com",
            "name": "User Name",
            "picture": "https://example.com/picture.jpg"
        }
    ],
    "messages": []
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
        "is_private": false,
        "join_code": null,
        "users": [
            {
                "id": 1,
                "email": "user@example.com",
                "name": "User Name",
                "picture": "https://example.com/picture.jpg"
            }
        ],
        "messages": []
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
    "is_private": false,
    "join_code": null,
    "users": [
        {
            "id": 1,
            "email": "user@example.com",
            "name": "User Name",
            "picture": "https://example.com/picture.jpg"
        }
    ],
    "messages": []
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
    "description": "Updated general discussion channel",
    "is_private": false,
    "join_code": null
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
    "is_private": false,
    "join_code": null,
    "users": [
        {
            "id": 1,
            "email": "user@example.com",
            "name": "User Name",
            "picture": "https://example.com/picture.jpg"
        }
    ],
    "messages": []
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
        "name": "User Name",
        "picture": "https://example.com/picture.jpg"
    },
    "reactions": []
}
```

### 2. List Channel Messages
```http
GET /channels/{channel_id}/messages?skip=0&limit=50&include_reactions=true
```

Returns messages from a channel with pagination.

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 50)
- `include_reactions` (optional): Whether to include message reactions (default: false)

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
                "name": "User Name",
                "picture": "https://example.com/picture.jpg"
            },
            "reactions": []
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
        "name": "User Name",
        "picture": "https://example.com/picture.jpg"
    },
    "reactions": []
}
```

### 4. Delete Message
```http
DELETE /channels/{channel_id}/messages/{message_id}
```

Deletes a message. Only the message author can perform this action.

**Response (200 OK):**
Returns the deleted message object.

## Channel Membership and Roles

### 1. List Channel Members
```http
GET /channels/{channel_id}/members
```

Returns a list of users who are members of the channel.

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "email": "user1@example.com",
        "name": "User One",
        "picture": "https://example.com/picture1.jpg"
    },
    {
        "id": 2,
        "email": "user2@example.com",
        "name": "User Two",
        "picture": "https://example.com/picture2.jpg"
    }
]
```

### 2. Remove Channel Member
```http
DELETE /channels/{channel_id}/members/{user_id}
```

Removes a user from a channel. Only the channel owner can perform this action.

**Response (200 OK):**
```json
{
    "message": "Member removed successfully"
}
```

### 3. Update Channel Privacy
```http
PUT /channels/{channel_id}/privacy
```

Updates a channel's privacy settings. Only the channel owner can perform this action.

**Request Body:**
```json
{
    "is_private": true,
    "join_code": "optional_join_code"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "channel-name",
    "description": "Channel description",
    "is_private": true,
    "join_code": "abc123xyz",
    "owner_id": 1,
    "created_at": "2024-01-07T12:00:00Z",
    "users": [
        {
            "id": 1,
            "email": "user@example.com",
            "name": "User Name",
            "picture": "https://example.com/picture.jpg"
        }
    ],
    "messages": []
}
```

### 4. Create Channel Invite
```http
POST /channels/{channel_id}/invite
```

Creates an invite code for the channel. Any channel member can create an invite.

**Response (200 OK):**
```json
{
    "join_code": "abc123xyz",
    "channel_id": 1
}
```

### 5. Get User's Channel Role
```http
GET /channels/{channel_id}/role?user_id={user_id}
```

Returns the role of a specific user in the channel.

**Response (200 OK):**
```json
{
    "id": 1,
    "channel_id": 1,
    "user_id": 2,
    "role": "moderator",
    "created_at": "2024-01-07T12:00:00Z"
}
```

### 6. Update User's Channel Role
```http
PUT /channels/{channel_id}/roles/{user_id}
```

Updates a user's role in the channel. Only the channel owner can perform this action.

**Request Body:**
```json
{
    "role": "moderator"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "channel_id": 1,
    "user_id": 2,
    "role": "moderator",
    "created_at": "2024-01-07T12:00:00Z"
}
```

### 7. Leave Channel
```http
POST /channels/{channel_id}/leave
```

Allows a user to leave a channel. If the user is the owner, ownership will be transferred to another member if possible.

**Response (200 OK):**
```json
{
    "message": "Successfully left the channel"
}
```

## Reaction Management

### 1. List All Reactions
```http
GET /reactions/?skip=0&limit=100
```

Returns a list of all available reactions with pagination.

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100)

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "code": "thumbs_up",
        "is_system": true,
        "image_url": null,
        "created_at": "2024-01-08T12:00:00Z"
    },
    {
        "id": 2,
        "code": "heart",
        "is_system": true,
        "image_url": null,
        "created_at": "2024-01-08T12:00:00Z"
    }
]
```

### 2. Add Reaction to Message
```http
POST /channels/{channel_id}/messages/{message_id}/reactions
```

Adds a reaction to a message. If the user has already added this reaction to this message, returns the existing reaction.

**Request Body:**
```json
{
    "reaction_id": 1
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "message_id": 1,
    "reaction_id": 1,
    "user_id": 1,
    "created_at": "2024-01-08T12:00:00Z",
    "code": "thumbs_up",
    "reaction": {
        "id": 1,
        "code": "thumbs_up",
        "is_system": true,
        "image_url": null,
        "created_at": "2024-01-08T12:00:00Z"
    },
    "user": {
        "id": 1,
        "email": "user@example.com",
        "name": "User Name",
        "picture": "https://example.com/picture.jpg"
    }
}
```

### 3. Remove Reaction from Message
```http
DELETE /channels/{channel_id}/messages/{message_id}/reactions/{reaction_id}
```

Removes a user's reaction from a message.

**Response (200 OK):**
```json
{
    "message": "Reaction removed successfully"
}
```

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
            "name": "User Name",
            "picture": "https://example.com/picture.jpg"
        },
        "reactions": []
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
            "name": "User Name",
            "picture": "https://example.com/picture.jpg"
        },
        "reactions": []
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
        "owner_id": 1,
        "is_private": false,
        "join_code": null
    }
}
```

5. **Member Joined**
```json
{
    "type": "member_joined",
    "channel_id": 1,
    "user": {
        "id": 1,
        "email": "user@example.com",
        "name": "User Name",
        "picture": "https://example.com/picture.jpg"
    }
}
```

6. **Member Left**
```json
{
    "type": "member_left",
    "channel_id": 1,
    "user_id": 1
}
```

7. **Role Updated**
```json
{
    "type": "role_updated",
    "channel_id": 1,
    "user_id": 1,
    "role": "moderator"
}
```

8. **Privacy Updated**
```json
{
    "type": "privacy_updated",
    "channel_id": 1,
    "is_private": true
}
```

9. **Add Reaction**
```json
{
    "type": "message_reaction_add",
    "channel_id": 1,
    "message_id": 1,
    "reaction": {
        "id": 1,
        "reaction_id": 1,
        "user_id": 1,
        "created_at": "2024-01-08T12:00:00Z",
        "user": {
            "id": 1,
            "email": "user@example.com",
            "name": "User Name",
            "picture": "https://example.com/picture.jpg"
        }
    }
}
```

10. **Remove Reaction**
```json
{
    "type": "message_reaction_remove",
    "channel_id": 1,
    "message_id": 1,
    "reaction_id": 1,
    "user_id": 1
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

### Create DM Channel
```http
POST /channels/dm
```

Creates a new DM (Direct Message) channel with multiple users. DM channels are always private.

**Request Body:**
```json
{
    "user_ids": [2, 3, 4],  // IDs of users to include in the DM (excluding the creator)
    "name": "optional-group-name"  // Optional name for group DMs with more than 2 users
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "dm-user1-user2",  // Auto-generated for 2-person DMs
    "description": "Direct Message Channel",
    "owner_id": 1,
    "created_at": "2024-01-07T12:00:00Z",
    "is_private": true,
    "is_dm": true,
    "join_code": null,
    "users": [
        {
            "id": 1,
            "email": "user1@example.com",
            "name": "User One",
            "picture": "https://example.com/picture1.jpg"
        },
        {
            "id": 2,
            "email": "user2@example.com",
            "name": "User Two",
            "picture": "https://example.com/picture2.jpg"
        }
    ],
    "messages": []
}
```

**Error Responses:**
- `400 Bad Request`: If the creator is included in user_ids or if any user ID is invalid
- `401 Unauthorized`: If the user is not authenticated 

### 2. List User's DMs
```http
GET /channels/me/dms?skip=0&limit=100
```

Returns all DM channels the current user is a member of, ordered by most recent message.

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100)

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "dm-user1-user2",
        "description": "Direct Message Channel",
        "owner_id": 1,
        "created_at": "2024-01-07T12:00:00Z",
        "is_private": true,
        "is_dm": true,
        "join_code": null,
        "users": [
            {
                "id": 1,
                "email": "user1@example.com",
                "name": "User One",
                "picture": "https://example.com/picture1.jpg"
            },
            {
                "id": 2,
                "email": "user2@example.com",
                "name": "User Two",
                "picture": "https://example.com/picture2.jpg"
            }
        ],
        "messages": []
    }
]
```

### 3. List User's Channels
```http
GET /channels/me?skip=0&limit=100
```

Returns all channels the current user is a member of, ordered by most recent message.

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
        "is_private": false,
        "join_code": null,
        "users": [
            {
                "id": 1,
                "email": "user@example.com",
                "name": "User Name",
                "picture": "https://example.com/picture.jpg"
            }
        ],
        "messages": []
    }
]
``` 