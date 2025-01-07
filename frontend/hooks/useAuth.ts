import { useAuth0 } from '@auth0/auth0-react';
import { useEffect } from 'react';
import { createAuthenticatedApi } from '@/utils/api';

export function useAuth() {
  const {
    isAuthenticated,
    isLoading,
    user,
    loginWithRedirect,
    logout,
    getAccessTokenSilently,
  } = useAuth0();

  useEffect(() => {
    console.log('Auth state changed:', { isAuthenticated, isLoading, user });
    
    const syncUserWithBackend = async () => {
      if (isAuthenticated && user) {
        try {
          const token = await getAccessTokenSilently();
          console.log('Syncing user with token:', token);
          const api = createAuthenticatedApi(token);
          await api.post('/auth/sync', {
            email: user.email,
            auth0_id: user.sub,
            name: user.name
          });
        } catch (error) {
          console.error('Error syncing user with backend:', error);
        }
      }
    };

    syncUserWithBackend();
  }, [isAuthenticated, user, getAccessTokenSilently]);

  const login = () => loginWithRedirect();

  const signOut = () => {
    logout({
      logoutParams: {
        returnTo: window.location.origin,
      },
    });
  };

  return {
    isAuthenticated,
    isLoading,
    user,
    login,
    signOut,
    getAccessTokenSilently,
  };
} 