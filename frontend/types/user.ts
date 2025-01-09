export interface User {
    id: number;
    email: string;
    name: string;
    picture?: string;
    bio?: string;
    auth0_id: string;
    is_active: boolean;
    created_at: string;
} 