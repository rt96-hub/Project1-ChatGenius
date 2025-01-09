import { useState, useEffect, useRef } from 'react';
import { PaperAirplaneIcon, UsersIcon } from '@heroicons/react/24/outline';
import ChannelHeader from './ChannelHeader';
import ChatMessage from './ChatMessage';
import MemberListModal from './MemberListModal';
import { useConnection } from '../contexts/ConnectionContext';
import { useApi } from '@/hooks/useApi';
import type { Channel, ChannelRole } from '../types/channel';

interface ChatAreaProps {
  channelId: number | null;
  onChannelUpdate?: () => void;
  onChannelDelete?: () => void;
}

interface Message {
  id: number;
  content: string;
  created_at: string;
  updated_at?: string;
  user_id: number;
  channel_id: number;
  user?: {
    id: number;
    email: string;
    name: string;
    picture?: string;
  };
  reactions?: Array<{
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
    user: {
      id: number;
      email: string;
      name: string;
      picture?: string;
    };
  }>;
}

export default function ChatArea({ channelId, onChannelUpdate, onChannelDelete }: ChatAreaProps) {
  const api = useApi();
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [channel, setChannel] = useState<Channel | null>(null);
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [skip, setSkip] = useState(0);
  const [showMembers, setShowMembers] = useState(false);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const currentChannelRef = useRef<number | null>(null);
  const { connectionStatus, sendMessage, addMessageListener } = useConnection();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    // Cleanup function to abort any pending requests when unmounting
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  useEffect(() => {
    // Abort any pending requests when switching channels
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    currentChannelRef.current = channelId;
    
    if (channelId) {
      // Reset state for new channel
      setMessages([]);
      setSkip(0);
      setHasMore(true);
      setChannel(null);
      setIsInitialLoad(true);
      
      // Create new abort controller for this channel's requests
      abortControllerRef.current = new AbortController();
      
      fetchMessages(0, true);
      fetchChannelDetails();

      // Set up WebSocket message listener
      const removeListener = addMessageListener((data) => {
        // Only process messages for the current channel
        if (data.channel_id === currentChannelRef.current) {
          switch (data.type) {
            case 'new_message':
              setMessages(prev => [...prev, data.message].sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()));
              scrollToBottom();
              break;
            case 'message_update':
              setMessages(prev => prev.map(msg => 
                msg.id === data.message.id 
                  ? {
                      ...data.message,
                      reactions: msg.reactions // Preserve existing reactions
                    }
                  : msg
              ));
              break;
            case 'message_delete':
              setMessages(prev => prev.filter(msg => msg.id !== data.message_id));
              break;
            case 'message_reaction_add':
              setMessages(prev => prev.map(msg =>
                msg.id === data.message_id
                  ? {
                      ...msg,
                      reactions: [...(msg.reactions || []), {
                        ...data.reaction,
                        reaction: {
                          id: data.reaction.reaction_id,
                          code: data.reaction.code || data.reaction.reaction?.code || 'unknown',
                          is_system: true,
                          image_url: null
                        }
                      }]
                    }
                  : msg
              ));
              break;
            case 'message_reaction_remove':
              setMessages(prev => prev.map(msg =>
                msg.id === data.message_id
                  ? {
                      ...msg,
                      reactions: (msg.reactions || []).filter(r => 
                        !(r.reaction_id === data.reaction_id && r.user_id === data.user_id)
                      )
                    }
                  : msg
              ));
              break;
            case 'channel_update':
              setChannel(data.channel);
              if (onChannelUpdate) {
                onChannelUpdate();
              }
              break;
            case 'member_joined':
              setChannel(prev => prev ? {
                ...prev,
                users: [...prev.users, data.user],
                member_count: prev.member_count + 1
              } : null);
              break;
            case 'member_left':
              setChannel(prev => prev ? {
                ...prev,
                users: prev.users.filter(u => u.id !== data.user_id),
                member_count: prev.member_count - 1
              } : null);
              break;
            case 'role_updated':
              setChannel(prev => prev ? {
                ...prev,
                users: prev.users.map(u => 
                  u.id === data.user_id 
                    ? { ...u, role: data.role }
                    : u
                )
              } : null);
              break;
            case 'privacy_updated':
              setChannel(prev => prev ? {
                ...prev,
                is_private: data.is_private
              } : null);
              break;
          }
        }
      });

      return () => {
        removeListener();
        if (abortControllerRef.current) {
          abortControllerRef.current.abort();
        }
      };
    } else {
      setChannel(null);
      setMessages([]);
      setSkip(0);
      setHasMore(true);
    }
  }, [channelId]);

  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container || messages.length === 0) return;

    // On initial load, scroll to bottom
    if (isInitialLoad) {
      container.scrollTop = container.scrollHeight;
      setIsInitialLoad(false);
      return;
    }

    // For new messages, only scroll if they're very recent
    const lastMessage = messages[messages.length - 1];
    if (lastMessage.created_at > (new Date(Date.now() - 1000).toISOString())) {
      container.scrollTop = container.scrollHeight;
    }
  }, [messages, isInitialLoad]);

  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      if (container.scrollTop < 100 && !isLoadingMore && hasMore) {
        loadMoreMessages();
      }
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, [isLoadingMore, hasMore, messagesContainerRef.current]);

  const loadMoreMessages = async () => {
    if (!channelId || isLoadingMore || !hasMore || channelId !== currentChannelRef.current) return;
    setIsLoadingMore(true);
    const container = messagesContainerRef.current;
    const previousScrollHeight = container ? container.scrollHeight : 0;
    const previousScrollTop = container ? container.scrollTop : 0;
    const response = await fetchMessages(skip + 50, false);
    if (channelId === currentChannelRef.current) {
      setSkip(prev => prev + 50);
      setIsLoadingMore(false);
      if (container && response) {
        const newScrollHeight = container.scrollHeight;
        container.scrollTop = newScrollHeight - previousScrollHeight + previousScrollTop;
      }
    }
  };

  const fetchMessages = async (skipCount: number, isInitial: boolean) => {
    if (!channelId || channelId !== currentChannelRef.current) return null;
    try {
      const response = await api.get(`/channels/${channelId}/messages`, {
        params: { 
          skip: skipCount, 
          limit: 50,
          include_reactions: true
        },
        signal: abortControllerRef.current?.signal
      });
      
      // Double check channel hasn't changed during request
      if (channelId !== currentChannelRef.current) return null;
      
      if (isInitial) {
        setMessages(response.data.messages.sort((a: Message, b: Message) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()));
      } else {
        setMessages(prev => {
          const existingIds = new Set(prev.map((m: Message) => m.id));
          const newMessages = response.data.messages.filter((m: Message) => !existingIds.has(m.id));
          return [...newMessages, ...prev].sort((a: Message, b: Message) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
        });
      }
      setHasMore(response.data.has_more);
      return response.data.messages;
    } catch (error: unknown) {
      if ((error as { name?: string }).name === 'AbortError') {
        // Request was aborted, ignore
        return null;
      }
      console.error('Failed to fetch messages:', error);
      return null;
    }
  };

  useEffect(() => {
    const fetchCurrentUser = async () => {
      try {
        const response = await api.get('/users/me');
        setCurrentUserId(response.data.id);
      } catch (error) {
        console.error('Failed to fetch current user:', error);
      }
    };
    fetchCurrentUser();
  }, []);

  const fetchChannelDetails = async () => {
    if (!channelId) return;
    try {
      const response = await api.get(`/channels/${channelId}`);
      setChannel(response.data);
    } catch (error) {
      console.error('Failed to fetch channel details:', error);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!channelId || !newMessage.trim()) return;

    try {
      // Send message through WebSocket
      sendMessage({
        channel_id: channelId,
        content: newMessage.trim()
      });
      setNewMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
      // Fallback to HTTP if WebSocket fails
      await api.post(
        `/channels/${channelId}/messages`,
        { content: newMessage }
      );
      setNewMessage('');
      fetchMessages(0, true);
    }
  };

  const handleChannelUpdate = () => {
    fetchChannelDetails();
    if (onChannelUpdate) {
      onChannelUpdate();
    }
  };

  const handleChannelDelete = () => {
    if (onChannelDelete) {
      onChannelDelete();
    }
  };

  const handleMessageUpdate = (updatedMessage: Message) => {
    setMessages(prev => prev.map(msg => 
      msg.id === updatedMessage.id ? updatedMessage : msg
    ));
  };

  const handleMessageDelete = (messageId: number) => {
    setMessages(prev => prev.filter(msg => msg.id !== messageId));
  };

  const handleUpdateMemberRole = async (userId: number, role: ChannelRole) => {
    if (!channel) return;
    try {
      await api.put(`/channels/${channel.id}/roles/${userId}`, { role });
    } catch (error) {
      console.error('Failed to update member role:', error);
    }
  };

  const handleRemoveMember = async (userId: number) => {
    if (!channel) return;
    try {
      await api.delete(`/channels/${channel.id}/members/${userId}`);
    } catch (error) {
      console.error('Failed to remove member:', error);
    }
  };

  const handleGenerateInvite = async () => {
    if (!channel) return;
    try {
      await api.post(`/channels/${channel.id}/invite`);
      if (onChannelUpdate) {
        onChannelUpdate();
      }
    } catch (error) {
      console.error('Failed to generate invite:', error);
    }
  };

  const handleLeaveChannel = async () => {
    if (!channel) return;
    try {
      await api.post(`/channels/${channel.id}/leave`);
      if (onChannelDelete) {
        onChannelDelete();
      }
    } catch (error) {
      console.error('Failed to leave channel:', error);
    }
  };

  if (!channelId) {
    return (
      <div className="flex-1 flex items-center justify-center bg-white text-gray-500">
        Select a channel to start messaging
      </div>
    );
  }

  return (
    <div className="flex h-full">
      <div className="flex-1 flex flex-col overflow-hidden">
        {channel && currentUserId && (
          <ChannelHeader
            channel={channel}
            currentUserId={currentUserId}
            onChannelUpdate={onChannelUpdate || (() => {})}
            onChannelDelete={onChannelDelete}
            onUpdateMemberRole={handleUpdateMemberRole}
            onRemoveMember={handleRemoveMember}
            onGenerateInvite={handleGenerateInvite}
            onToggleMembers={() => setShowMembers(!showMembers)}
            showMembers={showMembers}
          />
        )}
        <div className="flex-1">
          <div 
            id="scrollableDiv"
            ref={messagesContainerRef}
            className="h-full overflow-y-auto p-4 space-y-4"
            style={{ height: 'calc(100vh - 180px)' }}
          >
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                currentUserId={currentUserId || 0}
                channelId={channelId}
                onMessageUpdate={handleMessageUpdate}
                onMessageDelete={handleMessageDelete}
              />
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>
        <div className="flex-none border-t border-gray-200 p-4 bg-white">
          <form onSubmit={handleSendMessage} className="flex items-center gap-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Type a message..."
              className="flex-1 rounded-lg border border-gray-200 px-4 py-2 focus:outline-none focus:border-blue-500"
            />
            <button
              type="button"
              onClick={() => setShowMembers(!showMembers)}
              className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
              title={showMembers ? "Hide Members" : "Show Members"}
            >
              <UsersIcon className="h-5 w-5" />
            </button>
            <button
              type="submit"
              className="flex-none p-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600"
              disabled={!newMessage.trim()}
            >
              <PaperAirplaneIcon className="h-5 w-5" />
            </button>
          </form>
        </div>

        {channel && currentUserId && (
          <MemberListModal
            isOpen={showMembers}
            onClose={() => setShowMembers(false)}
            channel={channel}
            currentUserId={currentUserId}
            onUpdateMemberRole={handleUpdateMemberRole}
            onRemoveMember={handleRemoveMember}
            onLeaveChannel={handleLeaveChannel}
          />
        )}
      </div>
    </div>
  );
} 