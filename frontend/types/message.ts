import type { User } from './user';

export interface Message {
    id: number;
    content: string;
    created_at: string;
    updated_at: string;
    user_id: number;
    channel_id: number;
    user: User;
    reactions: any[]; // We can define a proper Reaction type if needed
} 