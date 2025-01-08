# Frontend App Directory Documentation

## Directory Structure
```
frontend/app/
├── globals.css        # Global styles
├── layout.tsx         # Root layout component
├── page.tsx          # Main page component
├── login/            # Login page directory
└── signup/           # Signup page directory
```

## File Descriptions

### `layout.tsx`
The root layout component that wraps all pages in the application.

**Key Components:**
- `RootLayout`: The main layout component that provides the basic HTML structure and context providers.

**Dependencies:**
- `next/font/google`: For loading the Inter font
- `@/contexts/Auth0Provider`: Authentication context provider
- `@/contexts/ConnectionContext`: WebSocket connection context provider

**Functionality:**
- Sets up the base HTML structure
- Configures metadata for the application
- Provides authentication context through Auth0
- Provides WebSocket connection context
- Applies global font styles (Inter)

### `page.tsx`
The main page component that serves as the home page of the application.

**Key Components:**
- `Home`: The main page component implementing the chat interface

**Dependencies:**
- `Header`: Main application header component
- `Sidebar`: Channel list and navigation component
- `ChatArea`: Main chat interface component
- `ProtectedRoute`: Authentication wrapper component

**State Management:**
- `selectedChannelId`: Tracks the currently selected channel
- `refreshChannelList`: Trigger for refreshing the channel list

**Key Functions:**
- `handleChannelSelect`: Manages channel selection
- `handleChannelUpdate`: Triggers channel list refresh
- `handleChannelDelete`: Handles channel deletion and cleanup

**Layout Structure:**
- Implements a responsive layout with:
  - Fixed header
  - Sidebar (64 units wide)
  - Main chat area (flexible width)
  - Full-height design with overflow handling

### `globals.css`
Global CSS styles using Tailwind CSS framework.

**Features:**
- Tailwind CSS integration
- Root CSS variables for:
  - Foreground colors
  - Background colors
- Base styling for body element

**CSS Imports:**
- Tailwind base styles
- Tailwind components
- Tailwind utilities

### Login and Signup Directories
Dedicated directories for authentication-related pages:
- `login/`: Contains login page components and logic
- `signup/`: Contains signup page components and logic

## Component Relationships

The application follows a hierarchical structure:
1. `layout.tsx` provides the application shell and context providers
2. `page.tsx` implements the main application interface
3. Authentication routes (`login/` and `signup/`) are separate pages
4. All components are wrapped in the Auth0 and Connection contexts

## Key Features
- Protected routing with authentication
- Real-time chat functionality
- Channel management
- Responsive design
- WebSocket-based communication
- Authentication with Auth0

## Usage Notes
- All client-side components are marked with 'use client' directive
- Components use TypeScript for type safety
- Tailwind CSS is used for styling
- The application follows a modular architecture for easy maintenance 