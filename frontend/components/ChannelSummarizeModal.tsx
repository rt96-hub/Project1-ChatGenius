import { useState } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { useApi } from '@/hooks/useApi';
import { useAI } from '@/hooks/useAI';

interface ChannelSummarizeModalProps {
    isOpen: boolean;
    onClose: () => void;
    channelId: number;
}

export default function ChannelSummarizeModal({ isOpen, onClose, channelId }: ChannelSummarizeModalProps) {
    const api = useApi();
    const { isLoading: aiLoading } = useAI();
    const [quantity, setQuantity] = useState('');
    const [timeUnit, setTimeUnit] = useState('days');
    const [summary, setSummary] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    if (!isOpen) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        setSummary('');

        try {
            const response = await api.get(`/ai/channels/${channelId}/summarize`, {
                params: {
                    quantity: parseInt(quantity),
                    time_unit: timeUnit,
                }
            });

            setSummary(response.data.summary);
        } catch (err) {
            console.error('Failed to generate summary:', err);
            setError('Failed to generate summary. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-lg max-h-[80vh] flex flex-col">
                <div className="flex justify-between items-center p-4 border-b shrink-0">
                    <h2 className="text-lg font-semibold">Summarize Channel Messages</h2>
                    <button
                        onClick={onClose}
                        className="text-gray-500 hover:text-gray-700"
                    >
                        <XMarkIcon className="h-5 w-5" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-4 border-b shrink-0">
                    <div className="flex gap-2 items-center">
                        <input
                            type="number"
                            value={quantity}
                            onChange={(e) => setQuantity(e.target.value)}
                            min="1"
                            required
                            placeholder="Enter number"
                            className="border rounded px-3 py-2 w-32 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <select
                            value={timeUnit}
                            onChange={(e) => setTimeUnit(e.target.value)}
                            className="border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="hours">Hours</option>
                            <option value="days">Days</option>
                            <option value="weeks">Weeks</option>
                        </select>
                        <button
                            type="submit"
                            disabled={isLoading || aiLoading || !quantity}
                            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-blue-300 disabled:cursor-not-allowed ml-2"
                        >
                            {isLoading || aiLoading ? 'Generating...' : 'Generate Summary'}
                        </button>
                    </div>
                </form>

                <div className="p-4 overflow-y-auto flex-grow">
                    {error && (
                        <div className="text-red-500 mb-4">{error}</div>
                    )}
                    {summary && (
                        <div className="bg-gray-50 rounded-lg p-4">
                            <h3 className="text-gray-900 font-semibold mb-2">Summary:</h3>
                            <div className="prose prose-sm max-w-none">
                                <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">{summary}</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
} 