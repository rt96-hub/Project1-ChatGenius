# Frontend Contexts Documentation

This document provides detailed information about the context providers used in the frontend application.

## Table of Contents
1. [Auth0Provider](#auth0provider)
2. [ConnectionContext](#connectioncontext)

## Auth0Provider

**File**: `Auth0Provider.tsx`

### Overview
A wrapper component that provides Auth0 authentication functionality throughout the application. It extends the base Auth0 provider with custom configuration and routing handling.

### Key Components

#### Auth0Provider Component
- **Purpose**: Configures and initializes Auth0 authentication for the application
- **Props**:
  - `children`: ReactNode - Child components to be wrapped with Auth0 context

### Configuration
- Uses environment variables:
  - `NEXT_PUBLIC_AUTH0_DOMAIN`: Auth0 domain
  - `NEXT_PUBLIC_AUTH0_CLIENT_ID`: Auth0 client ID
  - `NEXT_PUBLIC_AUTH0_AUDIENCE`: API audience identifier

### Features
- Handles authentication redirects
- Configures authorization parameters:
  - Redirect URI: Set to the current window origin
  - Scope: 'openid profile email'
  - Response type: 'token id_token'
- Enables refresh tokens
- Uses localStorage for token caching

## ConnectionContext

**File**: `ConnectionContext.tsx`

### Overview
Manages WebSocket connections for real-time communication in the application, handling connection states, message passing, and idle status detection.

### Types and Interfaces

#### ConnectionStatus
```typescript
type ConnectionStatus = 'connected' | 'disconnected' | 'connecting' | 'idle' | 'away';
```

#### WebSocketMessage
```typescript
interface WebSocketMessage {
  type: string;
  channel_id: number;
  [key: string]: any;
}
```

#### ConnectionContextType
```typescript
interface ConnectionContextType {
  connectionStatus: ConnectionStatus;
  sendMessage: (message: any) => void;
  addMessageListener: (callback: (message: WebSocketMessage) => void) => () => void;
}
```

### Key Components

#### ConnectionProvider
- **Purpose**: Provides WebSocket connection management and real-time messaging capabilities
- **Props**:
  - `children`: ReactNode - Child components to be wrapped with connection context

### Features

#### WebSocket Management
- Automatic connection establishment when authenticated
- Exponential backoff for reconnection attempts
- Connection status tracking
- Secure connection with Auth0 token integration

#### Idle Detection
- Tracks user activity through mouse and keyboard events
- Automatically sets status to 'idle' after 30 seconds of inactivity
- Updates status to 'connected' on user activity

#### Message Handling
- **sendMessage**: Sends messages through WebSocket
  ```typescript
  sendMessage(message: any): void
  ```
- **addMessageListener**: Registers callbacks for incoming messages
  ```typescript
  addMessageListener(callback: (message: WebSocketMessage) => void): () => void
  ```

### WebSocket Connection Details
- **URL Format**: `ws://localhost:8000/ws?token=${token}`
- **Authentication**: Uses Auth0 access token
- **States Handled**:
  - Connection establishment
  - Error handling
  - Automatic reconnection
  - Clean disconnection

### Usage Example
```typescript
import { useConnection } from '../contexts/ConnectionContext';

function MyComponent() {
  const { connectionStatus, sendMessage, addMessageListener } = useConnection();

  // Listen for messages
  useEffect(() => {
    const cleanup = addMessageListener((message) => {
      console.log('Received message:', message);
    });
    return cleanup;
  }, []);

  // Send a message
  const handleSend = () => {
    sendMessage({
      type: 'chat_message',
      channel_id: 123,
      content: 'Hello!'
    });
  };
}
```

### Error Handling
- Logs connection errors
- Implements automatic reconnection with exponential backoff
- Handles authentication state changes
- Graceful connection closure on component unmount

### Dependencies
- React
- @auth0/auth0-react
- WebSocket API 