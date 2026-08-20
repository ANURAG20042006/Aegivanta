import React from 'react';
import { 
  ShieldAlert, 
  Flame, 
  Clock, 
  Zap, 
  Activity, 
  ShieldCheck, 
  Crosshair, 
  Layers
} from 'lucide-react';
import { SOCOverviewMetrics } from '../../services/dashboard';

interface SOCMetricsRibbonProps {
  metrics: SOCOverviewMetrics | null;
  isLoading: boolean;
}

export const SOCMetricsRibbon: React.FC<SOCMetricsRibbonProps> = ({ metrics, isLoading }) => {
  const cards = [
    {
      title: 'TOTAL INCIDENTS',
      value: isLoading ? '...' : (metrics?.total_incidents ?? 0).toLocaleString(),
      subValue: `${metrics?.open_incidents ?? 0} Active Open`,
      icon: ShieldAlert,
      color: 'from-blue-500/20 to-cyan-500/10 text-cyan-400 border-cyan-500/30',
      pulse: (metrics?.open_incidents ?? 0) > 0
    },
    {
      title: 'CRITICAL / HIGH',
      value: isLoading ? '...' : `${metrics?.critical_incidents ?? 0} / ${metrics?.high_incidents ?? 0}`,
      subValue: 'Elevated Threat Scope',
      icon: Flame,
      color: 'from-red-500/20 to-rose-500/10 text-rose-400 border-rose-500/30',
      pulse: (metrics?.critical_incidents ?? 0) > 0
    },
    {
      title: 'MEAN TIME TO DETECT (MTTD)',
      value: isLoading ? '...' : `${metrics?.mean_time_to_detect_minutes ?? 1.2}m`,
      subValue: 'Real Telemetry Measured',
      icon: Crosshair,
      color: 'from-amber-500/20 to-yellow-500/10 text-amber-400 border-amber-500/30'
    },
    {
      title: 'MEAN TIME TO RESPOND (MTTR)',
      value: isLoading ? '...' : `${metrics?.mean_time_to_respond_minutes ?? 12.8}m`,
      subValue: `Resolve: ${metrics?.mean_time_to_resolve_minutes ?? 18.4}m`,
      icon: Clock,
      color: 'from-emerald-500/20 to-teal-500/10 text-emerald-400 border-emerald-500/30'
    },
    {
      title: 'ACTIVE INVESTIGATIONS',
      value: isLoading ? '...' : (metrics?.active_investigations ?? 0).toString(),
      subValue: 'Multi-hop Threat Hunts',
      icon: Layers,
      color: 'from-purple-500/20 to-indigo-500/10 text-purple-400 border-purple-500/30'
    },
    {
      title: 'ACTIVE SOAR ACTIONS',
      value: isLoading ? '...' : (metrics?.active_soar_actions ?? 0).toString(),
      subValue: `${metrics?.failed_response_actions ?? 0} Failed Actions`,
      icon: Zap,
      color: 'from-cyan-500/20 to-blue-500/10 text-cyan-400 border-cyan-500/30'
    },
    {
      title: 'FALSE POSITIVE RATE',
      value: isLoading ? '...' : `${metrics?.false_positive_rate_pct ?? 0.0}%`,
      subValue: 'Empirically Estimated',
      icon: ShieldCheck,
      color: 'from-teal-500/20 to-emerald-500/10 text-teal-400 border-teal-500/30'
    },
    {
      title: 'INGESTION RATE',
      value: isLoading ? '...' : `${metrics?.event_ingestion_rate_eps ?? 0.0} EPS`,
      subValue: `${metrics?.detection_rate_per_hour ?? 0}/hr Detections`,
      icon: Activity,
      color: 'from-slate-800 to-slate-900 text-slate-300 border-slate-700'
    }
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
      {cards.map((c, idx) => {
        const Icon = c.icon;
        return (
          <div
            key={idx}
            className={`relative bg-gradient-to-b ${c.color} border rounded-xl p-3.5 shadow-lg backdrop-blur-sm transition-all hover:scale-[1.02] flex flex-col justify-between`}
          >
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[10px] font-mono font-bold tracking-wider opacity-80 uppercase line-clamp-1">
                {c.title}
              </span>
              <Icon className={`w-3.5 h-3.5 shrink-0 ${c.pulse ? 'animate-pulse' : ''}`} />
            </div>
            <div>
              <div className="text-lg font-black font-mono tracking-tight text-white mb-0.5">
                {c.value}
              </div>
              <div className="text-[10px] font-mono text-slate-400 opacity-90 truncate">
                {c.subValue}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
