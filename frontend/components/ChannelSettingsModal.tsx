import { useState, useEffect } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { useApi } from '@/hooks/useApi';
import type { Channel, ChannelRole } from '../types/channel';
import MembersList from './MembersList';
import ConfirmDialog from './ConfirmDialog';

interface ChannelSettingsModalProps {
    isOpen: boolean;
    onClose: () => void;
    channel: Channel;
    currentUserId: number;
    onUpdateChannel: (updates: Partial<Channel>) => void;
    onUpdateMemberRole: (userId: number, role: ChannelRole) => void;
    onRemoveMember: (userId: number) => void;
    onDeleteChannel: () => void;
}

function classNames(...classes: string[]) {
    return classes.filter(Boolean).join(' ');
}

export default function ChannelSettingsModal({
    isOpen,
    onClose,
    channel,
    currentUserId,
    onUpdateChannel,
    onUpdateMemberRole,
    onRemoveMember,
    onDeleteChannel
}: ChannelSettingsModalProps) {
    const api = useApi();
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [activeTab, setActiveTab] = useState('general');
    const [name, setName] = useState(channel.name);
    const [description, setDescription] = useState(channel.description || '');
    const [isSaving, setIsSaving] = useState(false);
    const [isTogglingPrivacy, setIsTogglingPrivacy] = useState(false);
    const isOwner = channel.owner_id === currentUserId;

    useEffect(() => {
        setName(channel.name);
        setDescription(channel.description || '');
    }, [channel]);

    useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === 'Escape' && isOpen) {
                onClose();
            }
        };

        if (isOpen) {
            document.addEventListener('keydown', handleEscape);
            document.body.style.overflow = 'hidden';
        }

        return () => {
            document.removeEventListener('keydown', handleEscape);
            document.body.style.overflow = 'unset';
        };
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    const tabs = [
        { id: 'general', name: 'General' },
        { id: 'privacy', name: 'Privacy' },
        { id: 'members', name: 'Members' }
    ];

    const handleUpdateChannel = async () => {
        if (!isOwner) return;
        
        setIsSaving(true);
        try {
            await api.put(`/channels/${channel.id}`, {
                name,
                description: description || null
            });
            onUpdateChannel({ name, description: description || undefined });
        } catch (error) {
            console.error('Failed to update channel:', error);
        } finally {
            setIsSaving(false);
        }
    };

    const handleDeleteChannel = async () => {
        try {
            await api.delete(`/channels/${channel.id}`);
            onDeleteChannel();
            onClose();
        } catch (error) {
            console.error('Failed to delete channel:', error);
        }
    };

    const renderTabContent = () => {
        switch (activeTab) {
            case 'general':
                return (
                    <div className="space-y-6">
                        <div>
                            <label htmlFor="channel-name" className="block text-sm font-medium leading-6 text-gray-900">
                                Channel Name
                            </label>
                            <div className="mt-2">
                                <input
                                    type="text"
                                    name="channel-name"
                                    id="channel-name"
                                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    disabled={!isOwner}
                                />
                            </div>
                        </div>

                        <div>
                            <label htmlFor="description" className="block text-sm font-medium leading-6 text-gray-900">
                                Description
                            </label>
                            <div className="mt-2">
                                <textarea
                                    id="description"
                                    name="description"
                                    rows={3}
                                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                    value={description}
                                    onChange={(e) => setDescription(e.target.value)}
                                    disabled={!isOwner}
                                />
                            </div>
                        </div>

                        <div className="flex justify-between items-center pt-4">
                            {isOwner && (
                                <button
                                    type="button"
                                    onClick={handleUpdateChannel}
                                    disabled={isSaving}
                                    className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {isSaving ? 'Saving...' : 'Save Changes'}
                                </button>
                            )}
                            {isOwner && (
                                <button
                                    type="button"
                                    onClick={() => setShowDeleteConfirm(true)}
                                    className="rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600"
                                >
                                    Delete Channel
                                </button>
                            )}
                        </div>
                    </div>
                );
            case 'privacy':
                return (
                    <div className="space-y-6">
                        <div>
                            <div className="flex items-center">
                                <button
                                    type="button"
                                    role="switch"
                                    aria-checked={channel.is_private}
                                    onClick={async () => {
                                        if (!isOwner || isTogglingPrivacy) return;
                                        setIsTogglingPrivacy(true);
                                        try {
                                            await api.put(`/channels/${channel.id}/privacy`, {
                                                is_private: !channel.is_private
                                            });
                                            onUpdateChannel({ is_private: !channel.is_private });
                                        } catch (error) {
                                            console.error('Failed to update channel privacy:', error);
                                        } finally {
                                            setIsTogglingPrivacy(false);
                                        }
                                    }}
                                    className={classNames(
                                        channel.is_private ? 'bg-indigo-600' : 'bg-gray-200',
                                        'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2',
                                        !isOwner ? 'cursor-not-allowed opacity-50' : '',
                                        isTogglingPrivacy ? 'opacity-50 cursor-wait' : ''
                                    )}
                                    disabled={!isOwner || isTogglingPrivacy}
                                >
                                    <span
                                        aria-hidden="true"
                                        className={classNames(
                                            channel.is_private ? 'translate-x-5' : 'translate-x-0',
                                            'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out'
                                        )}
                                    />
                                </button>
                                <span className="ml-3">
                                    <span className="text-sm font-medium text-gray-900">
                                        Private Channel
                                    </span>
                                </span>
                            </div>
                            <p className="mt-2 text-sm text-gray-500">
                                When enabled, the channel cannot be found by non members in search and users can only join through invites.
                            </p>
                        </div>
                    </div>
                );
            case 'members':
                return (
                    <MembersList
                        members={channel.users}
                        currentUserId={currentUserId}
                        isOwner={isOwner}
                        onUpdateRole={onUpdateMemberRole}
                        onRemoveMember={onRemoveMember}
                    />
                );
            default:
                return null;
        }
    };

    return (
        <div className="fixed inset-0 z-50 overflow-y-auto">
            {/* Backdrop */}
            <div 
                className="fixed inset-0 bg-black bg-opacity-25 transition-opacity"
                onClick={onClose}
            />

            {/* Dialog */}
            <div className="flex min-h-full items-center justify-center p-4 text-center">
                <div 
                    className="relative w-full max-w-2xl transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all"
                    onClick={e => e.stopPropagation()}
                >
                    <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                        <button
                            type="button"
                            className="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                            onClick={onClose}
                        >
                            <span className="sr-only">Close</span>
                            <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                        </button>
                    </div>

                    <h3 className="text-lg font-medium leading-6 text-gray-900">
                        Channel Settings
                    </h3>

                    <div className="mt-6">
                        {/* Tabs */}
                        <div className="border-b border-gray-200">
                            <nav className="-mb-px flex space-x-8" aria-label="Tabs">
                                {tabs.map((tab) => (
                                    <button
                                        key={tab.id}
                                        onClick={() => setActiveTab(tab.id)}
                                        className={classNames(
                                            activeTab === tab.id
                                                ? 'border-indigo-500 text-indigo-600'
                                                : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700',
                                            'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium'
                                        )}
                                    >
                                        {tab.name}
                                    </button>
                                ))}
                            </nav>
                        </div>

                        {/* Tab Content */}
                        <div className="mt-4">
                            {renderTabContent()}
                        </div>
                    </div>
                </div>
            </div>

            <ConfirmDialog
                isOpen={showDeleteConfirm}
                onClose={() => setShowDeleteConfirm(false)}
                onConfirm={handleDeleteChannel}
                title="Delete Channel"
                message="Are you sure you want to delete this channel? This action cannot be undone."
                confirmText="Delete"
                type="danger"
            />
        </div>
    );
} 