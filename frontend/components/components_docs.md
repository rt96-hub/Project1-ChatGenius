# Frontend Components Documentation

This document provides a comprehensive overview of the components used in the frontend of our Slack-like communication platform. Each component is detailed with its purpose, functionality, and data flow.

## Component Dependencies Overview

### Main App Dependencies
The following components are directly used by the main app (`app/page.tsx`):
- `Header`
- `Sidebar`
- `ChatArea`
- `ProtectedRoute`

### Component Hierarchy
```
app/page.tsx
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
    │   └── EmojiSelector
    ├── UserProfilePopout
    └── MembersList
```

## Core Components

### ChatArea.tsx
**Purpose**: Main chat interface component that handles message display, sending, and real-time updates.

**Key Features**:
- Real-time message display and updates using WebSocket
- Infinite scroll for message history
- Message sending functionality
- Channel information display
- Reaction management
- Member list integration
- Direct Message navigation support
- File upload functionality with progress tracking
- File preview before sending
- Support for messages with attachments

**Props**:
```typescript
interface ChatAreaProps {
  channelId: number | null;
  onChannelUpdate?: () => void;
  onChannelDelete?: () => void;
  onNavigateToDM?: (channelId: number) => void;
}
```

**File Upload Features**:
- File selection through FileUploadButton
- File preview before upload
- Upload progress tracking
- Error handling with retry option
- Support for multiple file types
- Size limit validation
- MIME type validation

**WebSocket Events**:
- `new_message`: Received when a new message is sent
- `message_update`: Received when a message is edited
- `message_delete`: Received when a message is deleted
- `message_reaction_add`: Received when a reaction is added
- `message_reaction_remove`: Received when a reaction is removed
- `channel_update`: Received when channel details are updated
- `member_joined`: Received when a new member joins
- `member_left`: Received when a member leaves
- `role_updated`: Received when a member's role changes
- `privacy_updated`: Received when channel privacy changes

**API Endpoints**:
- GET `/channels/{channelId}/messages`
  ```typescript
  // Request Parameters
  {
    skip: number;  // Pagination offset
    limit: number; // Number of messages to fetch (default: 50)
  }
  // Response
  {
    messages: Message[];
    has_more: boolean;
  }
  ```
- GET `/channels/{channelId}`
  ```typescript
  // Response
  {
    id: number;
    name: string;
    description: string | null;
    owner_id: number;
    is_private: boolean;
    member_count: number;
    users: User[];
  }
  ```
- POST `/channels/{channelId}/messages`
  ```typescript
  // Request Body
  {
    content: string;
  }
  // Response: Message object
  ```
- POST `/channels/{channelId}/messages/with-file`
  ```typescript
  // Request: multipart/form-data
  {
    file: File;
    content?: string;  // Optional message text
  }
  // Response: Message object with file metadata
  ```

### ChatMessage.tsx
**Purpose**: Individual message component handling display and message actions.

**Key Features**:
- Message content display with markdown support
- Edit/Delete functionality for message owners
- Timestamp display with edit indicator
- User avatar and profile link
- Emoji reactions with counter
- Reaction management (add/remove)
- Direct Message initiation through user profile
- File attachment display with download option
- File type icons based on MIME type
- File size formatting

**Props**:
```typescript
interface ChatMessageProps {
  message: Message;
  currentUserId: number;
  channelId: number;
  onMessageUpdate: (updatedMessage: Message) => void;
  onMessageDelete: (messageId: number) => void;
  onNavigateToDM?: (channelId: number) => void;
  onReply?: (parentMessage: Message) => void;
}
```

**Message Interface Updates**:
```typescript
interface Message {
  id: number;
  content: string;
  created_at: string;
  updated_at?: string;
  user_id: number;
  channel_id: number;
  user?: User;
  reactions?: Reaction[];
  files?: Array<{
    id: number;
    message_id: number;
    file_name: string;
    content_type: string;
    file_size: number;
    uploaded_at: string;
    uploaded_by: number;
  }>;
}
```

