# Frontend Hooks Documentation

This directory contains custom React hooks that handle authentication and API interactions for the application.

## Table of Contents
- [useAuth](#useauth)
- [useApi](#useapi)
- [useAI](#useai)

## useAuth

**File**: `useAuth.ts`

### Overview
A custom hook that manages authentication state and user synchronization with the backend using Auth0. This hook serves as the primary authentication interface for the application, handling both Auth0 authentication and backend user synchronization.

### Dependencies
- `@auth0/auth0-react`: Auth0's React SDK for authentication state management
- `@/utils/api`: Local API utility for making authenticated requests
- `react`: For hooks and effects

### Used By
- `components/AuthButton.tsx`: For login/logout functionality and user display
- `components/Header.tsx`: For user authentication state and profile management
- `components/ProtectedRoute.tsx`: For route protection and token verification
- Other components requiring authentication state

### Implementation Details

The hook wraps Auth0's `useAuth0` hook and adds the following functionality:

1. **Authentication State Management**
   - Tracks authentication status through `isAuthenticated`
   - Manages loading states via `isLoading`
   - Provides user information through `user` object
   - Logs authentication state changes for debugging

2. **User Synchronization with Backend**
   - Automatically triggered when authentication state changes
   - Uses `useEffect` to monitor auth state changes
   - Makes POST request to `/auth/sync` endpoint when user authenticates

3. **Authentication Methods**
   - `login()`: Initiates Auth0 login flow with redirect
   - `signOut()`: Handles user logout and redirects to home page
   - `getAccessTokenSilently()`: Retrieves JWT token for authenticated requests

### API Interactions

#### User Sync Request
```http
POST /auth/sync
Authorization: Bearer <auth0_token>

Request Body:
{
    "email": string,
    "auth0_id": string,
    "name": string
}

Response (200 OK):
{
    "id": number,
    "email": string,
    "name": string,
    "picture": string,
    "auth0_id": string,
    "is_active": boolean,
    "created_at": string
}
```

### Usage Example

```typescript
const {
  isAuthenticated,
  isLoading,
  user,
  login,
  signOut,
  getAccessTokenSilently
} = useAuth();

// Check authentication status
if (isLoading) {
  return <div>Loading...</div>;
}

if (!isAuthenticated) {
  return <button onClick={login}>Log in</button>;
}
```

## useApi

**File**: `useApi.ts`

### Overview
A custom hook that provides an authenticated Axios instance for making API requests. It automatically injects Auth0 tokens into request headers and handles token management.

### Dependencies
- `@auth0/auth0-react`: For accessing Auth0 authentication functions
- `@/utils/api`: Pre-configured Axios instance
- `react`: For hooks and effects

### Used By
- `components/CreateChannelModal.tsx`: For channel creation API calls
- `components/UserProfilePopout.tsx`: For user profile management
- `components/EmojiSelector.tsx`: For emoji-related API interactions
- Other components requiring authenticated API access

### Implementation Details

1. **Request Interceptor Setup**
   - Uses Axios interceptors to modify requests before they are sent
   - Automatically injects Auth0 token into Authorization header
   - Includes detailed logging for debugging purposes
   - Cleans up interceptors on component unmount

2. **Token Management**
   - Automatically retrieves fresh Auth0 tokens using `getAccessTokenSilently`
   - Adds token to request headers in format: `Authorization: Bearer ${token}`
   - Handles token acquisition errors gracefully

3. **Debug Logging**
   - Logs token acquisition
   - Logs request headers before and after modification
   - Logs request URLs for debugging
   - Logs any token acquisition errors

### Error Handling
- Catches and logs token acquisition errors
- Allows requests to proceed even if token acquisition fails
- Provides detailed error information for debugging

### Usage Example

```typescript
const api = useApi();

// Make authenticated requests
try {
  const response = await api.get('/users/me');
  console.log('User data:', response.data);
} catch (error) {
  console.error('API request failed:', error);
}
```

### Best Practices
1. Always use this hook for making authenticated API requests
2. Handle errors appropriately in components using try-catch blocks
3. Consider implementing request retries for token acquisition failures
4. Use the hook within authenticated routes/components only
5. Prefer this hook over direct `createAuthenticatedApi` usage in React components 

## useAI

**File**: `useAI.ts`

### Overview
A custom hook that provides access to the AI assistant functionality, managing conversation state and interactions with the AI system. This hook must be used within components wrapped by the `AIProvider`.

### Dependencies
- `react`: For context functionality
- `@/contexts/AIContext`: For AI state management
- `@/types/ai`: For TypeScript type definitions

### Used By
- `components/AISidebar.tsx`: For AI conversation management and display
- `components/ChatArea.tsx`: For AI message integration
- Other components requiring AI functionality

### Implementation Details

The hook provides the following functionality:

1. **Sidebar State Management**
   - `isOpen`: Boolean indicating if the AI sidebar is visible
   - `toggleSidebar()`: Function to toggle sidebar visibility

2. **Conversation Management**
   - `currentConversation`: Current active AI conversation
   - `conversationHistory`: Array of all AI conversations
   - `sendMessage()`: Function to send messages to the AI

3. **Loading and Error States**
   - `isLoading`: Boolean indicating if an AI operation is in progress
   - `error`: String containing any error messages

### API Interface

```typescript
interface UseAIReturn {
    isOpen: boolean;
    toggleSidebar: () => void;
    currentConversation: AIConversation | null;
    conversationHistory: AIConversation[];
    sendMessage: (channelId: number, message: string) => Promise<void>;
    isLoading: boolean;
    error: string | null;
}
```

### Usage Example

```typescript
const {
    isOpen,
    toggleSidebar,
    currentConversation,
    sendMessage,
    isLoading,
    error
} = useAI();

// Send a message to the AI
try {
    await sendMessage(channelId, "What's the status of this project?");
} catch (error) {
    console.error('Failed to send message to AI:', error);
}
```

### Best Practices
1. Always use this hook within components wrapped by AIProvider
2. Handle loading and error states appropriately in UI
3. Implement proper error handling for AI operations
4. Use TypeScript types for type safety
5. Consider implementing retry logic for failed operations 