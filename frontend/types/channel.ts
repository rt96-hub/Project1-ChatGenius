import type { Message } from './message';
import type { User } from './user';

export interface Channel {
    id: number;
    name: string;
    description: string;
    owner_id: number;
    created_at: string;
    is_private: boolean;
    is_dm: boolean;
    join_code: string | null;
    users: ChannelMember[];
    messages: Message[];
    member_count: number;
    role?: ChannelRole;
}

export type ChannelRole = 'owner' | 'moderator' | 'member';

export interface ChannelMember {
    id: number;
    name: string;
    email: string;
    picture?: string;
    role: ChannelRole;
}