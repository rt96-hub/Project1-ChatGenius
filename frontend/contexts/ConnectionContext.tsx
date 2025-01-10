'use client';

import React, { createContext, useContext, useEffect, useRef, useState } from 'react';
import { useAuth0 } from '@auth0/auth0-react';

type ConnectionStatus = 'connected' | 'disconnected' | 'connecting' | 'idle' | 'away';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

interface WebSocketMessage {
  type: string;
  channel_id: number;
  [key: string]: any;
}

interface ConnectionContextType {
  connectionStatus: ConnectionStatus;
  sendMessage: (message: any) => void;
  addMessageListener: (callback: (message: WebSocketMessage) => void) => () => void;
}

const ConnectionContext = createContext<ConnectionContextType | undefined>(undefined);

export function ConnectionProvider({ children }: { children: React.ReactNode }) {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');
  const websocketRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const messageListeners = useRef<((message: WebSocketMessage) => void)[]>([]);
  const lastActivityRef = useRef<number>(Date.now());
  const idleCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const { getAccessTokenSilently, isAuthenticated } = useAuth0();

  const updateLastActivity = () => {
    lastActivityRef.current = Date.now();
    if (websocketRef.current?.readyState === WebSocket.OPEN) {
      setConnectionStatus('connected');
    }
  };

  // Setup idle detection
  useEffect(() => {
    const events = ['mousedown', 'keydown', 'touchstart', 'mousemove'];
    
    events.forEach(event => {
      window.addEventListener(event, updateLastActivity);
    });

    // Check for idle status every second
    idleCheckIntervalRef.current = setInterval(() => {
      const timeSinceLastActivity = Date.now() - lastActivityRef.current;
      if (websocketRef.current?.readyState === WebSocket.OPEN) {
        if (timeSinceLastActivity > 30000 && connectionStatus === 'connected') { // 30 seconds
          setConnectionStatus('idle');
        }
      }
    }, 1000);

    return () => {
      events.forEach(event => {
        window.removeEventListener(event, updateLastActivity);
      });
      if (idleCheckIntervalRef.current) {
        clearInterval(idleCheckIntervalRef.current);
      }
    };
  }, [connectionStatus]);

  const setupWebSocket = async () => {
    if (websocketRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    if (!isAuthenticated) {
      console.log('Not authenticated, skipping WebSocket connection');
      setConnectionStatus('disconnected');
      return;
    }

    try {
      setConnectionStatus('connecting');
      const token = await getAccessTokenSilently();
      console.log('Setting up WebSocket with token');
      
      const ws = new WebSocket(`${WS_URL}/ws?token=${encodeURIComponent(token)}`);      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('WebSocket received message:', data);
        // Notify all listeners of the message
        messageListeners.current.forEach(listener => listener(data));
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('disconnected');
      };

      ws.onclose = (event) => {
        console.log(`WebSocket closed with code ${event.code}`);
        websocketRef.current = null;
        setConnectionStatus('disconnected');

        // Only attempt to reconnect if authenticated and it wasn't a normal closure
        if (isAuthenticated && event.code !== 1000) {
          // Implement exponential backoff for reconnection
          const backoffDelay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
          reconnectAttempts.current++;
          
          console.log(`Attempting to reconnect in ${backoffDelay}ms...`);
          setTimeout(() => {
            if (isAuthenticated) {
              setupWebSocket();
            }
          }, backoffDelay);
        }
      };

      ws.onopen = () => {
        console.log('WebSocket connection established');
        reconnectAttempts.current = 0;
        setConnectionStatus('connected');
      };

      websocketRef.current = ws;
    } catch (error) {
      console.error('Error setting up WebSocket:', error);
      setConnectionStatus('disconnected');
    }
  };

  // Setup WebSocket when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      setupWebSocket();
    } else {
      // Close existing connection if user becomes unauthenticated
      if (websocketRef.current) {
        websocketRef.current.close(1000);
        websocketRef.current = null;
      }
      setConnectionStatus('disconnected');
    }
    
    return () => {
      if (websocketRef.current) {
        websocketRef.current.close(1000);
        websocketRef.current = null;
      }
    };
  }, [isAuthenticated]);

  const sendMessage = async (message: any) => {
    if (websocketRef.current?.readyState === WebSocket.OPEN) {
      console.log('Sending WebSocket message:', message);
      websocketRef.current.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
      // Attempt to reconnect
      await setupWebSocket();
    }
  };

  const addMessageListener = (callback: (message: WebSocketMessage) => void) => {
    messageListeners.current.push(callback);
    return () => {
      messageListeners.current = messageListeners.current.filter(listener => listener !== callback);
    };
  };

  return (
    <ConnectionContext.Provider value={{ connectionStatus, sendMessage, addMessageListener }}>
      {children}
    </ConnectionContext.Provider>
  );
}

export function useConnection() {
  const context = useContext(ConnectionContext);
  if (context === undefined) {
    throw new Error('useConnection must be used within a ConnectionProvider');
  }
  return context;
} 