'use client';

import { useState } from 'react';
import Image from 'next/image';
import UserProfilePopout from './UserProfilePopout';

export type ConnectionStatus = 'connected' | 'idle' | 'away' | 'disconnected' | 'connecting';

interface User {
  id: number;
  email: string;
  name: string;
  picture?: string;
  bio?: string;
}

interface ProfileStatusProps {
  user: User;
  connectionStatus: ConnectionStatus;
  onProfileUpdate?: (updates: { name?: string; bio?: string }) => Promise<void>;
  onNavigateToDM?: (channelId: number) => void;
}

const getStatusColor = (status: ConnectionStatus): string => {
  switch (status) {
    case 'connected':
      return 'bg-green-500';
    case 'idle':
      return 'bg-yellow-500';
    case 'away':
      return 'bg-red-500';
    case 'disconnected':
    case 'connecting':
      return 'bg-gray-400';
    default:
      return 'bg-gray-400';
  }
};

const getStatusTitle = (status: ConnectionStatus): string => {
  switch (status) {
    case 'connected':
      return 'Active';
    case 'idle':
      return 'Idle';
    case 'away':
      return 'Away';
    case 'disconnected':
      return 'Offline';
    case 'connecting':
      return 'Connecting...';
    default:
      return 'Unknown';
  }
};

export default function ProfileStatus({ user, connectionStatus, onProfileUpdate, onNavigateToDM }: ProfileStatusProps) {
  const [showProfile, setShowProfile] = useState(false);
  const initial = user.name ? user.name[0].toUpperCase() : user.email[0].toUpperCase();

  return (
    <>
      <button 
        className="relative inline-block cursor-pointer hover:opacity-90 transition-opacity"
        onClick={() => setShowProfile(true)}
      >
        {/* Profile Circle */}
        {user.picture ? (
          <Image 
            src={user.picture} 
            alt={user.name} 
            width={36}
            height={36}
            className="rounded-full object-cover shadow-sm"
          />
        ) : (
          <div className="w-9 h-9 rounded-full bg-indigo-600 flex items-center justify-center text-white font-medium text-sm shadow-sm">
            {initial}
          </div>
        )}
        
        {/* Status Indicator */}
        <div 
          className={`absolute bottom-0 right-0 w-3.5 h-3.5 rounded-full border-2 border-white ${getStatusColor(connectionStatus)} shadow-sm`}
          title={`Status: ${getStatusTitle(connectionStatus)}`}
        />
      </button>

      {/* Profile Popout */}
      {showProfile && (
        <UserProfilePopout
          user={user}
          isCurrentUser={true}
          onClose={() => setShowProfile(false)}
          onUpdate={onProfileUpdate}
          onNavigateToDM={onNavigateToDM}
        />
      )}
    </>
  );
} 