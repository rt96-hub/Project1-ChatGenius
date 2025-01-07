'use client';

import { useState, useCallback } from 'react';
import Header from '../components/Header'
import Sidebar from '../components/Sidebar'
import ChatArea from '../components/ChatArea'

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
    <div className="flex flex-col h-screen w-full">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar 
          onChannelSelect={handleChannelSelect} 
          refreshTrigger={refreshChannelList}
        />
        <ChatArea 
          channelId={selectedChannelId} 
          onChannelUpdate={handleChannelUpdate}
          onChannelDelete={handleChannelDelete}
        />
      </div>
    </div>
  )
} 