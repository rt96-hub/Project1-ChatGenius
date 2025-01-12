import React, { useState, useEffect, useCallback } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { useApi } from '@/hooks/useApi';
import type { Channel } from '../types/channel';
import ChannelCard from './ChannelCard';
import { SearchInput } from './SearchInput';
import { useSearch } from '@/hooks/useSearch';
import { useSearchApi } from '@/lib/api/search';

interface ChannelListPopoutProps {
    isOpen: boolean;
    onClose: () => void;
    onChannelJoin: (channelId: number) => void;
}

export default function ChannelListPopout({ isOpen, onClose, onChannelJoin }: ChannelListPopoutProps) {
    const api = useApi();
    const searchApi = useSearchApi();
    const [baseChannels, setBaseChannels] = useState<Channel[]>([]);
    const [joiningChannelId, setJoiningChannelId] = useState<number | null>(null);
    const [error, setError] = useState('');

    const { query, setQuery, results: searchResults, isLoading: isSearching } = useSearch<Channel[]>({
        searchFn: async (query) => {
            const response = await searchApi.searchChannels({ 
                query,
                is_dm: false,
                include_private: false
            });
            return response.channels;
        },
        debounceMs: 300
    });

    const fetchChannels = useCallback(async () => {
        setError('');
        try {
            const response = await api.get('/channels/available');
            setBaseChannels(response.data);
        } catch (error) {
            console.error('Failed to fetch available channels:', error);
            setError('Failed to load available channels');
        }
    }, [api]);

    useEffect(() => {
        if (isOpen) {
            fetchChannels();
            setQuery(''); // Reset search when opening
        }
    }, [isOpen, fetchChannels, setQuery]);

    const handleJoinChannel = async (channelId: number) => {
        setJoiningChannelId(channelId);
        setError('');
        try {
            await api.post(`/channels/${channelId}/join`);
            onChannelJoin(channelId);
            onClose();
        } catch (error) {
            console.error('Failed to join channel:', error);
            setError('Failed to join channel');
        } finally {
            setJoiningChannelId(null);
        }
    };

    // Use search results if there's a query, otherwise use base channels
    const displayedChannels = query ? (searchResults || []) : baseChannels;

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 overflow-y-auto">
            {/* Backdrop */}
            <div 
                className="fixed inset-0 bg-black bg-opacity-25 transition-opacity"
                onClick={onClose}
            />

            {/* Dialog */}
            <div className="flex min-h-full items-center justify-center p-4 text-center">
                <div 
                    className="relative w-full max-w-2xl transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all"
                    onClick={e => e.stopPropagation()}
                >
                    <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                        <button
                            type="button"
                            className="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                            onClick={onClose}
                        >
                            <span className="sr-only">Close</span>
                            <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                        </button>
                    </div>

                    <h3 className="text-lg font-medium leading-6 text-gray-900">
                        Browse Channels
                    </h3>

                    {/* Search Bar */}
                    <div className="mt-4">
                        <SearchInput
                            value={query}
                            onChange={setQuery}
                            placeholder="Search channels..."
                            isLoading={isSearching}
                        />
                    </div>

                    {/* Channel List */}
                    <div className="mt-6 space-y-4 max-h-[60vh] overflow-y-auto">
                        {isSearching ? (
                            <div className="text-center text-gray-500">Searching channels...</div>
                        ) : error ? (
                            <div className="text-center text-red-500">{error}</div>
                        ) : displayedChannels.length === 0 ? (
                            <div className="text-center text-gray-500">
                                {query ? 'No channels found matching your search' : 'No channels available to join'}
                            </div>
                        ) : (
                            displayedChannels.map(channel => (
                                <ChannelCard
                                    key={channel.id}
                                    channel={channel}
                                    onJoin={handleJoinChannel}
                                    isJoining={joiningChannelId === channel.id}
                                />
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
} 