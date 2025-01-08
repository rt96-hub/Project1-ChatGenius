# Frontend Hooks Documentation

This directory contains custom React hooks that handle authentication and API interactions for the application.

## Table of Contents
- [useAuth](#useauth)
- [useApi](#useapi)

## useAuth

**File**: `useAuth.ts`

### Overview
A custom hook that manages authentication state and user synchronization with the backend using Auth0.

### Dependencies
- `@auth0/auth0-react`: Auth0's React SDK
- `@/utils/api`: Local API utility for making authenticated requests

### Exported Functions

#### `useAuth()`

Returns an object containing authentication state and methods:

```typescript
{
  isAuthenticated: boolean;
  isLoading: boolean;
  user: Auth0User | undefined;
  login: () => void;
  signOut: () => void;
  getAccessTokenSilently: () => Promise<string>;
}
```

### Key Features

1. **Authentication State Management**
   - Tracks authentication status
   - Manages loading states
   - Provides user information

2. **User Synchronization**
   - Automatically syncs Auth0 user data with backend when authentication state changes
   - Sends user data to `/auth/sync` endpoint with:
     ```typescript
     {
       email: string;
       auth0_id: string;
       name: string;
     }
     ```

3. **Authentication Methods**
   - `login()`: Initiates Auth0 login flow with redirect
   - `signOut()`: Handles user logout and redirects to home page
   - `getAccessTokenSilently()`: Retrieves JWT token for authenticated requests

## useApi

**File**: `useApi.ts`

### Overview
A custom hook that sets up an authenticated API instance with automatic token injection.

### Dependencies
- `@auth0/auth0-react`: Auth0's React SDK
- `@/utils/api`: Axios-based API instance

### Exported Functions

#### `useApi()`

Returns the configured API instance with authentication interceptors.

### Key Features

1. **Automatic Token Injection**
   - Intercepts all API requests
   - Automatically adds Auth0 access token to request headers
   - Format: `Authorization: Bearer ${token}`

2. **Request Lifecycle Management**
   - Sets up request interceptors when component mounts
   - Cleans up interceptors when component unmounts
   - Handles token acquisition errors

### Usage Example

```typescript
const api = useApi();
// Make authenticated requests
await api.get('/some-endpoint');
```

### Error Handling
- Logs token acquisition errors to console
- Maintains detailed request debugging information
- Tracks request headers and URLs for debugging purposes 