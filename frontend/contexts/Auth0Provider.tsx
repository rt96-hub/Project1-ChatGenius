'use client';

import { Auth0Provider as BaseAuth0Provider } from '@auth0/auth0-react';
import { useRouter } from 'next/navigation';
import { ReactNode } from 'react';

interface Auth0ProviderProps {
  children: ReactNode;
}

export function Auth0Provider({ children }: Auth0ProviderProps) {
  const router = useRouter();

  const domain = process.env.NEXT_PUBLIC_AUTH0_DOMAIN || '';
  const clientId = process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID || '';

  const onRedirectCallback = (appState: any) => {
    router.push(appState?.returnTo || '/');
  };

  return (
    <BaseAuth0Provider
      domain={domain}
      clientId={clientId}
      authorizationParams={{
        redirect_uri: typeof window !== 'undefined' ? window.location.origin : '',
      }}
      onRedirectCallback={onRedirectCallback}
    >
      {children}
    </BaseAuth0Provider>
  );
} 