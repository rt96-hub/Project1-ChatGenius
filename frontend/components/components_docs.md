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
- Reaction management
- Member list integration

**Props**:
```typescript
interface ChatAreaProps {
  channelId: number | null;
  onChannelUpdate?: () => void;
  onChannelDelete?: () => void;
}
```

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

### ChatMessage.tsx
**Purpose**: Individual message component handling display and message actions.

**Key Features**:
- Message content display with markdown support
- Edit/Delete functionality for message owners
- Timestamp display with edit indicator
- User avatar and profile link
- Emoji reactions with counter
- Reaction management (add/remove)

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

**Props**:
```typescript
interface UserProfilePopoutProps {
  user: Auth0User;
  onClose: () => void;
  onUpdateProfile?: (updates: { name?: string; bio?: string }) => Promise<void>;
}
```

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