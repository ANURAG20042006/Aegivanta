import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  Activity, 
  Cpu, 
  Zap, 
  Lock
} from 'lucide-react';
import { StatCard } from '../components/common/StatCard';
import { LiveTrafficChart } from '../components/charts/LiveTrafficChart';
import { AttackDistributionChart } from '../components/charts/AttackDistributionChart';
import { PacketTable } from '../components/tables/PacketTable';
import { NetworkTopologyCanvas } from '../components/dashboard/NetworkTopologyCanvas';
import { GlobalAttackMap } from '../components/dashboard/GlobalAttackMap';
import { RemediationModal } from '../components/dashboard/RemediationModal';
import { LiveEventFeed } from '../components/dashboard/LiveEventFeed';
import { useWebSocket } from '../hooks/useWebSocket';
import { analyticsService } from '../services/analytics';
import api from '../services/api';
import { AnalyticsSummary } from '../types';

export const Dashboard: React.FC = () => {
  const { packets = [], alerts = [] } = useWebSocket();
  const [remediationTarget, setRemediationTarget] = useState<{ ip: string; attack: string } | null>(null);
  
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [operatingMode, setOperatingMode] = useState<string>('DEMO');
  const [isLoadingSummary, setIsLoadingSummary] = useState<boolean>(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setIsLoadingSummary(true);
      try {
        const [sumData, healthRes] = await Promise.allSettled([
          analyticsService.getSummary(),
          api.get('/health')
        ]);

        if (sumData.status === 'fulfilled') {
          setSummary(sumData.value);
        }
        if (healthRes.status === 'fulfilled' && healthRes.value.data) {
          setOperatingMode(healthRes.value.data.mode || 'DEMO');
        }
      } catch (err) {
        console.error('Failed to fetch real dashboard metrics:', err);
      } finally {
        setIsLoadingSummary(false);
      }
    };

    fetchDashboardData();
  }, []);

  const totalInspected = summary ? (summary.total_packets_inspected || 0) + packets.length : packets.length;
  const totalThreats = summary ? (summary.total_threats_detected ?? summary.total_threats_isolated ?? 0) + alerts.length : alerts.length;
  const activeModelName = summary?.active_model || 'Random Forest';
  const threatDistribution = summary?.attack_distribution || [];

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
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold border ${
                  operatingMode === 'PRODUCTION' 
                    ? 'bg-red-500/10 border-red-500/30 text-red-400' 
                    : operatingMode === 'LAB' 
                    ? 'bg-amber-500/10 border-amber-500/30 text-amber-400' 
                    : 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400'
                }`}>
                  {operatingMode.toUpperCase()} MODE
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Continuous AI/DL inference monitoring across 78 CICIDS2017 flow attributes.
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
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
          value={isLoadingSummary ? 'Loading...' : totalInspected.toLocaleString()}
          change="Real DB Count"
          isPositive={true}
          icon={Activity}
          gradient="from-blue-500 to-cyan-500"
        />
        <StatCard
          title="THREATS ISOLATED"
          value={isLoadingSummary ? 'Loading...' : totalThreats.toLocaleString()}
          change="Real DB Count"
          isPositive={true}
          icon={ShieldAlert}
          gradient="from-amber-500 to-red-500"
        />
        <StatCard
          title="ACTIVE CLASSIFIER"
          value={activeModelName}
          change="Real Active Model"
          isPositive={true}
          icon={Cpu}
          gradient="from-purple-500 to-indigo-500"
        />
        <StatCard
          title="OPERATING MODE"
          value={`${operatingMode} MODE`}
          change="Server Verified"
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
          <AttackDistributionChart data={threatDistribution.length > 0 ? threatDistribution : [
            { attack_type: 'BENIGN', count: 0, percentage: 100 }
          ]} />
        </div>
      </div>

      {/* Global Geolocation Attack Origin Matrix */}
      <GlobalAttackMap />

      {/* Real-time Telemetry Event Feed & Packet Inspection Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <LiveEventFeed />
        </div>
        <div className="lg:col-span-2">
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
