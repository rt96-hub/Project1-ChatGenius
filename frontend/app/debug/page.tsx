'use client';
import { useEffect, useState } from 'react';

interface WindowInfo {
  href: string;
  host: string;
  hostname: string;
  protocol: string;
}

export default function Debug() {
  const [windowInfo, setWindowInfo] = useState<WindowInfo | null>(null);

  useEffect(() => {
    // Access window object only after component mounts (client-side)
    setWindowInfo({
      href: window.location.href,
      host: window.location.host,
      hostname: window.location.hostname,
      protocol: window.location.protocol,
    });
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Debug Info</h1>
      
      <h2 className="text-xl font-semibold mt-4 mb-2">Environment Variables:</h2>
      <pre className="bg-gray-100 p-4 rounded-lg overflow-auto">
        {JSON.stringify({
          NEXT_PUBLIC_AUTH0_DOMAIN: process.env.NEXT_PUBLIC_AUTH0_DOMAIN,
          NEXT_PUBLIC_AUTH0_CLIENT_ID: process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID,
          NEXT_PUBLIC_AUTH0_AUDIENCE: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
          NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
          NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL,
        }, null, 2)}
      </pre>

      <h2 className="text-xl font-semibold mt-4 mb-2">Window Location:</h2>
      <pre className="bg-gray-100 p-4 rounded-lg overflow-auto">
        {windowInfo ? JSON.stringify(windowInfo, null, 2) : 'Loading...'}
      </pre>
    </div>
  );
}