import React, { createContext, useState, useEffect, ReactNode, useCallback, useRef } from 'react';
import { useAuth } from '../hooks/useAuth';

export interface PacketEvent {
  type: string;
  timestamp: number;
  source_ip: string;
  destination_ip: string;
  protocol: string;
  packet_length: number;
  is_malicious: boolean;
  attack_type: string;
  confidence_score: number | null;
  confidence_available?: boolean;
  severity: string;
  incident_id?: string;
  source_port?: number;
  destination_port?: number;
  model_used?: string;
  attack_probabilities?: Record<string, number>;
}

export interface WebSocketContextType {
  isConnected: boolean;
  latestPacket: PacketEvent | null;
  packetStream: PacketEvent[];
  threatAlerts: PacketEvent[];
  packets: PacketEvent[];
  alerts: PacketEvent[];
}

export const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const WebSocketProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { token } = useAuth();
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [latestPacket, setLatestPacket] = useState<PacketEvent | null>(null);
  const [packetStream, setPacketStream] = useState<PacketEvent[]>([]);
  const [threatAlerts, setThreatAlerts] = useState<PacketEvent[]>([]);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<any>(null);

  const connect = useCallback(() => {
    if (!token) {
      setIsConnected(false);
      return;
    }

    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = window.location.hostname === 'localhost' ? 'localhost:8000' : window.location.host;
    const socketUrl = `${wsProtocol}//${wsHost}/ws/threats?token=${encodeURIComponent(token)}`;

    try {
      const ws = new WebSocket(socketUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        console.log('Connected to SentinelAI Live Threat WebSocket Stream.');
      };

      ws.onmessage = (event) => {
        try {
          const packet = JSON.parse(event.data);

          // Handle server-side heartbeat ping
          if (packet.type === 'PING') {
            if (ws.readyState === WebSocket.OPEN) {
              ws.send(JSON.stringify({ type: 'PONG' }));
            }
            return;
          }

          if (packet.type === 'PACKET_STREAM' || packet.type === 'THREAT_EVENT' || packet.type === 'SYSTEM_STATUS') {
            const pktEvent: PacketEvent = packet;
            setLatestPacket(pktEvent);
            setPacketStream((prev) => [pktEvent, ...prev.slice(0, 49)]);

            if (pktEvent.is_malicious) {
              setThreatAlerts((prev) => [pktEvent, ...prev.slice(0, 19)]);
            }
          }
        } catch (e) {
          console.error('Error parsing WebSocket telemetry frame:', e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        wsRef.current = null;
        // Schedule auto-reconnect in 3s
        if (token) {
          clearTimeout(reconnectTimerRef.current);
          reconnectTimerRef.current = setTimeout(connect, 3000);
        }
      };

      ws.onerror = (err) => {
        console.warn('WebSocket connection event:', err);
        try {
          ws.close();
        } catch {}
      };
    } catch (err) {
      console.error('Failed to establish WebSocket connection:', err);
      if (token) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = setTimeout(connect, 3000);
      }
    }
  }, [token]);

  useEffect(() => {
    connect();

    return () => {
      clearTimeout(reconnectTimerRef.current);
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect]);

  return (
    <WebSocketContext.Provider
      value={{
        isConnected,
        latestPacket,
        packetStream,
        threatAlerts,
        packets: packetStream,
        alerts: threatAlerts,
      }}
    >
      {children}
    </WebSocketContext.Provider>
  );
};
