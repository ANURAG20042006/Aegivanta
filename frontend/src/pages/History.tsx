import React, { useState, useEffect } from 'react';
import { Filter, RefreshCw, Radio, Download } from 'lucide-react';
import { IncidentTable } from '../components/tables/IncidentTable';
import { incidentsService } from '../services/incidents';
import { IncidentItem } from '../types';
import { useWebSocket } from '../hooks/useWebSocket';

export const HistoryPage: React.FC = () => {
  const [incidents, setIncidents] = useState<IncidentItem[]>([]);
  const [total, setTotal] = useState(0);
  const [severity, setSeverity] = useState('');
  const [maliciousOnly, setMaliciousOnly] = useState(false);
  const [offset, setOffset] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');
  const [reloadKey, setReloadKey] = useState(0);
  const { threatAlerts } = useWebSocket();
  const pageSize = 25;

  useEffect(() => {
    const fetchIncidents = async () => {
      setIsLoading(true);
      setErrorMessage('');
      try {
        const result = await incidentsService.list({
          limit: pageSize,
          offset,
          severity: severity || undefined,
          is_malicious: maliciousOnly || undefined,
        });
        setIncidents(result.incidents || result.items || []);
        setTotal(result.total || 0);
      } catch (err) {
        console.error('Failed to load incident history:', err);
        setErrorMessage('We could not load saved alerts. Live alerts are still shown below.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchIncidents();
  }, [offset, severity, maliciousOnly, reloadKey]);

  const liveIncidents: IncidentItem[] = (threatAlerts || [])
    .filter((alert) => !severity || alert.severity === severity)
    .filter((alert) => !maliciousOnly || alert.is_malicious)
    .map((alert, index) => ({
      id: `live-${alert.timestamp}-${index}`,
      source_ip: alert.source_ip || '192.168.1.100',
      destination_ip: alert.destination_ip || '10.0.0.1',
      source_port: alert.source_port || 443,
      destination_port: alert.destination_port || 80,
      protocol: alert.protocol || 'TCP',
      attack_type: alert.attack_type || 'Malicious Flow',
      confidence_score: typeof alert.confidence_score === 'number' ? alert.confidence_score : null,
      is_malicious: alert.is_malicious,
      severity: alert.severity || 'High',
      model_name: 'Live monitor',
      timestamp: new Date().toISOString(),
    }));

  const isShowingLiveAlerts = total === 0 && incidents.length === 0 && liveIncidents.length > 0;
  const visibleIncidents = isShowingLiveAlerts ? liveIncidents : incidents;
  const visibleTotal = isShowingLiveAlerts ? liveIncidents.length : total;
  const firstVisible = visibleTotal === 0 ? 0 : offset + 1;
  const lastVisible = Math.min(offset + pageSize, visibleTotal);

  const handleExportCSV = () => {
    if (!visibleIncidents.length) return;
    const headers = ["ID", "Source IP", "Destination IP", "Protocol", "Attack Type", "Confidence", "Is Malicious", "Severity", "Timestamp"];
    const rows = visibleIncidents.map(i => [
      i.id, i.source_ip, i.destination_ip, i.protocol, i.attack_type, i.confidence_score, i.is_malicious, i.severity, i.timestamp
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `sentinelai_incident_report_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl flex items-center justify-between">
        <div>
          <h1 className="text-xl font-mono font-bold text-white">Alert history</h1>
          <p className="text-xs text-slate-400 font-mono mt-1">Review traffic that SentinelAI has checked and any alerts it found.</p>
        </div>
        <div className="flex items-center space-x-2 text-xs font-mono text-cyan-400">
          <Filter className="w-4 h-4" />
          <button type="button" onClick={() => setReloadKey((key) => key + 1)} title="Refresh alerts" aria-label="Refresh alerts" className="p-1.5 rounded border border-slate-700 hover:border-cyan-400 transition-colors">
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
          <select value={severity} onChange={(event) => { setSeverity(event.target.value); setOffset(0); }} className="bg-slate-900 border border-slate-700 rounded px-2 py-1">
            <option value="">All priorities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={maliciousOnly} onChange={(event) => { setMaliciousOnly(event.target.checked); setOffset(0); }} />
            Show threats only
          </label>
          <button
            type="button"
            onClick={handleExportCSV}
            className="flex items-center gap-1 text-xs font-semibold text-teal-300 bg-teal-500/10 border border-teal-500/30 px-3 py-1 rounded hover:bg-teal-500/20 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      <div className="glass-panel p-5 rounded-xl">
        {errorMessage && (
          <div className="friendly-note mb-4 flex items-center justify-between gap-3 text-xs text-slate-400 font-mono">
            <span>{errorMessage}</span>
            <button type="button" onClick={() => setReloadKey((key) => key + 1)} className="flex items-center gap-1 text-cyan-400 hover:text-cyan-300">
              <RefreshCw className="w-3.5 h-3.5" /> Try again
            </button>
          </div>
        )}
        {isShowingLiveAlerts && (
          <div className="mb-4 flex items-center gap-2 text-[10px] text-cyan-400 font-mono">
            <Radio className="w-3.5 h-3.5 animate-pulse" /> Showing alerts received during this live session. Saved results will appear here after an inspection.
          </div>
        )}
        <div className="flex items-center justify-between mb-4 text-xs font-mono text-slate-500">
          <span>{isLoading ? 'Loading alerts...' : visibleTotal === 0 ? 'No alerts yet' : `Showing ${firstVisible}–${lastVisible} of ${visibleTotal} alerts`}</span>
          <div className="flex gap-2">
            <button disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - pageSize))} className="px-2 py-1 border border-slate-700 rounded disabled:opacity-40">Previous</button>
            <button disabled={offset + pageSize >= visibleTotal} onClick={() => setOffset(offset + pageSize)} className="px-2 py-1 border border-slate-700 rounded disabled:opacity-40">Next</button>
          </div>
        </div>
        <IncidentTable incidents={visibleIncidents} />
      </div>
    </div>
  );
};