**File Display Features**:
- File type icons for different MIME types
- File name and size display
- Download functionality
- Loading state during download
- Error handling with toast notifications
- Dark mode support

**API Endpoints**:
- PUT `/channels/{channelId}/messages/{messageId}`
  ```typescript
  // Request Body
  {
    content: string;
  }
  // Response: Updated Message object
  ```
- DELETE `/channels/{channelId}/messages/{messageId}`
  ```typescript
  // Response: Status 200 on success
  ```
- POST `/channels/{channelId}/messages/{messageId}/reactions`
  ```typescript
  // Request Body
  {
    reaction_id: number;
  }
  // Response: New Reaction object
  ```
- DELETE `/channels/{channelId}/messages/{messageId}/reactions/{reactionId}`
  ```typescript
  // Response: Status 200 on success
  ```

**Key Functions**:
- `handleAddReaction`: Manages adding emoji reactions
- `handleRemoveReaction`: Manages removing emoji reactions
- `handleEdit`: Handles message editing
- `handleDelete`: Handles message deletion
- `handleSendDM`: Opens DM channel with message author

### ChannelHeader.tsx
**Purpose**: Displays channel information and provides channel management controls.

**Key Features**:
- Channel name with privacy indicator (# for public, 🔒 for private)
- Channel description display
- Member count with toggle button
- Channel settings access for owners
- Integration with ChannelSettingsModal

**Props**:
```typescript
interface ChannelHeaderProps {
  channel: Channel;
  currentUserId: number;
  onChannelUpdate: () => void;
  onChannelDelete?: () => void;
  onUpdateMemberRole: (userId: number, role: ChannelRole) => void;
  onRemoveMember: (userId: number) => void;
  onGenerateInvite: () => void;
  onToggleMembers: () => void;
  showMembers: boolean;
}
```

### EmojiSelector.tsx
**Purpose**: Popup component for selecting emoji reactions.

**Key Features**:
- Displays available emoji reactions
- Handles emoji selection
- Click-outside detection for closing
- Loading state while fetching reactions
- Support for both system emojis and custom image-based reactions

**Props**:
```typescript
interface EmojiSelectorProps {
  onSelect: (reactionId: number) => void;
  onClose: () => void;
  position: { top: number; left: number };
}
```

**API Endpoints**:
- GET `/reactions/`
  ```typescript
  // Response
  {
    id: number;
    code: string;
    is_system: boolean;
    image_url: string | null;
    created_at: string;
  }[]
  ```

### UserProfilePopout.tsx
**Purpose**: Displays and manages user profile information.

**Key Features**:
- Display user profile information
- Profile picture display
- User status management
- Integration with Auth0 user metadata
- Direct Message functionality with existing/new DM channel creation

**Props**:
```typescript
interface UserProfilePopoutProps {
  user: User;
  isCurrentUser: boolean;
  onClose: () => void;
  onUpdate?: (updatedUser: User) => void;
  onNavigateToDM?: (channelId: number) => void;  // For handling DM navigation
}
```

**API Endpoints**:
- GET `/users/{id}` - Fetch user data
- PUT `/users/me/name` - Update user name
- PUT `/users/me/bio` - Update user bio
- GET `/channels/dm/check/{other_user_id}` - Check for existing DM channel
- POST `/channels/dm` - Create new DM channel

**State Management**:
- `isEditing`: Controls profile edit mode
- `isDMLoading`: Handles loading state during DM operations
- `error`: Stores error messages
- `currentUser`: Stores the current user data
- `isFetching`: Handles loading state during data fetching

**Key Functions**:
- `handleSubmit`: Handles profile updates
- `handleSendDM`: Manages DM channel creation/navigation
  1. Checks for existing DM channel
  2. If exists, navigates to it
  3. If not, creates new DM channel and navigates to it

### ProfileStatus.tsx
**Purpose**: Shows user status and provides access to profile management.

**Key Features**:
- User status indicator
- Profile picture display
- Click to open UserProfilePopout
- Connection status display

**Props**:
```typescript
interface ProfileStatusProps {
  user: Auth0User;
  connectionStatus: ConnectionStatus;
  onProfileUpdate?: (updates: { name?: string; bio?: string }) => Promise<void>;
}
```

### ChannelSettingsModal.tsx
**Purpose**: Modal interface for managing channel settings.

**Key Features**:
- Channel name and description editing
- Privacy settings management
- Member role management
- Invite code generation
- Channel deletion option

**Props**:
```typescript
interface ChannelSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  channel: Channel;
  currentUserId: number;
  onUpdateChannel: () => void;
  onUpdateMemberRole: (userId: number, role: ChannelRole) => void;
  onRemoveMember: (userId: number) => void;
  onGenerateInvite: () => void;
  onDeleteChannel: () => void;
}
```

**API Endpoints**:
- PUT `/channels/{id}`
  ```typescript
  // Request Body
  {
    name?: string;
    description?: string;
    is_private?: boolean;
  }
  // Response: Updated Channel object
  ```
- DELETE `/channels/{id}`
  ```typescript
  // Response: Status 200 on success
  ```
- POST `/channels/{id}/invite`
  ```typescript
  // Response
  {
    code: string;
    expires_at: string;
  }
  ```

### MembersList.tsx
**Purpose**: Displays and manages channel members.

**Key Features**:
- List of channel members with roles
- Role management for channel owners
- Member removal functionality
- Online status indicators

**Props**:
```typescript
interface MembersListProps {
  members: ChannelMember[];
  currentUserId: number;
  isOwner: boolean;
  onUpdateRole: (userId: number, role: ChannelRole) => void;
  onRemoveMember: (userId: number) => void;
}
```

### ConfirmDialog.tsx
**Purpose**: Reusable confirmation dialog for destructive actions.

**Props**:
```typescript
interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  type?: 'danger' | 'warning';
}
```

### AuthButton.tsx
**Purpose**: Authentication control component using Auth0.

**Key Features**:
- Login/Logout functionality
- Authentication state display
- Integration with Auth0's Universal Login

### CreateChannelModal.tsx
**Purpose**: Modal for creating new channels.

**Key Features**:
- Channel creation form
- Privacy settings
- Description field
- Validation

**API Endpoints**:
- POST `/channels`
  ```typescript
  // Request Body
  {
    name: string;
    description?: string;
    is_private?: boolean;
  }
  // Response: New Channel object
  ```

### Sidebar.tsx
**Purpose**: Main navigation component displaying channels and direct messages.

**Key Features**:
- Displays list of channels
- Displays list of direct messages (limited to 5)
- Channel creation functionality
- Visual indicators for private channels and selected channel
- Role badges for moderators and owners
- Real-time updates through WebSocket connection

**Props**:
```typescript
interface SidebarProps {
    onChannelSelect: (channelId: number) => void;
    refreshTrigger: number;
}
```

**API Endpoints**:
- GET `/channels/me`
  ```typescript
  // Response: Array of Channel objects
  ```
- GET `/channels/me/dms?limit=5`
  ```typescript
  // Response: Array of DM Channel objects
  ```

**State Management**:
- `channels`: Regular channels list
- `dmChannels`: Direct message channels list (limited to 5)
- `selectedChannelId`: Currently selected channel
- `isCreateModalOpen`: Controls channel creation modal

**WebSocket Events**:
- Listens for `channel_update` events
- Updates both regular and DM channels in real-time

**Dependencies**:
- `useApi`: For making authenticated API requests
- `useAuth`: For accessing current user information
- `useConnection`: For WebSocket connection management

### ViewDMsModal.tsx
**Purpose**: Modal component for viewing all direct message channels.

**Key Features**:
- Displays a complete list of user's DM channels
- Search bar for filtering DMs (UI only for now)
- Shows other participants' names for each DM
- Shows timestamp of last message in each DM
- Sorts DMs by most recent message first
- Clickable DM entries that navigate to the conversation

**Props**:
```typescript
interface ViewDMsModalProps {
    isOpen: boolean;
    onClose: () => void;
    onDMSelect: (channelId: number) => void;
    currentUserId: number;
    dmChannels: Channel[];
}
```

**Data Display**:
- Uses the `messages` array from each channel to determine the last message timestamp
- Sorts channels based on their most recent message's `created_at` timestamp
- Shows "No messages" for channels without any messages

### NewDMModal.tsx
**Purpose**: Modal component for creating new direct message conversations.

**Key Features**:
- Displays list of users ordered by last DM interaction
- Search bar for filtering users (UI only for now)
- User profile pictures and email display
- Shows timestamp of last DM with each user (or "Never" if no previous DMs)
- Creates new DM channel on user selection

**Props**:
```typescript
interface NewDMModalProps {
    isOpen: boolean;
    onClose: () => void;
    onDMCreated: (channelId: number) => void;
}
```

**Data Structure**:
```typescript
interface UserWithLastDM {
    user: User;
    last_dm_at: string | null;  // Timestamp of last DM, null if no DM exists
    channel_id: number | null;  // ID of existing DM channel, null if none exists
}
```

**API Endpoints**:
- GET `/users/by-last-dm`
  ```typescript
  // Response
  {
    user: {
        id: number;
        email: string;
        name: string;
        picture?: string;
        bio?: string;
    };
    last_dm_at: string | null;
    channel_id: number | null;
  }[]
  ```
- POST `/channels/dm`
  ```typescript
  // Request Body
  {
    user_ids: number[];
  }
  // Response: Channel object
  ```

**Dependencies**:
- `useApi`: For making authenticated API requests
- `MagnifyingGlassIcon`: From Heroicons for search UI

## Data Models

### Message Interface
```typescript
interface Message {
  id: number;
  content: string;
  created_at: string;
  updated_at?: string;
  user_id: number;
  channel_id: number;
  user?: User;
  reactions?: Reaction[];
  files?: Array<{
    id: number;
    message_id: number;
    file_name: string;
    content_type: string;
    file_size: number;
    uploaded_at: string;
    uploaded_by: number;
  }>;
}
```

### Channel Interface
```typescript
interface Channel {
  id: number;
  name: string;
  description: string | null;
  owner_id: number;
  is_private: boolean;
  member_count: number;
  users: User[];
}
```

### User Interface
```typescript
interface User {
  id: number;
  email: string;
  name: string;
  picture?: string;
  bio?: string;
}
```

### Reaction Interface
```typescript
interface Reaction {
  id: number;
  message_id: number;
  reaction_id: number;
  user_id: number;
  created_at: string;
  code?: string;
  reaction: {
    id: number;
    code: string;
    is_system: boolean;
    image_url: string | null;
  };
  user: User;
}
```

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

### Dependencies and Contexts

All components generally depend on the following shared resources:

**Contexts:**
- `ConnectionContext`: WebSocket connection management
- `Auth0Provider`: Authentication state and methods
- `ApiContext`: API client and utilities

**Hooks:**
- `useAuth`: Authentication state and methods
- `useApi`: API client and utilities
- `useConnection`: WebSocket connection management

**UI Libraries:**
- `@heroicons/react`: Icon components
- `@headlessui/react`: UI components (modals, dropdowns)
- TailwindCSS: Styling

**Types:**
All components use shared type definitions from `@/types/*`:
- `Channel`
- `Message`
- `User`
- `Reaction`

## Component Usage Map

### Header.tsx
**Used by:** `app/page.tsx`
**Dependencies:**
- `ProfileStatus`
- `@heroicons/react/24/outline`: `{ Bars3Icon, MagnifyingGlassIcon }`
- `useAuth`
- `useConnection`

### Sidebar.tsx
**Used by:** `app/page.tsx`
**Dependencies:**
- `CreateChannelModal`
- `ViewDMsModal`
- `NewDMModal`
- `ConfirmDialog`
- `@heroicons/react/24/outline`: Various icons
- `useApi`
- `useAuth`
- `useConnection`

### ChatArea.tsx
**Used by:** `app/page.tsx`
**Dependencies:**
- `ChannelHeader`
- `ChatMessage`
- `MembersList`
- `ChannelSettingsModal`
- `useConnection`
- `useApi`

### ChatMessage.tsx
**Used by:** `ChatArea`
**Dependencies:**
- `EmojiSelector`
- `UserProfilePopout`
- `useApi`

### UserProfilePopout.tsx
**Used by:** `ChatMessage`
**Dependencies:**
- `useAuth`
- `useApi`

### EmojiSelector.tsx
**Used by:** `ChatMessage`
**Dependencies:**
- `useApi`
- `useClickOutside` (custom hook)

### ChannelHeader.tsx
**Used by:** `ChatArea`
**Dependencies:**
- `ChannelSettingsModal`
- `MembersList`

### MembersList.tsx
**Used by:** 
- `ChatArea`
- `ChannelSettingsModal`
**Dependencies:**
- `useApi`

### ConfirmDialog.tsx
**Used by:**
- `Sidebar`
- `ChannelSettingsModal`
- `ChatMessage`
**Dependencies:**
- `@headlessui/react`

### CreateChannelModal.tsx
**Used by:** `Sidebar`
**Dependencies:**
- `useApi`
- `@headlessui/react`

### ViewDMsModal.tsx
**Used by:** `Sidebar`
**Dependencies:**
- `useApi`
- `@headlessui/react`

### NewDMModal.tsx
**Used by:** `Sidebar`
**Dependencies:**
- `useApi`
- `@headlessui/react`

### ChannelSettingsModal.tsx
**Used by:**
- `ChatArea`
- `ChannelHeader`
**Dependencies:**
- `MembersList`
- `ConfirmDialog`
- `useApi`
- `@headlessui/react`

### ProtectedRoute.tsx
**Used by:** `app/page.tsx`
**Dependencies:**
- `useAuth`

### ProfileStatus.tsx
**Used by:** `Header`
**Dependencies:**
- `useAuth`
- `useConnection`

## File Components

### FileUploadButton
A button component that handles file selection and initial validation.

**Props:**
- `onFileSelect: (file: File) => void` - Callback when a file is selected
- `disabled?: boolean` - Whether the button is disabled
- `maxSizeMB?: number` - Maximum file size in MB (default: 50)
- `allowedTypes?: string[]` - Array of allowed MIME types (default: ['image/*', 'application/pdf', 'text/*'])

**Features:**
- File type validation
- File size validation
- Tooltip on hover
- Accessible button and input
- Dark mode support

### FilePreview
A component that displays file information before upload.

**Props:**
- `file: File` - The file to preview
- `onRemove: () => void` - Callback to remove the file

**Features:**
- File name display with truncation
- File size formatting
- Remove button
- Dark mode support

### FileUploadProgress
A progress bar component for file uploads.

**Props:**
- `fileName: string` - Name of the file being uploaded
- `progress: number` - Upload progress (0-100)
- `onCancel: () => void` - Callback to cancel upload
- `error?: string` - Optional error message

**Features:**
- Progress bar visualization
- Cancel button
- Error state handling
- Retry option on error
- Dark mode support

### MessageAttachment
A component for displaying file attachments in messages.

**Props:**
- `id: number` - File ID
- `fileName: string` - Name of the file
- `fileSize: number` - Size of the file in bytes
- `contentType: string` - MIME type of the file
- `messageId: number` - ID of the associated message

**Features:**
- File type icon based on MIME type
- File name and size display
- Download functionality with loading state
- Error handling with toast notifications
- Dark mode support 