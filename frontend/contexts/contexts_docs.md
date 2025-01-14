# Frontend Contexts Documentation

This document provides detailed information about the context providers used in the frontend application.

## Table of Contents
1. [Auth0Provider](#auth0provider)
2. [ConnectionContext](#connectioncontext)
3. [AIContext](#aicontext)

## Auth0Provider

**File**: `Auth0Provider.tsx`

### Overview
A wrapper component that provides Auth0 authentication functionality throughout the application. It extends the base Auth0 provider with custom configuration and routing handling.

### Implementation Details

#### Dependencies
- `@auth0/auth0-react`: For Auth0 authentication functionality
- `next/navigation`: For routing capabilities
- `react`: For component and type definitions

#### Component Structure
```typescript
interface Auth0ProviderProps {
  children: ReactNode;
}
```

### Key Features

#### Environment Configuration
- Uses the following environment variables:
  - `NEXT_PUBLIC_AUTH0_DOMAIN`: Auth0 domain
  - `NEXT_PUBLIC_AUTH0_CLIENT_ID`: Auth0 client ID
  - `NEXT_PUBLIC_AUTH0_AUDIENCE`: API audience identifier

#### Authentication Configuration
- **Redirect Handling**: 
  - Automatically redirects users after authentication
  - Uses the Next.js router for navigation
  - Falls back to root ('/') if no redirect URL is specified

#### Security Features
- Implements secure token storage using localStorage
- Enables refresh tokens for continuous authentication
- Configures proper authorization scopes:
  - openid
  - profile
  - email

### Used By
- `app/layout.tsx`: Root layout component wraps the entire application
- `hooks/useAuth.ts`: Custom hook for authentication management
- `hooks/useApi.ts`: API utility hook for authenticated requests
- `components/AuthButton.tsx`: Authentication UI component
- `components/Header.tsx`: Main navigation header

## ConnectionContext

**File**: `ConnectionContext.tsx`

### Overview
Manages WebSocket connections for real-time communication in the application, providing connection state management, message handling, and user activity monitoring.

### Implementation Details

#### Dependencies
- `react`: For context and hooks functionality
- `@auth0/auth0-react`: For authentication integration

#### Environment Configuration
- Uses `NEXT_PUBLIC_WS_URL` environment variable (defaults to 'ws://localhost:8000')

#### Type Definitions

```typescript
type ConnectionStatus = 'connected' | 'disconnected' | 'connecting' | 'idle' | 'away';

interface WebSocketMessage {
  type: string;
  channel_id: number;
  [key: string]: any;
}

interface ConnectionContextType {
  connectionStatus: ConnectionStatus;
  sendMessage: (message: any) => void;
  addMessageListener: (callback: (message: WebSocketMessage) => void) => () => void;
}
```

### Key Components

#### ConnectionProvider
- **Purpose**: Main context provider component
- **Props**: 
  ```typescript
  { children: React.ReactNode }
  ```

#### useConnection Hook
- **Purpose**: Custom hook to access connection context
- **Returns**: ConnectionContextType
- **Error Handling**: Throws error if used outside ConnectionProvider

### Core Features

#### WebSocket Management
1. **Connection Setup**
   - Automatically establishes connection when authenticated
   - Uses Auth0 token for authentication
   - WebSocket URL format: `${WS_URL}/ws?token=${token}`

2. **Reconnection Logic**
   - Implements exponential backoff strategy
   - Maximum retry delay: 30 seconds
   - Retries only on unexpected closures

3. **Connection State Tracking**
   ```typescript
   const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');
   ```

#### Activity Monitoring
1. **Event Listeners**
   - Tracks: mousedown, keydown, touchstart, mousemove
   - Updates lastActivity timestamp on any user interaction

2. **Idle Detection**
   - Checks activity every second
   - Marks as idle after 30 seconds of inactivity
   - Automatically returns to 'connected' on activity

### Message Handling

#### Outgoing Messages
Messages sent through the WebSocket should follow this format:
```typescript
{
  type: string;      // Message type identifier
  channel_id: number; // Target channel ID
  // Additional properties based on message type
}
```

#### Incoming Messages
Messages received from the WebSocket are parsed JSON objects with the same structure as outgoing messages.

### Error Handling
1. **Connection Errors**
   - Logs errors to console
   - Sets status to 'disconnected'
   - Triggers reconnection process

2. **Authentication Errors**
   - Prevents connection attempts when unauthenticated
   - Closes existing connections on authentication loss

### Used By
- `app/layout.tsx`: Root layout component for WebSocket initialization
- `components/Header.tsx`: For displaying connection status
- `components/ChatArea.tsx`: For real-time message handling
- `components/ProfileStatus.tsx`: For showing user connection state

### Best Practices
1. Always clean up message listeners using the returned cleanup function
2. Check connection status before critical operations
3. Handle potential connection errors in your components
4. Use TypeScript interfaces for type safety in messages
5. Implement proper error handling for WebSocket operations
6. Monitor connection status changes for UI updates 

## AIContext

**File**: `AIContext.tsx`

### Overview
Manages AI conversation state and interactions throughout the application. This context provider enables real-time AI assistance features and conversation management.

### Implementation Details

#### Dependencies
- `react`: For context and hooks functionality
- `@/hooks/useApi`: For making API requests to the AI backend
- `@/types/ai`: For TypeScript type definitions

#### Type Definitions

```typescript
interface AIContextType {
    isOpen: boolean;
    toggleSidebar: () => void;
    currentConversation: AIConversation | null;
    conversationHistory: AIConversation[];
    sendMessage: (channelId: number, message: string) => Promise<void>;
    isLoading: boolean;
    error: string | null;
}

interface AIProviderProps {
    children: ReactNode;
}
```

### Key Features

#### State Management
1. **Sidebar Control**
   - Manages visibility of AI sidebar
   - Provides toggle functionality

2. **Conversation Tracking**
   - Maintains current active conversation
   - Stores conversation history
   - Updates conversations in real-time

3. **Loading and Error States**
   - Tracks ongoing AI operations
   - Manages error messages
   - Provides loading indicators

### API Interactions

#### Send Message Request
```http
POST /ai/channels/{channelId}/query
Request Body:
{
    "query": string
}

Response (200 OK):
{
    "conversation": {
        "id": string,
        "messages": Array<{
            "id": string,
            "content": string,
            "role": "user" | "assistant"
        }>
    }
}
```

### Used By
- `hooks/useAI.ts`: Custom hook for accessing AI functionality
- `components/AISidebar.tsx`: AI conversation interface
- `components/ChatArea.tsx`: Message display and interaction
- Other components requiring AI features

### Best Practices
1. Wrap components requiring AI functionality with AIProvider
2. Handle loading states appropriately
3. Implement proper error handling
4. Use TypeScript types for type safety
5. Consider caching strategies for conversation history 