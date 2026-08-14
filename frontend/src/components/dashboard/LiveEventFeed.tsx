import React, { useState } from 'react';
import { 
  Radio, 
  ShieldAlert, 
  ShieldCheck, 
  Pause, 
  Play, 
  ChevronRight,
  ExternalLink
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useWebSocket } from '../../hooks/useWebSocket';

export const LiveEventFeed: React.FC = () => {
  const { isConnected, packetStream = [], threatAlerts = [] } = useWebSocket();
  const [isPaused, setIsPaused] = useState(false);
  const [filterType, setFilterType] = useState<'all' | 'threats' | 'benign'>('all');

  const displayedPackets = (filterType === 'threats' 
    ? threatAlerts 
    : filterType === 'benign' 
    ? packetStream.filter(p => !p.is_malicious) 
    : packetStream
  ).slice(0, 15);

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl backdrop-blur-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-xl border ${
            isConnected 
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' 
              : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
          }`}>
            <Radio className={`w-4 h-4 ${isConnected ? 'animate-pulse' : ''}`} />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-slate-100 font-mono tracking-wide">
                LIVE SOC TELEMETRY STREAM
              </h3>
              <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-ping' : 'bg-rose-400'}`} />
            </div>
            <p className="text-[11px] text-slate-400">
              Real-time socket pipeline inspecting ingress/egress network flows.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {/* Filter Pills */}
          <div className="bg-slate-950 p-1 rounded-xl border border-slate-800 flex items-center space-x-1 text-[11px] font-mono">
            <button
              onClick={() => setFilterType('all')}
              className={`px-2.5 py-1 rounded-lg transition-colors cursor-pointer ${
                filterType === 'all' ? 'bg-cyan-500/20 text-cyan-300 font-bold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              All ({packetStream.length})
            </button>
            <button
              onClick={() => setFilterType('threats')}
              className={`px-2.5 py-1 rounded-lg transition-colors cursor-pointer ${
                filterType === 'threats' ? 'bg-red-500/20 text-red-300 font-bold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Threats ({threatAlerts.length})
            </button>
          </div>

          <button
            onClick={() => setIsPaused(!isPaused)}
            className="p-1.5 bg-slate-950 hover:bg-slate-800 text-slate-300 rounded-xl border border-slate-800 transition-colors cursor-pointer"
            title={isPaused ? 'Resume Stream' : 'Pause Stream'}
          >
            {isPaused ? <Play className="w-3.5 h-3.5 text-emerald-400" /> : <Pause className="w-3.5 h-3.5 text-amber-400" />}
          </button>
        </div>
      </div>

      {/* Stream Items List */}
      <div className="space-y-2 max-h-[360px] overflow-y-auto pr-1">
        {displayedPackets.length === 0 ? (
          <div className="text-center py-10 text-slate-500 text-xs font-mono">
            Awaiting real-time telemetry events from sensor interface...
          </div>
        ) : (
          displayedPackets.map((pkt, idx) => {
            const isThreat = pkt.is_malicious;
            return (
              <div
                key={pkt.incident_id || `${pkt.timestamp}-${idx}`}
                className={`flex items-center justify-between p-3 rounded-xl border transition-all duration-150 ${
                  isThreat
                    ? 'bg-red-950/20 border-red-900/40 hover:border-red-700/60'
                    : 'bg-slate-950/50 border-slate-800/80 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center space-x-3 min-w-0">
                  <div className={`p-1.5 rounded-lg border ${
                    isThreat 
                      ? 'bg-red-500/10 border-red-500/30 text-red-400' 
                      : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                  }`}>
                    {isThreat ? <ShieldAlert className="w-3.5 h-3.5" /> : <ShieldCheck className="w-3.5 h-3.5" />}
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center space-x-2">
                      <span className={`text-xs font-bold font-mono truncate ${isThreat ? 'text-red-300' : 'text-slate-200'}`}>
                        {isThreat ? pkt.attack_type : 'BENIGN TRAFFIC'}
                      </span>
                      {isThreat && (
                        <span className="px-1.5 py-0.2 rounded text-[10px] font-mono font-black uppercase bg-red-500/20 border border-red-500/40 text-red-300">
                          {pkt.severity || 'HIGH'}
                        </span>
                      )}
                    </div>
                    <div className="text-[11px] font-mono text-slate-400 flex items-center space-x-2 mt-0.5">
                      <span>{pkt.source_ip}</span>
                      <ChevronRight className="w-3 h-3 text-slate-600" />
                      <span>{pkt.destination_ip}</span>
                      <span className="text-slate-600">|</span>
                      <span className="text-slate-500">{pkt.protocol}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-3 ml-2 shrink-0 text-right">
                  {pkt.confidence_score !== null && pkt.confidence_score !== undefined && (
                    <div className="hidden sm:block text-right">
                      <span className="text-[10px] text-slate-500 block uppercase font-mono">Conf</span>
                      <span className="text-xs font-mono font-bold text-cyan-400">
                        {(pkt.confidence_score * 100).toFixed(1)}%
                      </span>
                    </div>
                  )}
                  {pkt.incident_id && (
                    <Link
                      to={`/incidents/${pkt.incident_id}`}
                      className="p-1.5 bg-slate-900 hover:bg-cyan-950 text-slate-400 hover:text-cyan-400 rounded-lg border border-slate-800 hover:border-cyan-800 transition-colors"
                      title="Investigate Incident"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </Link>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
