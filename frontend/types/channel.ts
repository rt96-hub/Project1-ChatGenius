export type ChannelRole = 'owner' | 'moderator' | 'member';

export interface Channel {
    id: number;
    name: string;
    description: string | null;
    owner_id: number;
    created_at: string;
    is_private: boolean;
    join_code: string | null;
    is_dm?: boolean;
    member_count: number;
    users: Array<{
        id: number;
        email: string;
        name: string;
        picture?: string;
        role?: ChannelRole;
    }>;
    messages: Array<{
        id: number;
        content: string;
        created_at: string;
        user_id: number;
    }>;
}