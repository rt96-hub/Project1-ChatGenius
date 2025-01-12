# ChatGenius Frontend Documentation

## Overview
ChatGenius is a workplace messaging application built with Next.js, utilizing modern web technologies and best practices. The application provides real-time messaging capabilities, channel management, and direct messaging features.

## Directory Structure
```
frontend/
├── app/                 # Next.js app directory (pages and layouts)
├── components/          # Reusable React components
├── contexts/           # React context providers
├── hooks/              # Custom React hooks
├── lib/                # Utility functions and helpers
├── public/             # Static assets
├── types/              # TypeScript type definitions
└── utils/              # Utility functions
```

## Core Technologies
- **Next.js**: Frontend framework (version 15.1.3)
- **React**: UI library (version 19.0.0)
- **TypeScript**: Programming language
- **Tailwind CSS**: Utility-first CSS framework
- **Auth0**: Authentication provider
- **Axios**: HTTP client
- **WebSocket**: Real-time communication

## Key Components and Their Interactions

### 1. Application Layout (`app/layout.tsx`)
- Serves as the root layout component
- Provides authentication context through Auth0Provider
- Manages WebSocket connection context
- Applies global styles and fonts

### 2. Main Page (`app/page.tsx`)
- Implements the primary chat interface
- Coordinates between Sidebar and ChatArea components
- Manages channel selection and updates
- Protected by authentication

### 3. Core Components Hierarchy
```
Layout
├── Header
│   └── ProfileStatus
├── Sidebar
│   ├── CreateChannelModal
│   ├── ViewDMsModal
│   ├── NewDMModal
│   └── ConfirmDialog
└── ChatArea
    ├── ChannelHeader
    ├── ChatMessage
    │   ├── EmojiSelector
    │   └── UserProfilePopout
    ├── MembersList
    └── ChannelSettingsModal
```

## Data Flow and State Management

### 1. Authentication Flow
- Managed by Auth0Provider (context)
- Used throughout the application for protected routes
- Provides user information and authentication state
- Components can access auth state via `useAuth` hook

### 2. Real-time Communication
- Managed by ConnectionContext
- Handles WebSocket connections for real-time updates
- Used primarily in ChatArea for message updates
- Components access connection state via `useConnection` hook

### 3. API Integration
- Centralized API calls through custom hooks
- Axios instance configured with base URL and interceptors
- Endpoints organized by feature (channels, messages, users)
- Error handling and response transformation

## Key Features and Implementation

### 1. Channel Management
- Creation through CreateChannelModal
- Settings management via ChannelSettingsModal
- Real-time updates for channel changes
- Support for public and private channels

### 2. Messaging System
- Real-time message delivery
- Message reactions (emoji)
- User mentions and notifications
- Infinite scroll for message history

### 3. User Interaction
- User profile viewing
- Status updates
- Direct messaging
- Member management in channels

## Component Dependencies

### Header Component
- Dependencies: ProfileStatus, Auth0, Connection Context
- Purpose: Navigation and user status display

### Sidebar Component
- Dependencies: Channel modals, Auth0, API hooks
- Purpose: Channel and DM navigation

### ChatArea Component
- Dependencies: Message components, WebSocket connection
- Purpose: Main messaging interface

## State Management Patterns

1. **Authentication State**
   - Managed by Auth0Provider
   - Global access through useAuth hook
   - Controls protected route access

2. **WebSocket Connection**
   - Managed by ConnectionContext
   - Handles real-time updates
   - Used for message delivery

3. **UI State**
   - Local component state for modals
   - Shared state through context where needed
   - Props for component communication

## Best Practices Implemented

1. **Code Organization**
   - Modular component architecture
   - Clear separation of concerns
   - Type safety with TypeScript

2. **Performance**
   - Component code splitting
   - Optimized real-time updates
   - Efficient state management

3. **Security**
   - Protected routes
   - Secure authentication
   - API request validation

4. **UI/UX**
   - Responsive design with Tailwind
   - Consistent error handling
   - Loading states and feedback

## Development Guidelines

1. **Component Creation**
   - Use functional components
   - Implement proper TypeScript types
   - Include necessary prop validation

2. **State Management**
   - Use hooks for local state
   - Context for global state
   - Props for component communication

3. **Styling**
   - Use Tailwind CSS classes
   - Follow responsive design patterns
   - Maintain consistent theming

4. **Testing**
   - Write unit tests for components
   - Test real-time functionality
   - Validate authentication flows

## Development Setup and Deployment

### Local Development
The application uses Docker for local development to ensure consistency across development environments.

#### Prerequisites
- Docker and Docker Compose installed
- Node.js 20.x (for local tooling)
- `.env.local` file with required environment variables

#### Environment Variables
Local development requires the following environment variables in `.env.local`:

1. **Frontend Variables**
   - `NEXT_PUBLIC_API_URL`: Backend API URL (default: `http://localhost:8000`)
   - `NEXT_PUBLIC_WS_URL`: WebSocket URL (default: `ws://localhost:8000`)
   - `NEXT_PUBLIC_AUTH0_DOMAIN`: Auth0 tenant domain
   - `NEXT_PUBLIC_AUTH0_CLIENT_ID`: Auth0 application client ID
   - `NEXT_PUBLIC_AUTH0_AUDIENCE`: Auth0 API identifier

