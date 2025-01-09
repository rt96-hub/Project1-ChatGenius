import React, { useState } from 'react';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { useApi } from '@/hooks/useApi';
import type { Channel } from '../types/channel';

interface ViewDMsModalProps {
    isOpen: boolean;
    onClose: () => void;
    onDMSelect: (channelId: number) => void;
    currentUserId: number;
    dmChannels: Channel[];
}

export default function ViewDMsModal({ isOpen, onClose, onDMSelect, currentUserId, dmChannels }: ViewDMsModalProps) {
    const [searchQuery, setSearchQuery] = useState('');

    // Sort channels by last message date
    const sortedChannels = [...dmChannels].sort((a, b) => {
        const aLastMessage = a.messages.length > 0 ? new Date(a.messages[a.messages.length - 1].created_at).getTime() : 0;
        const bLastMessage = b.messages.length > 0 ? new Date(b.messages[b.messages.length - 1].created_at).getTime() : 0;
        return bLastMessage - aLastMessage; // Most recent first
    });

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
                <h2 className="text-xl font-bold mb-4 text-gray-900">Direct Messages</h2>
                
                {/* Search Bar */}
                <div className="relative mb-4">
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search direct messages..."
                        className="w-full pl-10 pr-3 py-2 text-gray-900 bg-white rounded-md border border-gray-300 shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
                    />
                    <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                </div>

                {/* DM List */}
                <div className="max-h-96 overflow-y-auto">
                    <ul className="space-y-2">
                        {sortedChannels.map((channel) => (
                            <li key={channel.id}>
                                <button
                                    onClick={() => {
                                        onDMSelect(channel.id);
                                        onClose();
                                    }}
                                    className="w-full text-left px-4 py-3 rounded-md hover:bg-gray-100 transition-colors flex items-center gap-3"
                                >
                                    <div className="flex-1">
                                        <span className="font-medium text-gray-900">
                                            {channel.users
                                                .filter(user => user.id !== currentUserId)
                                                .map(user => user.name)
                                                .join(', ')}
                                        </span>
                                        <p className="text-xs text-gray-400">
                                            Last message: {channel.messages.length > 0 
                                                ? new Date(channel.messages[channel.messages.length - 1].created_at).toLocaleString() 
                                                : 'No messages'}
                                        </p>
                                    </div>
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Footer */}
                <div className="flex justify-end gap-2 pt-4 mt-4 border-t border-gray-200">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
} 