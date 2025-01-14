import { useContext } from 'react';
import AIContext from '@/contexts/AIContext';
import type { AIConversation } from '@/types/ai';

interface UseAIReturn {
    isOpen: boolean;
    toggleSidebar: () => void;
    currentConversation: AIConversation | null;
    conversationHistory: AIConversation[];
    sendMessage: (channelId: number, message: string) => Promise<number | undefined>;
    isLoading: boolean;
    error: string | null;
}

export function useAI(): UseAIReturn {
    const context = useContext(AIContext);
    if (!context) {
        throw new Error('useAI must be used within an AIProvider');
    }
    return context;
}

export default useAI; 