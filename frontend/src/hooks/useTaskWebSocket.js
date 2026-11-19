import { useState, useEffect, useRef, useCallback } from 'react';

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000/api/websockets/ws/tasks';

export const useTaskWebSocket = (taskId) => {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [pendingApproval, setPendingApproval] = useState(null);
  const wsRef = useRef(null);

  const connect = useCallback(() => {
    if (!taskId) return;

    const wsUrl = `${WS_BASE_URL}/${taskId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'APPROVAL_REQUIRED') {
          setPendingApproval(data.payload);
        } else if (data.type === 'APPROVAL_RESOLVED') {
          setPendingApproval(null);
        }

        setMessages((prev) => [...prev, data]);
      } catch (err) {
        console.error('Failed to parse WS message:', err);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      // Attempt auto-reconnect after 3 seconds
      setTimeout(() => {
        if (taskId) connect();
      }, 3000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      ws.close();
    };

    wsRef.current = ws;
  }, [taskId]);

  useEffect(() => {
    setMessages([]);
    setPendingApproval(null);
    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [taskId, connect]);

  return { messages, isConnected, pendingApproval };
};