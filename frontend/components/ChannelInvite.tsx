import { useState } from 'react';
import { ClipboardDocumentIcon, CheckIcon } from '@heroicons/react/24/outline';

interface ChannelInviteProps {
    channelId: number;
    joinCode: string | null;
    onGenerateInvite: () => void;
}

export default function ChannelInvite({ channelId, joinCode, onGenerateInvite }: ChannelInviteProps) {
    const [copied, setCopied] = useState(false);

    const handleCopy = async () => {
        if (joinCode) {
            try {
                await navigator.clipboard.writeText(joinCode);
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        }
    };

    const inviteUrl = joinCode 
        ? `${window.location.origin}/join?code=${joinCode}`
        : null;

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h3 className="text-base font-semibold leading-6 text-gray-900">
                    Channel Invite
                </h3>
                <button
                    type="button"
                    onClick={onGenerateInvite}
                    className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                >
                    Generate New Invite
                </button>
            </div>

            {joinCode && (
                <div className="mt-2 space-y-3">
                    <div>
                        <label htmlFor="invite-code" className="block text-sm font-medium leading-6 text-gray-900">
                            Invite Code
                        </label>
                        <div className="mt-1 flex rounded-md shadow-sm">
                            <div className="relative flex flex-grow items-stretch focus-within:z-10">
                                <input
                                    type="text"
                                    name="invite-code"
                                    id="invite-code"
                                    className="block w-full rounded-none rounded-l-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                    value={joinCode}
                                    readOnly
                                />
                            </div>
                            <button
                                type="button"
                                onClick={handleCopy}
                                className="relative -ml-px inline-flex items-center gap-x-1.5 rounded-r-md px-3 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                            >
                                {copied ? (
                                    <CheckIcon className="h-5 w-5 text-green-600" aria-hidden="true" />
                                ) : (
                                    <ClipboardDocumentIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
                                )}
                                {copied ? 'Copied!' : 'Copy'}
                            </button>
                        </div>
                    </div>

                    <div>
                        <label htmlFor="invite-url" className="block text-sm font-medium leading-6 text-gray-900">
                            Invite URL
                        </label>
                        <div className="mt-1 flex rounded-md shadow-sm">
                            <div className="relative flex flex-grow items-stretch focus-within:z-10">
                                <input
                                    type="text"
                                    name="invite-url"
                                    id="invite-url"
                                    className="block w-full rounded-none rounded-l-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                    value={inviteUrl || ''}
                                    readOnly
                                />
                            </div>
                            <button
                                type="button"
                                onClick={() => {
                                    if (inviteUrl) {
                                        navigator.clipboard.writeText(inviteUrl);
                                        setCopied(true);
                                        setTimeout(() => setCopied(false), 2000);
                                    }
                                }}
                                className="relative -ml-px inline-flex items-center gap-x-1.5 rounded-r-md px-3 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                            >
                                {copied ? (
                                    <CheckIcon className="h-5 w-5 text-green-600" aria-hidden="true" />
                                ) : (
                                    <ClipboardDocumentIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
                                )}
                                {copied ? 'Copied!' : 'Copy'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {!joinCode && (
                <p className="text-sm text-gray-500">
                    No invite code generated yet. Click the button above to generate one.
                </p>
            )}
        </div>
    );
} 