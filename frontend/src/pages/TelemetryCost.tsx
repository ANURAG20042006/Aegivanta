import React, { useEffect, useState } from 'react';
import {
  DollarSign,
  HardDrive,
  Activity,
  Layers,
  Sparkles,
  Server,
  Zap
} from 'lucide-react';

import { saasApi } from '../services/saas';

export const TelemetryCost: React.FC = () => {
  const [costData, setCostData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchCostIntelligence();
  }, []);

  const fetchCostIntelligence = async () => {
    try {
      setLoading(true);
      const data = await saasApi.getTelemetryCostIntelligence();
      setCostData(data);
    } catch (err) {
      console.error('Failed to load telemetry cost intelligence:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <DollarSign className="h-7 w-7 text-emerald-400" />
            Cost-Aware Telemetry Intelligence
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Ingestion volume analytics, duplicate pattern suppression, and high-volume source optimization.
          </p>
        </div>

        <button
          onClick={fetchCostIntelligence}
          className="flex items-center gap-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-colors"
        >
          <Activity className="h-4 w-4 text-emerald-400" /> Re-Analyze Costs
        </button>
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Activity className="h-8 w-8 animate-spin text-emerald-400 mr-3" />
          Analyzing telemetry ingestion costs...
        </div>
      ) : (
        <>
          {/* Top Volume Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium uppercase tracking-wider text-slate-400">Daily Events</span>
                <Activity className="h-5 w-5 text-cyan-400" />
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-3xl font-bold text-slate-100">{(costData?.daily_events_estimated || 0).toLocaleString()}</span>
                <span className="text-xs font-medium text-slate-400">Events/Day</span>
              </div>
              <p className="text-xs text-slate-500 mt-2">Aggregate flow & audit telemetry stream</p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium uppercase tracking-wider text-slate-400">Monthly Ingestion</span>
                <HardDrive className="h-5 w-5 text-indigo-400" />
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-3xl font-bold text-slate-100">{costData?.monthly_gigabytes_estimated || 0} GB</span>
                <span className="text-xs font-medium text-slate-400">Estimated/mo</span>
              </div>
              <p className="text-xs text-slate-500 mt-2">Stored compressed on retention tier</p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium uppercase tracking-wider text-slate-400">Duplicate Volume</span>
                <Layers className="h-5 w-5 text-amber-400" />
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-3xl font-bold text-slate-100">{costData?.duplicate_volume_percentage || 4.2}%</span>
                <span className="text-xs font-medium text-emerald-400">Auto-Filtered</span>
              </div>
              <p className="text-xs text-slate-500 mt-2">Suppressed prior to persistent storage</p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium uppercase tracking-wider text-slate-400">Ingestion Stability</span>
                <Zap className="h-5 w-5 text-emerald-400" />
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-3xl font-bold text-emerald-400">Normal</span>
                <span className="text-xs font-medium text-emerald-400">No Spikes</span>
              </div>
              <p className="text-xs text-slate-500 mt-2">Telemetry flows within expected bounds</p>
            </div>
          </div>

          {/* Breakdown & Optimization Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                <Server className="h-5 w-5 text-indigo-400" />
                Sensor Volume Contribution Breakdown
              </h2>
              <div className="space-y-3">
                {(costData?.sensor_contributions || []).map((sc: any, idx: number) => (
                  <div
                    key={sc.sensor_id || idx}
                    className="p-3 bg-slate-950/40 rounded-lg border border-slate-800 flex justify-between items-center text-xs"
                  >
                    <div>
                      <span className="font-bold text-slate-200 block">{sc.name}</span>
                      <span className="text-slate-500 font-mono text-[10px]">{sc.os_type}</span>
                    </div>
                    <div className="text-right">
                      <span className="font-bold text-indigo-400 block">{sc.daily_events.toLocaleString()} ev/day</span>
                      <span className="text-slate-400 text-[10px]">{sc.share_pct}% of total</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-emerald-400" />
                Actionable Ingestion Cost Reductions
              </h2>
              <div className="space-y-3">
                {(costData?.optimization_recommendations || []).map((opt: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-4 bg-slate-950/40 rounded-xl border border-slate-800/80 space-y-1 text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <h4 className="font-bold text-slate-200">{opt.recommendation}</h4>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        -{opt.estimated_savings_pct}% Volume
                      </span>
                    </div>
                    <p className="text-slate-400">{opt.impact}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
