# Frontend Components Documentation

This document provides a comprehensive overview of the components used in the frontend of our Slack-like communication platform. Each component is detailed with its purpose, functionality, and data flow.

## Core Components

### ChatArea.tsx
**Purpose**: Main chat interface component that handles message display, sending, and real-time updates.

**Key Features**:
- Real-time message display and updates using WebSocket
- Infinite scroll for message history
- Message sending functionality
- Channel information display

**Props**:
```typescript
interface ChatAreaProps {
  channelId: number | null;
  onChannelUpdate?: () => void;
  onChannelDelete?: () => void;
}
```

**Data Flow**:
- Incoming:
  - Channel messages via WebSocket and REST API
  - Channel details from `/channels/{channelId}`
  - User information from `/users/me`
- Outgoing:
  - New messages via WebSocket (fallback to HTTP POST)
  - Message updates and deletions

**Key Functions**:
- `fetchMessages`: Loads message history with pagination
- `handleSendMessage`: Sends new messages through WebSocket/HTTP
- `loadMoreMessages`: Implements infinite scroll functionality

**API Interactions**:
- GET `/channels/{channelId}/messages`
  - Request Parameters:
    ```typescript
    {
      skip: number;  // Pagination offset
      limit: number; // Number of messages to fetch (default: 50)
    }
    ```
  - Response:
    ```typescript
    {
      messages: Message[];
      has_more: boolean;
    }
    ```

- GET `/channels/{channelId}`
  - Response:
    ```typescript
    {
      id: number;
      name: string;
      description: string | null;
      owner_id: number;
    }
    ```

- GET `/users/me`
  - Response:
    ```typescript
    {
      id: number;
      email: string;
      name?: string;
    }
    ```

- POST `/channels/{channelId}/messages` (HTTP fallback)
  - Request Body:
    ```typescript
    {
      content: string;
    }
    ```
  - Response: Message object

### ChatMessage.tsx
**Purpose**: Individual message component handling display and message actions.

**Key Features**:
- Message content display
- Edit/Delete functionality for message owners
- Timestamp display
- Visual feedback on hover

**Props**:
```typescript
interface ChatMessageProps {
  message: Message;
  currentUserId: number;
  channelId: number;
  onMessageUpdate: (updatedMessage: Message) => void;
  onMessageDelete: (messageId: number) => void;
}
```

**API Interactions**:
- PUT `/channels/{channelId}/messages/{messageId}`
  - Request Body:
    ```typescript
    {
      content: string;
    }
    ```
  - Response: Updated Message object

- DELETE `/channels/{channelId}/messages/{messageId}`
  - Response: Status 200 on success

### Sidebar.tsx
**Purpose**: Navigation component showing channels and direct messages.

**Features**:
- Channel list display
- Direct message conversations
- Channel creation interface
- Navigation between different chat spaces

### ProtectedRoute.tsx
**Purpose**: Authentication wrapper component for protected routes.

**Features**:
- Route protection based on authentication status
- Redirect to login for unauthenticated users
- Loading state handling during auth check

### Header.tsx
**Purpose**: Application header with navigation and user controls.

**Features**:
- User profile display
- Navigation menu
- Authentication status
- App branding

### CreateChannelModal.tsx
**Purpose**: Modal component for creating new channels.

**Features**:
- Channel creation form
- Validation
- Success/Error handling

**API Interactions**:
- POST `/channels`
  - Request Body:
    ```typescript
    {
      name: string;
      description?: string;
    }
    ```
  - Response:
    ```typescript
    {
      id: number;
      name: string;
      description: string | null;
      owner_id: number;
    }
    ```

