import { useState, useEffect } from 'react';
import { XMarkIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';
import { useApi } from '@/hooks/useApi';
import { useAI } from '@/contexts/AIContext';
import type { AIConversation } from '@/types/ai';

interface AISidebarProps {
    isOpen: boolean;
    onClose: () => void;
    channelId: number;
}

export default function AISidebar({ isOpen, onClose, channelId }: AISidebarProps) {
    const api = useApi();
    const { sendMessage, isLoading, error } = useAI();
    const [query, setQuery] = useState('');
    const [conversations, setConversations] = useState<AIConversation[]>([]);
    const [expandedConversation, setExpandedConversation] = useState<number | null>(null);

    // Fetch conversations when the component mounts or channelId changes
    useEffect(() => {
        const fetchConversations = async () => {
            if (!channelId) return;
            
            try {
                const response = await api.get(`/ai/channels/${channelId}/conversations`);
                setConversations(response.data.conversations);
            } catch (error) {
                console.error('Failed to fetch AI conversations:', error);
                setConversations([]);
            }
        };

        fetchConversations();
    }, [channelId, api]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        try {
            await sendMessage(channelId, query);
            setQuery('');
            
            // Refresh conversations after sending message
            const response = await api.get(`/ai/channels/${channelId}/conversations`);
            setConversations(response.data.conversations);
        } catch (error) {
            console.error('Failed to submit AI query:', error);
        }
    };

    const toggleConversation = (conversationId: number) => {
        setExpandedConversation(expandedConversation === conversationId ? null : conversationId);
    };

    return (
        <div className={`fixed right-0 top-0 h-full w-80 bg-white border-l border-gray-200 
                        shadow-lg transform transition-transform duration-300 
                        dark:bg-gray-800 dark:border-gray-700
                        ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}>
            {/* Header */}
            <div className="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">AI Assistant</h2>
                <button
                    onClick={onClose}
                    className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                >
                    <XMarkIcon className="h-5 w-5" />
                </button>
            </div>

            {/* Main Content */}
            <div className="flex flex-col h-[calc(100%-8rem)]">
                {/* Conversation History */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {error && (
                        <div className="text-center text-red-500 dark:text-red-400 mb-4">
                            {error}
                        </div>
                    )}
                    {isLoading && conversations.length === 0 ? (
                        <div className="text-center text-gray-500 dark:text-gray-400">
                            Loading conversations...
                        </div>
                    ) : conversations.length === 0 ? (
                        <div className="text-center text-gray-500 dark:text-gray-400">
                            No conversations yet. Ask a question to get started!
                        </div>
                    ) : (
                        conversations.map((conversation) => (
                            <div key={conversation.id} className="border border-gray-200 rounded-lg dark:border-gray-700">
                                <button
                                    onClick={() => toggleConversation(conversation.id)}
                                    className="w-full flex justify-between items-center p-3 hover:bg-gray-50 dark:hover:bg-gray-700"
                                >
                                    <span className="text-sm text-gray-700 dark:text-gray-300">
                                        {conversation.messages[0]?.message.slice(0, 50)}...
                                    </span>
                                    {expandedConversation === conversation.id ? (
                                        <ChevronUpIcon className="h-4 w-4" />
                                    ) : (
                                        <ChevronDownIcon className="h-4 w-4" />
                                    )}
                                </button>
                                {expandedConversation === conversation.id && (
                                    <div className="p-3 border-t border-gray-200 dark:border-gray-700 space-y-2">
                                        {conversation.messages.map((message) => (
                                            <div
                                                key={message.id}
                                                className={`p-2 rounded-lg ${
                                                    message.role === 'user'
                                                        ? 'bg-blue-50 dark:bg-blue-900 ml-4'
                                                        : 'bg-gray-50 dark:bg-gray-700 mr-4'
                                                }`}
                                            >
                                                <p className="text-sm">{message.message}</p>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))
                    )}
                </div>

                {/* Query Input */}
                <div className="p-4 border-t border-gray-200 dark:border-gray-700">
                    <form onSubmit={handleSubmit} className="flex flex-col gap-2">
                        <textarea
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Ask me anything about this channel..."
                            className="w-full p-2 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                            rows={3}
                            disabled={isLoading}
                        />
                        <button
                            type="submit"
                            disabled={!query.trim() || isLoading}
                            className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isLoading ? 'Processing...' : 'Ask AI Assistant'}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
} 