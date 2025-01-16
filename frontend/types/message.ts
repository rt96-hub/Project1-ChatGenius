import type { User } from './user';

export interface MessageReaction {
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

export interface MessageFile {
  id: number;
  message_id: number;
  file_name: string;
  content_type: string;
  file_size: number;
  uploaded_at: string;
  uploaded_by: number;
}

export interface Message {
  id: number;
  content: string;
  created_at: string;
  updated_at?: string;
  user_id: number;
  channel_id: number;
  parent_id: number | null;
  parent?: Message | null;
  has_replies?: boolean;
  from_ai?: boolean;
  user?: User;
  reactions?: MessageReaction[];
  files?: MessageFile[];
} 