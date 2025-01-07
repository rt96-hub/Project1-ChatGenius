'use client';

import { useAuth } from '@/hooks/useAuth';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { createAuthenticatedApi } from '@/utils/api';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, login, getAccessTokenSilently } = useAuth();
  const [isVerifying, setIsVerifying] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const verifyAuth = async () => {
      console.log('Auth state:', { isAuthenticated, isLoading });
      
      if (isAuthenticated) {
        try {
          const token = await getAccessTokenSilently();
          console.log('Protected route token:', token);
          const api = createAuthenticatedApi(token);
          // Verify token with backend
          await api.get('/auth/verify');
          setIsVerifying(false);
        } catch (error) {
          console.error('Token verification failed:', error);
          login();
        }
      } else if (!isLoading) {
        console.log('Not authenticated, redirecting to login');
        login();
      }
    };

    verifyAuth();
  }, [isLoading, isAuthenticated, login, getAccessTokenSilently]);

  if (isLoading || isVerifying) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return isAuthenticated ? <>{children}</> : null;
} 