### ChannelHeader Component
The `ChannelHeader` component displays the channel information at the top of a channel view. It shows:
- Channel name with privacy indicator (# for public, 🔒 for private)
- Channel description (if any)
- Member count with toggle button
- Settings button (opens ChannelSettingsModal)
- Leave channel button (for non-owners)

Props:
- `channel`: Channel object containing channel details
- `currentUserId`: ID of the current user
- `onChannelUpdate`: Callback when channel is updated
- `onChannelDelete`: Optional callback when channel is deleted
- `onUpdateMemberRole`: Callback to update a member's role
- `onRemoveMember`: Callback to remove a member
- `onGenerateInvite`: Callback to generate invite code
- `onToggleMembers`: Callback to toggle members list visibility
- `showMembers`: Boolean indicating if members list is visible

### AuthButton.tsx
**Purpose**: Authentication control component.

**Features**:
- Login/Logout functionality
- Authentication state display
- OAuth integration

### SignupForm.tsx
**Purpose**: User registration form component.

**Features**:
- User registration form
- Input validation
- Error handling
- Success feedback

**API Interactions**:
- POST `/register`
  - Request Body:
    ```typescript
    {
      email: string;
      password: string;
    }
    ```
  - Response:
    ```typescript
    {
      id: number;
      email: string;
    }
    ```

- POST `/token` (Auto-login after signup)
  - Request Body (x-www-form-urlencoded):
    ```
    username: string;
    password: string;
    ```
  - Response:
    ```typescript
    {
      access_token: string;
      token_type: string;
    }
    ```

### LoginForm.tsx
**Purpose**: User login form component.

**Features**:
- Login form
- Credential validation
- Error display
- OAuth options

**API Interactions**:
- POST `/auth/login`
  - Request Body:
    ```typescript
    {
      email: string;
      password: string;
    }
    ```
  - Response:
    ```typescript
    {
      access_token: string;
      token_type: string;
    }
    ```

### ProfileStatus.tsx
**Purpose**: User profile status display and management.

**Features**:
- Status display
- Status update interface
- Online/Offline indication

**API Interactions**:
- PUT `/users/status`
  - Request Body:
    ```typescript
    {
      status: string;
      status_emoji?: string;
    }
    ```
  - Response:
    ```typescript
    {
      id: number;
      status: string;
      status_emoji: string | null;
      updated_at: string;
    }
    ```

## Data Models

### Message Interface
```typescript
interface Message {
  id: number;
  content: string;
  created_at: string;
  updated_at: string;
  user_id: number;
  channel_id: number;
  user?: {
    id: number;
    email: string;
    name?: string;
  };
}
```

### Channel Interface
```typescript
interface Channel {
  id: number;
  name: string;
  description: string | null;
  owner_id: number;
}
```

## WebSocket Events

The application uses WebSocket for real-time updates with the following events:

- `new_message`: Received when a new message is sent
- `message_update`: Received when a message is edited
- `message_delete`: Received when a message is deleted
- `channel_update`: Received when channel details are updated

## Context Usage

Components utilize the following contexts:
- `ConnectionContext`: WebSocket connection management
- `Auth0Provider`: Authentication state and methods

## Styling

Components use Tailwind CSS for styling with consistent class patterns for:
- Layout structure
- Responsive design
- Interactive elements
- Theme colors
- Typography

## Error Handling

Components implement consistent error handling patterns:
- API error catching and display
- User feedback for actions
- Fallback UI states
- Network error recovery 

## Channel Management Components

### ConfirmDialog
A reusable confirmation dialog component for destructive actions.

**Props:**
- `isOpen`: boolean - Controls the visibility of the dialog
- `onClose`: () => void - Handler for closing the dialog
- `onConfirm`: () => void - Handler for confirming the action
- `title`: string - Dialog title
- `message`: string - Dialog message
- `confirmText`: string (optional) - Text for confirm button (default: "Confirm")
- `cancelText`: string (optional) - Text for cancel button (default: "Cancel")
- `type`: 'danger' | 'warning' (optional) - Style variant (default: "danger")

### MembersList
Displays a list of channel members with their roles and actions.

**Props:**
- `members`: ChannelMember[] - Array of channel members
- `currentUserId`: number - ID of the current user
- `isOwner`: boolean - Whether the current user is the channel owner
- `onUpdateRole`: (userId: number, role: ChannelRole) => void - Handler for updating member roles
- `onRemoveMember`: (userId: number) => void - Handler for removing members

### ChannelInvite
Component for generating and displaying channel invite codes.

**Props:**
- `channelId`: number - ID of the channel
- `joinCode`: string | null - Current invite code
- `onGenerateInvite`: () => void - Handler for generating new invite codes

### ChannelSettingsModal Component
The `ChannelSettingsModal` component provides a modal interface for managing channel settings. It includes:

Tabs:
1. General
   - Channel name editing (owner only)
   - Channel description editing (owner only)
   - Channel deletion option (owner only)
2. Privacy
   - Private/Public toggle
   - Invite code management (for private channels)
3. Members
   - Member list management
   - Role updates
   - Member removal

Features:
- Real-time updates for channel name and description (saves on blur)
- Confirmation dialog for channel deletion
- API integration for all channel operations

Props:
- `isOpen`: Boolean to control modal visibility
- `onClose`: Callback to close the modal
- `channel`: Channel object containing channel details
- `currentUserId`: ID of the current user
- `onUpdateChannel`: Callback when channel is updated
- `onUpdateMemberRole`: Callback to update a member's role
- `onRemoveMember`: Callback to remove a member
- `onGenerateInvite`: Callback to generate invite code
- `onDeleteChannel`: Callback when channel is deleted

API Endpoints Used:
- PUT `/channels/{id}` - Update channel details
- DELETE `/channels/{id}` - Delete channel
- POST `/channels/{id}/leave` - Leave channel

**Dependencies:**
- @headlessui/react for modal and tabs components
- @heroicons/react for icons
- TailwindCSS for styling 