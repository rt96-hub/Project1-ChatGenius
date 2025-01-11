# Frontend Types Suggestions

This document outlines potential improvements, cleanup suggestions, and opportunities for new features in the types system.

## Code Cleanup Suggestions

### 1. Message Type Consolidation
Currently, there are two different `Message` interfaces:
- One in `channel.ts`
- One in `message.ts`

**Suggestion:** Consolidate these into a single `Message` type in `message.ts` and update all references.
```typescript
// Proposed consolidated Message type
export interface Message {
    id: number;
    content: string;
    created_at: string;
    updated_at: string;
    user_id: number;
    channel_id: number;
    user: User;
    reactions: Reaction[];  // Add proper Reaction type
}
```

### 2. Define Reaction Type
The `reactions` array in `Message` currently uses `any[]`.

**Suggestion:** Create a proper `Reaction` type:
```typescript
// Create new file: reaction.ts
export interface Reaction {
    id: number;
    message_id: number;
    user_id: number;
    emoji_code: string;
    created_at: string;
    user: User;
}
```

### 3. Date Handling
All date fields are currently strings.

**Suggestion:** Consider using a more specific type for dates:
```typescript
type ISODateString = string;  // Type alias for clarity

// Use in interfaces
interface User {
    // ...
    created_at: ISODateString;
}
```

### 4. Role-Based Type Guards
Add type guards for role-based operations.

**Suggestion:**
```typescript
// Add to channel.ts
export function isChannelOwner(role: ChannelRole): boolean {
    return role === 'owner';
}

export function canModerateChannel(role: ChannelRole): boolean {
    return role === 'owner' || role === 'moderator';
}
```

## Simplification Opportunities

### 1. User Type Hierarchy
Create a hierarchy of user types to handle different contexts:

```typescript
// Base user information
interface BaseUser {
    id: number;
    name: string;
    email: string;
    picture?: string;
}

// Extended user for profile
interface UserProfile extends BaseUser {
    bio?: string;
    auth0_id: string;
    is_active: boolean;
    created_at: string;
}

// Channel member specific
interface ChannelMember extends BaseUser {
    role: ChannelRole;
}
```

### 2. Channel Type Variants
Split channel types based on their nature:

```typescript
interface BaseChannel {
    id: number;
    name: string;
    created_at: string;
    member_count: number;
}

interface GroupChannel extends BaseChannel {
    description: string | null;
    owner_id: number;
    is_private: boolean;
    is_dm: false;
    join_code: string | null;
}

interface DirectMessageChannel extends BaseChannel {
    is_dm: true;
    participants: User[];
}

type Channel = GroupChannel | DirectMessageChannel;
```

## Easy Entry Points for New Features

### 1. Channel Categories
Add support for channel organization:

```typescript
interface ChannelCategory {
    id: number;
    name: string;
    channels: Channel[];
    order: number;
}

// Add to Channel interface:
interface Channel {
    // ... existing properties
    category_id?: number;
}
```

### 2. Message Threading
Add support for threaded conversations:

```typescript
interface Thread {
    id: number;
    parent_message_id: number;
    messages: Message[];
    participant_count: number;
    last_reply_at: string;
}

// Add to Message interface:
interface Message {
    // ... existing properties
    thread?: Thread;
    reply_count?: number;
}
```

### 3. User Presence System
Add types for user presence tracking:

```typescript
type UserStatus = 'online' | 'idle' | 'do_not_disturb' | 'offline';

interface UserPresence {
    user_id: number;
    status: UserStatus;
    last_active: string;
    custom_status?: string;
}

// Add to User interface:
interface User {
    // ... existing properties
    presence?: UserPresence;
}
```

### 4. Message Formatting
Add support for rich text formatting:

```typescript
interface MessageFormat {
    bold?: [number, number][];      // Ranges of bold text
    italic?: [number, number][];    // Ranges of italic text
    code?: [number, number][];      // Ranges of code blocks
    links?: Array<{
        range: [number, number];
        url: string;
    }>;
}

// Add to Message interface:
interface Message {
    // ... existing properties
    formatting?: MessageFormat;
}
```

## Performance Optimization Suggestions

1. Consider using TypeScript's `Pick` and `Omit` utility types for API responses that don't need full objects
2. Add readonly modifiers to properties that shouldn't change after initialization
3. Use discriminated unions for better type safety in WebSocket events

## Type Safety Improvements

1. Add strict null checks for optional properties
2. Use const assertions for role types
3. Add validation functions with type predicates
4. Consider using branded types for IDs to prevent mixing different types of IDs

## Documentation Improvements

1. Add JSDoc comments to all interfaces and types
2. Include examples of correct usage
3. Document breaking changes in type definitions
4. Add migration guides for major type changes

## Next Steps

1. Implement the Reaction type as it's currently using `any[]`
2. Consolidate the Message interfaces
3. Add type guards for role-based operations
4. Consider implementing the user presence system
5. Add support for message threading
6. Implement channel categories

These changes will improve type safety, reduce code duplication, and prepare the system for new features while maintaining backward compatibility. 