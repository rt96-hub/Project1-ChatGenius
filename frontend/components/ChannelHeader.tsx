import { useState, useEffect } from 'react';
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

    // Update form values when channel changes or when entering edit mode
    useEffect(() => {
        setNewName(channel.name);
        setNewDescription(channel.description || '');
    }, [channel, isEditing]);

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

    return (
        <div className="border-b border-gray-200 bg-white p-4">
            {isEditing ? (
                <div className="space-y-3">
                    <input
                        type="text"
                        value={newName}
                        onChange={(e) => setNewName(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Channel name"
                    />
                    <input
                        type="text"
                        value={newDescription}
                        onChange={(e) => setNewDescription(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Channel description (optional)"
                    />
                    <div className="flex gap-2">
                        <button
                            onClick={handleUpdate}
                            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
                        >
                            Save
                        </button>
                        <button
                            onClick={() => setIsEditing(false)}
                            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            ) : (
                <div className="flex justify-between items-start">
                    <div>
                        <h2 className="text-xl font-semibold text-gray-900">{channel.name}</h2>
                        {channel.description && (
                            <p className="mt-1 text-gray-600">{channel.description}</p>
                        )}
                    </div>
                    {channel.owner_id === currentUserId && (
                        <div className="flex gap-2">
                            <button
                                onClick={() => setIsEditing(true)}
                                className="p-2 text-gray-500 hover:text-gray-700 rounded-full hover:bg-gray-100"
                            >
                                <PencilIcon className="h-5 w-5" />
                            </button>
                            <button
                                onClick={handleDelete}
                                className="p-2 text-gray-500 hover:text-red-600 rounded-full hover:bg-gray-100"
                            >
                                <TrashIcon className="h-5 w-5" />
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
} 