import type { User } from './user';

export interface Message {
    id: number;
    content: string;
    created_at: string;
    updated_at: string;
    channel_id: number;
    user_id: number;
    parent_id?: number;
    has_replies: boolean;
    user: User;
} 