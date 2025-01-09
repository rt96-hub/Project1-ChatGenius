# Frontend Contexts Documentation

This document provides detailed information about the context providers used in the frontend application.

## Table of Contents
1. [Auth0Provider](#auth0provider)
2. [ConnectionContext](#connectioncontext)

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

#### Usage Example
```typescript
import { Auth0Provider } from '../contexts/Auth0Provider';

function App({ children }) {
  return (
    <Auth0Provider>
      {children}
    </Auth0Provider>
  );
}
```

## ConnectionContext

**File**: `ConnectionContext.tsx`

### Overview
Manages WebSocket connections for real-time communication in the application, providing connection state management, message handling, and user activity monitoring.

### Implementation Details

#### Dependencies
- `react`: For context and hooks functionality
- `@auth0/auth0-react`: For authentication integration

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
   - WebSocket URL format: `ws://localhost:8000/ws?token=${token}`

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

#### Message Handling

1. **Sending Messages**
   ```typescript
   const sendMessage = async (message: any) => {
     // Sends JSON-stringified message if connected
     // Attempts reconnection if disconnected
   }
   ```

2. **Receiving Messages**
   ```typescript
   ws.onmessage = (event) => {
     const data = JSON.parse(event.data);
     messageListeners.current.forEach(listener => listener(data));
   }
   ```

3. **Message Listener Management**
   ```typescript
   const addMessageListener = (callback: (message: WebSocketMessage) => void) => {
     // Adds listener and returns cleanup function
   }
   ```

### WebSocket Communication Formats

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

### Usage Example
```typescript
import { useConnection } from '../contexts/ConnectionContext';

function ChatComponent() {
  const { connectionStatus, sendMessage, addMessageListener } = useConnection();

  useEffect(() => {
    const cleanup = addMessageListener((message) => {
      // Handle incoming message
    });
    return cleanup;
  }, []);

  const sendChatMessage = () => {
    sendMessage({
      type: 'chat_message',
      channel_id: 123,
      content: 'Hello!'
    });
  };

  return (
    <div>
      <p>Status: {connectionStatus}</p>
      <button onClick={sendChatMessage}>Send Message</button>
    </div>
  );
}
```

### Best Practices
1. Always clean up message listeners using the returned cleanup function
2. Check connection status before critical operations
3. Handle potential connection errors in your components
4. Use TypeScript interfaces for type safety in messages 