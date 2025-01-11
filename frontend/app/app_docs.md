# Frontend App Directory Documentation

## Directory Structure
```
frontend/app/
├── debug/             # Debug utilities and information display
│   └── page.tsx      # Debug page component
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
- `@/contexts/Auth0Provider`: Authentication context provider
- `@/contexts/ConnectionContext`: WebSocket connection context

**Functionality:**
- Sets up the base HTML structure with language set to English
- Configures metadata including title "ChatGenius" and description
- Provides authentication context through Auth0
- Provides WebSocket connection context for real-time messaging
- Applies global font styles using Inter font

### `page.tsx`
The main page component implementing the chat interface.

**Key Components:**
- `Home`: The main page component implementing the chat interface
  - Protected by `ProtectedRoute` component

**Dependencies:**
- `@/components/Header`: Application header component
- `@/components/Sidebar`: Channel list component
- `@/components/ChatArea`: Main chat interface component
- `@/components/ProtectedRoute`: Authentication protection HOC
- React hooks: useState, useCallback

**State Management:**
- `selectedChannelId`: Tracks currently selected channel
- `refreshChannelList`: Counter for channel list refresh

**Key Functions:**
- `handleChannelSelect(channelId: number)`: Sets selected channel
- `handleChannelUpdate()`: Refreshes channel list
- `handleChannelDelete()`: Handles channel deletion
- `handleNavigateToDM(channelId: number)`: Handles direct message navigation

### `debug/page.tsx`
Debug utility page for development and troubleshooting.

**Key Components:**
- `Debug`: Component displaying debug information

**Dependencies:**
- React hooks: useEffect, useState

**Functionality:**
- Displays environment variables (Auth0, API URLs)
- Shows window location information
- Provides development debugging tools

### `globals.css`
Global CSS styles using Tailwind CSS framework.

**Features:**
- Tailwind CSS integration
- Theme color variables:
  - Foreground colors
  - Background colors
- Base styling for body element

## Component Dependencies and Usage

### Components Using App Files:
- `layout.tsx` is used by:
  - All pages in the application
  - Next.js routing system

- `page.tsx` depends on:
  - `@/components/Header`
  - `@/components/Sidebar`
  - `@/components/ChatArea`
  - `@/components/ProtectedRoute`
  - `@/contexts/Auth0Provider` (via layout)
  - `@/contexts/ConnectionContext` (via layout)

### Data Flow and State Management:
1. Authentication State (Auth0Provider)
   - Managed in layout.tsx
   - Used by Header, ProtectedRoute
   - Controls access to protected routes

2. WebSocket Connection (ConnectionProvider)
   - Managed in layout.tsx
   - Used by ChatArea
   - Handles real-time updates

3. Channel Management (page.tsx)
   - State shared between Sidebar and ChatArea
   - Coordinates channel selection and updates
   - Manages direct message navigation

## Best Practices Implemented
- Client-side components marked with 'use client'
- Responsive layout with Tailwind CSS
- Protected route implementation for security
- Centralized state management
- Modular component architecture
- Debug tools for development 