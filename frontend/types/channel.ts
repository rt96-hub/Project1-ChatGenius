export type ChannelRole = 'owner' | 'moderator' | 'member';

export interface Channel {
    id: number;
    name: string;
    description: string | null;
    owner_id: number;
    created_at: string;
    is_private: boolean;
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