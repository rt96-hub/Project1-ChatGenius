'use client';

import React from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface FileUploadProgressProps {
  fileName: string;
  progress: number;
  onCancel: () => void;
  error?: string;
}

export const FileUploadProgress: React.FC<FileUploadProgressProps> = ({
  fileName,
  progress,
  onCancel,
  error,
}) => {
  return (
    <div className="w-full max-w-sm bg-white dark:bg-gray-800 rounded-lg shadow p-3">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
          {fileName}
        </span>
        <button
          onClick={onCancel}
          className="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
          aria-label="Cancel upload"
        >
          <XMarkIcon className="h-4 w-4 text-gray-500" />
        </button>
      </div>

      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mb-2">
        <div
          className={`h-2.5 rounded-full transition-all duration-300 ${
            error ? 'bg-red-500' : 'bg-blue-500'
          }`}
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="flex justify-between items-center">
        <span className="text-xs text-gray-500 dark:text-gray-400">
          {error ? (
            <span className="text-red-500">{error}</span>
          ) : (
            `${Math.round(progress)}%`
          )}
        </span>
        {error && (
          <button
            onClick={onCancel}
            className="text-xs text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300"
          >
            Retry
          </button>
        )}
      </div>
    </div>
  );
}; 