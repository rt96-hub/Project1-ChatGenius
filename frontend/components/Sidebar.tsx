import { useState, useEffect, useCallback } from 'react';
import { 
    HashtagIcon, 
    PlusIcon, 
    LockClosedIcon,
    ChatBubbleLeftRightIcon,
    ListBulletIcon,
    MagnifyingGlassIcon,
    SparklesIcon
} from '@heroicons/react/24/outline';
import { useApi } from '@/hooks/useApi';
import { useAuth } from '@/hooks/useAuth';
import CreateChannelModal from './CreateChannelModal';
import ViewDMsModal from './ViewDMsModal';
import NewDMModal from './NewDMModal';
import { useConnection } from '@/contexts/ConnectionContext';
import type { Channel } from '../types/channel';
import ChannelListPopout from './ChannelListPopout';

interface SidebarProps {
    onChannelSelect: (channelId: number) => void;
    refreshTrigger: number;
}

export default function Sidebar({ onChannelSelect, refreshTrigger }: SidebarProps) {
    const api = useApi();
    const { user } = useAuth();
    const [channels, setChannels] = useState<Channel[]>([]);
    const [dmChannels, setDmChannels] = useState<Channel[]>([]);
    const [aiChannel, setAiChannel] = useState<Channel | null>(null);
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [isViewDMsModalOpen, setIsViewDMsModalOpen] = useState(false);
    const [isNewDMModalOpen, setIsNewDMModalOpen] = useState(false);
    const [selectedChannelId, setSelectedChannelId] = useState<number | null>(null);
    const { addMessageListener } = useConnection();
    const currentUserId = user?.id;
    const [isChannelListOpen, setIsChannelListOpen] = useState(false);

    const fetchChannels = useCallback(async () => {
        try {
            const response = await api.get('/channels/me');
            const allChannels = response.data;
            setChannels(allChannels.filter((ch: Channel) => !ch.is_dm));
        } catch (error) {
            console.error('Failed to fetch channels:', error);
        }
    }, [api]);

    const fetchDmChannels = useCallback(async () => {
        try {
            const response = await api.get('/channels/me/dms?limit=5');
            setDmChannels(response.data);
        } catch (error) {
            console.error('Failed to fetch DM channels:', error);
        }
    }, [api]);

    const fetchAiChannel = useCallback(async () => {
        try {
            const response = await api.get('/channels/me/ai-dm');
            setAiChannel(response.data);
        } catch (error) {
            console.error('Failed to fetch AI channel:', error);
        }
    }, [api]);

    useEffect(() => {
        fetchChannels();
        fetchDmChannels();
        fetchAiChannel();
        
        const removeListener = addMessageListener((data) => {
            if (data.type === 'channel_update') {
                if (data.channel.ai_channel) {
                    setAiChannel(data.channel);
                } else if (data.channel.is_dm) {
                    setDmChannels(prevDms => 
                        prevDms.map(dm => 
                            dm.id === data.channel.id 
                                ? { ...dm, ...data.channel }
                                : dm
                        )
                    );
                } else {
                    setChannels(prevChannels => 
                        prevChannels.map(ch => 
                            ch.id === data.channel.id 
                                ? { ...ch, ...data.channel }
                                : ch
                        )
                    );
                }
            } else if (data.type === 'channel_created' && data.channel.is_dm) {
                setDmChannels(prevDms => {
                    const exists = prevDms.some(dm => dm.id === data.channel.id);
                    if (exists) return prevDms;
                    
                    return [data.channel, ...prevDms].slice(0, 5);
                });
            }
        });

        return () => {
            removeListener();
        };
    }, [refreshTrigger, addMessageListener, fetchChannels, fetchDmChannels, fetchAiChannel]);

    const handleChannelSelect = (channelId: number) => {
        setSelectedChannelId(channelId);
        onChannelSelect(channelId);
    };

    const handleChannelCreated = async (channelId: number) => {
        await fetchChannels();
        handleChannelSelect(channelId);
    };

    const getRoleBadge = (role?: string) => {
        if (!role || role === 'member') return null;
        
        return (
            <span className="ml-auto text-xs font-medium px-1.5 py-0.5 rounded-full bg-gray-700 text-gray-300">
                {role}
            </span>
        );
    };

    const handleDMCreated = async (channelId: number) => {
        await fetchDmChannels();
        handleChannelSelect(channelId);
    };

    const handleChannelJoined = async (channelId: number) => {
        await fetchChannels();
        handleChannelSelect(channelId);
    };

    return (
        <aside className="w-64 flex-none bg-gray-800 text-white flex flex-col h-full overflow-hidden">
            <div className="p-4 border-b border-gray-700 flex-none">
                <h2 className="text-xl font-bold">Workspace</h2>
            </div>
            
            <div className="flex-1 overflow-y-auto">
                {aiChannel && (
                    <div className="px-4 mb-6 mt-4">
                        <h3 className="text-gray-400 text-sm font-medium uppercase tracking-wide mb-2">AI Assistant</h3>
                        <button
                            onClick={() => handleChannelSelect(aiChannel.id)}
                            className={`flex items-center gap-2 w-full px-2 py-1.5 rounded transition-colors ${
                                selectedChannelId === aiChannel.id ? 'bg-gray-700' : 'hover:bg-gray-700'
                            }`}
                        >
                            <SparklesIcon className="h-4 w-4 flex-none" />
                            <span className="truncate">AI Assistant</span>
                        </button>
                    </div>
                )}

                <div className="px-4 mb-6">
                    <div className="flex justify-between items-center mb-2">
                        <h3 className="text-gray-400 text-sm font-medium uppercase tracking-wide">Channels</h3>
                        <div className="flex gap-1">
                            <button
                                onClick={() => setIsChannelListOpen(true)}
                                className="text-gray-400 hover:text-white transition-colors"
                                title="Browse Channels"
                            >
                                <MagnifyingGlassIcon className="h-5 w-5" />
                            </button>
                            <button
                                onClick={() => setIsCreateModalOpen(true)}
                                className="text-gray-400 hover:text-white transition-colors"
                                title="Create Channel"
                            >
                                <PlusIcon className="h-5 w-5" />
                            </button>
                        </div>
                    </div>
                    <ul className="space-y-1">
                        {channels.map((channel) => (
                            <li key={channel.id}>
                                <button
                                    onClick={() => handleChannelSelect(channel.id)}
                                    className={`flex items-center gap-2 w-full px-2 py-1.5 rounded transition-colors ${
                                        selectedChannelId === channel.id ? 'bg-gray-700' : 'hover:bg-gray-700'
                                    }`}
                                >
                                    {channel.is_private ? (
                                        <LockClosedIcon className="h-4 w-4 flex-none" />
                                    ) : (
                                        <HashtagIcon className="h-4 w-4 flex-none" />
                                    )}
                                    <span className="truncate">{channel.name}</span>
                                    {getRoleBadge(channel.role)}
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>

                <div className="px-4">
                    <div className="flex justify-between items-center mb-2">
                        <h3 className="text-gray-400 text-sm font-medium uppercase tracking-wide">Direct Messages</h3>
                        <div className="flex gap-1">
                            <button
                                onClick={() => setIsViewDMsModalOpen(true)}
                                className="text-gray-400 hover:text-white transition-colors"
                                title="View All DMs"
                            >
                                <ListBulletIcon className="h-5 w-5" />
                            </button>
                            <button
                                onClick={() => setIsNewDMModalOpen(true)}
                                className="text-gray-400 hover:text-white transition-colors"
                                title="New Direct Message"
                            >
                                <PlusIcon className="h-5 w-5" />
                            </button>
                        </div>
                    </div>
                    <ul className="space-y-1">
                        {dmChannels.map((channel) => (
                            <li key={channel.id}>
                                <button
                                    onClick={() => handleChannelSelect(channel.id)}
                                    className={`flex items-center gap-2 w-full px-2 py-1.5 rounded transition-colors ${
                                        selectedChannelId === channel.id ? 'bg-gray-700' : 'hover:bg-gray-700'
                                    }`}
                                >
                                    <ChatBubbleLeftRightIcon className="h-4 w-4 flex-none" />
                                    <span className="truncate">
                                        {(() => {
                                            const currentUserEmail = user?.email;
                                            const otherUser = channel.users.find(u => 
                                                (currentUserId && u.id !== currentUserId) || 
                                                (currentUserEmail && u.email !== currentUserEmail)
                                            );
                                            return otherUser?.name || 'Unknown User';
                                        })()}
                                    </span>
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            <CreateChannelModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                onChannelCreated={handleChannelCreated}
            />

            <ChannelListPopout
                isOpen={isChannelListOpen}
                onClose={() => setIsChannelListOpen(false)}
                onChannelJoin={handleChannelJoined}
            />

            <ViewDMsModal
                isOpen={isViewDMsModalOpen}
                onClose={() => setIsViewDMsModalOpen(false)}
                onDMSelect={handleChannelSelect}
                currentUserId={currentUserId || 0}
                dmChannels={dmChannels}
            />

            <NewDMModal
                isOpen={isNewDMModalOpen}
                onClose={() => setIsNewDMModalOpen(false)}
                onDMCreated={handleDMCreated}
            />
        </aside>
    );
} 