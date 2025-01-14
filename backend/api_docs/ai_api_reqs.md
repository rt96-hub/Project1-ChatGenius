# AI Assistant API Documentation

## Authentication

All endpoints require authentication via Bearer token. The user_id will be extracted from the authenticated token, and users can only access their own conversations.

## Endpoints

### 1. Get Channel AI Conversations
**Endpoint:** `GET /ai/channels/{channelId}/conversations`

**Purpose:** Retrieve all AI conversations for a specific channel that belong to the authenticated user.

**Authentication:** Required (Bearer token)

**Request Parameters:**
- `channelId`: number (path parameter)

**Access Control:**
- Only returns conversations created by the authenticated user
- User must be a member of the specified channel

**Response:**
```typescript
{
    conversations: Array<{
        id: string;
        channelId: number;
        userId: number;  // ID of the user who created the conversation
        messages: Array<{
            id: string;
            content: string;
            role: 'user' | 'assistant';
            timestamp: string;
        }>;
        createdAt: string;
        updatedAt: string;
    }>;
}
```

### 2. Get Single AI Conversation
**Endpoint:** `GET /ai/channels/{channelId}/conversations/{conversationId}`

**Purpose:** Retrieve a specific AI conversation with all its messages.

**Authentication:** Required (Bearer token)

**Request Parameters:**
- `channelId`: number (path parameter)
- `conversationId`: string (path parameter)

**Access Control:**
- Only the conversation creator can access it
- User must be a member of the specified channel

**Response:**
```typescript
{
    id: string;
    channelId: number;
    userId: number;  // ID of the user who created the conversation
    messages: Array<{
        id: string;
        content: string;
        role: 'user' | 'assistant';
        timestamp: string;
    }>;
    createdAt: string;
    updatedAt: string;
}
```

### 3. Create New AI Query
**Endpoint:** `POST /ai/channels/{channelId}/query`

**Purpose:** Submit a new query to the AI assistant and start a new conversation.

**Authentication:** Required (Bearer token)

**Request Parameters:**
- `channelId`: number (path parameter)

**Access Control:**
- User must be a member of the specified channel
- Created conversation will be associated with the authenticated user

**Request Body:**
```typescript
{
    query: string;
}
```

**Response:**
```typescript
{
    conversation: {
        id: string;
        channelId: number;
        userId: number;  // ID of the user who created the conversation
        messages: Array<{
            id: string;
            content: string;
            role: 'user' | 'assistant';
            timestamp: string;
        }>;
        createdAt: string;
        updatedAt: string;
    };
    message: {
        id: string;
        content: string;
        role: 'assistant';
        timestamp: string;
    };
}
```

### 4. Add Message to Conversation
**Endpoint:** `POST /ai/channels/{channelId}/conversations/{conversationId}/messages`

**Purpose:** Add a new message to an existing AI conversation.

**Authentication:** Required (Bearer token)

**Request Parameters:**
- `channelId`: number (path parameter)
- `conversationId`: string (path parameter)

**Access Control:**
- Only the conversation creator can add messages
- User must be a member of the specified channel

**Request Body:**
```typescript
{
    message: string;
}
```

**Response:**
```typescript
{
    id: string;
    channelId: number;
    userId: number;  // ID of the user who created the conversation
    messages: Array<{
        id: string;
        content: string;
        role: 'user' | 'assistant';
        timestamp: string;
    }>;
    createdAt: string;
    updatedAt: string;
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```typescript
{
    error: string;
    message: string;
}
```

### 401 Unauthorized
```typescript
{
    error: string;
    message: "Unauthorized access"
}
```

### 403 Forbidden
```typescript
{
    error: string;
    message: "You don't have permission to access this conversation"
}
```

### 404 Not Found
```typescript
{
    error: string;
    message: "Resource not found"
}
```

### 500 Internal Server Error
```typescript
{
    error: string;
    message: "Internal server error"
} 