import { useState, useRef, useCallback, useEffect } from 'react';
import { PencilIcon, TrashIcon, FaceSmileIcon, ArrowUturnLeftIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';
import Image from 'next/image';
import { useApi } from '@/hooks/useApi';
import UserProfilePopout from './UserProfilePopout';
import EmojiSelector from './EmojiSelector';
import { MessageAttachment } from './file/MessageAttachment';

interface User {
  id: number;
  email: string;
  name: string;
  picture?: string;
  bio?: string;
}

interface Reaction {
  id: number;
  message_id: number;
  reaction_id: number;
  user_id: number;
  created_at: string;
  code?: string;
  reaction: {
    id: number;
    code: string;
    is_system: boolean;
    image_url: string | null;
  };
  user: User;
}

interface Message {
  id: number;
  content: string;
  created_at: string;
  updated_at?: string;
  user_id: number;
  channel_id: number;
  parent_id: number | null;
  parent?: Message | null;
  has_replies?: boolean;
  user?: User;
  reactions?: Reaction[];
  files?: Array<{
    id: number;
    message_id: number;
    file_name: string;
    content_type: string;
    file_size: number;
    uploaded_at: string;
    uploaded_by: number;
  }>;
}

interface ChatMessageProps {
  message: Message;
  currentUserId: number;
  channelId: number;
  onMessageUpdate: (updatedMessage: Message) => void;
  onMessageDelete: (messageId: number) => void;
  onNavigateToDM?: (channelId: number) => void;
  onReply?: (parentMessage: Message) => void;
}

export default function ChatMessage({ message, currentUserId, channelId, onMessageUpdate, onMessageDelete, onNavigateToDM, onReply }: ChatMessageProps) {
  const api = useApi();
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(message.content);
  const [isHovered, setIsHovered] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [showEmojiSelector, setShowEmojiSelector] = useState(false);
  const [showReplies, setShowReplies] = useState(false);
  const [replies, setReplies] = useState<Message[]>([]);
  const [isLoadingReplies, setIsLoadingReplies] = useState(false);
  const messageRef = useRef<HTMLDivElement>(null);
  const isOwner = message.user_id === currentUserId;

  // Add useEffect to update replies when message is updated
  useEffect(() => {
    // Only update replies if the reply chain is open and this is a root message
    if (showReplies && message.parent_id === null && message.has_replies) {
      const fetchReplies = async () => {
        try {
          const response = await api.get(`/messages/${message.id}/reply-chain`);
          // Filter out the root message since we're already displaying it
          const replyChain = response.data.filter((m: Message) => m.id !== message.id);
          setReplies(replyChain);
        } catch (error) {
          console.error('Failed to fetch reply chain:', error);
        }
      };
      fetchReplies();
    }
  }, [message, showReplies, api]);

  // Memoize the handlers
  const handleAddReaction = useCallback(async (reactionId: number) => {
    try {
      // Check if user has already reacted with this emoji
      const existingReaction = message.reactions?.find(
        r => r.reaction_id === reactionId && r.user_id === currentUserId
      );
      
      if (existingReaction) {
        // If user has already reacted with this emoji, don't do anything
        setShowEmojiSelector(false);
        return;
      }

      const response = await api.post(`/channels/${channelId}/messages/${message.id}/reactions`, {
        reaction_id: reactionId
      });
      
      const updatedMessage = {
        ...message,
        reactions: [...(message.reactions || []), response.data]
      };
      onMessageUpdate(updatedMessage);
      setShowEmojiSelector(false);
    } catch (error) {
      console.error('Failed to add reaction:', error);
    }
  }, [api, channelId, message, onMessageUpdate, currentUserId]);

  const handleRemoveReaction = useCallback(async (reactionId: number) => {
    try {
      await api.delete(`/channels/${channelId}/messages/${message.id}/reactions/${reactionId}`);
      
      const updatedMessage = {
        ...message,
        reactions: (message.reactions || []).filter(r => 
          // Keep reactions that either have a different reaction_id OR are from a different user
          r.reaction_id !== reactionId || r.user_id !== currentUserId
        )
      };
      onMessageUpdate(updatedMessage);
    } catch (error) {
      console.error('Failed to remove reaction:', error);
    }
  }, [api, channelId, message, onMessageUpdate, currentUserId]);

  const handleEmojiSelectorClose = useCallback(() => {
    setShowEmojiSelector(false);
  }, []);

  const getEmojiSelectorPosition = () => {
    if (!messageRef.current) return { top: 0, left: 0 };
    const buttonRect = messageRef.current.querySelector('button[title="Add reaction"]')?.getBoundingClientRect();
    
    if (!buttonRect) return { top: 0, left: 0 };
    
    return {
      top: buttonRect.top + window.scrollY,
      left: buttonRect.right - 180, // Align right edge with the button's right edge (180px is the selector width)
    };
  };

  // Map emoji codes to actual emojis (same as in EmojiSelector)
  const emojiMap: { [key: string]: string } = {
    thumbs_up: '👍',
    heart: '❤️',
    smile: '😊',
    laugh: '😂',
    sad: '😢',
    angry: '😠',
    clap: '👏',
    fire: '🔥',
  };

  // Group reactions by type
  const groupedReactions = (message.reactions || []).reduce((acc, reaction) => {
    const key = reaction.reaction_id;
    if (!acc[key]) {
      acc[key] = {
        count: 0,
        users: [],
        code: reaction.code || reaction.reaction?.code || 'unknown',
        hasReacted: false
      };
    }
    acc[key].count++;
    acc[key].users.push(reaction.user);
    if (reaction.user_id === currentUserId) {
      acc[key].hasReacted = true;
    }
    return acc;
  }, {} as { [key: number]: { count: number; users: User[]; code: string; hasReacted: boolean } });

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

  const handleToggleReplies = async () => {
    // Only show replies dropdown for root messages that have replies
    if (!message.has_replies || message.parent_id !== null) return;
    
    if (!showReplies) {
      setIsLoadingReplies(true);
      try {
        // Use the reply-chain endpoint instead
        const response = await api.get(`/messages/${message.id}/reply-chain`);
        // Filter out the root message since we're already displaying it
        const replyChain = response.data.filter((m: Message) => m.id !== message.id);
        setReplies(replyChain);
      } catch (error) {
        console.error('Failed to fetch reply chain:', error);
      } finally {
        setIsLoadingReplies(false);
      }
    }
    setShowReplies(!showReplies);
  };

  if (!message.user) return null;

  // Ensure user has all required fields with fallbacks
  const user = {
    ...message.user,
    name: message.user.name || message.user.email || 'Unknown User',
    email: message.user.email || ''
  };

  const initial = (user.name[0] || '?').toUpperCase();

  return (
    <>
      <div 
        ref={messageRef}
        className="flex items-start gap-3 group relative px-2 py-1 -mx-2 rounded-md hover:bg-gray-100 transition-colors"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* User Avatar */}
        <button 
          onClick={() => setShowProfile(true)}
          className="flex-none focus:outline-none"
        >
          {user.picture ? (
            <Image 
              src={user.picture} 
              alt={user.name} 
              width={32}
              height={32}
              className="rounded-full object-cover"
            />
          ) : (
            <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center text-white font-medium text-sm">
              {initial}
            </div>
          )}
        </button>

        <div className="min-w-0 flex-1">
          <div className="flex items-baseline gap-2">
            <span className="font-medium truncate">
              {user.name}
            </span>
            <span className="text-xs text-gray-500 flex-none">
              {new Date(message.created_at).toLocaleTimeString()}
              {message.updated_at && message.updated_at !== message.created_at && (
                <span className="ml-1 italic">
                  (edited {new Date(message.updated_at).toLocaleTimeString()})
                </span>
              )}
            </span>
            {Object.entries(groupedReactions).length > 0 && (
              <div className="flex flex-wrap gap-1">
                {Object.entries(groupedReactions).map(([reactionId, data]) => (
                  <button
                    key={reactionId}
                    onClick={() => data.hasReacted ? handleRemoveReaction(Number(reactionId)) : handleAddReaction(Number(reactionId))}
                    className={`inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-full text-xs ${
                      data.hasReacted ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'
                    } hover:bg-gray-200 transition-colors`}
                    title={data.users.map(u => u.name).join(', ')}
                  >
                    <span className="leading-none">{emojiMap[data.code] || '❓'}</span>
                    <span className="leading-none">{data.count}</span>
                  </button>
                ))}
              </div>
            )}
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
            <div className="space-y-2">
              <p className="text-gray-800 break-words">{message.content}</p>
              {message.files && message.files.length > 0 && (
                <div className="space-y-2 mt-2">
                  {message.files.map((file) => (
                    <MessageAttachment
                      key={file.id}
                      id={file.id}
                      fileName={file.file_name}
                      fileSize={file.file_size}
                      contentType={file.content_type}
                    />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* Edit/Delete/Emoji buttons */}
        {isHovered && !isEditing && (
          <div className="absolute top-0 right-0 flex gap-1 bg-white shadow-sm border border-gray-100 rounded-md">
            <button
              onClick={() => setShowEmojiSelector(true)}
              className="p-1 text-gray-500 hover:text-yellow-500 hover:bg-gray-50"
              title="Add reaction"
            >
              <FaceSmileIcon className="h-4 w-4" />
            </button>
            <button
              onClick={() => onReply?.(message)}
              className="p-1 text-gray-500 hover:text-blue-500 hover:bg-gray-50"
              title="Reply to message"
            >
              <ArrowUturnLeftIcon className="h-4 w-4" />
            </button>
            {isOwner && (
              <>
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
              </>
            )}
          </div>
        )}
      </div>

      {/* Only show replies section for root messages that have replies */}
      {message.has_replies && message.parent_id === null && (
        <div className="ml-11">
          <button
            onClick={handleToggleReplies}
            className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
          >
            {isLoadingReplies ? (
              <span>Loading replies...</span>
            ) : (
              <>
                {showReplies ? (
                  <ChevronUpIcon className="h-4 w-4" />
                ) : (
                  <ChevronDownIcon className="h-4 w-4" />
                )}
                <span>
                  {showReplies ? 'Hide replies' : 'Show replies'}
                </span>
              </>
            )}
          </button>

          {showReplies && (
            <div className="mt-2 space-y-2 border-l-2 border-gray-200 pl-4">
              {replies.map(reply => (
                <ChatMessage
                  key={reply.id}
                  message={reply}
                  currentUserId={currentUserId}
                  channelId={channelId}
                  onMessageUpdate={onMessageUpdate}
                  onMessageDelete={onMessageDelete}
                  onNavigateToDM={onNavigateToDM}
                  onReply={onReply}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Profile Popout */}
      {showProfile && (
        <UserProfilePopout
          user={user}
          isCurrentUser={message.user_id === currentUserId}
          onClose={() => setShowProfile(false)}
          onNavigateToDM={onNavigateToDM}
        />
      )}

      {/* Emoji Selector */}
      {showEmojiSelector && (
        <EmojiSelector
          onSelect={handleAddReaction}
          onClose={handleEmojiSelectorClose}
          position={getEmojiSelectorPosition()}
        />
      )}
    </>
  );
} 