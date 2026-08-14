import React, { useState, useEffect } from 'react';
import { BarChart3, AlertOctagon } from 'lucide-react';
import api from '../services/api';

interface AnomalyItem {
  id: string;
  asset_id: string;
  metric_name: string;
  observed_value: number;
  baseline_mean: number;
  baseline_std: number;
  z_score: number;
  anomaly_score: number;
  severity: string;
  explanation: string;
  timestamp: string | null;
}

export const AnalyticsView: React.FC = () => {
  const [anomalies, setAnomalies] = useState<AnomalyItem[]>([]);
  const [metrics, setMetrics] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [anomRes, metricRes] = await Promise.all([
          api.get('/analytics/anomalies'),
          api.get('/analytics/metrics')
        ]);
        const anomList = Array.isArray(anomRes.data) ? anomRes.data : (anomRes.data?.items || []);
        setAnomalies(anomList);
        setMetrics(metricRes.data || {});
      } catch (err) {
        console.error('Failed to load analytics', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2.5">
          <BarChart3 className="w-7 h-7 text-emerald-400" />
          Advanced SOC Analytics & Behavioral Baselines
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Asset-specific statistical baselines, explainable anomaly detection ($z \ge 3.0$), and threat distribution.
        </p>
      </div>

      {/* Metric Cards */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="text-xs font-mono text-slate-400">Total Alerts</div>
            <div className="text-2xl font-bold text-slate-100 mt-1">{metrics.total_alerts}</div>
          </div>
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="text-xs font-mono text-slate-400">Active Incidents</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{metrics.total_incidents}</div>
          </div>
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="text-xs font-mono text-slate-400">Active IOC Indicators</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{metrics.active_threat_indicators}</div>
          </div>
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="text-xs font-mono text-slate-400">Behavioral Anomalies</div>
            <div className="text-2xl font-bold text-amber-400 mt-1">{metrics.total_anomalies_detected}</div>
          </div>
        </div>
      )}

      {/* Behavioral Anomalies Stream */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <AlertOctagon className="w-4 h-4 text-amber-400" />
            Explainable Behavioral Anomalies Stream
          </div>
          <div className="text-xs font-mono text-slate-500">Z-Score Statistical Deviation Threshold: 3.0σ</div>
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-xs font-mono text-slate-500 animate-pulse">
            LOADING BEHAVIORAL ANOMALY EVENTS...
          </div>
        ) : anomalies.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500">
            No active behavioral anomalies detected. Asset telemetry is within normal baseline distribution.
          </div>
        ) : (
          <div className="divide-y divide-slate-800/60">
            {anomalies.map(anom => (
              <div key={anom.id} className="p-4 hover:bg-slate-800/30 transition flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      anom.severity === 'CRITICAL'
                        ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                        : anom.severity === 'HIGH'
                        ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                        : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                    }`}>
                      {anom.severity} ({anom.anomaly_score}/100)
                    </span>
                    <span className="font-mono text-slate-300 font-medium">Metric: {anom.metric_name}</span>
                    <span className="text-slate-500 font-mono">Z-Score: +{anom.z_score}σ</span>
                  </div>
                  <p className="text-slate-300 font-mono text-[11px] leading-relaxed">
                    {anom.explanation}
                  </p>
                </div>
                <div className="text-right text-slate-500 font-mono text-[10px] shrink-0">
                  {anom.timestamp ? new Date(anom.timestamp).toLocaleString() : 'Just now'}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalyticsView;
