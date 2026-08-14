import React, { useState, useEffect } from 'react';
import { 
  BellRing, 
  ShieldAlert, 
  Search, 
  RefreshCw, 
  X,
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { AlertItem, AlertStatsResponse } from '../types';
import { alertService } from '../services/alertService';
import { useAuth } from '../hooks/useAuth';
import { useWebSocket } from '../hooks/useWebSocket';

export const AlertsPage: React.FC = () => {
  const { user } = useAuth();
  const { threatAlerts = [] } = useWebSocket();
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [stats, setStats] = useState<AlertStatsResponse>({
    total_active_alerts: 0,
    critical_alerts_count: 0,
    high_alerts_count: 0,
    new_alerts_count: 0,
    alerts_last_hour: 0,
    severity_breakdown: {}
  });

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [selectedSeverity, setSelectedSeverity] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [sourceIpFilter, setSourceIpFilter] = useState<string>('');
  const [activeAlertDetail, setActiveAlertDetail] = useState<AlertItem | null>(null);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState<boolean>(false);

  const canTriage = user?.role === 'admin' || user?.role === 'analyst';

  const fetchAlerts = async () => {
    setIsLoading(true);
    try {
      const [listRes, statsRes] = await Promise.allSettled([
        alertService.listAlerts({
          severity: selectedSeverity || undefined,
          status: selectedStatus || undefined,
          source_ip: sourceIpFilter || undefined
        }),
        alertService.getAlertStats()
      ]);

      if (listRes.status === 'fulfilled') {
        setAlerts(listRes.value.items || []);
      }
      if (statsRes.status === 'fulfilled') {
        setStats(statsRes.value);
      }
    } catch (err) {
      console.error('Failed to load live alerts:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [selectedSeverity, selectedStatus, sourceIpFilter]);

  // Re-fetch when a new WebSocket threat arrives
  useEffect(() => {
    if (threatAlerts.length > 0) {
      fetchAlerts();
    }
  }, [threatAlerts.length]);

  const handleUpdateStatus = async (alertId: string, newStatus: string) => {
    setIsUpdatingStatus(true);
    try {
      const updated = await alertService.updateStatus(alertId, newStatus);
      setAlerts((prev) => prev.map((a) => (a.id === updated.id ? updated : a)));
      if (activeAlertDetail && activeAlertDetail.id === updated.id) {
        setActiveAlertDetail(updated);
      }
      fetchAlerts();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update alert status');
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const getSeverityBadge = (sev: string) => {
    switch (sev.toLowerCase()) {
      case 'critical':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black uppercase bg-red-500/10 border border-red-500/30 text-red-400">CRITICAL</span>;
      case 'high':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase bg-amber-500/10 border border-amber-500/30 text-amber-400">HIGH</span>;
      case 'medium':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase bg-yellow-500/10 border border-yellow-500/30 text-yellow-400">MEDIUM</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">LOW</span>;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'new':
        return <span className="px-2 py-0.5 rounded-md text-[11px] font-bold bg-purple-500/10 border border-purple-500/30 text-purple-400 uppercase">NEW</span>;
      case 'acknowledged':
        return <span className="px-2 py-0.5 rounded-md text-[11px] font-bold bg-blue-500/10 border border-blue-500/30 text-blue-400 uppercase">ACKNOWLEDGED</span>;
      case 'investigating':
        return <span className="px-2 py-0.5 rounded-md text-[11px] font-bold bg-amber-500/10 border border-amber-500/30 text-amber-400 uppercase">INVESTIGATING</span>;
      case 'resolved':
        return <span className="px-2 py-0.5 rounded-md text-[11px] font-bold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 uppercase">RESOLVED</span>;
      default:
        return <span className="px-2 py-0.5 rounded-md text-[11px] font-bold bg-slate-500/10 border border-slate-500/30 text-slate-400 uppercase">DISMISSED</span>;
    }
  };

  return (
    <div className="space-y-6 pb-12 animate-fade-in">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-2xl text-red-400">
            <BellRing className="w-7 h-7 animate-pulse" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-100 font-mono uppercase tracking-wider">
              Live Threat Alert Center
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Continuous threat detections correlated from CatBoost ML inference, SHAP explanations, and network packet telemetry.
            </p>
          </div>
        </div>

        <button
          onClick={fetchAlerts}
          className="px-4 py-2.5 bg-slate-950 hover:bg-slate-800 text-cyan-400 border border-slate-800 rounded-xl text-xs font-mono font-bold transition-all flex items-center space-x-2 cursor-pointer self-start md:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh Alerts</span>
        </button>
      </div>

      {/* Stats Summary Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
          <span className="text-xs font-mono text-slate-400 uppercase">Active Actionable Alerts</span>
          <div className="text-2xl font-black font-mono text-slate-100 mt-1">{stats.total_active_alerts}</div>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
          <span className="text-xs font-mono text-red-400 uppercase">Critical Severity</span>
          <div className="text-2xl font-black font-mono text-red-400 mt-1">{stats.critical_alerts_count}</div>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
          <span className="text-xs font-mono text-amber-400 uppercase">High Severity</span>
          <div className="text-2xl font-black font-mono text-amber-400 mt-1">{stats.high_alerts_count}</div>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
          <span className="text-xs font-mono text-purple-400 uppercase">New Triage Queue</span>
          <div className="text-2xl font-black font-mono text-purple-400 mt-1">{stats.new_alerts_count}</div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 flex flex-wrap items-center gap-3">
        <div className="flex-1 min-w-[200px] relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
          <input
            type="text"
            value={sourceIpFilter}
            onChange={(e) => setSourceIpFilter(e.target.value)}
            placeholder="Filter by Source IP..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
          />
        </div>

        <select
          value={selectedSeverity}
          onChange={(e) => setSelectedSeverity(e.target.value)}
          className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-cyan-500 font-mono"
        >
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>

        <select
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-cyan-500 font-mono"
        >
          <option value="">All Statuses</option>
          <option value="new">New</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="investigating">Investigating</option>
          <option value="resolved">Resolved</option>
          <option value="dismissed">Dismissed</option>
        </select>
      </div>

      {/* Alerts Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-3.5">Alert ID & Title</th>
                <th className="px-4 py-3.5">Severity</th>
                <th className="px-4 py-3.5">Risk Score</th>
                <th className="px-4 py-3.5">Attack Classification</th>
                <th className="px-4 py-3.5">Source &rarr; Target</th>
                <th className="px-4 py-3.5">Status</th>
                <th className="px-4 py-3.5">Timestamp</th>
                <th className="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-slate-500">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-red-500" />
                    Loading alerts...
                  </td>
                </tr>
              ) : alerts.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-slate-500">
                    No security alerts found matching the current filter.
                  </td>
                </tr>
              ) : (
                alerts.map((alert) => (
                  <tr key={alert.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-bold text-slate-200 font-sans">{alert.title}</div>
                      <span className="text-[11px] text-cyan-400 font-mono">{alert.alert_id}</span>
                    </td>
                    <td className="px-4 py-4">
                      {getSeverityBadge(alert.severity)}
                    </td>
                    <td className="px-4 py-4">
                      <span className={`px-2 py-0.5 rounded-md font-bold border ${
                        alert.risk_score >= 75 ? 'bg-red-500/10 border-red-500/30 text-red-400' :
                        alert.risk_score >= 50 ? 'bg-amber-500/10 border-amber-500/30 text-amber-400' :
                        'bg-slate-950 border-slate-800 text-slate-300'
                      }`}>
                        {alert.risk_score.toFixed(1)}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <span className="font-bold text-slate-200">{alert.attack_type}</span>
                      {alert.confidence !== null && alert.confidence !== undefined && (
                        <div className="text-[10px] text-slate-500 mt-0.5">
                          Conf: {(alert.confidence * 100).toFixed(1)}%
                        </div>
                      )}
                    </td>
                    <td className="px-4 py-4 text-[11px] text-slate-300">
                      <div><span className="text-slate-500">Src:</span> {alert.source_ip}</div>
                      <div><span className="text-slate-500">Dst:</span> {alert.destination_ip}</div>
                    </td>
                    <td className="px-4 py-4">
                      {getStatusBadge(alert.status)}
                    </td>
                    <td className="px-4 py-4 text-slate-400 text-[11px]">
                      {new Date(alert.timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => setActiveAlertDetail(alert)}
                        className="px-3 py-1.5 bg-slate-950 hover:bg-cyan-950 text-cyan-400 rounded-lg border border-slate-800 hover:border-cyan-800 transition-colors text-xs font-mono cursor-pointer"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Alert Inspection Modal / Drawer */}
      {activeAlertDetail && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl animate-scale-in max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400">
                  <ShieldAlert className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-100 font-mono">
                    ALERT INSPECTOR: {activeAlertDetail.alert_id}
                  </h3>
                  <p className="text-xs text-slate-400 font-sans">
                    {activeAlertDetail.title}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setActiveAlertDetail(null)}
                className="text-slate-400 hover:text-slate-200 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs font-mono">
              {/* Telemetry Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-950 p-4 rounded-xl border border-slate-800">
                <div>
                  <span className="text-slate-500 uppercase block text-[10px]">Severity</span>
                  <div className="mt-1">{getSeverityBadge(activeAlertDetail.severity)}</div>
                </div>
                <div>
                  <span className="text-slate-500 uppercase block text-[10px]">Risk Score</span>
                  <span className="text-sm font-bold text-red-400 mt-1 block">{activeAlertDetail.risk_score.toFixed(1)} / 100</span>
                </div>
                <div>
                  <span className="text-slate-500 uppercase block text-[10px]">Confidence</span>
                  <span className="text-sm font-bold text-cyan-400 mt-1 block">
                    {activeAlertDetail.confidence ? `${(activeAlertDetail.confidence * 100).toFixed(1)}%` : 'N/A'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 uppercase block text-[10px]">Status</span>
                  <div className="mt-1">{getStatusBadge(activeAlertDetail.status)}</div>
                </div>
              </div>

              {/* Network flow info */}
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
                <div className="flex justify-between">
                  <span className="text-slate-500">Source IP & Port:</span>
                  <span className="text-slate-200 font-bold">{activeAlertDetail.source_ip}:{activeAlertDetail.source_port || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Target IP & Port:</span>
                  <span className="text-slate-200 font-bold">{activeAlertDetail.destination_ip}:{activeAlertDetail.destination_port || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Protocol:</span>
                  <span className="text-slate-200 font-bold">{activeAlertDetail.protocol}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Detection Source Engine:</span>
                  <span className="text-cyan-400 font-bold">{activeAlertDetail.source}</span>
                </div>
              </div>

              {/* SHAP Feature Explanations */}
              {activeAlertDetail.explanation && Object.keys(activeAlertDetail.explanation).length > 0 && (
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <div className="flex items-center space-x-2 mb-3 text-cyan-400 font-bold">
                    <Sparkles className="w-4 h-4" />
                    <span>Real SHAP Explainability (Top Influencing Features)</span>
                  </div>
                  <div className="space-y-2">
                    {Object.entries(activeAlertDetail.explanation).slice(0, 5).map(([feat, val]) => (
                      <div key={feat} className="flex items-center justify-between text-[11px]">
                        <span className="text-slate-400">{feat}</span>
                        <span className="text-amber-400 font-bold">SHAP: {Number(val).toFixed(4)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Correlated Incident CTA */}
              {activeAlertDetail.incident_id && (
                <div className="p-3 bg-cyan-950/30 border border-cyan-800/60 rounded-xl flex items-center justify-between">
                  <span className="text-cyan-300">Correlated into Security Incident:</span>
                  <Link
                    to={`/incidents/${activeAlertDetail.incident_id}`}
                    className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg font-bold flex items-center space-x-1.5 transition-colors"
                  >
                    <span>View Attack Timeline</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              )}

              {/* Triage Actions */}
              {canTriage && (
                <div className="pt-3 border-t border-slate-800 flex flex-wrap items-center justify-between gap-2">
                  <span className="text-slate-400 uppercase text-[10px]">Triage Actions:</span>
                  <div className="flex items-center space-x-2">
                    <button
                      disabled={isUpdatingStatus || activeAlertDetail.status === 'acknowledged'}
                      onClick={() => handleUpdateStatus(activeAlertDetail.id, 'acknowledged')}
                      className="px-3 py-1.5 bg-blue-950 hover:bg-blue-900 text-blue-300 border border-blue-800 rounded-lg transition-colors cursor-pointer disabled:opacity-40"
                    >
                      Acknowledge
                    </button>
                    <button
                      disabled={isUpdatingStatus || activeAlertDetail.status === 'investigating'}
                      onClick={() => handleUpdateStatus(activeAlertDetail.id, 'investigating')}
                      className="px-3 py-1.5 bg-amber-950 hover:bg-amber-900 text-amber-300 border border-amber-800 rounded-lg transition-colors cursor-pointer disabled:opacity-40"
                    >
                      Investigate
                    </button>
                    <button
                      disabled={isUpdatingStatus || activeAlertDetail.status === 'resolved'}
                      onClick={() => handleUpdateStatus(activeAlertDetail.id, 'resolved')}
                      className="px-3 py-1.5 bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-800 rounded-lg transition-colors cursor-pointer disabled:opacity-40"
                    >
                      Resolve
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
