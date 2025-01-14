export interface AIMessage {
    id: string;
    content: string;
    role: 'user' | 'assistant';
    timestamp: string;
}

export interface AIConversation {
    id: string;
    channelId: number;
    messages: AIMessage[];
    createdAt: string;
    updatedAt: string;
}

export interface AIResponse {
    conversation: AIConversation;
    message: AIMessage;
} 