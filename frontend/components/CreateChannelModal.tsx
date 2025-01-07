import React, { useState } from 'react';
import { useApi } from '@/hooks/useApi';

interface CreateChannelModalProps {
    isOpen: boolean;
    onClose: () => void;
    onChannelCreated: () => void;
}

export default function CreateChannelModal({ isOpen, onClose, onChannelCreated }: CreateChannelModalProps) {
    const api = useApi();
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        try {
            await api.post('/channels/', {
                name,
                description: description || null
            });
            
            setName('');
            setDescription('');
            onChannelCreated();
            onClose();
        } catch (error) {
            setError('Failed to create channel');
            console.error('Failed to create channel:', error);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
                <h2 className="text-xl font-bold mb-4">Create New Channel</h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                            Channel Name
                        </label>
                        <input
                            type="text"
                            id="name"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            required
                        />
                    </div>
                    <div>
                        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                            Description (optional)
                        </label>
                        <textarea
                            id="description"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            rows={3}
                        />
                    </div>
                    {error && (
                        <p className="text-red-500 text-sm">{error}</p>
                    )}
                    <div className="flex justify-end gap-2">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="px-4 py-2 text-sm font-medium text-white bg-blue-500 hover:bg-blue-600 rounded-md"
                        >
                            Create Channel
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
} 