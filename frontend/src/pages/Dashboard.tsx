import React, { useState, useEffect } from 'react';
import { AlertTriangle, Activity, Cpu, Server, Radio, ArrowRight, Info } from 'lucide-react';
import { Link } from 'react-router-dom';
import { StatCard } from '../components/common/StatCard';
import { LiveTrafficChart } from '../components/charts/LiveTrafficChart';
import { AttackDistributionChart } from '../components/charts/AttackDistributionChart';
import { IncidentTable } from '../components/tables/IncidentTable';
import { analyticsService } from '../services/analytics';
import { AnalyticsSummary } from '../types';
import { useWebSocket } from '../hooks/useWebSocket';
import { SentinelOrb } from '../components/common/SentinelOrb';

export const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const { threatAlerts } = useWebSocket();


  useEffect(() => {
    const loadSummary = async () => {
      try {
        const data = await analyticsService.getSummary();
        setSummary(data);
      } catch (err) {
        console.error('Failed to load dashboard summary:', err);
      }
    };
    loadSummary();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="dashboard-hero flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-2xl border border-slate-800">
        <div className="relative z-10">
          <h1 className="text-xl font-mono font-extrabold text-white tracking-tight">
            Security overview
          </h1>
          <p className="text-xs text-slate-400 font-mono mt-1">
            See what is happening on your network right now. Detection model: <span className="text-cyan-400 font-bold">{summary?.active_model || 'Loading'}</span>
          </p>
        </div>

        <div className="flex items-center space-x-4 relative z-10">
          <SentinelOrb threatCount={threatAlerts.length} status={summary?.network_status || 'MONITORING'} />
          <div className={`px-4 py-2 rounded-xl font-mono text-xs font-bold border flex items-center space-x-2 ${
            summary?.network_status === 'CRITICAL'
              ? 'bg-rose-500/20 text-rose-400 border-rose-500/40 animate-pulse'
              : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
          }`}>
            <Radio className="w-4 h-4 animate-ping" />
            <span>Network: {summary?.network_status || 'Loading'}</span>
          </div>
        </div>
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Traffic checked"
          value={summary ? summary.total_packets_inspected : '—'}
          subtitle="Network activity reviewed"
          icon={Activity}
          color="cyan"
        />
        <StatCard
          title="Threats found"
          value={summary ? summary.total_threats_detected : '—'}
          subtitle="Activity that may need attention"
          icon={AlertTriangle}
          color="crimson"
        />
        <StatCard
          title="Detection confidence"
          value={summary ? `${(summary.prediction_accuracy * 100).toFixed(2)}%` : '—'}
          subtitle="How reliable the current model is"
          icon={Cpu}
          color="emerald"
        />
        <StatCard
          title="Models available"
          value={summary ? `${summary.model_performance.length} / 12` : '—'}
          subtitle="Detection options online"
          icon={Server}
          color="purple"
        />
      </div>

      <div className="glass-panel p-5 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-cyan-400 mt-0.5" />
          <div>
            <h2 className="text-sm font-semibold text-white">New to SentinelAI?</h2>
            <p className="text-xs text-slate-400 mt-1">Upload a traffic file to check for threats, or open the history to review previous alerts.</p>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link to="/prediction" className="friendly-link">Inspect traffic <ArrowRight className="w-3.5 h-3.5" /></Link>
          <Link to="/history" className="friendly-link secondary">View alerts <ArrowRight className="w-3.5 h-3.5" /></Link>
        </div>
      </div>

      {/* Live Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-panel p-5 rounded-xl">
          <h2 className="text-xs font-mono text-slate-400 uppercase tracking-wider mb-4 flex items-center justify-between">
            <span>Traffic over time</span>
            <span className="text-cyan-400 font-normal">Packets per second</span>
          </h2>
          <LiveTrafficChart />
        </div>

        <div className="glass-panel p-5 rounded-xl">
          <h2 className="text-xs font-mono text-slate-400 uppercase tracking-wider mb-4">
            Types of activity
          </h2>
          <AttackDistributionChart distribution={summary?.attack_distribution} />
        </div>
      </div>

      {/* Live Threat Telemetry & Recent Incidents */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-panel p-5 rounded-xl space-y-4">
          <h2 className="text-xs font-mono text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <span>Recent alerts</span>
            <span className="text-rose-400 text-[10px]">Needs attention</span>
          </h2>
          <IncidentTable incidents={summary?.recent_incidents || []} />
        </div>

        {/* Live alert ticker */}
        <div className="glass-panel p-5 rounded-xl space-y-3">
          <h2 className="text-xs font-mono text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <span>Live alerts</span>
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          </h2>
          <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
            {threatAlerts.length === 0 ? (
              <div className="text-xs font-mono text-slate-500 py-6 text-center">
                No new alerts. SentinelAI is watching your network.
              </div>
            ) : (
              threatAlerts.map((t, idx) => (
                <div key={idx} className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-xs font-mono space-y-1">
                  <div className="flex justify-between items-center text-rose-400 font-bold">
                    <span>{t.attack_type}</span>
                    <span className="text-[10px] text-slate-400">{t.severity}</span>
                  </div>
                  <div className="text-[11px] text-slate-300">
                    Src: {t.source_ip} | Proto: {t.protocol}
                  </div>
                  <div className="text-[10px] text-slate-500">
                    Confidence: {(t.confidence_score * 100).toFixed(1)}%
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
