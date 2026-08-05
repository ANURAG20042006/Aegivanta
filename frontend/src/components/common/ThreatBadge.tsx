import React from 'react';

interface ThreatBadgeProps {
  severity: 'Low' | 'Medium' | 'High' | 'Critical' | string;
  isMalicious?: boolean;
}

export const ThreatBadge: React.FC<ThreatBadgeProps> = ({ severity, isMalicious = true }) => {
  if (!isMalicious || severity === 'Low') {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-mono font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
        Normal
      </span>
    );
  }

  const badgeStyles: Record<string, string> = {
    Medium: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    High: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
    Critical: 'bg-rose-500/20 text-rose-400 border-rose-500/50 animate-pulse shadow-[0_0_10px_rgba(244,63,94,0.3)]',
  };

  const style = badgeStyles[severity] || badgeStyles['Medium'];

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-mono font-bold border ${style}`}>
      {severity === 'Critical' ? 'Urgent' : severity}
    </span>
  );
};
