'use client';

import { useState, useCallback } from 'react';
import Header from '../components/Header'
import Sidebar from '../components/Sidebar'
import ChatArea from '../components/ChatArea'
import { ProtectedRoute } from '@/components/ProtectedRoute';

export default function Home() {
  const [selectedChannelId, setSelectedChannelId] = useState<number | null>(null);
  const [refreshChannelList, setRefreshChannelList] = useState(0);

  const handleChannelSelect = (channelId: number) => {
    setSelectedChannelId(channelId);
  };

  const handleChannelUpdate = useCallback(() => {
    setRefreshChannelList(prev => prev + 1); // Trigger a refresh
  }, []);

  const handleChannelDelete = useCallback(() => {
    setSelectedChannelId(null); // Clear selected channel
    setRefreshChannelList(prev => prev + 1); // Refresh channel list
  }, []);

  return (
    <ProtectedRoute>
      <div className="flex flex-col h-screen w-full overflow-hidden">
        <Header />
        <div className="flex flex-1 overflow-hidden">
          <div className="flex-none w-64">
            <Sidebar 
              onChannelSelect={handleChannelSelect} 
              refreshTrigger={refreshChannelList}
            />
          </div>
          <div className="flex-1 overflow-hidden">
            <ChatArea 
              channelId={selectedChannelId} 
              onChannelUpdate={handleChannelUpdate}
              onChannelDelete={handleChannelDelete}
            />
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
} 