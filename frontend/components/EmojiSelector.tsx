import { useEffect, useState, useRef, useCallback } from 'react';
import { useApi } from '@/hooks/useApi';
import Image from 'next/image';

interface Reaction {
  id: number;
  code: string;
  is_system: boolean;
  image_url: string | null;
  created_at: string;
}

interface EmojiSelectorProps {
  onSelect: (reactionId: number) => void;
  onClose: () => void;
  position: { top: number; left: number };
}

export default function EmojiSelector({ onSelect, onClose, position }: EmojiSelectorProps) {
  const api = useApi();
  const [reactions, setReactions] = useState<Reaction[]>([]);
  const [loading, setLoading] = useState(true);
  const popoutRef = useRef<HTMLDivElement>(null);
  const bufferSize = 15; // pixels of buffer zone
  const [isMouseInBuffer, setIsMouseInBuffer] = useState(false);

  // Separate useEffect for API call
  useEffect(() => {
    const fetchReactions = async () => {
      try {
        const response = await api.get('/reactions/');
        setReactions(response.data);
      } catch (error) {
        console.error('Failed to fetch reactions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchReactions();
  }, [api]); // Add api dependency

  // Memoize the mouse move handler
  const handleMouseMove = useCallback((event: MouseEvent) => {
    if (!popoutRef.current) return;

    const rect = popoutRef.current.getBoundingClientRect();
    const isInBuffer = 
      event.clientX >= rect.left - bufferSize &&
      event.clientX <= rect.right + bufferSize &&
      event.clientY >= rect.top - bufferSize &&
      event.clientY <= rect.bottom + bufferSize;

    setIsMouseInBuffer(isInBuffer);
    
    if (!isInBuffer && !isMouseInBuffer) {
      onClose();
    }
  }, [isMouseInBuffer, onClose, bufferSize]);

  // Separate useEffect for event listeners
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (popoutRef.current && !popoutRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('mousemove', handleMouseMove);
    
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('mousemove', handleMouseMove);
    };
  }, [handleMouseMove]); // Only depend on the memoized handler

  // Map emoji codes to actual emojis
  const emojiMap: { [key: string]: string } = {
    thumbs_up: '👍',
    heart: '❤️',
    smile: '😊',
    laugh: '😂',
    sad: '😢',
    angry: '😠',
    clap: '👏',
    fire: '🔥',
    poop: '💩',
  };

  return (
    <div
      ref={popoutRef}
      className="absolute z-50 bg-white rounded-lg shadow-lg border border-gray-200 p-2"
      style={{
        top: `${position.top}px`,
        left: `${position.left}px`,
        transform: 'translateY(-100%)', // Move up by its own height
        marginBottom: '-8px', // Add a small gap between selector and message
      }}
    >
      {loading ? (
        <div className="flex items-center justify-center p-2">
          <div className="w-5 h-5 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="grid grid-cols-5 gap-1" style={{ width: '180px' }}>
          {reactions.map((reaction) => (
            <button
              key={reaction.id}
              onClick={() => onSelect(reaction.id)}
              className="hover:bg-gray-100 p-1.5 rounded-full transition-colors flex items-center justify-center"
              title={reaction.code}
            >
              {reaction.image_url ? (
                <Image
                  src={reaction.image_url}
                  alt={reaction.code}
                  width={24}
                  height={24}
                  className="object-contain"
                />
              ) : (
                <span className="text-xl leading-none">{emojiMap[reaction.code] || '❓'}</span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
} 