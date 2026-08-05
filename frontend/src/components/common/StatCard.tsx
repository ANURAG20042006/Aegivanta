import React from 'react';
import { LucideIcon } from 'lucide-react';

export interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  change?: string;
  isPositive?: boolean;
  trend?: string;
  trendType?: 'positive' | 'negative' | 'neutral';
  color?: 'cyan' | 'emerald' | 'crimson' | 'amber' | 'purple';
  gradient?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  change,
  isPositive = true,
  trend,
  trendType = 'neutral',
  color = 'cyan',
}) => {
  const colorMap = {
    cyan: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30',
    emerald: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
    crimson: 'text-rose-400 bg-rose-500/10 border-rose-500/30',
    amber: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
    purple: 'text-purple-400 bg-purple-500/10 border-purple-500/30',
  };

  const displayTrend = change || trend;
  const isPos = isPositive || trendType === 'positive';

  return (
    <div className="glass-panel depth-card p-5 rounded-xl transition-all duration-300 hover:border-slate-700 hover:shadow-lg relative overflow-hidden group">
      <div className="flex items-center justify-between">
        <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">{title}</span>
        <div className={`p-2.5 rounded-lg border ${colorMap[color]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-4 flex items-baseline justify-between">
        <div className="text-2xl font-bold font-mono text-white tracking-tight">{value}</div>
        {displayTrend && (
          <span
            className={`text-xs font-mono px-2 py-0.5 rounded ${
              isPos
                ? 'text-emerald-400 bg-emerald-500/10'
                : 'text-rose-400 bg-rose-500/10'
            }`}
          >
            {displayTrend}
          </span>
        )}
      </div>

      {subtitle && <p className="mt-1 text-[11px] text-slate-500 font-sans">{subtitle}</p>}
    </div>
  );
};
