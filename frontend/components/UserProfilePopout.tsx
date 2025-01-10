'use client';

import { useState, useEffect } from 'react';
import { XMarkIcon, PencilIcon } from '@heroicons/react/24/outline';
import { useApi } from '@/hooks/useApi';
import Image from 'next/image';

interface User {
  id: number;
  email: string;
  name: string;
  picture?: string;
  bio?: string;
}

interface UserProfilePopoutProps {
  user: User;
  isCurrentUser: boolean;
  onClose: () => void;
  onUpdate?: (updatedUser: User) => void;
  onNavigateToDM?: (channelId: number) => void;
}

export default function UserProfilePopout({ 
  user, 
  isCurrentUser, 
  onClose,
  onUpdate,
  onNavigateToDM
}: UserProfilePopoutProps) {
  const api = useApi();
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(user.name);
  const [bio, setBio] = useState(user.bio || '');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentUser, setCurrentUser] = useState<User>(user);
  const [isFetching, setIsFetching] = useState(true);
  const [isDMLoading, setIsDMLoading] = useState(false);

  // Fetch latest user data when modal opens
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        setIsFetching(true);
        const response = await api.get(isCurrentUser ? '/users/me' : `/users/${user.id}`);
        const userData = response.data;
        setCurrentUser(userData);
        setName(userData.name);
        setBio(userData.bio || '');
      } catch (err) {
        console.error('Failed to fetch user data:', err);
        setError('Failed to load user data.');
      } finally {
        setIsFetching(false);
      }
    };

    fetchUserData();
  }, [user.id, isCurrentUser, api]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isCurrentUser) return;

    setIsLoading(true);
    setError('');

    try {
      let updatedUser = { ...currentUser };
      
      // Update name if changed
      if (name !== currentUser.name) {
        console.log('Sending name update request:', { name });
        const nameResponse = await api.put('/users/me/name', { name });
        console.log('Name update response:', nameResponse.data);
        updatedUser = { ...updatedUser, ...nameResponse.data };
      }
      
      // Update bio if changed
      if (bio !== currentUser.bio) {
        console.log('Sending bio update request:', { bio });
        const bioResponse = await api.put('/users/me/bio', { bio });
        console.log('Bio update response:', bioResponse.data);
        updatedUser = { ...updatedUser, ...bioResponse.data };
      }

      setCurrentUser(updatedUser);
      if (onUpdate) {
        onUpdate(updatedUser);
      }
      setIsEditing(false);
    } catch (err) {
      console.error('Update failed:', err);
      setError('Failed to update profile. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setName(currentUser.name);
    setBio(currentUser.bio || '');
    setIsEditing(false);
    setError('');
  };

  // New function to handle DM creation/navigation
  const handleSendDM = async () => {
    if (!onNavigateToDM || isCurrentUser) return;
    
    try {
      setIsDMLoading(true);
      setError('');
      
      // First, check if a DM channel already exists
      const checkResponse = await api.get(`/channels/dm/check/${user.id}`);
      const existingChannelId = checkResponse.data.channel_id;
      
      if (existingChannelId) {
        // If DM exists, navigate to it
        onNavigateToDM(existingChannelId);
        onClose();
      } else {
        // If no DM exists, create a new one
        const createResponse = await api.post('/channels/dm', {
          user_ids: [user.id]
        });
        onNavigateToDM(createResponse.data.id);
        onClose();
      }
    } catch (err) {
      console.error('Failed to handle DM:', err);
      setError('Failed to open direct message. Please try again.');
    } finally {
      setIsDMLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6 relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
        >
          <XMarkIcon className="h-6 w-6" />
        </button>

        {isFetching ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-500">Loading...</div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Profile Picture */}
            <div className="flex justify-center">
              {currentUser.picture ? (
                <Image
                  src={currentUser.picture}
                  alt={`${currentUser.name}'s profile`}
                  width={96}
                  height={96}
                  className="rounded-full object-cover"
                />
              ) : (
                <div className="w-24 h-24 rounded-full bg-indigo-600 flex items-center justify-center text-white text-2xl font-medium">
                  {(currentUser.name || currentUser.email || '?')[0].toUpperCase()}
                </div>
              )}
            </div>

            {isEditing ? (
              /* Edit Form */
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                    Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="bio" className="block text-sm font-medium text-gray-700">
                    Bio
                  </label>
                  <textarea
                    id="bio"
                    value={bio}
                    onChange={(e) => setBio(e.target.value)}
                    rows={3}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    placeholder="Tell us about yourself..."
                  />
                </div>

                {error && (
                  <p className="text-sm text-red-600">{error}</p>
                )}

                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={handleCancel}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                    disabled={isLoading}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 disabled:opacity-50"
                    disabled={isLoading}
                  >
                    {isLoading ? 'Saving...' : 'Save'}
                  </button>
                </div>
              </form>
            ) : (
              /* View Mode */
              <div className="space-y-4">
                <div className="text-center">
                  <h2 className="text-xl font-bold text-gray-900">{currentUser.name}</h2>
                  <p className="text-sm text-gray-500">{currentUser.email}</p>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-gray-700">Bio</h3>
                  <p className="mt-1 text-sm text-gray-600 whitespace-pre-wrap">
                    {currentUser.bio || 'No bio yet.'}
                  </p>
                </div>

                {isCurrentUser ? (
                  <button
                    onClick={() => setIsEditing(true)}
                    className="mt-4 flex items-center justify-center w-full px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    <PencilIcon className="w-4 h-4 mr-2" />
                    Edit Profile
                  </button>
                ) : (
                  <button
                    onClick={handleSendDM}
                    disabled={isDMLoading}
                    className="mt-4 flex items-center justify-center w-full px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 disabled:opacity-50"
                  >
                    {isDMLoading ? 'Opening Chat...' : 'Send Direct Message'}
                  </button>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
} 