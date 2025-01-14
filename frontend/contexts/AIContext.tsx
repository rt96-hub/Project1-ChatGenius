'use client';

import { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { useApi } from '@/hooks/useApi';
import type { AIMessage, AIConversation } from '@/types/ai';

interface AIContextType {
    isOpen: boolean;
    toggleSidebar: () => void;
    currentConversation: AIConversation | null;
    conversationHistory: AIConversation[];
    sendMessage: (channelId: number, message: string) => Promise<number | undefined>;
    isLoading: boolean;
    error: string | null;
}

const AIContext = createContext<AIContextType | null>(null);

interface AIProviderProps {
    children: ReactNode;
}

export function AIProvider({ children }: AIProviderProps) {
    const api = useApi();
    const [isOpen, setIsOpen] = useState(false);
    const [currentConversation, setCurrentConversation] = useState<AIConversation | null>(null);
    const [conversationHistory, setConversationHistory] = useState<AIConversation[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const toggleSidebar = useCallback(() => {
        setIsOpen(prev => !prev);
    }, []);

    const sendMessage = useCallback(async (channelId: number, message: string) => {
        if (!message.trim()) return;

        try {
            setIsLoading(true);
            setError(null);

            // Always create a new conversation
            const response = await api.post(`/ai/channels/${channelId}/query`, {
                query: message.trim()
            });
            const newConversation = response.data.conversation;
            setCurrentConversation(newConversation);
            setConversationHistory(prev => [newConversation, ...prev]);
            return newConversation.id; // Return the new conversation ID
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to send message');
            console.error('Failed to send message:', err);
        } finally {
            setIsLoading(false);
        }
    }, [api]);

    const value = {
        isOpen,
        toggleSidebar,
        currentConversation,
        conversationHistory,
        sendMessage,
        isLoading,
        error
    };

    return <AIContext.Provider value={value}>{children}</AIContext.Provider>;
}

export function useAI() {
    const context = useContext(AIContext);
    if (!context) {
        throw new Error('useAI must be used within an AIProvider');
    }
    return context;
}

export default AIContext; 