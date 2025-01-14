# AI Sidebar Implementation Plan

## 1. Component Structure

### New Components
- [x] `AISidebarButton` - Button in channel header to toggle AI sidebar
- [x] `AISidebar` - Main container for AI interface
- [x] `AIQueryInput` - Input area for user questions
- [x] `AIResponse` - Component to display AI responses
- [x] `AIConversationHistory` - Collapsible list of past conversations
- [x] `AIConversationPill` - Individual conversation summary in history

### Component Hierarchy
[CODE START]
ChannelHeader
└── AISidebarButton

AISidebar
├── AIQueryInput
├── AIResponse
└── AIConversationHistory
    └── AIConversationPill
[CODE END]

## 2. Types and Interfaces

### Create new types in `types/ai.ts`
- [x] Define conversation types:
[CODE START]
interface AIConversation {
    id: string;
    channelId: number;
    messages: AIMessage[];
    createdAt: string;
    updatedAt: string;
}

interface AIMessage {
    id: string;
    content: string;
    role: 'user' | 'assistant';
    timestamp: string;
}
[CODE END]

## 3. State Management

### Create AI Context
- [x] Create `contexts/AIContext.tsx`:
[CODE START]
interface AIContextType {
    isOpen: boolean;
    toggleSidebar: () => void;
    currentConversation: AIConversation | null;
    conversationHistory: AIConversation[];
    sendMessage: (message: string) => Promise<void>;
}
[CODE END]

## 4. Styling

### Add Tailwind Classes
- [x] AISidebar:
[CODE START]
<div className="fixed right-0 top-0 h-full w-80 bg-white border-l border-gray-200 
                shadow-lg transform transition-transform duration-300 
                dark:bg-gray-800 dark:border-gray-700">
[CODE END]

- [x] AIQueryInput:
[CODE START]
<div className="flex flex-col gap-2 p-4 border-t border-gray-200 
                dark:border-gray-700">
[CODE END]

## 5. API Integration

### New Endpoints
- [ ] Create endpoints in backend:
[CODE START]
POST /api/channels/{channelId}/ai/query
GET /api/channels/{channelId}/ai/conversations
GET /api/channels/{channelId}/ai/conversations/{conversationId}
[CODE END]

## 6. Implementation Steps

### Phase 1: Basic Structure
- [x] Add AISidebarButton to ChannelHeader
- [x] Implement basic AISidebar with open/close functionality
- [x] Add AIQueryInput with basic styling
- [x] Create AIResponse component for displaying messages

### Phase 2: Conversation History
- [x] Implement AIConversationHistory component
- [x] Create collapsible AIConversationPill components
- [x] Add conversation selection functionality

### Phase 3: API Integration
- [ ] Implement API endpoints for AI interactions
- [ ] Add loading states during API calls
- [ ] Implement error handling

### Phase 4: Polish
- [x] Add animations for sidebar open/close
- [x] Implement proper scroll behavior
- [ ] Add loading indicators
- [ ] Add error states and retry functionality

## 7. Component Details

### AISidebarButton
Purpose: Toggle the AI sidebar visibility
[CODE START]
interface AISidebarButtonProps {
    onClick: () => void;
    isOpen: boolean;
}
[CODE END]

### AISidebar
Purpose: Main container for AI functionality
[CODE START]
interface AISidebarProps {
    isOpen: boolean;
    onClose: () => void;
    channelId: number;
}
[CODE END]

### AIQueryInput
Purpose: Input field for user questions
[CODE START]
interface AIQueryInputProps {
    onSubmit: (query: string) => Promise<void>;
    isLoading: boolean;
}
[CODE END]

## 8. References

### Existing Components to Modify
typescript:frontend/components/ChatArea.tsx
startLine: 1
endLine: 59

### Channel Header Location
typescript:frontend/components/components_docs.md
startLine: 217
endLine: 217
