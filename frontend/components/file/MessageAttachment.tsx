'use client';

import React, { useState } from 'react';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import { useApi } from '@/hooks/useApi';

interface MessageAttachmentProps {
  id: number;
  fileName: string;
  fileSize: number;
  contentType: string;
}

export const MessageAttachment: React.FC<MessageAttachmentProps> = ({
  id,
  fileName,
  fileSize,
  contentType,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const api = useApi();

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  };

  const getFileIcon = () => {
    if (contentType.startsWith('image/')) {
      return '🖼️';
    } else if (contentType.startsWith('video/')) {
      return '🎥';
    } else if (contentType === 'application/pdf') {
      return '📄';
    } else if (contentType.startsWith('text/')) {
      return '📝';
    }
    return '📎';
  };

  const handleDownload = async () => {
    try {
      setIsLoading(true);
      const response = await api.get(`/files/${id}/download-url`);
      if (!response.data) throw new Error('Failed to get download URL');
      
      const { download_url } = response.data;
      
      // Create a temporary link and click it to start the download
      const link = document.createElement('a');
      link.href = download_url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Failed to download file');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center gap-3 p-2 bg-gray-50 dark:bg-gray-800 rounded-lg max-w-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors group">
      <span className="text-2xl" role="img" aria-label="File type">
        {getFileIcon()}
      </span>
      
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
          {fileName}
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          {formatFileSize(fileSize)}
        </p>
      </div>

      <button
        onClick={handleDownload}
        disabled={isLoading}
        className={`p-2 rounded-full ${
          isLoading
            ? 'opacity-50 cursor-not-allowed'
            : 'hover:bg-gray-200 dark:hover:bg-gray-600'
        } transition-colors`}
        aria-label="Download file"
      >
        <ArrowDownTrayIcon className={`h-5 w-5 ${
          isLoading ? 'text-gray-400' : 'text-gray-500 group-hover:text-gray-700 dark:group-hover:text-gray-300'
        }`} />
      </button>
    </div>
  );
}; 