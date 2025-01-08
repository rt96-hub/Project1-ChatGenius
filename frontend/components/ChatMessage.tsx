import { useState } from 'react';
import { PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import { useApi } from '@/hooks/useApi';

interface User {
  id: number;
  email: string;
  name?: string;
}

interface Message {
  id: number;
  content: string;
  created_at: string;
  updated_at: string;
  user_id: number;
  channel_id: number;
  user?: User;
}

interface ChatMessageProps {
  message: Message;
  currentUserId: number;
  channelId: number;
  onMessageUpdate: (updatedMessage: Message) => void;
  onMessageDelete: (messageId: number) => void;
}

export default function ChatMessage({ message, currentUserId, channelId, onMessageUpdate, onMessageDelete }: ChatMessageProps) {
  const api = useApi();
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(message.content);
  const [isHovered, setIsHovered] = useState(false);
  const isOwner = message.user_id === currentUserId;

  const handleEdit = async () => {
    try {
      const response = await api.put(`/channels/${channelId}/messages/${message.id}`, {
        content: editContent
      });
      onMessageUpdate(response.data);
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to edit message:', error);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this message?')) return;
    
    try {
      await api.delete(`/channels/${channelId}/messages/${message.id}`);
      onMessageDelete(message.id);
    } catch (error) {
      console.error('Failed to delete message:', error);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleEdit();
    } else if (e.key === 'Escape') {
      setIsEditing(false);
      setEditContent(message.content);
    }
  };

  return (
    <div 
      className="flex items-start gap-3 group relative px-2 py-1 -mx-2 rounded-md hover:bg-gray-100 transition-colors"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="w-8 h-8 rounded-full bg-gray-300 flex-none" />
      <div className="min-w-0 flex-1">
        <div className="flex items-baseline gap-2">
          <span className="font-medium truncate">
            {message.user?.email || 'Unknown User'}
          </span>
          <span className="text-xs text-gray-500 flex-none">
            {new Date(message.created_at).toLocaleTimeString()}
            {message.updated_at && message.updated_at !== message.created_at && (
              <span className="ml-1 italic">
                (edited {new Date(message.updated_at).toLocaleTimeString()})
              </span>
            )}
          </span>
        </div>
        {isEditing ? (
          <div className="mt-1">
            <textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[60px] resize-none"
              autoFocus
            />
            <div className="flex gap-2 mt-2">
              <button
                onClick={handleEdit}
                className="px-3 py-1 text-sm bg-blue-500 text-white rounded-md hover:bg-blue-600"
              >
                Save
              </button>
              <button
                onClick={() => {
                  setIsEditing(false);
                  setEditContent(message.content);
                }}
                className="px-3 py-1 text-sm bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <p className="text-gray-800 break-words">{message.content}</p>
        )}
      </div>
      
      {/* Edit/Delete buttons */}
      {isOwner && isHovered && !isEditing && (
        <div className="absolute top-0 right-0 flex gap-1 bg-white shadow-sm border border-gray-100 rounded-md">
          <button
            onClick={() => {
              setIsEditing(true);
              setEditContent(message.content);
            }}
            className="p-1 text-gray-500 hover:text-blue-600 hover:bg-gray-50"
            title="Edit message"
          >
            <PencilIcon className="h-4 w-4" />
          </button>
          <button
            onClick={handleDelete}
            className="p-1 text-gray-500 hover:text-red-600 hover:bg-gray-50"
            title="Delete message"
          >
            <TrashIcon className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
} 