import type { User } from './user';
import type { Message } from './message';

export type ChannelRole = 'owner' | 'moderator' | 'member';

export interface ChannelMember extends User {
    role: ChannelRole;
}

export interface Channel {
    id: number;
    name: string;
    description?: string;
    is_private: boolean;
    is_dm: boolean;
    ai_channel?: boolean;
    created_at: string;
    owner_id: number;
    users: ChannelMember[];
    messages: Message[];
    member_count: number;
    role?: ChannelRole;
}