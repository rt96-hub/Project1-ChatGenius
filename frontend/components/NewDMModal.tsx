import React, { useState, useEffect } from 'react';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { useApi } from '@/hooks/useApi';

interface User {
    id: number;
    email: string;
    name: string;
    picture?: string;
    bio?: string;
}

interface UserWithLastDM {
    user: User;
    last_dm_at: string | null;
    channel_id: number | null;
}

interface NewDMModalProps {
    isOpen: boolean;
    onClose: () => void;
    onDMCreated: (channelId: number) => void;
}

export default function NewDMModal({ isOpen, onClose, onDMCreated }: NewDMModalProps) {
    const api = useApi();
    const [searchQuery, setSearchQuery] = useState('');
    const [users, setUsers] = useState<UserWithLastDM[]>([]);
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (isOpen) {
            fetchUsers();
        }
    }, [isOpen]);

    const fetchUsers = async () => {
        setIsLoading(true);
        try {
            const response = await api.get('/users/by-last-dm');
            setUsers(response.data);
            setError('');
        } catch (error) {
            console.error('Failed to fetch users:', error);
            setError('Failed to load users');
        } finally {
            setIsLoading(false);
        }
    };

    const handleDMAction = async (userId: number, existingChannelId: number | null) => {
        try {
            if (existingChannelId) {
                // If there's an existing channel, just open it
                onDMCreated(existingChannelId);
                onClose();
            } else {
                // Create new DM channel if none exists
                const response = await api.post('/channels/dm', {
                    user_ids: [userId]
                });
                onDMCreated(response.data.id);
                onClose();
            }
        } catch (error) {
            console.error('Failed to handle DM action:', error);
            setError('Failed to handle DM action');
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
                <h2 className="text-xl font-bold mb-4 text-gray-900">New Direct Message</h2>
                
                {/* Search Bar */}
                <div className="relative mb-4">
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search users..."
                        className="w-full pl-10 pr-3 py-2 text-gray-900 bg-white rounded-md border border-gray-300 shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
                    />
                    <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                </div>

                {/* Users List */}
                <div className="max-h-96 overflow-y-auto">
                    {isLoading ? (
                        <div className="text-center py-4 text-gray-500">Loading users...</div>
                    ) : error ? (
                        <div className="text-center py-4 text-red-500">{error}</div>
                    ) : (
                        <ul className="space-y-2">
                            {users.map(({ user, last_dm_at, channel_id }) => (
                                <li key={user.id}>
                                    <button
                                        onClick={() => handleDMAction(user.id, channel_id)}
                                        className="w-full text-left px-4 py-3 rounded-md hover:bg-gray-100 transition-colors flex items-center gap-3"
                                    >
                                        {user.picture && (
                                            <img
                                                src={user.picture}
                                                alt={user.name}
                                                className="w-8 h-8 rounded-full"
                                            />
                                        )}
                                        <div className="flex-1">
                                            <span className="font-medium text-gray-900">{user.name}</span>
                                            <p className="text-sm text-gray-500">{user.email}</p>
                                            <p className="text-xs text-gray-400">
                                                Last message: {last_dm_at ? new Date(last_dm_at).toLocaleString() : 'Never'}
                                            </p>
                                        </div>
                                    </button>
                                </li>
                            ))}
                        </ul>
                    )}
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