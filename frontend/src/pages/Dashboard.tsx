import React, { useState } from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  Activity, 
  Cpu, 
  Zap, 
  Radio, 
  Lock,
  ChevronDown
} from 'lucide-react';
import { StatCard } from '../components/common/StatCard';
import { ThreatBadge } from '../components/common/ThreatBadge';
import { LiveTrafficChart } from '../components/charts/LiveTrafficChart';
import { AttackDistributionChart } from '../components/charts/AttackDistributionChart';
import { PacketTable } from '../components/tables/PacketTable';
import { NetworkTopologyCanvas } from '../components/dashboard/NetworkTopologyCanvas';
import { GlobalAttackMap } from '../components/dashboard/GlobalAttackMap';
import { RemediationModal } from '../components/dashboard/RemediationModal';
import { useWebSocket } from '../hooks/useWebSocket';

export const Dashboard: React.FC = () => {
  const { isConnected, packets = [], alerts = [] } = useWebSocket();
  const [remediationTarget, setRemediationTarget] = useState<{ ip: string; attack: string } | null>(null);
  const [activeModel, setActiveModel] = useState<string>(() => localStorage.getItem('sentinel_default_model') || 'XGBoost v2.1');

  const totalInspected = 142850 + (packets?.length || 0);
  const totalThreats = 1842 + (alerts?.length || 0);

  const mockThreatSummary = [
    { attack_type: 'DDoS', count: 850, percentage: 46.1 },
    { attack_type: 'DoS Hulk', count: 420, percentage: 22.8 },
    { attack_type: 'Port Scan', count: 310, percentage: 16.8 },
    { attack_type: 'Botnet', count: 160, percentage: 8.7 },
    { attack_type: 'SQL Injection', count: 102, percentage: 5.6 },
  ];

  const handleModelChange = (model: string) => {
    setActiveModel(model);
    localStorage.setItem('sentinel_default_model', model);
  };

  return (
    <div className="space-y-6 pb-12 animate-fade-in">
      {/* Top Banner Status */}
      <div className="relative bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 border border-slate-800 rounded-2xl p-6 shadow-2xl overflow-hidden">
        <div className="absolute -right-12 -bottom-12 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-cyan-500/10 border border-cyan-500/30 rounded-2xl text-cyan-400 shadow-inner">
              <ShieldCheck className="w-8 h-8 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-3">
                <h1 className="text-2xl font-black text-slate-100 uppercase tracking-wider font-mono">
                  SentinelAI Threat Operations Center
                </h1>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-ping" />
                  REAL-TIME ACTIVE
                </span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/10 border border-amber-500/30 text-amber-400">
                  DEMO MODE (SYNTHETIC STREAM)
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Continuous AI/DL inference monitoring across 78 CICIDS2017 flow attributes.
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Live Model Switcher */}
            <div className="relative">
              <select
                value={activeModel}
                onChange={(e) => handleModelChange(e.target.value)}
                className="bg-slate-950 border border-slate-700 text-cyan-400 font-mono text-xs px-3.5 py-2 rounded-xl focus:outline-none focus:border-cyan-400 cursor-pointer appearance-none pr-8 shadow-inner"
              >
                <option value="XGBoost v2.1">Model: XGBoost</option>
                <option value="Random Forest">Model: Random Forest</option>
                <option value="LightGBM">Model: LightGBM</option>
                <option value="1D-CNN DeepNet">Model: PyTorch 1D-CNN</option>
                <option value="Autoencoder Zero-Day">Model: Deep Autoencoder (Zero-Day)</option>
              </select>
              <ChevronDown className="w-4 h-4 text-slate-400 absolute right-2.5 top-2.5 pointer-events-none" />
            </div>

            <button
              onClick={() => setRemediationTarget({ ip: '192.168.1.105', attack: 'DDoS' })}
              className="px-4 py-2 text-xs font-bold bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white rounded-xl shadow-lg shadow-red-600/30 transition-all flex items-center space-x-2 cursor-pointer"
            >
              <Lock className="w-4 h-4" />
              <span>CONTAIN THREAT IP</span>
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="TOTAL PACKETS INSPECTED"
          value={totalInspected.toLocaleString()}
          change="+14.2% / sec"
          isPositive={true}
          icon={Activity}
          gradient="from-blue-500 to-cyan-500"
        />
        <StatCard
          title="THREATS ISOLATED"
          value={totalThreats.toLocaleString()}
          change="-3.8% this hour"
          isPositive={true}
          icon={ShieldAlert}
          gradient="from-amber-500 to-red-500"
        />
        <StatCard
          title="ACTIVE CLASSIFIER"
          value={activeModel}
          change="Real-time Active"
          isPositive={true}
          icon={Cpu}
          gradient="from-purple-500 to-indigo-500"
        />
        <StatCard
          title="STREAM LATENCY"
          value="4.2 ms"
          change="Sub-millisecond buffer"
          isPositive={true}
          icon={Zap}
          gradient="from-emerald-500 to-teal-500"
        />
      </div>

      {/* Live Topology Canvas */}
      <NetworkTopologyCanvas />

      {/* Live Charts & Global Threat Matrix */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <LiveTrafficChart packets={packets} />
        </div>
        <div>
          <AttackDistributionChart data={mockThreatSummary} />
        </div>
      </div>

      {/* Global Geolocation Attack Origin Matrix */}
      <GlobalAttackMap />

      {/* Live WebSocket Alerts Panel & Packet Table */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Real-time Ticker */}
        <div className="bg-slate-900/80 border border-slate-800/80 rounded-xl p-5 backdrop-blur-md space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <div className="flex items-center space-x-2">
              <Radio className="w-4 h-4 text-cyan-400 animate-pulse" />
              <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Live WebSocket Feed</h3>
            </div>
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400' : 'bg-red-400'}`} />
          </div>

          <div className="space-y-2.5 max-h-[320px] overflow-y-auto pr-1">
            {!alerts || alerts.length === 0 ? (
              <div className="text-center py-8 text-xs text-slate-500">
                Listening for incoming threat telemetry...
              </div>
            ) : (
              alerts.map((alert, i) => {
                const attack = alert?.attack_type || 'Malicious Flow';
                const ip = alert?.source_ip || '192.168.1.100';
                const sev = alert?.severity || 'High';

                return (
                  <div
                    key={i}
                    className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 space-y-1 animate-slide-in"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-red-400">{attack}</span>
                      <ThreatBadge severity={sev} />
                    </div>
                    <div className="flex items-center justify-between text-[11px] text-slate-400">
                      <span className="font-mono">{ip}</span>
                      <span>
                        Confidence: {typeof alert?.confidence_score === 'number'
                          ? `${(alert.confidence_score * 100).toFixed(0)}%`
                          : 'N/A'}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Packet Stream Table */}
        <div className="lg:col-span-3">
          <PacketTable
            packets={packets}
            onSelectPacket={(pkt) => {
              if (pkt && pkt.is_malicious) {
                setRemediationTarget({
                  ip: pkt.source_ip || '192.168.1.105',
                  attack: pkt.attack_type || 'Malicious Flow'
                });
              }
            }}
          />
        </div>
      </div>

      {/* Containment Modal */}
      {remediationTarget && (
        <RemediationModal
          isOpen={true}
          onClose={() => setRemediationTarget(null)}
          targetIp={remediationTarget.ip}
          attackType={remediationTarget.attack}
        />
      )}
    </div>
  );
};
