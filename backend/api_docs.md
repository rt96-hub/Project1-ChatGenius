# API Documentation

## Authentication
All endpoints except WebSocket connections require a valid JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

### Sync Auth0 User
**Endpoint**: `POST /auth/sync`  
**Description**: Synchronize Auth0 user data with local database.

**Request Body**:
```json
{
    "auth0_id": "auth0|123",
    "email": "user@example.com",
    "name": "John Doe",
    "picture": "https://example.com/avatar.jpg"
}
```

**Response**: User object

### Verify Auth
**Endpoint**: `GET /auth/verify`  
**Description**: Verify Auth0 token and return user data.

**Response**:
```json
{
    "valid": true,
    "user": {
        "id": 1,
        "email": "user@example.com",
        "name": "John Doe",
        "picture": "https://example.com/avatar.jpg",
        "bio": "User biography",
        "is_active": true,
        "created_at": "2024-03-15T12:34:56.789Z"
    }
}
```

## User Management

### Get Current User
**Endpoint**: `GET /users/me`  
**Description**: Get the current authenticated user's profile.

**Response**: User object

### Get Users by Last DM
**Endpoint**: `GET /users/by-last-dm`  
**Description**: Get all users ordered by their last DM interaction with the current user. Users with no DM history appear first.

**Query Parameters**:
- `skip`: Number of users to skip (default: 0)
- `limit`: Maximum number of users to return (default: 100)

**Response**: Array of UserWithLastDM objects
```json
[
    {
        "user": {
            "id": 1,
            "email": "user@example.com",
            "name": "John Doe"
        },
        "last_dm_at": "2024-03-15T12:34:56.789Z",
        "channel_id": 123
    }
]
```

### Get All Users
**Endpoint**: `GET /users`  
**Description**: Get a list of all users.

**Query Parameters**:
- `skip`: Number of users to skip (default: 0)
- `limit`: Maximum number of users to return (default: 100)

**Response**: Array of User objects

### Get User by ID
**Endpoint**: `GET /users/{user_id}`  
**Description**: Get a specific user's profile.

**Response**: User object

### Update User Bio
**Endpoint**: `PUT /users/me/bio`  
**Description**: Update the current user's bio.

**Request Body**:
```json
{
    "bio": "New biography text"
}
```

**Response**: Updated User object

### Update User Name
**Endpoint**: `PUT /users/me/name`  
**Description**: Update the current user's name.

**Request Body**:
```json
{
    "name": "New Name"
}
```

**Response**: Updated User object

## Channel Management

### Create Channel
**Endpoint**: `POST /channels`  
**Description**: Create a new channel.

**Request Body**:
```json
{
    "name": "general",
    "description": "General discussion"
}
```

**Response**: Channel object

### Get User Channels
**Endpoint**: `GET /channels/me`  
**Description**: Get all channels the current user is a member of.

**Query Parameters**:
- `skip`: Number of channels to skip (default: 0)
- `limit`: Maximum number of channels to return (default: 100)

**Response**: Array of Channel objects

### Get Available Channels
**Endpoint**: `GET /channels/available`  
**Description**: Get all public channels that the user can join.

**Query Parameters**:
- `skip`: Number of channels to skip (default: 0)
- `limit`: Maximum number of channels to return (default: 50)

**Response**: Array of Channel objects

### Get Channel
**Endpoint**: `GET /channels/{channel_id}`  
**Description**: Get channel details.

**Response**: Channel object with members

### Update Channel
**Endpoint**: `PUT /channels/{channel_id}`  
**Description**: Update channel details. Only channel owner can perform this action.

**Request Body**:
```json
{
    "name": "new-name",
    "description": "Updated description"
}
```

**Response**: Updated Channel object

### Delete Channel
**Endpoint**: `DELETE /channels/{channel_id}`  
**Description**: Delete a channel. Only channel owner can perform this action.

**Response**: Deleted Channel object

### Join Channel
**Endpoint**: `POST /channels/{channel_id}/join`  
**Description**: Join a public channel.

**Response**: Channel object

