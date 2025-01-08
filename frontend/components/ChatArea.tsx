import { useState, useEffect, useRef } from 'react';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';
import ChannelHeader from './ChannelHeader';
import ChatMessage from './ChatMessage';
import { useConnection } from '../contexts/ConnectionContext';
import { useApi } from '@/hooks/useApi';

interface ChatAreaProps {
  channelId: number | null;
  onChannelUpdate?: () => void;
  onChannelDelete?: () => void;
}

interface Message {
  id: number;
  content: string;
  created_at: string;
  user_id: number;
  channel_id: number;
  user?: {
    id: number;
    email: string;
  };
}

interface Channel {
  id: number;
  name: string;
  description: string | null;
  owner_id: number;
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
                msg.id === data.message.id ? data.message : msg
              ));
              break;
            case 'message_delete':
              setMessages(prev => prev.filter(msg => msg.id !== data.message_id));
              break;
            case 'channel_update':
              setChannel(data.channel);
              if (onChannelUpdate) {
                onChannelUpdate();
              }
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
    // Scroll to bottom on initial load
    if (messages.length <= 50) {
      const container = messagesContainerRef.current;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    }
  }, [messages]);

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
        params: { skip: skipCount, limit: 50 },
        signal: abortControllerRef.current?.signal
      });
      
      // Double check channel hasn't changed during request
      if (channelId !== currentChannelRef.current) return null;
      
      if (isInitial) {
        setMessages(response.data.messages.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()));
      } else {
        setMessages(prev => {
          const existingIds = new Set(prev.map(m => m.id));
          const newMessages = response.data.messages.filter(m => !existingIds.has(m.id));
          return [...newMessages, ...prev].sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
        });
      }
      setHasMore(response.data.has_more);
      return response.data.messages;
    } catch (error) {
      if (error.name === 'AbortError') {
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

  if (!channelId) {
    return (
      <div className="flex-1 flex items-center justify-center bg-white text-gray-500">
        Select a channel to start messaging
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {channel && currentUserId && (
        <ChannelHeader
          channel={channel}
          currentUserId={currentUserId}
          onChannelUpdate={handleChannelUpdate}
          onChannelDelete={handleChannelDelete}
        />
      )}
      <div 
        id="scrollableDiv"
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto p-4 space-y-4"
        style={{ height: 'calc(100vh - 180px)' }}
      >
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message}
            currentUserId={currentUserId || 0}
            channelId={channelId || 0}
            onMessageUpdate={handleMessageUpdate}
            onMessageDelete={handleMessageDelete}
          />
        ))}
        <div ref={messagesEndRef} />
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
            type="submit"
            className="flex-none p-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600"
            disabled={!newMessage.trim()}
          >
            <PaperAirplaneIcon className="h-5 w-5" />
          </button>
        </form>
      </div>
    </div>
  );
} 