2. **Backend Variables** (required for full stack development)
   - `DB_URL`: PostgreSQL connection string
   - `AUTH0_DOMAIN`: Auth0 tenant domain
   - `AUTH0_API_IDENTIFIER`: Auth0 API identifier
   - `AUTH0_CLIENT_ID`: Auth0 application client ID
   - `AUTH0_CLIENT_SECRET`: Auth0 client secret

#### Running Locally
1. Start the development environment:
   ```bash
   ./local-dev.sh
   ```
   This script:
   - Stops any running containers
   - Rebuilds containers with current code
   - Starts the application in development mode

2. Access the application:
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:8000`

### Production Deployment

#### Environment Setup
Production deployment requires setting the following environment variables:

1. **Required Environment Variables**
   - `EC2_PUBLIC_DNS`: Public DNS of the EC2 instance
   - All Auth0 variables as listed in local development
   - Database credentials for production database

2. **URL Configuration**
   Production URLs are automatically configured using the EC2_PUBLIC_DNS:
   - API URL: `https://${EC2_PUBLIC_DNS}/api`
   - WebSocket URL: `wss://${EC2_PUBLIC_DNS}/api`

#### Build Process
The frontend is built using multi-stage Docker builds:

1. **Build Stage**
   ```dockerfile
   # Build arguments for environment variables
   ARG NEXT_PUBLIC_AUTH0_DOMAIN
   ARG NEXT_PUBLIC_AUTH0_CLIENT_ID
   ARG NEXT_PUBLIC_AUTH0_AUDIENCE
   ARG NEXT_PUBLIC_API_URL
   ARG NEXT_PUBLIC_WS_URL
   ```

2. **Runtime Stage**
   - Node.js 20-alpine base image
   - Production-optimized build
   - Minimal runtime dependencies

#### Deployment Steps
1. Ensure all environment variables are set in the deployment environment
2. Build and deploy using Docker Compose:
   ```bash
   docker-compose up --build -d
   ```

### Docker Configuration

#### Development (`docker-compose.local.yml`)
- Hot-reload enabled for frontend and backend
- Volume mounts for local development
- Development-specific environment variables
- Exposed ports for direct access

#### Production (`docker-compose.yml`)
- Production-optimized builds
- No volume mounts
- HTTPS/WSS endpoints
- API path prefixing (`/api`)
- Production environment variables

### Troubleshooting

1. **Local Development**
   - Clear Docker volumes if database issues occur
   - Check `.env.local` file for correct variables
   - Verify Docker and Docker Compose installation

2. **Production**
   - Verify EC2 security group settings
   - Check SSL certificate configuration
   - Validate environment variables in deployment environment

### Best Practices

1. **Environment Variables**
   - Never commit sensitive values to version control
   - Use different values for development and production
   - Document all required variables

2. **Docker**
   - Use multi-stage builds for smaller images
   - Implement proper caching strategies
   - Regular security updates

3. **Deployment**
   - Regular backup of production data
   - Monitoring of system resources
   - Proper logging configuration

## Related Documentation
- See `app/app_docs.md` for page components
- See `components/components_docs.md` for UI components
- See `contexts/contexts_docs.md` for state management
- See `lib/lib_docs.md` for utilities
- See `public/public_docs.md` for assets 

## Search Components and Functionality

### Search Hook (`hooks/useSearch.ts`)
- Generic hook for handling debounced search functionality
- Manages search state, loading state, and error handling
- Configurable debounce time (default: 300ms)
- Type-safe with TypeScript generics

### Search API (`lib/api/search.ts`)
- Centralized API functions for all search endpoints
- Type-safe interfaces for search parameters
- Handles requests to:
  - Message search
  - User search
  - Channel search
  - File search

### SearchInput Component (`components/SearchInput.tsx`)
- Reusable search input with loading state
- Consistent styling with Tailwind CSS
- Loading spinner for active searches
- Search icon from Heroicons

### Usage Example
```typescript
const MyComponent = () => {
  const { query, setQuery, results, isLoading } = useSearch({
    searchFn: (q) => searchUsers({ query: q }),
    debounceMs: 300,
  });

  return (
    <SearchInput
      value={query}
      onChange={setQuery}
      isLoading={isLoading}
      placeholder="Search users..."
    />
  );
};
``` 

### Message Reply System
The application supports threaded conversations through a reply system. When a user replies to a message:

1. **Reply Creation**
   - Endpoint: `POST /channels/{channel_id}/messages/{parent_id}/reply`
   - WebSocket event includes `parent_id` and `parent` references
   - Reply messages are not shown in the main thread
   - Parent messages show a "Show replies" button when they have replies

2. **Reply Chain Display**
   - Replies are fetched using `GET /messages/{message_id}/reply-chain`
   - Replies are displayed in a collapsible thread under the parent message
   - The UI visually indicates the reply relationship with indentation and borders

3. **Reply State Management**
   - `replyingTo` state in ChatArea tracks the message being replied to
   - Visual indicator shows which message is being replied to
   - Reply state is cleared after sending the reply

4. **WebSocket Events for Replies**
   ```typescript
   // New message event with reply
   {
     type: "new_message",
     channel_id: number,
     message: {
       content: string,
       parent_id: number,
       parent: Message | null
     }
   }
   ``` 