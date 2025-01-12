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

### 6. List Users by Last DM
```http
GET /users/by-last-dm?skip=0&limit=100
```

Returns a list of users ordered by their last one-on-one DM interaction with the current user. Only includes users who have or could have a one-on-one DM with the current user. Users with no DM history appear first, followed by users ordered by ascending date of last DM (most recent DM appears last).

**Important Notes:**
- Only includes one-on-one DMs (channels with exactly 2 users)
- Each user pair will have at most one DM channel
- Group DMs are not included in this endpoint

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100)

**Response (200 OK):**
```json
[
    {
        "user": {
            "id": 2,
            "email": "user2@example.com",
            "name": "User Two",
            "picture": "https://example.com/picture2.jpg",
            "auth0_id": "auth0|234567890",
            "is_active": true,
            "created_at": "2024-01-07T12:00:00Z",
            "bio": null
        },
        "last_dm_at": null,     // No DM history
        "channel_id": null      // No DM channel exists yet
    },
    {
        "user": {
            "id": 3,
            "email": "user3@example.com",
            "name": "User Three",
            "picture": "https://example.com/picture3.jpg",
            "auth0_id": "auth0|345678901",
            "is_active": true,
            "created_at": "2024-01-07T12:00:00Z",
            "bio": null
        },
        "last_dm_at": "2024-01-08T10:00:00Z",  // Last DM was on this date
        "channel_id": 123                       // ID of their one-on-one DM channel
    }
]
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
    "is_private": false
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
    "is_private": false
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

### 2. Get Available Channels
```http
GET /channels/available
```

Get all public channels that the current user can join.

**Query Parameters:**
- `skip` (optional): Number of channels to skip (default: 0)
- `limit` (optional): Maximum number of channels to return (default: 50)

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "General",
        "description": "General discussion channel",
        "created_at": "2024-01-07T12:00:00Z",
        "owner_id": 1,
        "is_private": false,
        "is_dm": false,
        "users": [
            {
                "id": 1,
                "email": "user1@example.com",
                "name": "User One",
                "picture": "https://example.com/picture1.jpg"
            }
        ]
    }
]
```

### 3. Join Channel
```http
POST /channels/{channel_id}/join
```

Join a public channel.

