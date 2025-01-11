# Frontend Utils Documentation

This directory contains utility functions and configurations used throughout the frontend application.

## Table of Contents
- [API Utility](#api-utility)

## API Utility

**File**: `api.ts`

### Overview
The API utility provides a configured Axios instance for making HTTP requests to the backend server. It includes support for both unauthenticated and authenticated requests, with environment-aware configuration.

### Dependencies
- `axios`: HTTP client for making requests
- `@auth0/auth0-react`: (indirect dependency) Used in conjunction with authentication

### Configuration
The API utility uses environment variables for configuration:
- `NEXT_PUBLIC_API_URL`: The base URL for API requests (defaults to 'http://localhost:8000')

### Exports

#### Default Export: `api`
A pre-configured Axios instance with the following setup:
```typescript
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
});
```

#### Named Export: `createAuthenticatedApi(token: string)`
A function that creates an authenticated version of the API instance by adding the JWT token to request headers.

### Usage in Application

The API utility is used in several key components and hooks:

1. **useAuth Hook** (`hooks/useAuth.ts`)
   - Uses `createAuthenticatedApi` for authenticated requests
   - Handles user authentication and synchronization

2. **useApi Hook** (`hooks/useApi.ts`)
   - Uses the base `api` instance
   - Manages API requests and state

3. **ProtectedRoute Component** (`components/ProtectedRoute.tsx`)
   - Uses `createAuthenticatedApi` for route protection
   - Verifies authentication status

### Best Practices
1. Always use environment variables for configuration when possible
2. Use `useApi` hook for authenticated requests in components
3. Use `createAuthenticatedApi` for authenticated requests outside of React components
4. Use the default `api` export for unauthenticated requests only
5. Include error handling when making direct API calls

### Security Considerations
- Authentication tokens are managed securely through Auth0 integration
- Environment variables are used to configure API endpoints
- Token injection is handled through headers rather than URL parameters 