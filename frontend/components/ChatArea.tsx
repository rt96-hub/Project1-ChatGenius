import { useState, useEffect, useRef, useCallback } from 'react';
import { PaperAirplaneIcon, ArrowUturnLeftIcon } from '@heroicons/react/24/outline';
import ChannelHeader from './ChannelHeader';
import ChatMessage from './ChatMessage';
import MemberListModal from './MemberListModal';
import AISidebar from './AISidebar';
import { useConnection } from '../contexts/ConnectionContext';
import { useApi } from '@/hooks/useApi';
import type { Channel, ChannelRole } from '../types/channel';
import { FileUploadButton } from './file/FileUploadButton';
import { FilePreview } from './file/FilePreview';
import { FileUploadProgress } from './file/FileUploadProgress';

interface ChatAreaProps {
  channelId: number | null;
  onChannelUpdate?: () => void;
  onChannelDelete?: () => void;
  onNavigateToDM?: (channelId: number) => void;
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

export default function ChatArea({ channelId, onChannelUpdate, onChannelDelete, onNavigateToDM }: ChatAreaProps) {
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
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const currentChannelRef = useRef<number | null>(null);
  const { addMessageListener } = useConnection();
  const [isUserSentMessage, setIsUserSentMessage] = useState(false);
  const [replyingTo, setReplyingTo] = useState<Message | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [showAISidebar, setShowAISidebar] = useState(false);

  const fetchChannelDetails = useCallback(async () => {
    if (!channelId) return;
    try {
      const response = await api.get(`/channels/${channelId}`);
      setChannel(response.data);
    } catch (error) {
      console.error('Failed to fetch channel details:', error);
    }
  }, [channelId, api]);

  const fetchMessages = useCallback(async (skipCount: number, isInitial: boolean) => {
    if (!channelId) return;
    try {
      setIsLoadingMore(true);
      const response = await api.get(`/messages/${channelId}/messages`, {
        params: { skip: skipCount, limit: 50 },
        signal: abortControllerRef.current?.signal
      });
      const newMessages = response.data.messages;
      setMessages(prev => {
        const combined = isInitial ? newMessages : [...newMessages, ...prev];
        return combined.sort((a: Message, b: Message) => 
          new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        );
      });
      setHasMore(newMessages.length === 50);
      setSkip(skipCount + newMessages.length);
    } catch (error: unknown) {
      if (error && typeof error === 'object' && 'name' in error && error.name !== 'AbortError') {
        console.error('Failed to fetch messages:', error);
      }
    } finally {
      setIsLoadingMore(false);
    }
  }, [channelId, api]);

  const loadMoreMessages = useCallback(async () => {
    if (!hasMore || isLoadingMore) return;
    await fetchMessages(skip, false);
  }, [hasMore, isLoadingMore, fetchMessages, skip]);

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
      setNewMessage(''); // Reset the textarea content when switching channels
      
      // Create new abort controller for this channel's requests
      abortControllerRef.current = new AbortController();
      
      fetchMessages(0, true);
      fetchChannelDetails();

      // Set up WebSocket message listener
      const removeListener = addMessageListener(
        (data) => {
          if (currentChannelRef.current !== data.channel_id) {
            return;
          }
          switch (data.type) {
            case 'new_message':
              console.log('Processing new message:', data.message);
              setMessages(prev => {
                // Check if message already exists to prevent duplicates
                if (prev.some(m => m.id === data.message.id)) {
                  return prev;
                }

                // If this is a reply message, update the parent's has_replies flag
                if (data.message.parent_id) {
                  return prev.map(msg => 
                    msg.id === data.message.parent_id
                      ? { ...msg, has_replies: true }
                      : msg
                  );
                }

                // Only add non-reply messages to the main chat area
                const newMessages = [...prev, data.message].sort((a, b) => 
                  new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
                );
                // If this is a message from the current user, trigger scroll
                if (data.message.user_id === currentUserId) {
                  setIsUserSentMessage(true);
                }
                return newMessages;
              });
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
      );

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
  }, [channelId, addMessageListener, currentUserId, fetchChannelDetails, fetchMessages, onChannelUpdate]);

  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container || messages.length === 0 || !channel) return;

    // On initial load, wait for next frame to ensure layout is stable
    if (isInitialLoad) {
      requestAnimationFrame(() => {
        if (container) {
          container.scrollTop = container.scrollHeight;
          setIsInitialLoad(false);
        }
      });
      return;
    }

