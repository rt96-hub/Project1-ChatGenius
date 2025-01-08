export type ChannelRole = 'owner' | 'moderator' | 'member';

export interface ChannelMember {
    id: number;
    email: string;
    name: string;
    role: ChannelRole;
    picture?: string;
}

export interface Channel {
    id: number;
    name: string;
    description: string;
    owner_id: number;
    created_at: string;
    is_private: boolean;
    join_code?: string;
    role?: ChannelRole;
    member_count: number;
    users: ChannelMember[];
} 