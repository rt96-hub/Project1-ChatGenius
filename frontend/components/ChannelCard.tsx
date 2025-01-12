import React from 'react';
import { HashtagIcon, LockClosedIcon, UserGroupIcon } from '@heroicons/react/24/outline';
import type { Channel } from '../types/channel';

interface ChannelCardProps {
    channel: Channel;
    onJoin: (channelId: number) => void;
    isJoining?: boolean;
}

export default function ChannelCard({ channel, onJoin, isJoining = false }: ChannelCardProps) {
    return (
        <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                    {channel.is_private ? (
                        <LockClosedIcon className="h-5 w-5 text-gray-500" />
                    ) : (
                        <HashtagIcon className="h-5 w-5 text-gray-500" />
                    )}
                    <div>
                        <h3 className="font-medium text-gray-900">{channel.name}</h3>
                        {channel.description && (
                            <p className="text-sm text-gray-500 mt-1">{channel.description}</p>
                        )}
                    </div>
                </div>
                <button
                    onClick={() => onJoin(channel.id)}
                    disabled={isJoining}
                    className="ml-4 px-3 py-1.5 text-sm font-medium text-white bg-blue-500 hover:bg-blue-600 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {isJoining ? 'Joining...' : 'Join'}
                </button>
            </div>
            <div className="flex items-center gap-1 mt-3 text-sm text-gray-500">
                <UserGroupIcon className="h-4 w-4" />
                <span>{channel.users.length} members</span>
            </div>
        </div>
    );
} 