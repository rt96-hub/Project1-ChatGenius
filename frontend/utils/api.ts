'use client';

import axios from 'axios';
import { useAuth0 } from '@auth0/auth0-react';

// Create an axios instance
const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Create a function to get the API instance with auth configuration
export function createAuthenticatedApi() {
  const { getAccessTokenSilently } = useAuth0();

  // Add a request interceptor to automatically add the token
  api.interceptors.request.use(async (config) => {
    try {
      const token = await getAccessTokenSilently();
      config.headers.Authorization = `Bearer ${token}`;
    } catch (error) {
      console.error('Error getting access token:', error);
    }
    return config;
  }, (error) => {
    return Promise.reject(error);
  });

  return api;
}

export default api; 