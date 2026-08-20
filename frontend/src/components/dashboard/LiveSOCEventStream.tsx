import React, { useState } from 'react';
import { 
  Radio, 
  Pause, 
  Play, 
  ShieldAlert, 
  Zap, 
  Crosshair, 
  Activity, 
  Info, 
  Flame,
  ChevronRight,
  X
} from 'lucide-react';
import { SOCEventItem } from '../../services/dashboard';

interface LiveSOCEventStreamProps {
  events: SOCEventItem[];
  isConnected: boolean;
}

export const LiveSOCEventStream: React.FC<LiveSOCEventStreamProps> = ({ events, isConnected }) => {
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [activeEvent, setActiveEvent] = useState<SOCEventItem | null>(null);

  const filteredEvents = events.filter((e) => {
    if (selectedSeverity !== 'ALL' && e.severity !== selectedSeverity) return false;
    if (selectedType !== 'ALL' && e.type !== selectedType) return false;
    return true;
  });

  const getSeverityBadge = (sev: string) => {
    switch (sev.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-red-500/20 text-red-400 border-red-500/40 animate-pulse';
      case 'HIGH':
        return 'bg-rose-500/20 text-rose-400 border-rose-500/40';
      case 'MEDIUM':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
      case 'LOW':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/40';
      default:
        return 'bg-slate-700/50 text-slate-300 border-slate-600';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type.toUpperCase()) {
      case 'NEW_INCIDENT':
      case 'INCIDENT_SEVERITY_ESCALATION':
        return <Flame className="w-3.5 h-3.5 text-red-400 shrink-0" />;
      case 'NEW_DETECTION':
        return <ShieldAlert className="w-3.5 h-3.5 text-amber-400 shrink-0" />;
      case 'THREAT_INTEL_MATCH':
        return <Crosshair className="w-3.5 h-3.5 text-purple-400 shrink-0" />;
      case 'LATERAL_MOVEMENT_DETECTION':
        return <Activity className="w-3.5 h-3.5 text-rose-400 shrink-0" />;
      case 'RESPONSE_ACTION_EXECUTED':
      case 'RESPONSE_ACTION_APPROVED':
        return <Zap className="w-3.5 h-3.5 text-cyan-400 shrink-0" />;
      default:
        return <Info className="w-3.5 h-3.5 text-slate-400 shrink-0" />;
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-xl backdrop-blur-md flex flex-col h-[380px]">
      {/* Header & Controls */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-cyan-400">
            <Radio className={`w-4 h-4 ${isConnected ? 'animate-pulse' : 'text-slate-500'}`} />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-mono font-bold text-slate-100 uppercase tracking-wider">
                Real-Time SOC Event Stream
              </span>
              <span className={`inline-flex items-center px-1.5 py-0.2 rounded text-[10px] font-mono font-bold border ${
                isConnected ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-red-500/10 border-red-500/30 text-red-400'
              }`}>
                {isConnected ? 'LIVE' : 'DISCONNECTED'}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {/* Severity Filter */}
          <select
            value={selectedSeverity}
            onChange={(e) => setSelectedSeverity(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-2 py-1 text-[11px] font-mono text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
            <option value="INFO">Info</option>
          </select>

          {/* Type Filter */}
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-2 py-1 text-[11px] font-mono text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Event Types</option>
            <option value="NEW_INCIDENT">New Incident</option>
            <option value="NEW_DETECTION">New Detection</option>
            <option value="THREAT_INTEL_MATCH">Threat Intel Match</option>
            <option value="LATERAL_MOVEMENT_DETECTION">Lateral Movement</option>
            <option value="RESPONSE_ACTION_EXECUTED">SOAR Action</option>
            <option value="SYSTEM_ALERT">System Alert</option>
          </select>

          {/* Pause / Resume */}
          <button
            onClick={() => setIsPaused(!isPaused)}
            className={`p-1.5 rounded-lg border text-xs font-mono transition-colors ${
              isPaused ? 'bg-amber-500/20 border-amber-500/40 text-amber-400' : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-slate-200'
            }`}
            title={isPaused ? 'Resume live feed' : 'Pause live feed'}
          >
            {isPaused ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Stream List */}
      <div className="flex-1 overflow-y-auto divide-y divide-slate-800/60 font-mono text-xs mt-2 pr-1 space-y-1">
        {filteredEvents.length === 0 ? (
          <div className="h-full flex items-center justify-center text-slate-500 text-xs">
            {isPaused ? 'FEED PAUSED — WAITING TO RESUME' : 'NO EVENTS RECORDED IN CURRENT WINDOW'}
          </div>
        ) : (
          filteredEvents.map((evt) => (
            <div
              key={evt.event_id || evt.sequence}
              onClick={() => setActiveEvent(evt)}
              className="p-2.5 rounded-xl bg-slate-950/40 hover:bg-slate-800/60 border border-transparent hover:border-slate-700/60 transition-all cursor-pointer flex items-center justify-between group"
            >
              <div className="flex items-center space-x-2.5 overflow-hidden">
                {getTypeIcon(evt.type)}
                <div className="min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-slate-200 truncate">{evt.title}</span>
                    <span className={`px-1.5 py-0.2 rounded text-[9px] font-bold border ${getSeverityBadge(evt.severity)}`}>
                      {evt.severity}
                    </span>
                    <span className="text-[10px] text-slate-500 shrink-0">
                      #{evt.sequence}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 truncate mt-0.5">{evt.description}</p>
                </div>
              </div>

              <div className="flex items-center space-x-2 shrink-0 ml-3">
                <span className="text-[10px] text-slate-500">
                  {new Date(evt.timestamp).toLocaleTimeString()}
                </span>
                <ChevronRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-cyan-400 transition-colors" />
              </div>
            </div>
          ))
        )}
      </div>

      {/* Event Details Inspector Modal */}
      {activeEvent && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4 font-mono">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2">
                {getTypeIcon(activeEvent.type)}
                <h3 className="text-sm font-bold text-slate-100 uppercase">{activeEvent.type}</h3>
              </div>
              <button onClick={() => setActiveEvent(null)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-slate-500">Title:</span>
                <p className="text-slate-200 font-bold mt-0.5">{activeEvent.title}</p>
              </div>
              <div>
                <span className="text-slate-500">Description:</span>
                <p className="text-slate-300 mt-0.5">{activeEvent.description}</p>
              </div>
              <div className="grid grid-cols-2 gap-3 bg-slate-950 p-3 rounded-xl border border-slate-800">
                <div>
                  <span className="text-slate-500">Severity:</span>
                  <p className={`font-bold mt-0.5 text-slate-200`}>{activeEvent.severity}</p>
                </div>
                <div>
                  <span className="text-slate-500">Sequence:</span>
                  <p className="text-slate-200 font-bold mt-0.5">#{activeEvent.sequence}</p>
                </div>
                <div>
                  <span className="text-slate-500">Timestamp:</span>
                  <p className="text-slate-300 mt-0.5">{new Date(activeEvent.timestamp).toLocaleString()}</p>
                </div>
                <div>
                  <span className="text-slate-500">Event ID:</span>
                  <p className="text-slate-400 font-mono text-[10px] truncate mt-0.5">{activeEvent.event_id}</p>
                </div>
              </div>

              {activeEvent.metadata && Object.keys(activeEvent.metadata).length > 0 && (
                <div>
                  <span className="text-slate-500">Payload Metadata:</span>
                  <pre className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-[10px] text-cyan-300 overflow-x-auto mt-1 max-h-36">
                    {JSON.stringify(activeEvent.metadata, null, 2)}
                  </pre>
                </div>
              )}
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setActiveEvent(null)}
                className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