**Path Parameters:**
- `channel_id`: ID of the channel to join

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "General",
    "description": "General discussion channel",
    "created_at": "2024-01-07T12:00:00Z",
    "owner_id": 1,
    "is_private": false,
    "is_dm": false,
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
    ]
}
```

**Error Responses:**
- `404 Not Found`: Channel does not exist
- `403 Forbidden`: Cannot join private or DM channels directly
- `400 Bad Request`: Failed to join channel (e.g., already a member)

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

Returns messages from a channel with pagination. Messages that are replies will include their parent message data.

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 50)
- `include_reactions` (optional): Whether to include message reactions (default: false)

**Response (200 OK):**
```json
{
    "messages": [
        {
            "id": 2,
            "content": "This is a reply",
            "created_at": "2024-01-07T12:00:00Z",
            "updated_at": "2024-01-07T12:00:00Z",
            "user_id": 1,
            "channel_id": 1,
            "parent_id": 1,
            "user": {
                "id": 1,
                "email": "user@example.com",
                "name": "User Name",
                "picture": "https://example.com/picture.jpg"
            },
            "reactions": [],
            "parent": {
                "id": 1,
                "content": "Original message",
                "created_at": "2024-01-07T11:00:00Z",
                "updated_at": "2024-01-07T11:00:00Z",
                "user_id": 2,
                "channel_id": 1,
                "parent_id": null,
                "user": {
                    "id": 2,
                    "email": "user2@example.com",
                    "name": "User Two",
                    "picture": "https://example.com/picture2.jpg"
                }
            }
        },
        {
            "id": 1,
            "content": "Original message",
            "created_at": "2024-01-07T11:00:00Z",
            "updated_at": "2024-01-07T11:00:00Z",
            "user_id": 2,
            "channel_id": 1,
            "parent_id": null,
            "user": {
                "id": 2,
                "email": "user2@example.com",
                "name": "User Two",
                "picture": "https://example.com/picture2.jpg"
            },
            "reactions": [],
            "parent": null
        }
    ],
    "total": 2,
    "has_more": false
}
```

**Notes on Reply Chains:**
- Messages with `parent_id === null` are original messages
- Messages with `parent_id !== null` are replies
- Each message can have at most one reply (enforced by unique constraint)
- When replying to a message that already has replies, the new reply is automatically attached to the last message in the chain
- The frontend can reconstruct reply chains by:
  1. Finding messages with parent_id to identify replies
  2. Using the parent object to get the original message content and author
  3. Following parent_id references to build the complete chain

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
    "is_private": true
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "channel-name",
    "description": "Channel description",
    "is_private": true,
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

2. **Channel Created**
```json
{
    "type": "channel_created",
    "channel": {
        "id": 1,
        "name": "dm-user1-user2",
        "description": "Direct Message Channel",
        "owner_id": 1,
        "created_at": "2024-01-07T12:00:00Z",
        "is_private": true,
        "is_dm": true,
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
        ]
    }
}
```

3. **Message Update**
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

4. **Message Delete**
```json
{
    "type": "message_delete",
    "channel_id": 1,
    "message_id": 1
}
```

5. **Channel Update**
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

6. **Member Joined**
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

7. **Member Left**
```json
{
    "type": "member_left",
    "channel_id": 1,
    "user_id": 1
}
```

8. **Role Updated**
```json
{
    "type": "role_updated",
    "channel_id": 1,
    "user_id": 1,
    "role": "moderator"
}
```

9. **Privacy Updated**
```json
{
    "type": "privacy_updated",
    "channel_id": 1,
    "is_private": true
}
```

10. **Add Reaction**
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

11. **Remove Reaction**
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

### Check Existing DM Channel
```http
GET /channels/dm/check/{other_user_id}
```

Checks if there's an existing one-on-one DM channel between the current user and another user. This is useful to avoid creating duplicate DM channels between the same users.

**Parameters:**
- `other_user_id`: The ID of the user to check for an existing DM channel with

**Response (200 OK):**
```json
{
    "channel_id": 123  // ID of the existing DM channel, or null if none exists
}
```

**Error Responses:**
- `401 Unauthorized`: If the user is not authenticated
- `404 Not Found`: If the other user doesn't exist
- `500 Internal Server Error`: If there's a server error

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

### Messages

#### 1. Create Message Reply
```http
POST /channels/{channel_id}/messages/{parent_id}/reply
```

Creates a reply to a message. If the parent message already has a reply, the new message will be automatically attached to the last message in the reply chain.

**Implementation Details:**
- Function: `create_message_reply_endpoint` in main.py
- CRUD: `create_reply` in crud.py
- Models: Message model with parent/child relationships
- Schemas: MessageReplyCreate, Message

**Request Body:**
```json
{
    "content": "This is a reply message"
}
```

**Response (200 OK):**
```json
{
    "id": 2,
    "content": "This is a reply message",
    "created_at": "2024-01-07T12:00:00Z",
    "updated_at": "2024-01-07T12:00:00Z",
    "user_id": 1,
    "channel_id": 1,
    "parent_id": 1,
    "has_replies": false,
    "user": {
        "id": 1,
        "email": "user@example.com",
        "name": "User Name",
        "picture": "https://example.com/picture.jpg"
    },
    "reactions": [],
    "parent": {
        "id": 1,
        "content": "Original message",
        "created_at": "2024-01-07T11:00:00Z",
        "updated_at": "2024-01-07T11:00:00Z",
        "user_id": 2,
        "channel_id": 1,
        "parent_id": null,
        "user": {
            "id": 2,
            "email": "user2@example.com",
            "name": "User Two",
            "picture": "https://example.com/picture2.jpg"
        }
    }
}
```

**WebSocket Events:**
Two events are broadcast when a reply is created:
1. `message_created` for the new reply
2. `message_update` for the root message to update its has_replies status

#### 2. Get Message Reply Chain
```http
GET /messages/{message_id}/reply-chain
```

Returns all messages in a reply chain for a given message ID, including:
1. All parent messages (if the given message is a reply)
2. The message itself
3. All replies in the chain

Messages are ordered by created_at date (ascending).

**Implementation Details:**
- Function: `get_message_reply_chain_endpoint` in main.py
- CRUD: `get_message_reply_chain` in crud.py
- Models: Message model with parent/child relationships
- Schemas: Message

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "content": "Original message",
        "created_at": "2024-01-07T11:00:00Z",
        "updated_at": "2024-01-07T11:00:00Z",
        "user_id": 1,
        "channel_id": 1,
        "parent_id": null,
        "has_replies": true,
        "user": {
            "id": 1,
            "email": "user@example.com",
            "name": "User Name",
            "picture": "https://example.com/picture.jpg"
        }
    },
    {
        "id": 2,
        "content": "First reply",
        "created_at": "2024-01-07T12:00:00Z",
        "updated_at": "2024-01-07T12:00:00Z",
        "user_id": 2,
        "channel_id": 1,
        "parent_id": 1,
        "has_replies": true,
        "user": {
            "id": 2,
            "email": "user2@example.com",
            "name": "User Two",
            "picture": "https://example.com/picture2.jpg"
        }
    },
    {
        "id": 3,
        "content": "Second reply",
        "created_at": "2024-01-07T13:00:00Z",
        "updated_at": "2024-01-07T13:00:00Z",
        "user_id": 1,
        "channel_id": 1,
        "parent_id": 2,
        "has_replies": false,
        "user": {
            "id": 1,
            "email": "user@example.com",
            "name": "User Name",
            "picture": "https://example.com/picture.jpg"
        }
    }
]
```

**Error Responses:**
- `404 Not Found`: Message not found
- `403 Forbidden`: User is not a member of the channel containing the message

### Get Channel Messages
```http
GET /channels/{channel_id}/messages?skip=0&limit=50&include_reactions=false&parent_only=true
```

Retrieves messages from a channel with pagination support.

