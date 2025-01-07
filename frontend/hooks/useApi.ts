'use client';

import { useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import api from '@/utils/api';

export function useApi() {
  const { getAccessTokenSilently } = useAuth0();

  useEffect(() => {
    // Set up the request interceptor
    const interceptor = api.interceptors.request.use(async (config) => {
      try {
        const token = await getAccessTokenSilently();
        console.log('Token acquired:', token);
        console.log('Request headers before:', config.headers);
        config.headers.Authorization = `Bearer ${token}`;
        console.log('Request headers after:', config.headers);
        console.log('Request URL:', config.url);
      } catch (error) {
        console.error('Error getting access token:', error);
      }
      return config;
    });

    // Clean up the interceptor when the component unmounts
    return () => {
      api.interceptors.request.eject(interceptor);
    };
  }, [getAccessTokenSilently]);

  return api;
} 