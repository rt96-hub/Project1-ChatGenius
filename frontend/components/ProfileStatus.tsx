'use client';

import { useEffect, useState } from 'react';

export type ConnectionStatus = 'connected' | 'idle' | 'away' | 'disconnected';

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
      return 'bg-gray-400';
    default:
      return 'bg-gray-400';
  }
};

export default function ProfileStatus({ email, connectionStatus }: ProfileStatusProps) {
  // Get first letter of email for avatar
  const initial = email ? email[0].toUpperCase() : '?';

  return (
    <div className="relative inline-block">
      {/* Profile Circle */}
      <div className="w-9 h-9 rounded-full bg-indigo-600 flex items-center justify-center text-white font-medium text-sm shadow-sm">
        {initial}
      </div>
      
      {/* Status Indicator */}
      <div 
        className={`absolute bottom-0 right-0 w-3.5 h-3.5 rounded-full border-2 border-white ${getStatusColor(connectionStatus)} shadow-sm`}
        title={`Status: ${connectionStatus}`}
      />
    </div>
  );
} 