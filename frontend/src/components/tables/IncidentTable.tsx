import React from 'react';
import { ThreatBadge } from '../common/ThreatBadge';
import { IncidentItem } from '../../types';

interface IncidentTableProps {
  incidents: IncidentItem[];
}

export const IncidentTable: React.FC<IncidentTableProps> = ({ incidents }) => {
  if (!incidents || incidents.length === 0) {
    return (
      <div className="p-8 text-center text-slate-500 font-mono text-xs">
        No alerts have been recorded yet. Your network looks quiet.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left border-collapse text-xs font-mono">
        <thead>
          <tr className="border-b border-slate-800 bg-slate-900/80 text-slate-400 uppercase tracking-wider">
            <th className="p-3">When</th>
            <th className="p-3">From</th>
            <th className="p-3">To</th>
            <th className="p-3">What we found</th>
            <th className="p-3">Confidence</th>
            <th className="p-3">Priority</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60">
          {incidents.map((inc) => (
            <tr key={inc.id} className="hover:bg-slate-800/40 transition-colors">
              <td className="p-3 text-slate-400">{inc.timestamp.substring(0, 19).replace('T', ' ')}</td>
              <td className="p-3 text-cyan-400">{inc.source_ip}</td>
              <td className="p-3 text-slate-400">{inc.destination_ip}</td>
              <td className={`p-3 font-bold ${inc.is_malicious ? 'text-rose-400' : 'text-emerald-400'}`}>{inc.attack_type}</td>
              <td className="p-3 text-slate-300">{(inc.confidence_score * 100).toFixed(1)}%</td>
              <td className="p-3">
                <ThreatBadge severity={inc.severity} isMalicious={inc.is_malicious} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
