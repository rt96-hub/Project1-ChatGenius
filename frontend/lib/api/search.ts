import { useApi } from '@/hooks/useApi';
import type { Channel } from '@/types/channel';
import type { User } from '@/types/user';
import type { Message } from '@/types/message';

// Base interfaces
export interface SearchParams {
  query: string;
  limit?: number;
  skip?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface MessageSearchParams extends SearchParams {
  channel_id?: number;
  from_date?: string;
  to_date?: string;
  from_user?: number;
}

export interface UserSearchParams extends SearchParams {
  exclude_channel?: number;
  only_channel?: number;
}

export interface ChannelSearchParams extends SearchParams {
  include_private?: boolean;
  is_dm?: boolean;
  member_id?: number;
}

export interface FileSearchParams extends SearchParams {
  channel_id?: number;
  file_type?: string;
  from_date?: string;
  to_date?: string;
  uploaded_by?: number;
}

// File type definitions
export interface File {
  id: number;
  file_name: string;
  content_type: string;
  file_size: number;
  message_id: number;
  s3_key: string;
  uploaded_at: string;
  uploaded_by: number;
  channel_id: number;
  highlight?: {
    file_name: string[];
    message_content?: string[];
  };
}

// Response types
export interface SearchResponse<T> {
  total: number;
  has_more: boolean;
  items: T[];  // Generic array of items
}

export interface MessageSearchResponse extends SearchResponse<{
  id: number;
  content: string;
  created_at: string;
  updated_at: string;
  channel_id: number;
  user_id: number;
  channel: Channel;
  user: User;
  highlight?: {
    content: string[];
  };
}> {
  messages: SearchResponse<Message>['items'];  // Use the generic items array
}

export interface UserSearchResponse extends SearchResponse<User> {
  users: SearchResponse<User>['items'];
}

export interface ChannelSearchResponse extends SearchResponse<Channel> {
  channels: SearchResponse<Channel>['items'];
}

export interface FileSearchResponse extends SearchResponse<File> {
  files: SearchResponse<File>['items'];
}

// Create a hook to get authenticated search functions
export const useSearchApi = () => {
  const api = useApi();

  return {
    searchMessages: async (params: MessageSearchParams): Promise<MessageSearchResponse> => {
      const { data } = await api.get('/search/messages', { params });
      return data;
    },

    searchUsers: async (params: UserSearchParams): Promise<UserSearchResponse> => {
      const { data } = await api.get('/search/users', { params });
      return data;
    },

    searchChannels: async (params: ChannelSearchParams): Promise<ChannelSearchResponse> => {
      const { data } = await api.get('/search/channels', { params });
      return data;
    },

    searchFiles: async (params: FileSearchParams): Promise<FileSearchResponse> => {
      const { data } = await api.get('/search/files', { params });
      return data;
    }
  };
}; 