**Query Parameters:**
- `skip` (optional): Number of messages to skip (default: 0)
- `limit` (optional): Maximum number of messages to return (default: 50)
- `include_reactions` (optional): Whether to include reaction data (default: false)
- `parent_only` (optional): Whether to return only root messages (no replies) (default: true)

**Response (200 OK):**
```json
{
    "messages": [
        {
            "id": 1,
            "content": "Hello world!",
            "created_at": "2024-01-07T12:00:00Z",
            "updated_at": "2024-01-07T12:00:00Z",
            "user_id": 1,
            "channel_id": 1,
            "parent_id": null,
            "has_replies": true,
            "user": {
                "id": 1,
                "email": "user@example.com",
                "name": "User Name",
                "picture": "https://example.com/picture.jpg"
            },
            "reactions": [],
            "parent": null
        }
    ],
    "total": 100,
    "has_more": true
}
```

The `has_replies` field indicates whether a message has any replies, allowing the frontend to render appropriate UI elements. 

### Get Message Reply Chain
```http
GET /messages/{message_id}/reply-chain
```

Returns all messages in a reply chain for a given message ID. This includes:
1. All parent messages (if the given message is a reply)
2. The message itself
3. All replies in the chain

Messages are ordered by created_at date (ascending).

**Path Parameters:**
- `message_id`: ID of the message to get the reply chain for

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "content": "Original message",
        "created_at": "2024-01-07T11:00:00Z",
        "updated_at": "2024-01-07T11:00:00Z",
        "user_id": 1,
        "channel_id": 1,
        "parent_id": null,
        "has_replies": true,
        "user": {
            "id": 1,
            "email": "user@example.com",
            "name": "User Name",
            "picture": "https://example.com/picture.jpg"
        }
    },
    {
        "id": 2,
        "content": "First reply",
        "created_at": "2024-01-07T12:00:00Z",
        "updated_at": "2024-01-07T12:00:00Z",
        "user_id": 2,
        "channel_id": 1,
        "parent_id": 1,
        "has_replies": true,
        "user": {
            "id": 2,
            "email": "user2@example.com",
            "name": "User Two",
            "picture": "https://example.com/picture2.jpg"
        }
    },
    {
        "id": 3,
        "content": "Second reply",
        "created_at": "2024-01-07T13:00:00Z",
        "updated_at": "2024-01-07T13:00:00Z",
        "user_id": 1,
        "channel_id": 1,
        "parent_id": 2,
        "has_replies": false,
        "user": {
            "id": 1,
            "email": "user@example.com",
            "name": "User Name",
            "picture": "https://example.com/picture.jpg"
        }
    }
]
```

**Error Responses:**
- `404 Not Found`: Message not found
- `403 Forbidden`: User is not a member of the channel containing the message

## WebSocket Implementation Details

The WebSocket connection is managed by the `ConnectionManager` class in main.py, which handles:
- Connection limits (MAX_CONNECTIONS_PER_USER and MAX_TOTAL_CONNECTIONS)
- User-channel mapping
- Message broadcasting
- Connection cleanup

### Connection Manager Methods
- `connect`: Establishes new WebSocket connection
- `disconnect`: Cleans up disconnected WebSocket
- `broadcast_to_channel`: Sends message to all users in a channel
- `broadcast_member_joined`: Notifies when new member joins
- `broadcast_member_left`: Notifies when member leaves
- `broadcast_role_updated`: Notifies of role changes
- `broadcast_privacy_updated`: Notifies of privacy setting changes
- `broadcast_channel_created`: Notifies of new channel creation

### WebSocket Authentication
WebSocket connections require a valid Auth0 token passed as a query parameter:
```
ws://your-server/ws?token=<auth0_token>
```

The token is verified using the same Auth0 verification process as REST endpoints. 

## Database Models

### User Model
- Primary key: id (Integer)
- Unique fields: auth0_id (String), email (String)
- Relationships:
  - messages: One-to-many with Message
  - channels: Many-to-many with Channel through UserChannel

### Channel Model
- Primary key: id (Integer)
- Fields: name, description, is_private, is_dm, join_code
- Relationships:
  - messages: One-to-many with Message
  - users: Many-to-many with User through UserChannel
  - owner: Many-to-one with User
  - roles: One-to-many with ChannelRole

### Message Model
- Primary key: id (Integer)
- Fields: content, created_at, updated_at
- Relationships:
  - user: Many-to-one with User
  - channel: Many-to-one with Channel
  - reactions: One-to-many with MessageReaction
  - parent/reply: Self-referential one-to-one for reply chains

### Reaction System Models
- Reaction: Defines available reactions
- MessageReaction: Links messages, reactions, and users

## Implementation Notes

### Message Reply System
- Messages use a self-referential relationship with parent_id
- Each message can have at most one reply (enforced by unique constraint)
- Reply chains are built by following parent_id references
- When replying to a message with existing replies, the new reply is attached to the last message in the chain

### DM Channels
- DM channels are always private (enforced by CHECK constraint)
- Two-person DMs have auto-generated names
- Group DMs can have custom names
- Each user pair can have at most one DM channel

### Channel Privacy
- Channels can be public or private
- Private channels are invite-only
- DM channels are always private
- Channel privacy changes are broadcast via WebSocket 