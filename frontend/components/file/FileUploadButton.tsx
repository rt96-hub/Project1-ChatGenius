'use client';

import React, { useRef, useState } from 'react';
import { PaperClipIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import { FILE_UPLOAD_CONFIG } from '@/config/constants';

interface FileUploadButtonProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
  maxSizeMB?: number;
  allowedTypes?: string[];
}

export const FileUploadButton: React.FC<FileUploadButtonProps> = ({
  onFileSelect,
  disabled = false,
  maxSizeMB = FILE_UPLOAD_CONFIG.MAX_FILE_SIZE_MB,
  allowedTypes = FILE_UPLOAD_CONFIG.ALLOWED_FILE_TYPES,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isHovered, setIsHovered] = useState(false);

  const handleClick = () => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file size
    if (file.size > maxSizeMB * 1024 * 1024) {
      toast.error(`File size must be less than ${maxSizeMB}MB`);
      return;
    }

    // Validate file type
    const isAllowedType = allowedTypes.some(type => {
      if (type.endsWith('/*')) {
        const baseType = type.split('/')[0];
        return file.type.startsWith(`${baseType}/`);
      }
      return type === file.type;
    });

    if (!isAllowedType) {
      toast.error('File type not allowed');
      return;
    }

    onFileSelect(file);
    
    // Reset the input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="relative">
      <button
        type="button"
        onClick={handleClick}
        disabled={disabled}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className={`p-2 rounded-full transition-colors ${
          disabled
            ? 'opacity-50 cursor-not-allowed'
            : 'hover:bg-gray-100 dark:hover:bg-gray-700'
        }`}
        aria-label="Attach file"
      >
        <PaperClipIcon className="h-5 w-5 text-gray-500" />
      </button>
      
      {isHovered && !disabled && (
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-sm text-white bg-gray-800 rounded whitespace-nowrap">
          Attach file
        </div>
      )}

      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        onChange={handleFileChange}
        accept={allowedTypes.join(',')}
        aria-label="File upload"
      />
    </div>
  );
}; 