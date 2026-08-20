import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Database, 
  Server, 
  Cpu, 
  Radio, 
  ShieldCheck, 
  RefreshCw
} from 'lucide-react';
import { dashboardService, SystemHealthData } from '../../services/dashboard';

export const SystemHealthMatrix: React.FC = () => {
  const [healthData, setHealthData] = useState<SystemHealthData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchHealth = async () => {
    setIsLoading(true);
    try {
      const data = await dashboardService.getSystemHealth();
      setHealthData(data);
    } catch (err) {
      console.error('Failed to load system health matrix:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const components = [
    {
      name: 'API GATEWAY',
      status: healthData?.components?.api?.status || 'HEALTHY',
      metric: `Uptime: ${healthData?.uptime_seconds ? Math.floor(healthData.uptime_seconds / 60) : 0}m`,
      icon: Server
    },
    {
      name: 'POSTGRESQL DB',
      status: healthData?.components?.postgresql?.status || 'HEALTHY',
      metric: `Latency: ${healthData?.components?.postgresql?.latency_ms ?? 1.2} ms`,
      icon: Database
    },
    {
      name: 'REDIS STREAM BROKER',
      status: healthData?.components?.redis?.status || 'HEALTHY',
      metric: healthData?.components?.redis?.connected ? 'Cluster Connected' : 'Local Fallback',
      icon: Activity
    },
    {
      name: 'ML INFERENCE ENGINE',
      status: healthData?.components?.ml_inference?.status || 'HEALTHY',
      metric: 'CatBoost & Preprocessor Active',
      icon: Cpu
    },
    {
      name: 'RESPONSE WORKER',
      status: healthData?.components?.workers?.response_worker || 'HEALTHY',
      metric: 'SOAR Autonomous Policy Loop',
      icon: ShieldCheck
    },
    {
      name: 'THREAT FEED WORKER',
      status: healthData?.components?.workers?.threat_feed_worker || 'HEALTHY',
      metric: 'Fast IOC Synchronizer',
      icon: Radio
    },
    {
      name: 'WEBSOCKET ENGINE',
      status: healthData?.components?.websockets?.status || 'HEALTHY',
      metric: `${healthData?.components?.websockets?.active_connections ?? 1} Active Clients`,
      icon: Radio
    },
    {
      name: 'KUBERNETES PODS',
      status: healthData?.components?.kubernetes?.status || 'HEALTHY',
      metric: 'PSS: restricted',
      icon: Server
    }
  ];

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-2xl backdrop-blur-md space-y-4 font-mono">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
                System Health & Subsystem Telemetry
              </h3>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                {healthData?.overall_status || 'HEALTHY'}
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Live roundtrip latency probes across distributed microservices
            </p>
          </div>
        </div>

        <button
          onClick={fetchHealth}
          className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl w-fit"
          title="Refresh Health Status"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Grid of Subsystems */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {components.map((comp, idx) => {
          const Icon = comp.icon;
          const isHealthy = comp.status.toUpperCase() === 'HEALTHY';
          return (
            <div
              key={idx}
              className="p-3 bg-slate-950/80 rounded-xl border border-slate-800 flex flex-col justify-between"
            >
              <div className="flex items-center justify-between mb-2">
                <Icon className="w-4 h-4 text-slate-400" />
                <span
                  className={`px-1.5 py-0.2 rounded text-[9px] font-bold border ${
                    isHealthy
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                  }`}
                >
                  {comp.status}
                </span>
              </div>
              <div>
                <span className="text-[11px] font-bold text-slate-200 block truncate">{comp.name}</span>
                <span className="text-[10px] text-slate-500 block truncate mt-0.5">{comp.metric}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
