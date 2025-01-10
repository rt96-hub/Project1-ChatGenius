'use client';

import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create an axios instance
const api = axios.create({
  baseURL: API_URL,
});

// Create a function to get the API instance with auth configuration
export function createAuthenticatedApi(token: string) {
  // Add the authorization header
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  return api;
}

export default api;