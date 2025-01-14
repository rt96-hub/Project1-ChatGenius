# Frontend API Documentation

This document provides a comprehensive list of all API endpoints and WebSocket events used by frontend components.

## REST API Endpoints

### Authentication

#### User Sync
- **Endpoint**: `POST /auth/sync`
- **Used by**: `useAuth` hook
- **Request Body**:
```typescript
{
    email: string,
    auth0_id: string,
    name: string
}
```
- **Response**:
```typescript
{
    id: number,
    email: string,
    name: string,
    picture: string,
    auth0_id: string,
    is_active: boolean,
    created_at: string
}
```

### User Endpoints

#### Get Current User
- **Endpoint**: `GET /users/me`
- **Used by**: `ChatArea`, `UserProfile` components
- **Response**:
```typescript
{
    id: number,
    email: string,
    name: string,
    picture: string,
    auth0_id: string,
    is_active: boolean,
    created_at: string
}
```

#### Get Users by Last DM
- **Endpoint**: `GET /users/by-last-dm`
- **Used by**: `DMList` component
- **Response**:
```typescript
Array<{
    user: {
        id: number,
        email: string,
        name: string,
        picture?: string,
        bio?: string
    },
    last_dm_at: string | null,
    channel_id: number | null
}>
```

### Channel Endpoints

#### Get Channel Details
- **Endpoint**: `GET /channels/{channel_id}`
- **Used by**: `ChatArea`, `ChannelHeader` components
- **Response**:
```typescript
{
    id: number,
    name: string,
    description: string,
    owner_id: number,
    is_private: boolean,
    member_count: number,
    users: Array<{
        id: number,
        email: string,
        name: string
    }>
}
```

#### Get User Channels
- **Endpoint**: `GET /channels/me`
- **Used by**: `Sidebar` component
- **Response**: Array of Channel objects

#### Get User DM Channels
- **Endpoint**: `GET /channels/me/dms`
- **Used by**: `Sidebar` component
- **Query Parameters**:
```typescript
{
    limit?: number
}
```
- **Response**: Array of Channel objects

#### Create Channel
- **Endpoint**: `POST /channels`
- **Used by**: `CreateChannelModal` component
- **Request Body**:
```typescript
{
    name: string,
    description?: string,
    is_private?: boolean
}
```
- **Response**: Channel object

### Message Endpoints

#### Get Channel Messages
- **Endpoint**: `GET /channels/{channel_id}/messages`
- **Used by**: `ChatArea` component
- **Query Parameters**:
```typescript
{
    skip?: number,  // default: 0
    limit?: number  // default: 50
}
```
- **Response**:
```typescript
{
    messages: Array<{
        id: number,
        content: string,
        created_at: string,
        updated_at: string,
        user_id: number,
        channel_id: number,
        user: {
            id: number,
            email: string,
            name: string
        },
        reactions?: Array<{
            id: number,
            message_id: number,
            reaction_id: number,
            user_id: number,
            created_at: string,
            reaction: {
                id: number,
                code: string,
                is_system: boolean,
                image_url: string | null
            }
        }>
    }>,
    total: number,
    has_more: boolean
}
```

#### Send Message
- **Endpoint**: `POST /channels/{channel_id}/messages`
- **Used by**: `ChatArea` component
- **Request Body**:
```typescript
{
    content: string
}
```
- **Response**: Message object

#### Send Message with File
- **Endpoint**: `POST /channels/{channel_id}/messages/with-file`
- **Used by**: `ChatArea` component
- **Request Body**: FormData containing:
  - content: string
  - file: File

#### Reply to Message
- **Endpoint**: `POST /channels/{channel_id}/messages/{parent_id}/reply`
- **Used by**: `ChatArea` component
- **Request Body**:
```typescript
{
    content: string
}
```

#### Reply with File
- **Endpoint**: `POST /channels/{channel_id}/messages/{parent_id}/reply-with-file`
- **Used by**: `ChatArea` component
- **Request Body**: FormData containing:
  - content: string
  - file: File

#### Get Reply Chain
- **Endpoint**: `GET /messages/{message_id}/reply-chain`
- **Used by**: `ChatArea` component
- **Response**: Array of Message objects

#### Update Message
- **Endpoint**: `PUT /channels/{channel_id}/messages/{message_id}`
- **Used by**: `ChatMessage` component
- **Request Body**:
```typescript
{
    content: string
}
```

#### Delete Message
- **Endpoint**: `DELETE /channels/{channel_id}/messages/{message_id}`
- **Used by**: `ChatMessage` component

### Reaction Endpoints

#### Add Reaction
- **Endpoint**: `POST /channels/{channel_id}/messages/{message_id}/reactions`
- **Used by**: `ChatMessage` component
- **Request Body**:
```typescript
{
    reaction_id: number
}
```

#### Remove Reaction
- **Endpoint**: `DELETE /channels/{channel_id}/messages/{message_id}/reactions/{reaction_id}`
- **Used by**: `ChatMessage` component

### Search Endpoints

#### Search Messages
- **Endpoint**: `GET /search/messages`
- **Used by**: `SearchPanel` component
- **Query Parameters**:
```typescript
{
    query: string,
    channel_id?: number,
    from_date?: string,
    to_date?: string,
    from_user?: number,
    limit?: number,
    skip?: number,
    sort_by?: string,
    sort_order?: 'asc' | 'desc'
}
```

#### Search Users
- **Endpoint**: `GET /search/users`
- **Used by**: `UserSearch` component
- **Query Parameters**:
```typescript
{
    query: string,
    exclude_channel?: number,
    only_channel?: number,
    limit?: number,
    skip?: number
}
```

