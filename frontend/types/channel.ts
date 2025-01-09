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
    users: User[];
    messages: Message[];
}