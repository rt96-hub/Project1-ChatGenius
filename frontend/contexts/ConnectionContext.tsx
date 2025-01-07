'use client';

import React, { createContext, useContext, useEffect, useRef, useState } from 'react';

type ConnectionStatus = 'connected' | 'disconnected' | 'connecting';

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

  const setupWebSocket = () => {
    if (websocketRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const token = localStorage.getItem('token');
    if (!token) {
      console.log('No token available, skipping WebSocket connection');
      setConnectionStatus('disconnected');
      return;
    }

    setConnectionStatus('connecting');
    const ws = new WebSocket(`ws://localhost:8000/ws?token=${token}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
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

      // Only attempt to reconnect if we have a valid token and it wasn't a normal closure
      if (localStorage.getItem('token') && event.code !== 1000) {
        // Implement exponential backoff for reconnection
        const backoffDelay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
        reconnectAttempts.current++;
        
        console.log(`Attempting to reconnect in ${backoffDelay}ms...`);
        setTimeout(() => {
          if (localStorage.getItem('token')) {
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
  };

  useEffect(() => {
    setupWebSocket();
    return () => {
      if (websocketRef.current) {
        websocketRef.current.close(1000);
        websocketRef.current = null;
      }
    };
  }, []);

  const sendMessage = (message: any) => {
    if (websocketRef.current?.readyState === WebSocket.OPEN) {
      websocketRef.current.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
      // Attempt to reconnect
      setupWebSocket();
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