# Frontend Types Documentation

This document provides a comprehensive overview of the TypeScript types and interfaces used throughout the frontend application. Each type is detailed with its structure, dependencies, and usage across components.

## Type Files Overview

The types are organized into three main files:
- `channel.ts`: Channel-related types including Channel, ChannelMember, and ChannelRole
- `user.ts`: User-related types and interfaces
- `message.ts`: Message and reaction-related types

## Core Types

### Channel Types (`channel.ts`)

#### ChannelRole
```typescript
type ChannelRole = 'owner' | 'moderator' | 'member';
```
**Used by:**
- `ChannelMember` interface
- `Channel` interface
- `MembersList` component
- `ChannelSettingsModal` component

#### Channel
```typescript
interface Channel {
    id: number;
    name: string;
    description: string | null;
    owner_id: number;
    created_at: string;
    is_private: boolean;
    is_dm: boolean;
    join_code: string | null;
    users: ChannelMember[];
    messages: Message[];
    member_count: number;
    role?: ChannelRole;
}
```
**Used by:**
- `ChatArea` component
- `Sidebar` component
- `ChannelHeader` component
- `ChannelSettingsModal` component
- `ViewDMsModal` component

**API Endpoints:**
- GET `/channels/{id}`
- GET `/channels/me`
- GET `/channels/me/dms`
- POST `/channels`
- PUT `/channels/{id}`

#### ChannelMember
```typescript
interface ChannelMember {
    id: number;
    name: string;
    email: string;
    picture?: string;
    role: ChannelRole;
}
```
**Used by:**
- `Channel` interface
- `MembersList` component
- `UserProfilePopout` component

### User Types (`user.ts`)

#### User
```typescript
interface User {
    id: number;
    email: string;
    name: string;
    picture?: string;
    bio?: string;
    auth0_id: string;
    is_active: boolean;
    created_at: string;
}
```
**Used by:**
- `Message` interface
- `UserProfilePopout` component
- `ProfileStatus` component
- `NewDMModal` component
- `ChatMessage` component

**API Endpoints:**
- GET `/users/{id}`
- GET `/users/me`
- PUT `/users/me/name`
- PUT `/users/me/bio`
- GET `/users/by-last-dm`

### Message Types (`message.ts`)

#### Message
```typescript
interface Message {
    id: number;
    content: string;
    created_at: string;
    updated_at: string;
    user_id: number;
    channel_id: number;
    user: User;
    reactions: Reaction[];
}
```
**Used by:**
- `ChatArea` component
- `ChatMessage` component
- `Channel` interface

**API Endpoints:**
- GET `/channels/{channelId}/messages`
- POST `/channels/{channelId}/messages`
- PUT `/channels/{channelId}/messages/{messageId}`
- DELETE `/channels/{channelId}/messages/{messageId}`

## API Response Types

### Channel Endpoints

#### GET `/channels/{id}`
```typescript
Response: Channel
```

#### GET `/channels/me`
```typescript
Response: Channel[]
```

#### POST `/channels`
```typescript
Request: {
    name: string;
    description?: string;
    is_private?: boolean;
}
Response: Channel
```

### Message Endpoints

#### GET `/channels/{channelId}/messages`
```typescript
Request: {
    skip: number;
    limit: number;
}
Response: {
    messages: Message[];
    has_more: boolean;
}
```

#### POST `/channels/{channelId}/messages`
```typescript
Request: {
    content: string;
}
Response: Message
```

### User Endpoints

#### GET `/users/by-last-dm`
```typescript
Response: {
    user: User;
    last_dm_at: string | null;
    channel_id: number | null;
}[]
```

## WebSocket Event Types

The application uses WebSocket for real-time updates. Here are the event types and their corresponding data structures:

### Message Events
```typescript
interface NewMessageEvent {
    type: 'new_message';
    data: Message;
}

interface MessageUpdateEvent {
    type: 'message_update';
    data: Message;
}

interface MessageDeleteEvent {
    type: 'message_delete';
    data: { message_id: number };
}
```

### Channel Events
```typescript
interface ChannelUpdateEvent {
    type: 'channel_update';
    data: Channel;
}

interface MemberEvent {
    type: 'member_joined' | 'member_left';
    data: {
        channel_id: number;
        user: User;
    };
}

interface RoleUpdateEvent {
    type: 'role_updated';
    data: {
        channel_id: number;
        user_id: number;
        role: ChannelRole;
    };
}
```

## Type Dependencies

### Direct Dependencies
- `message.ts` depends on `user.ts`
- `channel.ts` contains internal dependencies between its interfaces

### Component Dependencies
Most frontend components depend on these types. Key dependencies include:
- `ChatArea`: Uses `Channel`, `Message`, `User`
- `Sidebar`: Uses `Channel`, `ChannelRole`
- `UserProfilePopout`: Uses `User`, `ChannelMember`
- `MembersList`: Uses `ChannelMember`, `ChannelRole`
- `ChatMessage`: Uses `Message`, `User`

## Best Practices

When using these types:
1. Always import types directly from their source files
2. Use type assertions sparingly
3. Leverage TypeScript's type inference when possible
4. Keep type definitions synchronized with API responses
5. Update this documentation when modifying types

## Notes

1. The `reactions` array in the `Message` interface currently uses `any[]`. Consider defining a proper `Reaction` type if needed.
2. Some optional fields (marked with `?`) indicate that the field might not be present in all contexts.
3. The `ChannelRole` type is used for access control throughout the application.
4. WebSocket events use these types for real-time updates.
``` 