    // Scroll to bottom if message was sent by user
    if (isUserSentMessage) {
      requestAnimationFrame(() => {
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
      setIsUserSentMessage(false);
      return;
    }

    // For new messages from others, only scroll if they're very recent
    const lastMessage = messages[messages.length - 1];
    if (lastMessage && Date.now() - new Date(lastMessage.created_at).getTime() < 1000) {
      requestAnimationFrame(() => {
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    }
  }, [messages, channel, isInitialLoad, isUserSentMessage]);

  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      if (container.scrollTop === 0 && hasMore && !isLoadingMore) {
        loadMoreMessages();
      }
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, [hasMore, isLoadingMore, loadMoreMessages]);

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
  }, [api]);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setUploadProgress(0);
    setUploadError(null);
  };

  const handleFileRemove = () => {
    setSelectedFile(null);
    setUploadProgress(0);
    setUploadError(null);
  };

  async function handleSendMessage(e?: React.FormEvent<HTMLFormElement>) {
    if (e) e.preventDefault();
  
    // Trim text
    const messageContent = newMessage.trim();
  
    // If there's no content and no file, do nothing
    if (!messageContent && !selectedFile) {
      return;
    }
  
    try {
      // Prepare form data
      const formData = new FormData();
      formData.append('content', messageContent);
      if (selectedFile) {
        formData.append('file', selectedFile);
      }
  
      // Decide on the endpoint based on whether it's a reply and has a file
      let endpoint: string;
      if (selectedFile) {
        if (replyingTo) {
          endpoint = `/messages/${channelId}/messages/${replyingTo.id}/reply-with-file`;
        } else {
          endpoint = `/messages/${channelId}/messages/with-file`;
        }
      } else {
        if (replyingTo) {
          endpoint = `/messages/${channelId}/messages/${replyingTo.id}/reply`;
        } else {
          endpoint = `/messages/${channelId}/messages`;
        }
      }
  
      // Send via API
      await api.post(endpoint, selectedFile ? formData : { content: messageContent }, {
        ...(selectedFile && {
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const progress = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              setUploadProgress(progress);
            }
          },
        }),
      });
  
      // Clear out the form states
      setNewMessage('');
      setSelectedFile(null);
      setUploadProgress(0);
      setUploadError(null);
      setReplyingTo(null); // Clear reply state after sending
  
      // Remove the redundant WebSocket broadcast since server handles it
      // sendMessage({
      //   type: 'new_message',
      //   channel_id: channelId,
      //   message: createdMessage
      // });
  
    } catch (error) {
      console.error('Failed to send message:', error);
      setUploadError(selectedFile ? 'Something went wrong while uploading your file.' : 'Failed to send message.');
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
    try {
      await api.patch(`/channels/${channelId}/members/${userId}`, { role });
    } catch (error) {
      console.error('Failed to update member role:', error);
    }
  };

  const handleRemoveMember = async (userId: number) => {
    try {
      await api.delete(`/channels/${channelId}/members/${userId}`);
    } catch (error) {
      console.error('Failed to remove member:', error);
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
      <div className="flex-1 flex flex-col h-full">
        {channel && currentUserId && (
          <div className="flex-none">
            <ChannelHeader
              channel={channel}
              currentUserId={currentUserId}
              onChannelUpdate={onChannelUpdate || (() => {})}
              onChannelDelete={onChannelDelete}
              onUpdateMemberRole={handleUpdateMemberRole}
              onRemoveMember={handleRemoveMember}
              onToggleMembers={() => setShowMembers(!showMembers)}
              showMembers={showMembers}
              onToggleAISidebar={() => setShowAISidebar(!showAISidebar)}
              showAISidebar={showAISidebar}
            />
          </div>
        )}
        <div 
          id="scrollableDiv"
          ref={messagesContainerRef}
          className="flex-1 overflow-y-auto p-4 space-y-4"
        >
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              currentUserId={currentUserId || 0}
              channelId={channelId}
              onMessageUpdate={handleMessageUpdate}
              onMessageDelete={handleMessageDelete}
              onNavigateToDM={onNavigateToDM}
              onReply={setReplyingTo}
            />
          ))}
          <div ref={messagesEndRef} />
        </div>
        <div className="flex-none border-t border-gray-200 p-4 bg-white">
          {replyingTo && (
            <div className="mb-2 px-4 py-2 bg-gray-100 rounded-lg flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <ArrowUturnLeftIcon className="h-4 w-4" />
                <span>Replying to {replyingTo.user?.name}</span>
                <span className="text-gray-400">&ldquo;{replyingTo.content.substring(0, 50)}...&rdquo;</span>
              </div>
              <button
                onClick={() => setReplyingTo(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
          )}
          {selectedFile && !uploadError && uploadProgress > 0 && uploadProgress < 100 && (
            <div className="mb-2">
              <FileUploadProgress
                fileName={selectedFile.name}
                progress={uploadProgress}
                onCancel={handleFileRemove}
              />
            </div>
          )}
          {selectedFile && (uploadProgress === 0 || uploadProgress === 100) && (
            <div className="mb-2">
              <FilePreview
                file={selectedFile}
                onRemove={handleFileRemove}
              />
            </div>
          )}
          <form onSubmit={handleSendMessage} className="flex items-end gap-2">
            <FileUploadButton
              onFileSelect={handleFileSelect}
              disabled={!!selectedFile || isLoadingMore}
            />
            <textarea
              ref={textareaRef}
              value={newMessage}
              onChange={(e) => {
                setNewMessage(e.target.value);
                e.target.style.height = '45px';
                e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`;
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  // Call handleSendMessage without passing e
                  handleSendMessage();
                }
              }}
              placeholder="Type a message..."
              className="flex-1 rounded-lg border border-gray-200 px-4 py-2 focus:outline-none focus:border-blue-500 resize-none overflow-y-auto min-h-[45px] max-h-[200px]"
              rows={1}
            />
            <button
              type="submit"
              className="flex-none p-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600"
              disabled={!newMessage.trim() && !selectedFile}
            >
              <PaperAirplaneIcon className="h-5 w-5" />
            </button>
          </form>
        </div>

        {channel && currentUserId && (
          <>
            <MemberListModal
              isOpen={showMembers}
              onClose={() => setShowMembers(false)}
              channel={channel}
              currentUserId={currentUserId}
              onUpdateMemberRole={handleUpdateMemberRole}
              onRemoveMember={handleRemoveMember}
              onLeaveChannel={handleLeaveChannel}
            />
            <AISidebar
              isOpen={showAISidebar}
              onClose={() => setShowAISidebar(false)}
              channelId={channel.id}
            />
          </>
        )}
      </div>
    </div>
  );
} 