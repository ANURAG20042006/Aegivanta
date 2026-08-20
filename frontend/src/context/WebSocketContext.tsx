import React, { createContext, useState, useEffect, ReactNode, useCallback, useRef } from 'react';
import { useAuth } from '../hooks/useAuth';
import { SOCEventItem } from '../services/dashboard';

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
  socEvents: SOCEventItem[];
  latestSOCEvent: SOCEventItem | null;
}

export const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const WebSocketProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { token } = useAuth();
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [latestPacket, setLatestPacket] = useState<PacketEvent | null>(null);
  const [packetStream, setPacketStream] = useState<PacketEvent[]>([]);
  const [threatAlerts, setThreatAlerts] = useState<PacketEvent[]>([]);
  const [socEvents, setSocEvents] = useState<SOCEventItem[]>([]);
  const [latestSOCEvent, setLatestSOCEvent] = useState<SOCEventItem | null>(null);

  const wsThreatsRef = useRef<WebSocket | null>(null);
  const wsSocRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<any>(null);
  const seenEventIdsRef = useRef<Set<string>>(new Set());

  const connect = useCallback(() => {
    if (!token) {
      setIsConnected(false);
      return;
    }

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = window.location.hostname === 'localhost' ? 'localhost:8000' : window.location.host;

    // 1. Connect SOC Operational Events Stream
    if (!wsSocRef.current || wsSocRef.current.readyState === WebSocket.CLOSED) {
      try {
        const socUrl = `${wsProtocol}//${wsHost}/ws/soc-events?token=${encodeURIComponent(token)}`;
        const socWs = new WebSocket(socUrl);
        wsSocRef.current = socWs;

        socWs.onopen = () => {
          setIsConnected(true);
        };

        socWs.onmessage = (event) => {
          try {
            const parsed = JSON.parse(event.data);

            if (parsed.type === 'PING') {
              if (socWs.readyState === WebSocket.OPEN) {
                socWs.send(JSON.stringify({ type: 'PONG' }));
              }
              return;
            }

            if (parsed.type === 'INIT_SYNC' && Array.isArray(parsed.events)) {
              const newEvts: SOCEventItem[] = parsed.events;
              newEvts.forEach(e => seenEventIdsRef.current.add(e.event_id));
              setSocEvents(newEvts);
              if (newEvts.length > 0) {
                setLatestSOCEvent(newEvts[0]);
              }
              return;
            }

            // Structured SOC Event
            const evt: SOCEventItem = parsed.data || parsed;
            if (evt && evt.event_id) {
              if (seenEventIdsRef.current.has(evt.event_id)) {
                return; // Suppress duplicate
              }
              seenEventIdsRef.current.add(evt.event_id);
              setLatestSOCEvent(evt);
              setSocEvents((prev) => [evt, ...prev.slice(0, 99)]);
            }
          } catch (err) {
            console.error('Error parsing SOC event frame:', err);
          }
        };

        socWs.onclose = () => {
          setIsConnected(false);
          wsSocRef.current = null;
        };

        socWs.onerror = () => {
          try { socWs.close(); } catch {}
        };
      } catch (err) {
        console.error('Failed to connect SOC Events WebSocket:', err);
      }
    }

    // 2. Connect Threat Packet Telemetry Stream
    if (!wsThreatsRef.current || wsThreatsRef.current.readyState === WebSocket.CLOSED) {
      try {
        const threatUrl = `${wsProtocol}//${wsHost}/ws/threats?token=${encodeURIComponent(token)}`;
        const threatWs = new WebSocket(threatUrl);
        wsThreatsRef.current = threatWs;

        threatWs.onmessage = (event) => {
          try {
            const packet = JSON.parse(event.data);
            if (packet.type === 'PING') {
              if (threatWs.readyState === WebSocket.OPEN) {
                threatWs.send(JSON.stringify({ type: 'PONG' }));
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
            console.error('Error parsing packet frame:', e);
          }
        };

        threatWs.onclose = () => {
          wsThreatsRef.current = null;
          if (token) {
            clearTimeout(reconnectTimerRef.current);
            reconnectTimerRef.current = setTimeout(connect, 3000);
          }
        };

        threatWs.onerror = () => {
          try { threatWs.close(); } catch {}
        };
      } catch (err) {
        console.error('Failed to connect threats websocket:', err);
      }
    }
  }, [token]);

  useEffect(() => {
    connect();

    return () => {
      clearTimeout(reconnectTimerRef.current);
      if (wsSocRef.current) {
        wsSocRef.current.close();
        wsSocRef.current = null;
      }
      if (wsThreatsRef.current) {
        wsThreatsRef.current.close();
        wsThreatsRef.current = null;
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
        socEvents,
        latestSOCEvent
      }}
    >
      {children}
    </WebSocketContext.Provider>
  );
};
