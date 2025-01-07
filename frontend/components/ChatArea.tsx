import { useState, useEffect, useRef, useCallback } from 'react';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';
import axios from 'axios';
import ChannelHeader from './ChannelHeader';
import InfiniteScroll from 'react-infinite-scroll-component';

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
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [channel, setChannel] = useState<Channel | null>(null);
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [skip, setSkip] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (channelId) {
      // Reset pagination when changing channels
      setMessages([]);
      setSkip(0);
      setHasMore(true);
      fetchMessages(0, true);
      fetchChannelDetails();
    } else {
      setChannel(null);
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
      console.log('Scroll position:', container.scrollTop);
      if (container.scrollTop < 100 && !isLoadingMore && hasMore) {
        console.log('Loading more messages...');
        loadMoreMessages();
      }
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, [isLoadingMore, hasMore, messagesContainerRef.current]);

  const loadMoreMessages = async () => {
    if (!channelId || isLoadingMore || !hasMore) return;
    console.log('Fetching more messages...');
    setIsLoadingMore(true);
    const container = messagesContainerRef.current;
    const previousScrollHeight = container ? container.scrollHeight : 0;
    const previousScrollTop = container ? container.scrollTop : 0;
    const response = await fetchMessages(skip + 50, false);
    setSkip(prev => prev + 50);
    setIsLoadingMore(false);
    if (container && response) {
      const newScrollHeight = container.scrollHeight;
      container.scrollTop = newScrollHeight - previousScrollHeight + previousScrollTop;
    }
  };

  const fetchMessages = async (skipCount: number, isInitial: boolean) => {
    if (!channelId) return null;
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://localhost:8000/channels/${channelId}/messages`, {
        params: { skip: skipCount, limit: 50 },
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (isInitial) {
        setMessages(response.data.messages);
      } else {
        // Add older messages to the beginning, ensuring no duplicates
        setMessages(prev => {
          const existingIds = new Set(prev.map(m => m.id));
          const newMessages = response.data.messages.filter(m => !existingIds.has(m.id));
          return [...newMessages, ...prev];
        });
      }
      setHasMore(response.data.has_more);
      return response.data.messages;
    } catch (error) {
      console.error('Failed to fetch messages:', error);
      return null;
    }
  };

  useEffect(() => {
    // Fetch current user info
    const fetchCurrentUser = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('http://localhost:8000/users/me', {
          headers: { Authorization: `Bearer ${token}` }
        });
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
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://localhost:8000/channels/${channelId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setChannel(response.data);
    } catch (error) {
      console.error('Failed to fetch channel details:', error);
    }
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!channelId || !newMessage.trim()) return;

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `http://localhost:8000/channels/${channelId}/messages`,
        { content: newMessage },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setNewMessage('');
      // Fetch only the most recent messages after sending
      setSkip(0);
      setHasMore(true);
      fetchMessages(0, true);
    } catch (error) {
      console.error('Failed to send message:', error);
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

  if (!channelId) {
    return (
      <div className="flex-1 flex items-center justify-center bg-white text-gray-500">
        Select a channel to start messaging
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-white">
      {channel && currentUserId && (
        <ChannelHeader
          channel={channel}
          currentUserId={currentUserId}
          onChannelUpdate={handleChannelUpdate}
          onChannelDelete={handleChannelDelete}
        />
      )}
      <InfiniteScroll
        dataLength={messages.length}
        next={loadMoreMessages}
        hasMore={hasMore}
        inverse={true} // This loads the data in reverse order
        scrollableTarget="scrollableDiv"
      >
        <div 
          id="scrollableDiv"
          ref={messagesContainerRef}
          className="flex-1 overflow-y-auto p-4 space-y-4"
          style={{ height: 'calc(100vh - 250px)', overflowY: 'auto' }} // Increase space for the text entry area
        >
          {messages.map((message) => (
            <div key={message.id} className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-gray-300" />
              <div>
                <div className="flex items-baseline gap-2">
                  <span className="font-medium">
                    {message.user?.email || 'Unknown User'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(message.created_at).toLocaleTimeString()}
                  </span>
                </div>
                <p className="text-gray-800">{message.content}</p>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} /> {/* Scroll anchor */}
        </div>
      </InfiniteScroll>
      <div className="border-t border-gray-200 p-4">
        <form onSubmit={sendMessage} className="flex items-center gap-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 rounded-lg border border-gray-200 px-4 py-2 focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            className="p-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600"
            disabled={!newMessage.trim()}
          >
            <PaperAirplaneIcon className="h-5 w-5" />
          </button>
        </form>
      </div>
    </div>
  );
} 