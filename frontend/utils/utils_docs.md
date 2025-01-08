# Frontend Utils Documentation

This directory contains utility functions and configurations used throughout the frontend application.

## Table of Contents
- [API Utility](#api-utility)

## API Utility

**File**: `api.ts`

### Overview
The API utility provides a configured Axios instance for making HTTP requests to the backend server. It includes support for both unauthenticated and authenticated requests.

### Dependencies
- `axios`: HTTP client for making requests
- `@auth0/auth0-react`: (indirect dependency) Used in conjunction with authentication

### Exports

#### Default Export: `api`
A pre-configured Axios instance with the following setup:
```typescript
const api = axios.create({
  baseURL: 'http://localhost:8000'
});
```

#### Named Export: `createAuthenticatedApi(token: string)`
A function that creates an authenticated version of the API instance by adding the JWT token to request headers.

### Usage Patterns

The API utility is used in several key areas of the application:

1. **Direct API Usage**
   ```typescript
   import api from '@/utils/api';
   // Make unauthenticated requests
   await api.get('/endpoint');
   ```

2. **Authenticated Requests**
   ```typescript
   import { createAuthenticatedApi } from '@/utils/api';
   const api = createAuthenticatedApi(token);
   await api.post('/auth/sync', data);
   ```

3. **With useApi Hook**
   The `useApi` hook in `hooks/useApi.ts` uses this utility to automatically inject authentication tokens into requests.

### Integration Points

1. **Authentication Flow**
   - Used in `useAuth` hook for user synchronization
   - Handles backend verification in `ProtectedRoute` component
   - Manages user authentication state

2. **Request Format Examples**

   a. User Synchronization (`/auth/sync`):
   ```typescript
   POST /auth/sync
   {
     email: string;
     auth0_id: string;
     name: string;
   }
   ```

   b. Token Verification (`/auth/verify`):
   ```typescript
   GET /auth/verify
   Headers: {
     Authorization: 'Bearer ${token}'
   }
   ```

### Error Handling
- The base configuration handles network errors
- Authentication errors are typically handled by the consuming components
- Token expiration is managed through Auth0 integration

### Best Practices
1. Always use the `useApi` hook for authenticated requests in components
2. Use `createAuthenticatedApi` for authenticated requests outside of React components
3. Use the default `api` export for unauthenticated requests only
4. Include error handling when making direct API calls 