import React, { useState, useEffect, useCallback } from 'react';
import { XMarkIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { useApi } from '@/hooks/useApi';
import type { Channel } from '../types/channel';
import ChannelCard from './ChannelCard';

interface ChannelListPopoutProps {
    isOpen: boolean;
    onClose: () => void;
    onChannelJoin: (channelId: number) => void;
}

export default function ChannelListPopout({ isOpen, onClose, onChannelJoin }: ChannelListPopoutProps) {
    const api = useApi();
    const [searchQuery, setSearchQuery] = useState('');
    const [channels, setChannels] = useState<Channel[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [joiningChannelId, setJoiningChannelId] = useState<number | null>(null);

    const fetchChannels = useCallback(async () => {
        setIsLoading(true);
        setError('');
        try {
            const response = await api.get('/channels/available');
            setChannels(response.data);
        } catch (error) {
            console.error('Failed to fetch available channels:', error);
            setError('Failed to load available channels');
        } finally {
            setIsLoading(false);
        }
    }, [api]);

    useEffect(() => {
        if (isOpen) {
            fetchChannels();
        }
    }, [isOpen, fetchChannels]);

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

    const filteredChannels = channels.filter(channel => 
        channel.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (channel.description?.toLowerCase().includes(searchQuery.toLowerCase()))
    );

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
                    <div className="relative mt-4">
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Search channels..."
                            className="w-full pl-10 pr-3 py-2 text-gray-900 bg-white rounded-md border border-gray-300 shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
                        />
                        <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                    </div>

                    {/* Channel List */}
                    <div className="mt-6 space-y-4 max-h-[60vh] overflow-y-auto">
                        {isLoading ? (
                            <div className="text-center text-gray-500">Loading channels...</div>
                        ) : error ? (
                            <div className="text-center text-red-500">{error}</div>
                        ) : filteredChannels.length === 0 ? (
                            <div className="text-center text-gray-500">
                                {searchQuery ? 'No channels found matching your search' : 'No channels available to join'}
                            </div>
                        ) : (
                            filteredChannels.map(channel => (
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