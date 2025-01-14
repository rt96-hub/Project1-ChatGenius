export interface AIMessage {
    id: number;
    message: string;
    role: 'user' | 'assistant';
    conversation_id: number;
    channel_id: number;
    user_id: number;
    timestamp: string;
    parameters?: Record<string, any>;
}

export interface AIConversation {
    id: number;
    channelId: number;
    userId: number;
    messages: AIMessage[];
    createdAt: string;
    updatedAt?: string;
}

export interface AIResponse {
    conversation: AIConversation;
    message: AIMessage;
} 