### Leave Channel
**Endpoint**: `POST /channels/{channel_id}/leave`  
**Description**: Leave a channel. If the owner leaves, ownership is transferred to another member.

**Response**:
```json
{
    "message": "Successfully left the channel"
}
```

### Get Channel Members
**Endpoint**: `GET /channels/{channel_id}/members`  
**Description**: Get all members of a channel.

**Response**: Array of UserInChannel objects

### Remove Channel Member
**Endpoint**: `DELETE /channels/{channel_id}/members/{user_id}`  
**Description**: Remove a member from a channel. Only channel owner can perform this action.

**Response**:
```json
{
    "message": "Member removed successfully"
}
```

### Update Channel Privacy
**Endpoint**: `PUT /channels/{channel_id}/privacy`  
**Description**: Update channel privacy settings. Only channel owner can perform this action.

**Request Body**:
```json
{
    "is_private": true
}
```

**Response**: Updated Channel object

### Get User Channel Role
**Endpoint**: `GET /channels/{channel_id}/role`  
**Description**: Get a user's role in a channel.

**Query Parameters**:
- `user_id`: ID of the user to get role for

**Response**: ChannelRole object

### Update Channel Role
**Endpoint**: `PUT /channels/{channel_id}/roles/{user_id}`  
**Description**: Update a user's role in a channel. Only channel owner can perform this action.

**Request Body**:
```json
{
    "role": "moderator"
}
```

**Response**: Updated ChannelRole object

## Message Management

### Create Message
**Endpoint**: `POST /channels/{channel_id}/messages`  
**Description**: Create a new message in a channel.

**Request Body**:
```json
{
    "content": "Hello, world!"
}
```

**Response**: Message object

### Get Channel Messages
**Endpoint**: `GET /channels/{channel_id}/messages`  
**Description**: Get messages in a channel.

**Query Parameters**:
- `skip`: Number of messages to skip (default: 0)
- `limit`: Maximum number of messages to return (default: 50)
- `include_reactions`: Whether to include message reactions (default: false)
- `parent_only`: Whether to only include parent messages (default: true)

**Response**:
```json
{
    "messages": [Message],
    "total": 100,
    "has_more": true
}
```

### Update Message
**Endpoint**: `PUT /channels/{channel_id}/messages/{message_id}`  
**Description**: Update a message. Only message author can perform this action.

**Request Body**:
```json
{
    "content": "Updated message content"
}
```

**Response**: Updated Message object

### Delete Message
**Endpoint**: `DELETE /channels/{channel_id}/messages/{message_id}`  
**Description**: Delete a message. Only message author can perform this action.

**Response**: Deleted Message object

### Create Message Reply
**Endpoint**: `POST /channels/{channel_id}/messages/{parent_id}/reply`  
**Description**: Create a reply to a message.

**Request Body**:
```json
{
    "content": "Reply message content"
}
```

**Response**: Message object

### Get Message Reply Chain
**Endpoint**: `GET /messages/{message_id}/reply-chain`  
**Description**: Get all messages in a reply chain, including parent messages and replies.

**Response**: Array of Message objects

## Direct Messages (DM)

### Create DM Channel
**Endpoint**: `POST /channels/dm`  
**Description**: Create a new DM channel with multiple users.

**Request Body**:
```json
{
    "user_ids": [1, 2, 3],
    "name": "Optional group name"
}
```

**Response**: Channel object

### Get User DMs
**Endpoint**: `GET /channels/me/dms`  
**Description**: Get all DM channels for the current user, ordered by most recent message.

**Query Parameters**:
- `skip`: Number of channels to skip (default: 0)
- `limit`: Maximum number of channels to return (default: 100)

**Response**: Array of Channel objects

### Check Existing DM
**Endpoint**: `GET /channels/dm/check/{other_user_id}`  
**Description**: Check if there's an existing one-on-one DM channel between the current user and another user.

**Response**:
```json
{
    "channel_id": 123
}
```

## Reactions

### List Reactions
**Endpoint**: `GET /reactions`  
**Description**: Get all available reactions.

