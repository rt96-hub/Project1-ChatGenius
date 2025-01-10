import { useState } from 'react';
import { 
    LockClosedIcon, 
    HashtagIcon,
    UsersIcon,
    Cog6ToothIcon
} from '@heroicons/react/24/outline';
//import { useApi } from '@/hooks/useApi';
import ChannelSettingsModal from './ChannelSettingsModal';
import type { Channel, ChannelRole } from '../types/channel';

interface ChannelHeaderProps {
    channel: Channel;
    currentUserId: number;
    onChannelUpdate: () => void;
    onChannelDelete?: () => void;
    onUpdateMemberRole: (userId: number, role: ChannelRole) => void;
    onRemoveMember: (userId: number) => void;
    onGenerateInvite: () => void;
    onToggleMembers: () => void;
    showMembers: boolean;
}

export default function ChannelHeader({ 
    channel, 
    currentUserId, 
    onChannelUpdate,
    onChannelDelete,
    onUpdateMemberRole,
    onRemoveMember,
    onGenerateInvite,
    onToggleMembers,
    showMembers
}: ChannelHeaderProps) {
    const [showSettings, setShowSettings] = useState(false);
    const isOwner = channel.owner_id === currentUserId;

    return (
        <>
            <div className="border-b border-gray-200 bg-white p-4">
                <div className="flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <div className="flex items-center gap-2">
                            {channel.is_private ? (
                                <LockClosedIcon className="h-5 w-5 text-gray-400" />
                            ) : (
                                <HashtagIcon className="h-5 w-5 text-gray-400" />
                            )}
                            <h2 className="text-xl font-semibold text-gray-900">{channel.name}</h2>
                        </div>
                        <button
                            onClick={() => onToggleMembers()}
                            className="flex items-center gap-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md px-2 py-1"
                            title={showMembers ? "Hide Members" : "Show Members"}
                        >
                            <UsersIcon className="h-4 w-4" />
                            <span className="text-sm">{channel.member_count}</span>
                        </button>
                    </div>

                    <div className="flex items-center gap-2">
                        {isOwner && (
                            <button
                                onClick={() => setShowSettings(true)}
                                className="p-2 text-gray-500 hover:text-gray-700 rounded-full hover:bg-gray-100"
                                title="Channel Settings"
                            >
                                <Cog6ToothIcon className="h-5 w-5" />
                            </button>
                        )}
                    </div>
                </div>
                {channel.description && (
                    <p className="mt-1 text-gray-600 text-sm">{channel.description}</p>
                )}
            </div>

            <ChannelSettingsModal
                isOpen={showSettings}
                onClose={() => setShowSettings(false)}
                channel={channel}
                currentUserId={currentUserId}
                onUpdateChannel={onChannelUpdate}
                onUpdateMemberRole={onUpdateMemberRole}
                onRemoveMember={onRemoveMember}
                onGenerateInvite={onGenerateInvite}
                onDeleteChannel={onChannelDelete || (() => {})}
            />
        </>
    );
} 