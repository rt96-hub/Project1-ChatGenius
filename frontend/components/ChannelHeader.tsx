import { useState, useEffect } from 'react';
import { PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import axios from 'axios';

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
    const [isEditing, setIsEditing] = useState(false);
    const [name, setName] = useState(channel.name);
    const [description, setDescription] = useState(channel.description || '');
    const [error, setError] = useState('');
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

    const isOwner = channel.owner_id === currentUserId;

    useEffect(() => {
        setName(channel.name);
        setDescription(channel.description || '');
    }, [channel]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token');
            await axios.put(
                `http://localhost:8000/channels/${channel.id}`,
                { name, description },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setIsEditing(false);
            onChannelUpdate();
        } catch (err) {
            setError('Failed to update channel');
        }
    };

    const handleCancel = () => {
        setName(channel.name);
        setDescription(channel.description || '');
        setError('');
        setIsEditing(false);
    };

    const handleStartEditing = () => {
        setName(channel.name);
        setDescription(channel.description || '');
        setError('');
        setIsEditing(true);
    };

    const handleDelete = async () => {
        try {
            const token = localStorage.getItem('token');
            await axios.delete(
                `http://localhost:8000/channels/${channel.id}`,
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setShowDeleteConfirm(false);
            if (onChannelDelete) {
                onChannelDelete();
            }
        } catch (err) {
            setError('Failed to delete channel');
        }
    };

    if (showDeleteConfirm) {
        return (
            <div className="border-b border-gray-200 p-4 bg-white">
                <div className="space-y-4">
                    <p className="text-gray-800">Are you sure you want to delete this channel? This action cannot be undone.</p>
                    <div className="flex justify-end gap-2">
                        <button
                            onClick={() => setShowDeleteConfirm(false)}
                            className="px-4 py-2 text-gray-600 hover:text-gray-800"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={handleDelete}
                            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                        >
                            Delete Channel
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    if (isEditing && isOwner) {
        return (
            <div className="border-b border-gray-200 p-4 bg-white">
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            className="w-full p-2 border rounded text-gray-900"
                            placeholder="Channel name"
                            required
                        />
                    </div>
                    <div>
                        <textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            className="w-full p-2 border rounded text-gray-900"
                            placeholder="Add a description..."
                            rows={2}
                        />
                    </div>
                    {error && <p className="text-red-500">{error}</p>}
                    <div className="flex justify-end gap-2">
                        <button
                            type="button"
                            onClick={handleCancel}
                            className="px-4 py-2 text-gray-600 hover:text-gray-800"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                        >
                            Save Changes
                        </button>
                    </div>
                </form>
            </div>
        );
    }

    return (
        <div className="border-b border-gray-200 p-4 bg-white">
            <div className="flex items-start justify-between">
                <div>
                    <h2 className="text-xl font-bold text-gray-900"># {channel.name}</h2>
                    {channel.description && (
                        <p className="text-gray-600 mt-1">{channel.description}</p>
                    )}
                </div>
                {isOwner && (
                    <div className="flex gap-2">
                        <button
                            onClick={handleStartEditing}
                            className="text-gray-400 hover:text-gray-600"
                            title="Edit channel"
                        >
                            <PencilIcon className="h-5 w-5" />
                        </button>
                        <button
                            onClick={() => setShowDeleteConfirm(true)}
                            className="text-gray-400 hover:text-red-600"
                            title="Delete channel"
                        >
                            <TrashIcon className="h-5 w-5" />
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
} 