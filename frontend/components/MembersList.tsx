import { useState } from 'react';
import { UserCircleIcon } from '@heroicons/react/24/outline';
import Image from 'next/image';
import type { ChannelMember, ChannelRole } from '../types/channel';
import ConfirmDialog from './ConfirmDialog';
import UserProfilePopout from './UserProfilePopout';

interface MembersListProps {
    members: ChannelMember[];
    currentUserId: number;
    isOwner: boolean;
    onUpdateRole: (userId: number, role: ChannelRole) => void;
    onRemoveMember: (userId: number) => void;
    onNavigateToDM?: (channelId: number) => void;
}

export default function MembersList({
    members,
    currentUserId,
    isOwner,
    onUpdateRole,
    onRemoveMember,
    onNavigateToDM
}: MembersListProps) {
    const [selectedMember, setSelectedMember] = useState<ChannelMember | null>(null);
    const [showRemoveConfirm, setShowRemoveConfirm] = useState(false);
    const [showProfile, setShowProfile] = useState<ChannelMember | null>(null);

    const handleRemove = (member: ChannelMember) => {
        setSelectedMember(member);
        setShowRemoveConfirm(true);
    };

    const confirmRemove = () => {
        if (selectedMember) {
            onRemoveMember(selectedMember.id);
            setShowRemoveConfirm(false);
            setSelectedMember(null);
        }
    };

    return (
        <div className="space-y-4">
            <div className="flow-root">
                <ul role="list" className="-my-5 divide-y divide-gray-200">
                    {members.map((member) => (
                        <li key={member.id} className="py-4">
                            <div className="flex items-center justify-between">
                                <div 
                                    className="flex items-center min-w-0 gap-x-3 cursor-pointer"
                                    onClick={() => setShowProfile(member)}
                                >
                                    {member.picture ? (
                                        <Image 
                                            src={member.picture} 
                                            alt={member.name}
                                            width={32}
                                            height={32}
                                            className="rounded-full"
                                        />
                                    ) : (
                                        <UserCircleIcon className="h-8 w-8 text-gray-400" />
                                    )}
                                    <div className="min-w-0">
                                        <p className="text-sm font-medium text-gray-900 truncate">
                                            {member.name}
                                        </p>
                                        <p className="text-sm text-gray-500 truncate">
                                            {member.email}
                                        </p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-x-3">
                                    {isOwner && member.id !== currentUserId && (
                                        <>
                                            <select
                                                value={member.role}
                                                onChange={(e) => onUpdateRole(member.id, e.target.value as ChannelRole)}
                                                className="block w-full rounded-md border-0 py-1.5 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                            >
                                                <option value="member">Member</option>
                                                <option value="moderator">Moderator</option>
                                            </select>
                                            <button
                                                type="button"
                                                onClick={() => handleRemove(member)}
                                                className="rounded-md bg-white px-2.5 py-1.5 text-sm font-semibold text-red-600 shadow-sm ring-1 ring-inset ring-red-300 hover:bg-red-50"
                                            >
                                                Remove
                                            </button>
                                        </>
                                    )}
                                    {!isOwner && member.role === 'owner' && (
                                        <span className="inline-flex items-center rounded-md bg-indigo-50 px-2 py-1 text-xs font-medium text-indigo-700 ring-1 ring-inset ring-indigo-700/10">
                                            Owner
                                        </span>
                                    )}
                                    {!isOwner && member.role !== 'owner' && (
                                        <span className="inline-flex items-center rounded-md bg-gray-50 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10">
                                            {member.role}
                                        </span>
                                    )}
                                    {isOwner && member.id === currentUserId && (
                                        <span className="inline-flex items-center rounded-md bg-indigo-50 px-2 py-1 text-xs font-medium text-indigo-700 ring-1 ring-inset ring-indigo-700/10">
                                            Owner
                                        </span>
                                    )}
                                </div>
                            </div>
                        </li>
                    ))}
                </ul>
            </div>

            {showProfile && (
                <UserProfilePopout
                    user={showProfile}
                    isCurrentUser={showProfile.id === currentUserId}
                    onClose={() => setShowProfile(null)}
                    onNavigateToDM={onNavigateToDM}
                />
            )}

            <ConfirmDialog
                isOpen={showRemoveConfirm}
                onClose={() => setShowRemoveConfirm(false)}
                onConfirm={confirmRemove}
                title="Remove Member"
                message={`Are you sure you want to remove ${selectedMember?.name} from the channel?`}
                confirmText="Remove"
                type="danger"
            />
        </div>
    );
} 