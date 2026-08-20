import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Activity, 
  Lock, 
  RefreshCw 
} from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';
import { dashboardService, SOCOverviewMetrics } from '../services/dashboard';
import { SOCMetricsRibbon } from '../components/dashboard/SOCMetricsRibbon';
import { LiveSOCEventStream } from '../components/dashboard/LiveSOCEventStream';
import { IncidentCommandTable } from '../components/dashboard/IncidentCommandTable';
import { AttackGraphPanel } from '../components/dashboard/AttackGraphPanel';
import { MitreMatrixWidget } from '../components/dashboard/MitreMatrixWidget';
import { ThreatIntelPanel } from '../components/dashboard/ThreatIntelPanel';
import { SOARCommandPanel } from '../components/dashboard/SOARCommandPanel';
import { SystemHealthMatrix } from '../components/dashboard/SystemHealthMatrix';
import { AdaptiveDetectionPanel } from '../components/dashboard/AdaptiveDetectionPanel';
import { AttackDistributionChart } from '../components/charts/AttackDistributionChart';
import { PacketTable } from '../components/tables/PacketTable';
import { RemediationModal } from '../components/dashboard/RemediationModal';

export const Dashboard: React.FC = () => {
  const { isConnected, packets = [], socEvents = [] } = useWebSocket();
  const [metrics, setMetrics] = useState<SOCOverviewMetrics | null>(null);
  const [isLoadingMetrics, setIsLoadingMetrics] = useState<boolean>(true);
  const [remediationTarget, setRemediationTarget] = useState<{ ip: string; attack: string } | null>(null);

  const fetchOverviewMetrics = async () => {
    setIsLoadingMetrics(true);
    try {
      const data = await dashboardService.getOverview();
      setMetrics(data);
    } catch (err) {
      console.error('Failed to load dashboard overview metrics:', err);
    } finally {
      setIsLoadingMetrics(false);
    }
  };

  useEffect(() => {
    fetchOverviewMetrics();
  }, []);

  return (
    <div className="space-y-6 pb-12 animate-fade-in font-mono">
      {/* Top Banner Status */}
      <div className="relative bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 border border-slate-800 rounded-2xl p-6 shadow-2xl overflow-hidden">
        <div className="absolute -right-12 -bottom-12 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="p-3.5 bg-cyan-500/10 border border-cyan-500/30 rounded-2xl text-cyan-400 shadow-inner">
              <ShieldCheck className="w-8 h-8 animate-pulse" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-3">
                <h1 className="text-2xl font-black text-slate-100 uppercase tracking-wider">
                  Aegivanta SOC Command Center
                </h1>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold border ${
                  isConnected 
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' 
                    : 'bg-red-500/10 border-red-500/30 text-red-400'
                }`}>
                  <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${isConnected ? 'bg-emerald-400 animate-ping' : 'bg-red-400'}`} />
                  {isConnected ? 'LIVE WEBSOCKET STREAM' : 'OFFLINE'}
                </span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
                  {metrics?.operating_mode || 'PRODUCTION'} MODE
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Unified operational visibility across ML threat detection, IOC intelligence, attack graph, SOAR, and MITRE matrix.
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={fetchOverviewMetrics}
              className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition-colors"
              title="Refresh Dashboard Overview"
            >
              <RefreshCw className={`w-4 h-4 ${isLoadingMetrics ? 'animate-spin' : ''}`} />
            </button>
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

      {/* 1. SOC Overview Metrics Ribbon */}
      <SOCMetricsRibbon metrics={metrics} isLoading={isLoadingMetrics} />

      {/* 2. Real-Time SOC Operational Event Stream & Telemetry */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <LiveSOCEventStream events={socEvents} isConnected={isConnected} />
        </div>
        <div className="lg:col-span-1">
          <AttackDistributionChart data={[
            { attack_type: 'DDoS', count: 12, percentage: 35 },
            { attack_type: 'Port Scan', count: 8, percentage: 25 },
            { attack_type: 'SQL Injection', count: 6, percentage: 20 },
            { attack_type: 'Botnet', count: 4, percentage: 12 },
            { attack_type: 'XSS', count: 2, percentage: 8 }
          ]} />
        </div>
      </div>

      {/* 3. Incident Command Center Table */}
      <IncidentCommandTable />

      {/* 4. Attack Graph & Lateral Movement Topology */}
      <AttackGraphPanel />

      {/* 5. MITRE Matrix & Threat Intelligence Double Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MitreMatrixWidget />
        <ThreatIntelPanel />
      </div>

      {/* 6. Autonomous SOAR Response & System Health */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SOARCommandPanel />
        <SystemHealthMatrix />
      </div>

      {/* 7. Phase 3.10 Adaptive ML Detection Intelligence & Model Governance */}
      <AdaptiveDetectionPanel />

      {/* 8. Live Packet Inspection & Telemetry Grid */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
            Deep Packet Telemetry Inspection
          </h3>
        </div>
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
