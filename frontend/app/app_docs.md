# Frontend App Directory Documentation

## Directory Structure
```
frontend/app/
├── globals.css        # Global styles using Tailwind CSS
├── layout.tsx         # Root layout component with providers
└── page.tsx          # Main chat interface page
```

## File Descriptions

### `layout.tsx`
The root layout component that wraps all pages in the application.

**Key Components:**
- `RootLayout`: The main layout component that provides the basic HTML structure and context providers
  - Props:
    - `children`: React nodes to be rendered within the layout

**Dependencies:**
- `next/font/google`: For loading the Inter font
- `@/contexts/Auth0Provider`: Authentication context provider for user authentication state
- `@/contexts/ConnectionContext`: WebSocket connection context for real-time communication

**Functionality:**
- Sets up the base HTML structure with language set to English
- Configures metadata including title "ChatGenius" and description
- Provides authentication context through Auth0 for user management
- Provides WebSocket connection context for real-time messaging
- Applies global font styles using Inter font
- Wraps all child components in necessary context providers

### `page.tsx`
The main page component that implements the chat interface.

**Key Components:**
- `Home`: The main page component implementing the chat interface
  - Protected by `ProtectedRoute` component to ensure authentication

**Dependencies:**
- `Header`: Application header showing user info and navigation
- `Sidebar`: Channel list and navigation component (64 units wide)
- `ChatArea`: Main chat interface for messages
- `ProtectedRoute`: HOC for authentication protection

**State Management:**
- `selectedChannelId`: (number | null) - Tracks the currently selected channel
- `refreshChannelList`: (number) - Counter to trigger channel list refresh

**Key Functions:**
- `handleChannelSelect(channelId: number)`: 
  - Sets the selected channel ID
  - Triggers chat area to load channel messages
- `handleChannelUpdate()`: 
  - Callback to refresh channel list
  - Triggered after channel modifications
- `handleChannelDelete()`: 
  - Clears selected channel
  - Triggers channel list refresh
  - Called after channel deletion

**Layout Structure:**
- Implements a responsive layout with:
  - Fixed header at top
  - Sidebar (fixed 64 units wide)
  - Main chat area (flexible width)
  - Full-height design with overflow handling
  - Nested flex containers for optimal space usage

### `globals.css`
Global CSS styles using Tailwind CSS framework.

**Features:**
- Tailwind CSS integration with base, components, and utilities
- Root CSS variables defining theme colors:
  - Foreground colors (default: black)
  - Background colors (gradient from rgb(214, 219, 220) to white)
- Base styling for body element with:
  - Text color using foreground RGB values
  - Background color using end RGB values

## Component Relationships and Data Flow

The application follows a hierarchical structure with data flow:

1. `layout.tsx` (Root)
   - Provides Auth0 authentication context
   - Provides WebSocket connection context
   - ↓
2. `page.tsx` (Main Interface)
   - Manages channel selection state
   - Coordinates between Sidebar and ChatArea
   - ↓
3. Child Components
   - `Header`: Shows user info, uses Auth0 context
   - `Sidebar`: Lists channels, triggers selection
   - `ChatArea`: Shows messages, uses connection context

## Authentication Flow

1. All pages wrapped in `ProtectedRoute`
2. Auth0Provider manages:
   - User authentication state
   - Login/logout operations
   - Token management
   - User profile data
   - Hosted login/signup pages
   - Profile management interface

**Note:** Authentication is fully handled by Auth0's hosted pages and services. We do not maintain custom login, signup, or profile pages as these are provided securely through Auth0's infrastructure.

## Real-time Communication

1. ConnectionProvider establishes WebSocket connection
2. Used by ChatArea for:
   - Real-time message updates
   - Channel status changes
   - User presence information

## Usage Notes
- All components use TypeScript for type safety
- Components marked with 'use client' for client-side rendering
- Tailwind CSS used exclusively for styling
- Modular architecture for maintainability
- Protected routes ensure authenticated access
- Real-time updates through WebSocket connection 