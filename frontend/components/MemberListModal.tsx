import { XMarkIcon } from '@heroicons/react/24/outline';
import type { Channel, ChannelRole } from '../types/channel';
import MembersList from './MembersList';

interface MemberListModalProps {
    isOpen: boolean;
    onClose: () => void;
    channel: Channel;
    currentUserId: number;
    onUpdateMemberRole: (userId: number, role: ChannelRole) => void;
    onRemoveMember: (userId: number) => void;
    onLeaveChannel: () => void;
}

export default function MemberListModal({
    isOpen,
    onClose,
    channel,
    currentUserId,
    onUpdateMemberRole,
    onRemoveMember,
    onLeaveChannel
}: MemberListModalProps) {
    const isOwner = channel.owner_id === currentUserId;

    if (!isOpen) return null;

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
                    className="relative w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all"
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

                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-medium leading-6 text-gray-900">
                            Channel Members
                        </h3>
                        {!isOwner && (
                            <button
                                onClick={onLeaveChannel}
                                className="px-3 py-2 text-sm font-semibold text-red-600 hover:text-red-500 rounded-md hover:bg-red-50"
                            >
                                Leave Channel
                            </button>
                        )}
                    </div>

                    <div className="mt-4">
                        <MembersList
                            members={channel.users}
                            currentUserId={currentUserId}
                            isOwner={isOwner}
                            onUpdateRole={onUpdateMemberRole}
                            onRemoveMember={onRemoveMember}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
} 