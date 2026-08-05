import React, { createContext, useState, useEffect, ReactNode } from 'react';

export interface PacketEvent {
  type: string;
  timestamp: number;
  source_ip: string;
  destination_ip: string;
  protocol: string;
  packet_length: number;
  is_malicious: boolean;
  attack_type: string;
  confidence_score: number;
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
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [latestPacket, setLatestPacket] = useState<PacketEvent | null>(null);
  const [packetStream, setPacketStream] = useState<PacketEvent[]>([]);
  const [threatAlerts, setThreatAlerts] = useState<PacketEvent[]>([]);

  useEffect(() => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = window.location.hostname === 'localhost' ? 'localhost:8000' : window.location.host;
    const socketUrl = `${wsProtocol}//${wsHost}/ws/threats`;

    let ws: WebSocket | null = null;
    try {
      ws = new WebSocket(socketUrl);

      ws.onopen = () => {
        setIsConnected(true);
        console.log('Connected to SentinelAI Threat WebSocket Stream.');
      };

      ws.onmessage = (event) => {
        try {
          const packet: PacketEvent = JSON.parse(event.data);
          setLatestPacket(packet);
          setPacketStream((prev) => [packet, ...prev.slice(0, 49)]); // Keep last 50

          if (packet.is_malicious) {
            setThreatAlerts((prev) => [packet, ...prev.slice(0, 19)]); // Keep last 20 threats
          }
        } catch (e) {
          console.error('Error parsing WebSocket message:', e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
      };

      ws.onerror = (err) => {
        console.error('WebSocket Error:', err);
      };
    } catch (err) {
      console.error('Failed to establish WebSocket connection:', err);
    }

    return () => {
      if (ws) ws.close();
    };
  }, []);

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
