import React, { useState, useEffect, useCallback } from 'react';
import Image from 'next/image';
import { useApi } from '@/hooks/useApi';
import { SearchInput } from './SearchInput';
import { useSearch } from '@/hooks/useSearch';
import { useSearchApi } from '@/lib/api/search';
import type { User } from '@/types/user';

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
    const searchApi = useSearchApi();
    const [baseUsers, setBaseUsers] = useState<UserWithLastDM[]>([]);
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const { query, setQuery, results: searchResults, isLoading: isSearching } = useSearch<UserWithLastDM[]>({
        searchFn: async (query) => {
            const response = await searchApi.searchUsers({ query });
            // Transform search results to match UserWithLastDM format
            const usersWithDM = response.users.map((user: User) => ({
                user,
                last_dm_at: null,
                channel_id: null
            }));
            return usersWithDM;
        },
        debounceMs: 300
    });

    const fetchUsers = useCallback(async () => {
        setIsLoading(true);
        try {
            const response = await api.get('/users/by-last-dm');
            setBaseUsers(response.data);
            setError('');
        } catch (error) {
            console.error('Failed to fetch users:', error);
            setError('Failed to load users');
        } finally {
            setIsLoading(false);
        }
    }, [api]);

    useEffect(() => {
        if (isOpen) {
            fetchUsers();
            setQuery(''); // Reset search when opening
        }
    }, [isOpen, fetchUsers, setQuery]);

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

    // Use search results if there's a query, otherwise use base users
    const displayedUsers = query ? (searchResults || []) : baseUsers;

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
                <h2 className="text-xl font-bold mb-4 text-gray-900">New Direct Message</h2>
                
                {/* Search Bar */}
                <div className="mb-4">
                    <SearchInput
                        value={query}
                        onChange={setQuery}
                        placeholder="Search users..."
                        isLoading={isSearching}
                    />
                </div>

                {/* Users List */}
                <div className="max-h-96 overflow-y-auto">
                    {(isLoading || isSearching) ? (
                        <div className="text-center py-4 text-gray-500">
                            {isSearching ? 'Searching users...' : 'Loading users...'}
                        </div>
                    ) : error ? (
                        <div className="text-center py-4 text-red-500">{error}</div>
                    ) : displayedUsers.length === 0 ? (
                        <div className="text-center py-4 text-gray-500">
                            {query ? 'No users found matching your search' : 'No users available'}
                        </div>
                    ) : (
                        <ul className="space-y-2">
                            {displayedUsers.map(({ user, last_dm_at, channel_id }) => (
                                <li key={user.id}>
                                    <button
                                        onClick={() => handleDMAction(user.id, channel_id)}
                                        className="w-full text-left px-4 py-3 rounded-md hover:bg-gray-100 transition-colors flex items-center gap-3"
                                    >
                                        {user.picture && (
                                            <Image
                                                src={user.picture}
                                                alt={user.name}
                                                width={32}
                                                height={32}
                                                className="rounded-full"
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