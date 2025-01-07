'use client';

import axios from 'axios';

// Create an axios instance
const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Create a function to get the API instance with auth configuration
export function createAuthenticatedApi(token: string) {
  // Add the authorization header
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  return api;
}

export default api; 