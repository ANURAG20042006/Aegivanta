import React from 'react';
import { PredictionResult } from '../../types';
import { ThreatBadge } from '../common/ThreatBadge';

interface PacketTableProps {
  packets: PredictionResult[];
  onSelectPacket?: (pkt: PredictionResult) => void;
}

export const PacketTable: React.FC<PacketTableProps> = ({ packets, onSelectPacket }) => {
  if (!packets || packets.length === 0) {
    return (
      <div className="p-8 text-center text-slate-500 font-mono text-xs bg-slate-900/80 border border-slate-800/80 rounded-xl">
        No packet vectors available. Upload a network traffic CSV to inspect flow threats.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto bg-slate-900/80 border border-slate-800/80 rounded-xl">
      <table className="w-full text-left border-collapse text-xs font-mono">
        <thead>
          <tr className="border-b border-slate-800 bg-slate-950/80 text-slate-400 uppercase tracking-wider">
            <th className="p-3">Status</th>
            <th className="p-3">Source IP</th>
            <th className="p-3">Destination IP</th>
            <th className="p-3">Proto / Port</th>
            <th className="p-3">Attack Classification</th>
            <th className="p-3">Confidence</th>
            <th className="p-3">Severity</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60">
          {packets.map((pkt, i) => (
            <tr
              key={pkt.incident_id || i}
              onClick={() => onSelectPacket && onSelectPacket(pkt)}
              className={`transition-colors cursor-pointer hover:bg-slate-800/60 ${
                pkt.is_malicious ? 'bg-rose-500/5' : ''
              }`}
            >
              <td className="p-3">
                <span
                  className={`w-2 h-2 rounded-full inline-block ${
                    pkt.is_malicious ? 'bg-rose-500 animate-ping' : 'bg-emerald-400'
                  }`}
                />
              </td>
              <td className="p-3 text-slate-200">{pkt.source_ip}:{pkt.source_port}</td>
              <td className="p-3 text-slate-400">{pkt.destination_ip}:{pkt.destination_port}</td>
              <td className="p-3 text-cyan-400">{pkt.protocol}</td>
              <td className="p-3 font-bold text-slate-100">{pkt.attack_type}</td>
              <td className="p-3 text-slate-300">
                {pkt.confidence_score !== null && pkt.confidence_score !== undefined
                  ? `${(pkt.confidence_score * 100).toFixed(1)}%`
                  : 'N/A'}
              </td>
              <td className="p-3">
                <ThreatBadge severity={pkt.severity} isMalicious={pkt.is_malicious} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
