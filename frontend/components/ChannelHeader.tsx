import { useState } from 'react';
import { PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import { useApi } from '@/hooks/useApi';

interface Channel {
    id: number;
    name: string;
    description: string | null;
    owner_id: number;
}

interface ChannelHeaderProps {
    channel: Channel;
    currentUserId: number;
    onChannelUpdate: () => void;
    onChannelDelete?: () => void;
}

export default function ChannelHeader({ channel, currentUserId, onChannelUpdate, onChannelDelete }: ChannelHeaderProps) {
    const api = useApi();
    const [isEditing, setIsEditing] = useState(false);
    const [newName, setNewName] = useState(channel.name);
    const [newDescription, setNewDescription] = useState(channel.description || '');

    const handleUpdate = async () => {
        try {
            await api.put(`/channels/${channel.id}`, {
                name: newName,
                description: newDescription || null
            });
            setIsEditing(false);
            onChannelUpdate();
        } catch (error) {
            console.error('Failed to update channel:', error);
        }
    };

    const handleDelete = async () => {
        if (!window.confirm('Are you sure you want to delete this channel?')) return;
        
        try {
            await api.delete(`/channels/${channel.id}`);
            if (onChannelDelete) {
                onChannelDelete();
            }
        } catch (error) {
            console.error('Failed to delete channel:', error);
        }
    };

    // ... rest of the component ...
} 