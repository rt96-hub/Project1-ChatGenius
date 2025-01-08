import { useEffect } from 'react';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

interface ConfirmDialogProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    title: string;
    message: string | JSX.Element;
    confirmText?: string;
    cancelText?: string;
    type?: 'danger' | 'warning';
}

export default function ConfirmDialog({
    isOpen,
    onClose,
    onConfirm,
    title,
    message,
    confirmText = 'Confirm',
    cancelText = 'Cancel',
    type = 'danger'
}: ConfirmDialogProps) {
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
                    <div className="flex items-center gap-3">
                        <div className={`rounded-full p-2 ${type === 'danger' ? 'bg-red-100' : 'bg-yellow-100'}`}>
                            <ExclamationTriangleIcon 
                                className={`h-6 w-6 ${type === 'danger' ? 'text-red-600' : 'text-yellow-600'}`} 
                            />
                        </div>
                        <h3 className="text-lg font-medium leading-6 text-gray-900">
                            {title}
                        </h3>
                    </div>

                    <div className="mt-3">
                        {typeof message === 'string' ? (
                            <p className="text-sm text-gray-500">{message}</p>
                        ) : (
                            message
                        )}
                    </div>

                    <div className="mt-6 flex justify-end gap-3">
                        <button
                            type="button"
                            className="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-500 focus-visible:ring-offset-2"
                            onClick={onClose}
                        >
                            {cancelText}
                        </button>
                        <button
                            type="button"
                            className={`inline-flex justify-center rounded-md border border-transparent px-4 py-2 text-sm font-medium text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 
                                ${type === 'danger' 
                                    ? 'bg-red-600 hover:bg-red-700 focus-visible:ring-red-500'
                                    : 'bg-yellow-600 hover:bg-yellow-700 focus-visible:ring-yellow-500'
                                }`}
                            onClick={onConfirm}
                        >
                            {confirmText}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
} 