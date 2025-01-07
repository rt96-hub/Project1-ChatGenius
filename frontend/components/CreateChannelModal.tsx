import React, { useState } from 'react';
import axios from 'axios';

interface CreateChannelModalProps {
    isOpen: boolean;
    onClose: () => void;
    onChannelCreated: () => void;
}

const CreateChannelModal: React.FC<CreateChannelModalProps> = ({ isOpen, onClose, onChannelCreated }) => {
    const [channelName, setChannelName] = useState('');
    const [description, setDescription] = useState('');
    const [error, setError] = useState('');

    if (!isOpen) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token');
            await axios.post('http://localhost:8000/channels/', 
                { 
                    name: channelName,
                    description: description.trim() || null
                },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setChannelName('');
            setDescription('');
            setError('');
            onChannelCreated();
            onClose();
        } catch (err) {
            setError('Failed to create channel');
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <div className="bg-white p-6 rounded-lg shadow-lg w-96">
                <h2 className="text-xl font-bold mb-4">Create New Channel</h2>
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        value={channelName}
                        onChange={(e) => setChannelName(e.target.value)}
                        placeholder="Channel name"
                        className="w-full p-2 border rounded mb-4 text-gray-900"
                        required
                    />
                    <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Channel description (optional)"
                        className="w-full p-2 border rounded mb-4 text-gray-900"
                        rows={3}
                    />
                    {error && <p className="text-red-500 mb-4">{error}</p>}
                    <div className="flex justify-end gap-2">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-gray-600 hover:text-gray-800"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                        >
                            Create
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateChannelModal; 