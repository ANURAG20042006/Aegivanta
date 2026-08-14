import React, { useState, useEffect } from 'react';
import { Activity, Clock, ShieldCheck, UserCheck, AlertOctagon, TrendingDown, Layers } from 'lucide-react';
import { socMetricsService, SOCOverviewData } from '../services/socMetricsService';

export const SOCAnalytics: React.FC = () => {
  const [overview, setOverview] = useState<SOCOverviewData | null>(null);
  const [workload, setWorkload] = useState<any | null>(null);
  const [lookbackDays, setLookbackDays] = useState<number>(30);

  useEffect(() => {
    loadMetrics();
  }, [lookbackDays]);

  const loadMetrics = async () => {
    try {
      const [ov, wl] = await Promise.all([
        socMetricsService.getOverview(lookbackDays),
        socMetricsService.getWorkload()
      ]);
      setOverview(ov);
      setWorkload(wl);
    } catch (err) {
      console.error('Failed to load SOC effectiveness metrics', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center bg-slate-900/40 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-indigo-500/10 rounded-lg text-indigo-400 border border-indigo-500/20">
              <Activity className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-wide">SOC Effectiveness Analytics</h1>
          </div>
          <p className="text-slate-400 text-sm">
            Empirical Security Operations Center performance indicators: Mean Time to Detect (MTTD), Mean Time to Respond (MTTR), and triage workload.
          </p>
        </div>

        {/* Lookback Selector */}
        <select
          value={lookbackDays}
          onChange={(e) => setLookbackDays(Number(e.target.value))}
          className="bg-slate-800 border border-slate-700 rounded-xl px-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
        >
          <option value={7}>Past 7 Days</option>
          <option value={30}>Past 30 Days</option>
          <option value={90}>Past 90 Days</option>
        </select>
      </div>

      {/* Primary KPI Grid */}
      {overview && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-slate-900/40 p-5 rounded-2xl border border-slate-800 space-y-2">
            <div className="text-xs text-slate-400 font-semibold uppercase flex items-center gap-1.5">
              <Clock className="w-4 h-4 text-indigo-400" />
              Mean Time to Detect (MTTD)
            </div>
            <div className="text-3xl font-bold text-indigo-300">
              {overview.mttd_minutes} <span className="text-xs font-normal text-slate-400">minutes</span>
            </div>
            <div className="text-xs text-slate-500">First telemetry detection to alert</div>
          </div>

          <div className="bg-slate-900/40 p-5 rounded-2xl border border-slate-800 space-y-2">
            <div className="text-xs text-slate-400 font-semibold uppercase flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              Mean Time to Respond (MTTR)
            </div>
            <div className="text-3xl font-bold text-emerald-300">
              {overview.mttr_minutes} <span className="text-xs font-normal text-slate-400">minutes</span>
            </div>
            <div className="text-xs text-slate-500">Incident creation to containment</div>
          </div>

          <div className="bg-slate-900/40 p-5 rounded-2xl border border-slate-800 space-y-2">
            <div className="text-xs text-slate-400 font-semibold uppercase flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-purple-400" />
              Alert Compression Ratio
            </div>
            <div className="text-3xl font-bold text-purple-300">
              {overview.alert_to_incident_ratio}:1
            </div>
            <div className="text-xs text-slate-500">{overview.sample_alerts_count} alerts &rarr; {overview.sample_incidents_count} incidents</div>
          </div>

          <div className="bg-slate-900/40 p-5 rounded-2xl border border-slate-800 space-y-2">
            <div className="text-xs text-slate-400 font-semibold uppercase flex items-center gap-1.5">
              <TrendingDown className="w-4 h-4 text-amber-400" />
              False Positive Rate
            </div>
            <div className="text-3xl font-bold text-amber-300">
              {overview.estimated_false_positive_rate_pct}%
            </div>
            <div className="text-xs text-slate-500">Based on closed incident outcomes</div>
          </div>
        </div>
      )}

      {/* Workload and Incident Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Incident Status Breakdown */}
        <div className="bg-slate-900/40 p-6 rounded-2xl border border-slate-800 space-y-4">
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <AlertOctagon className="w-4 h-4 text-indigo-400" />
            Incident Lifecycle Status
          </h2>
          <div className="grid grid-cols-2 gap-4 pt-2">
            <div className="p-4 bg-slate-800/40 rounded-xl border border-slate-800 space-y-1">
              <div className="text-xs text-slate-400">Open / Investigating</div>
              <div className="text-2xl font-bold text-amber-400">{overview?.open_incidents || 0}</div>
            </div>
            <div className="p-4 bg-slate-800/40 rounded-xl border border-slate-800 space-y-1">
              <div className="text-xs text-slate-400">Resolved / Contained</div>
              <div className="text-2xl font-bold text-emerald-400">{overview?.resolved_incidents || 0}</div>
            </div>
          </div>
        </div>

        {/* Analyst Workload Distribution */}
        <div className="bg-slate-900/40 p-6 rounded-2xl border border-slate-800 space-y-4">
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <UserCheck className="w-4 h-4 text-indigo-400" />
            Analyst Action & Triage Workload
          </h2>
          <div className="space-y-3 pt-2">
            {workload?.distribution_by_analyst && Object.entries(workload.distribution_by_analyst).length > 0 ? (
              Object.entries(workload.distribution_by_analyst).map(([actor, count]: [string, any]) => (
                <div key={actor} className="flex justify-between items-center p-3 bg-slate-800/40 rounded-xl border border-slate-800 text-xs">
                  <span className="font-semibold text-slate-200">{actor}</span>
                  <span className="px-2.5 py-1 rounded bg-indigo-500/10 text-indigo-400 font-mono font-bold">
                    {count} actions
                  </span>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 py-4 text-center">No analyst action logs recorded in window.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
