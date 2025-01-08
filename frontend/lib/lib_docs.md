# Frontend Library Documentation

## Overview
The `frontend/lib` directory is intended to house reusable utility functions, custom hooks, and helper methods that are used across the application. This directory follows Next.js best practices for organizing shared code.

## Directory Structure
Currently, the library directory is empty, but it is designed to contain the following types of files:

### API Utilities
- API client configurations
- Request/response type definitions
- API endpoint wrappers
- Authentication helpers

### Type Definitions
- Shared TypeScript interfaces
- Common type definitions
- API response types

### Utility Functions
- Date formatting
- String manipulation
- Data transformation
- Validation helpers

### Constants
- Environment variables
- Configuration constants
- Feature flags

## Current Project Setup

### Authentication
The project uses Auth0 for authentication, as indicated by the `@auth0/auth0-react` dependency in `package.json`. Authentication-related utilities should be placed in `lib/auth/`.

### API Integration
The project uses Axios for API requests (`axios` dependency in `package.json`). API-related utilities should be placed in `lib/api/`.

#### API Request/Response Formats

1. **User Endpoints**

   - GET `/users/me`
     ```typescript
     // Response
     {
       id: number;
       email: string;
       name: string;
       picture: string;
       auth0_id: string;
       is_active: boolean;
       created_at: string;
     }
     ```

2. **Channel Endpoints**

   - POST `/channels`
     ```typescript
     // Request
     {
       name: string;
       description: string;
     }
     
     // Response
     {
       id: number;
       name: string;
       description: string;
       owner_id: number;
       created_at: string;
       users: Array<{
         id: number;
         email: string;
         name: string;
       }>;
     }
     ```

   - GET `/channels/{channel_id}`
     ```typescript
     // Response
     {
       id: number;
       name: string;
       description: string;
       owner_id: number;
       created_at: string;
       users: Array<{
         id: number;
         email: string;
         name: string;
       }>;
     }
     ```

3. **Message Endpoints**

   - POST `/channels/{channel_id}/messages`
     ```typescript
     // Request
     {
       content: string;
     }
     
     // Response
     {
       id: number;
       content: string;
       created_at: string;
       updated_at: string;
       user_id: number;
       channel_id: number;
       user: {
         id: number;
         email: string;
         name: string;
       };
     }
     ```

   - GET `/channels/{channel_id}/messages`
     ```typescript
     // Query Parameters
     {
       skip?: number;  // default: 0
       limit?: number; // default: 50
     }
     
     // Response
     {
       messages: Array<{
         id: number;
         content: string;
         created_at: string;
         updated_at: string;
         user_id: number;
         channel_id: number;
         user: {
           id: number;
           email: string;
           name: string;
         };
       }>;
       total: number;
       has_more: boolean;
     }
     ```

### WebSocket Events

1. **New Message**
   ```typescript
   {
     type: 'new_message';
     channel_id: number;
     message: {
       id: number;
       content: string;
       created_at: string;
       updated_at: string;
       user_id: number;
       channel_id: number;
       user: {
         id: number;
         email: string;
         name: string;
       };
     };
   }
   ```

2. **Message Update**
   ```typescript
   {
     type: 'message_update';
     channel_id: number;
     message: {
       id: number;
       content: string;
       created_at: string;
       updated_at: string;
       user_id: number;
       channel_id: number;
       user: {
         id: number;
         email: string;
         name: string;
       };
     };
   }
   ```

3. **Message Delete**
   ```typescript
   {
     type: 'message_delete';
     channel_id: number;
     message_id: number;
   }
   ```

4. **Channel Update**
   ```typescript
   {
     type: 'channel_update';
     channel_id: number;
     channel: {
       id: number;
       name: string;
       description: string;
       owner_id: number;
     };
   }
   ```

### Error Responses

All endpoints may return the following error responses:

```typescript
// 401 Unauthorized
{
  detail: 'Invalid or missing token';
}

// 403 Forbidden
{
  detail: 'Not enough permissions';
}

// 404 Not Found
{
  detail: 'Resource not found';
}

// 400 Bad Request
{
  detail: 'Invalid request';
}

// 500 Internal Server Error
{
  detail: 'Internal server error';
}
```

### Component Libraries
The project includes:
- `@heroicons/react` for icons
- `react-infinite-scroll-component` for infinite scrolling functionality

## Best Practices

### File Organization
- Group related utilities in subdirectories
- Use clear, descriptive file names
- Include type definitions where applicable
- Document complex functions and utilities

### Importing
The project uses TypeScript path aliases:
```typescript
// Can use @ alias for imports (configured in tsconfig.json)
import { someUtil } from '@/lib/utils'
```

### Type Safety
- Leverage TypeScript's type system
- Export type definitions for shared interfaces
- Use strict type checking (enabled in tsconfig.json)

## Future Considerations

### Planned Library Structure
```
frontend/lib/
├── api/
│   ├── client.ts
│   ├── endpoints.ts
│   └── types.ts
├── auth/
│   ├── hooks.ts
│   └── utils.ts
├── constants/
│   └── index.ts
├── hooks/
│   └── index.ts
└── utils/
    └── index.ts
```

### Implementation Notes
- Keep utility functions pure and testable
- Document API request/response formats
- Include error handling utilities
- Add logging and monitoring helpers as needed

## Related Documentation
- See `frontend/hooks/hooks_docs.md` for custom React hooks
- See `frontend/contexts/contexts_docs.md` for React context providers
- See `frontend/components/components_docs.md` for reusable components
- See `frontend/app/app_docs.md` for page components and routing 