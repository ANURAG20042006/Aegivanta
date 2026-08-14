import React, { useState, useEffect } from 'react';
import { Globe, ShieldAlert, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';
import api from '../services/api';

interface MonitoringCheckItem {
  id: string;
  asset_id: string;
  monitor_type: string;
  target_url: string;
  expected_status_code: number;
  timeout_seconds: number;
  interval_seconds: number;
  is_enabled: boolean;
  health_state: string;
  consecutive_failures: number;
  last_check_at: string | null;
  last_status_code: number | null;
  last_response_time_ms: number | null;
  last_error_message: string | null;
  dns_resolved_ip: string | null;
}

export const MonitoringView: React.FC = () => {
  const [checks, setChecks] = useState<MonitoringCheckItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [runningId, setRunningId] = useState<string | null>(null);

  const fetchChecks = async () => {
    try {
      const res = await api.get('/monitoring/checks');
      setChecks(res.data || []);
    } catch (err) {
      console.error('Failed to load monitoring checks', err);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchChecks();
    const interval = setInterval(fetchChecks, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleRunCheck = async (checkId: string) => {
    setRunningId(checkId);
    try {
      await api.post(`/monitoring/checks/${checkId}/run`);
      await fetchChecks();
    } catch (err) {
      console.error('Failed to execute health check', err);
    } finally {
      setRunningId(null);
    }
  };

  const healthyCount = checks.filter(c => c.health_state === 'HEALTHY').length;
  const degradedCount = checks.filter(c => c.health_state === 'DEGRADED').length;
  const downCount = checks.filter(c => c.health_state === 'DOWN').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2.5">
            <Globe className="w-7 h-7 text-cyan-400" />
            Continuous Asset & Endpoint Monitoring
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            SSRF-protected HTTP/HTTPS health checks, latency tracking, and automatic outage escalation.
          </p>
        </div>
        <button
          onClick={() => { setIsRefreshing(true); fetchChecks(); }}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-300 hover:bg-slate-700 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <div className="text-xs font-mono text-slate-400">Total Monitored</div>
          <div className="text-2xl font-bold text-slate-100 mt-1">{checks.length}</div>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/60 border border-emerald-500/20">
          <div className="text-xs font-mono text-emerald-400 flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5" /> Healthy
          </div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">{healthyCount}</div>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/60 border border-amber-500/20">
          <div className="text-xs font-mono text-amber-400 flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5" /> Degraded
          </div>
          <div className="text-2xl font-bold text-amber-400 mt-1">{degradedCount}</div>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/60 border border-rose-500/20">
          <div className="text-xs font-mono text-rose-400 flex items-center gap-1.5">
            <ShieldAlert className="w-3.5 h-3.5" /> Outage (Down)
          </div>
          <div className="text-2xl font-bold text-rose-400 mt-1">{downCount}</div>
        </div>
      </div>

      {/* Checks Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="text-sm font-semibold text-slate-200">Active Monitoring Targets</div>
          <div className="text-xs font-mono text-slate-500">SSRF Enforcement Active</div>
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-xs font-mono text-slate-500 animate-pulse">
            LOADING MONITORING TELEMETRY...
          </div>
        ) : checks.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500">
            No active monitoring checks configured. Monitored endpoints will appear here.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/40 text-slate-400 font-mono border-b border-slate-800">
                <tr>
                  <th className="p-3">Target Endpoint</th>
                  <th className="p-3">Type</th>
                  <th className="p-3">Health Status</th>
                  <th className="p-3">Resolved IP</th>
                  <th className="p-3">HTTP Status</th>
                  <th className="p-3">Latency</th>
                  <th className="p-3">Last Check</th>
                  <th className="p-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {checks.map(check => {
                  const isHealthy = check.health_state === 'HEALTHY';
                  const isDown = check.health_state === 'DOWN';
                  return (
                    <tr key={check.id} className="hover:bg-slate-800/30 transition">
                      <td className="p-3 font-mono text-cyan-300 font-medium max-w-xs truncate">
                        {check.target_url}
                      </td>
                      <td className="p-3 font-mono text-slate-400">{check.monitor_type}</td>
                      <td className="p-3">
                        <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          isHealthy
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : isDown
                            ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                            : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        }`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${
                            isHealthy ? 'bg-emerald-400' : isDown ? 'bg-rose-400' : 'bg-amber-400'
                          }`} />
                          {check.health_state}
                        </span>
                      </td>
                      <td className="p-3 font-mono text-slate-400">{check.dns_resolved_ip || '—'}</td>
                      <td className="p-3 font-mono">
                        {check.last_status_code ? (
                          <span className={check.last_status_code === 200 ? 'text-emerald-400' : 'text-amber-400'}>
                            {check.last_status_code}
                          </span>
                        ) : '—'}
                      </td>
                      <td className="p-3 font-mono text-slate-300">
                        {check.last_response_time_ms ? `${check.last_response_time_ms} ms` : '—'}
                      </td>
                      <td className="p-3 font-mono text-slate-500">
                        {check.last_check_at ? new Date(check.last_check_at).toLocaleTimeString() : 'Never'}
                      </td>
                      <td className="p-3 text-right">
                        <button
                          onClick={() => handleRunCheck(check.id)}
                          disabled={runningId === check.id}
                          className="px-2.5 py-1 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 hover:bg-cyan-500/20 transition text-[10px] font-mono disabled:opacity-50"
                        >
                          {runningId === check.id ? 'TESTING...' : 'TEST NOW'}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default MonitoringView;
