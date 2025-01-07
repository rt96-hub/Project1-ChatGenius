import { useState, useEffect } from 'react';
import { HashtagIcon, PlusIcon, UserGroupIcon } from '@heroicons/react/24/outline';
import { useApi } from '@/hooks/useApi';
import CreateChannelModal from './CreateChannelModal';
import { useConnection } from '@/contexts/ConnectionContext';

interface Channel {
  id: number;
  name: string;
  description: string | null;
  owner_id: number;
}

interface SidebarProps {
  onChannelSelect: (channelId: number) => void;
  refreshTrigger: number;
}

export default function Sidebar({ onChannelSelect, refreshTrigger }: SidebarProps) {
  const api = useApi();
  const [channels, setChannels] = useState<Channel[]>([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedChannelId, setSelectedChannelId] = useState<number | null>(null);
  const { connectionStatus, addMessageListener } = useConnection();

  const fetchChannels = async () => {
    try {
      const response = await api.get('/channels/me');
      setChannels(response.data);
    } catch (error) {
      console.error('Failed to fetch channels:', error);
    }
  };

  useEffect(() => {
    fetchChannels();
    
    // Set up WebSocket message listener for channel updates
    const removeListener = addMessageListener((data) => {
      if (data.type === 'channel_update') {
        setChannels(prevChannels => 
          prevChannels.map(ch => 
            ch.id === data.channel.id 
              ? { ...ch, name: data.channel.name }
              : ch
          )
        );
      }
    });

    return () => {
      removeListener();
    };
  }, [refreshTrigger]);

  const handleChannelSelect = (channelId: number) => {
    setSelectedChannelId(channelId);
    onChannelSelect(channelId);
  };

  const handleChannelCreated = async (channelId: number) => {
    await fetchChannels();
    handleChannelSelect(channelId);
  };

  return (
    <aside className="w-64 flex-none bg-gray-800 text-white flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-gray-700 flex-none">
        <h2 className="text-xl font-bold">Workspace</h2>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        <div className="px-4 mb-6 mt-4">
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-gray-400 text-sm font-medium uppercase tracking-wide">Channels</h3>
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="text-gray-400 hover:text-white transition-colors"
              title="Create Channel"
            >
              <PlusIcon className="h-5 w-5" />
            </button>
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
                  <HashtagIcon className="h-4 w-4 flex-none" />
                  <span className="truncate">{channel.name}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="px-4">
          <h3 className="text-gray-400 text-sm font-medium mb-2 uppercase tracking-wide">Direct Messages</h3>
          <ul className="space-y-1">
            {['John Doe', 'Jane Smith', 'Team Lead'].map((user) => (
              <li key={user}>
                <button className="flex items-center gap-2 w-full px-2 py-1.5 rounded hover:bg-gray-700 transition-colors">
                  <UserGroupIcon className="h-4 w-4 flex-none" />
                  <span className="truncate">{user}</span>
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
    </aside>
  );
} 