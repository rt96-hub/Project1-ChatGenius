'use client';

import React from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface FilePreviewProps {
  file: File;
  onRemove: () => void;
}

export const FilePreview: React.FC<FilePreviewProps> = ({ file, onRemove }) => {
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  };

  return (
    <div className="flex items-center gap-2 p-2 bg-gray-50 dark:bg-gray-800 rounded-md max-w-sm">
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
          {file.name}
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          {formatFileSize(file.size)}
        </p>
      </div>
      
      <button
        type="button"
        onClick={onRemove}
        className="p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
        aria-label="Remove file"
      >
        <XMarkIcon className="h-4 w-4 text-gray-500" />
      </button>
    </div>
  );
}; 