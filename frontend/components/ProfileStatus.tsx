'use client';

import { useEffect, useState } from 'react';

export type ConnectionStatus = 'connected' | 'idle' | 'away' | 'disconnected' | 'connecting';

interface ProfileStatusProps {
  email: string;
  connectionStatus: ConnectionStatus;
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

export default function ProfileStatus({ email, connectionStatus }: ProfileStatusProps) {
  // Get first letter of email for avatar
  const initial = email ? email[0].toUpperCase() : '?';

  return (
    <button className="relative inline-block cursor-pointer hover:opacity-90 transition-opacity">
      {/* Profile Circle */}
      <div className="w-9 h-9 rounded-full bg-indigo-600 flex items-center justify-center text-white font-medium text-sm shadow-sm">
        {initial}
      </div>
      
      {/* Status Indicator */}
      <div 
        className={`absolute bottom-0 right-0 w-3.5 h-3.5 rounded-full border-2 border-white ${getStatusColor(connectionStatus)} shadow-sm`}
        title={`Status: ${getStatusTitle(connectionStatus)}`}
      />
    </button>
  );
} 