#### Search Channels
- **Endpoint**: `GET /search/channels`
- **Used by**: `ChannelSearch` component
- **Query Parameters**:
```typescript
{
    query: string,
    include_private?: boolean,
    is_dm?: boolean,
    member_id?: number,
    limit?: number,
    skip?: number
}
```

## WebSocket Events

### Connection
- **URL**: `${WS_URL}/ws?token=${token}`
- **Used by**: `ConnectionContext`

### Incoming Events

#### Message Events
```typescript
// New Message
{
    type: 'new_message',
    channel_id: number,
    message: {
        id: number,
        content: string,
        created_at: string,
        updated_at: string,
        user_id: number,
        channel_id: number,
        parent_id: number | null,  // Indicates if this is a reply message
        parent?: Message | null,   // Parent message details if this is a reply
        has_replies?: boolean,     // Indicates if message has replies
        user: {
            id: number,
            email: string,
            name: string
        }
    }
}

// Message Update
{
    type: 'message_update',
    channel_id: number,
    message: Message
}

// Message Delete
{
    type: 'message_delete',
    channel_id: number,
    message_id: number
}

// Message Reaction Add
{
    type: 'message_reaction_add',
    channel_id: number,
    message_id: number,
    reaction: {
        reaction_id: number,
        code: string,
        user_id: number
    }
}

// Message Reaction Remove
{
    type: 'message_reaction_remove',
    channel_id: number,
    message_id: number,
    reaction_id: number,
    user_id: number
}
```

#### Reply Message Behavior
When receiving a 'new_message' event, the frontend differentiates between regular messages and replies:

1. **Regular Messages** (`parent_id` is null):
   - Added directly to the message list
   - Displayed in the main chat flow

2. **Reply Messages** (`parent_id` is not null):
   - Added to the message list
   - Updates the parent message's `has_replies` flag to true
   - Parent message shows a "Show replies" button
   - Replies are displayed in a collapsible thread under the parent message
   - The UI traverses the reply chain using `parent_id` references to find and update the root message

#### Channel Events
```typescript
// Channel Update
{
    type: 'channel_update',
    channel_id: number,
    channel: {
        id: number,
        name: string,
        description: string,
        owner_id: number,
        is_private: boolean
    }
}

// Member Joined/Left
{
    type: 'member_joined' | 'member_left',
    channel_id: number,
    user: User
}

// Role Updated
{
    type: 'role_updated',
    channel_id: number,
    user_id: number,
    role: string
}

// Privacy Updated
{
    type: 'privacy_updated',
    channel_id: number,
    is_private: boolean
}
```

### Outgoing Events
Messages sent through the WebSocket connection should follow this format:
```typescript
{
    type: string,      // Event type
    channel_id: number, // Target channel ID
    // Additional properties based on event type
}
``` 

## Component API Interactions

### Components

#### ChatArea.tsx
- **REST Endpoints**:
  - `GET /channels/{channel_id}` - Fetch channel details
  - `GET /channels/{channel_id}/messages` - Fetch channel messages
  - `POST /channels/{channel_id}/messages/with-file` - Send message (used for both with and without file attachments)
  - `POST /channels/{channel_id}/messages/{parent_id}/reply-with-file` - Reply to message (used for both with and without file attachments)
  - `GET /messages/{message_id}/reply-chain` - Get reply chain
  - `GET /users/me` - Get current user
- **WebSocket Events**:
  - Listens for: 'new_message', 'message_update', 'message_delete', 'message_reaction_add', 'message_reaction_remove', 'channel_update', 'member_joined', 'member_left', 'role_updated', 'privacy_updated'
  - Sends: 'new_message'

#### ChatMessage.tsx
- **REST Endpoints**:
  - `PUT /channels/{channel_id}/messages/{message_id}` - Update message
  - `DELETE /channels/{channel_id}/messages/{message_id}` - Delete message
  - `POST /channels/{channel_id}/messages/{message_id}/reactions` - Add reaction
  - `DELETE /channels/{channel_id}/messages/{message_id}/reactions/{reaction_id}` - Remove reaction

#### Sidebar.tsx
- **REST Endpoints**:
  - `GET /channels/me` - Get user's channels
  - `GET /channels/me/dms` - Get user's DM channels
- **WebSocket Events**:
  - Listens for: 'channel_update', 'channel_created'

#### CreateChannelModal.tsx
- **REST Endpoints**:
  - `POST /channels` - Create new channel

#### SearchPanel.tsx
- **REST Endpoints**:
  - `GET /search/messages` - Search messages

#### UserSearch.tsx
- **REST Endpoints**:
  - `GET /search/users` - Search users

#### ChannelSearch.tsx
- **REST Endpoints**:
  - `GET /search/channels` - Search channels

#### DMList.tsx
- **REST Endpoints**:
  - `GET /users/by-last-dm` - Get users with recent DMs

### Contexts

#### ConnectionContext.tsx
- **WebSocket**:
  - Manages WebSocket connection: `${WS_URL}/ws?token=${token}`
  - Handles all WebSocket event dispatching to components

#### AuthContext.tsx
- **REST Endpoints**:
  - `POST /auth/sync` - Sync user data with backend

### Hooks

#### useAuth.ts
- **REST Endpoints**:
  - `POST /auth/sync` - Sync user data with backend

#### useApi.ts
- Provides authenticated Axios instance for all API calls
- Manages authentication token injection

### API Utilities

#### api.ts
- Configures base API instance with:
  - Base URL: `process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'`
  - Authentication header management 