**Query Parameters**:
- `skip`: Number of reactions to skip (default: 0)
- `limit`: Maximum number of reactions to return (default: 100)

**Response**: Array of Reaction objects

### Add Reaction
**Endpoint**: `POST /channels/{channel_id}/messages/{message_id}/reactions`  
**Description**: Add a reaction to a message.

**Request Body**:
```json
{
    "reaction_id": 1
}
```

**Response**: MessageReaction object

### Remove Reaction
**Endpoint**: `DELETE /channels/{channel_id}/messages/{message_id}/reactions/{reaction_id}`  
**Description**: Remove a reaction from a message.

**Response**:
```json
{
    "message": "Reaction removed successfully"
}
```

## WebSocket Events

### Connection
Connect to the WebSocket endpoint with:
```
ws://localhost:8000/ws?token=<jwt_token>
```

### Message Events

#### New Message
```json
{
    "type": "new_message",
    "channel_id": 123,
    "message": {
        "id": 1,
        "content": "Hello, world!",
        "created_at": "2024-03-15T12:34:56.789Z",
        "user_id": 456,
        "channel_id": 123,
        "user": {
            "id": 456,
            "email": "user@example.com",
            "name": "John Doe"
        }
    }
}
```

#### Message Update
```json
{
    "type": "message_update",
    "channel_id": 123,
    "message": {
        "id": 1,
        "content": "Updated content",
        "created_at": "2024-03-15T12:34:56.789Z",
        "updated_at": "2024-03-15T12:35:00.000Z",
        "user_id": 456,
        "channel_id": 123,
        "user": {
            "id": 456,
            "email": "user@example.com",
            "name": "John Doe"
        }
    }
}
```

#### Message Delete
```json
{
    "type": "message_delete",
    "channel_id": 123,
    "message_id": 1
}
```

### Channel Events

#### Channel Update
```json
{
    "type": "channel_update",
    "channel_id": 123,
    "channel": {
        "id": 123,
        "name": "updated-name",
        "description": "Updated description",
        "owner_id": 456
    }
}
```

#### Member Joined
```json
{
    "type": "member_joined",
    "channel_id": 123,
    "user": {
        "id": 456,
        "email": "user@example.com",
        "name": "John Doe",
        "picture": "https://example.com/avatar.jpg"
    }
}
```

#### Member Left
```json
{
    "type": "member_left",
    "channel_id": 123,
    "user_id": 456
}
```

### Reaction Events

#### Reaction Added
```json
{
    "type": "message_reaction_add",
    "channel_id": 123,
    "message_id": 456,
    "reaction": {
        "id": 1,
        "reaction_id": 2,
        "user_id": 789,
        "created_at": "2024-03-15T12:34:56.789Z",
        "reaction": {
            "id": 2,
            "code": ":smile:",
            "is_system": true,
            "image_url": "https://example.com/smile.png"
        },
        "user": {
            "id": 789,
            "email": "user@example.com",
            "name": "John Doe",
            "picture": "https://example.com/avatar.jpg"
        }
    }
}
```

#### Reaction Removed
```json
{
    "type": "message_reaction_remove",
    "channel_id": 123,
    "message_id": 456,
    "reaction_id": 2,
    "user_id": 789
}
```

## Environment Variables

### Server Configuration
- `ROOT_PATH`: Root path for the API (optional)
- `PORT`: Server port (default: 8000)

### Rate Limiting Configuration
- `MAX_SEARCH_REQUESTS_PER_MINUTE`: Maximum search requests per minute per user (default: 60)
- `SEARCH_RATE_LIMIT_WINDOW`: Time window in seconds for rate limiting (default: 60)

### WebSocket Configuration
- `MAX_WEBSOCKET_CONNECTIONS_PER_USER`: Maximum WebSocket connections per user (default: 5)
- `MAX_TOTAL_WEBSOCKET_CONNECTIONS`: Maximum total WebSocket connections (default: 1000)

### Auth0 Configuration
- `AUTH0_DOMAIN`: Auth0 domain for authentication

### Database Configuration
- `DATABASE_URL`: PostgreSQL database connection URL 