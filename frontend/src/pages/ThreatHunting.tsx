import React, { useState, useEffect } from 'react';
import { Search, Play, Bookmark, Clock, Database, Filter } from 'lucide-react';
import { huntingService, HuntingResultItem, SavedQuery } from '../services/huntingService';

export const ThreatHunting: React.FC = () => {
  const [entity, setEntity] = useState<string>('alerts');
  const [timeRange, setTimeRange] = useState<string>('24h');
  const [sourceIp, setSourceIp] = useState<string>('');
  const [destinationIp, setDestinationIp] = useState<string>('');
  const [attackType, setAttackType] = useState<string>('');
  const [severity, setSeverity] = useState<string>('');
  const [keyword, setKeyword] = useState<string>('');
  
  const [results, setResults] = useState<HuntingResultItem[]>([]);
  const [savedQueries, setSavedQueries] = useState<SavedQuery[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [durationMs, setDurationMs] = useState<number>(0);
  const [selectedItem, setSelectedItem] = useState<HuntingResultItem | null>(null);
  const [saveQueryName, setSaveQueryName] = useState<string>('');
  const [showSaveModal, setShowSaveModal] = useState<boolean>(false);

  useEffect(() => {
    loadSavedQueries();
    executeHunt();
  }, []);

  const loadSavedQueries = async () => {
    try {
      const q = await huntingService.getSavedQueries();
      setSavedQueries(q);
    } catch (err) {
      console.error('Failed to load saved hunting queries', err);
    }
  };

  const executeHunt = async (overrideParams?: any) => {
    setLoading(true);
    try {
      const filters: any = {};
      if (sourceIp) filters.source_ip = sourceIp;
      if (destinationIp) filters.destination_ip = destinationIp;
      if (attackType) filters.attack_type = attackType;
      if (severity) filters.severity = severity;
      if (keyword) filters.keyword = keyword;

      const payload = overrideParams || {
        entity,
        time_range: timeRange,
        filters,
        limit: 100
      };

      const res = await huntingService.executeQuery(payload);
      setResults(res.results || []);
      setDurationMs(res.query_duration_ms || 0);
      if (res.results && res.results.length > 0) {
        setSelectedItem(res.results[0]);
      } else {
        setSelectedItem(null);
      }
    } catch (err) {
      console.error('Threat hunt query failed', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApplySavedQuery = (sq: SavedQuery) => {
    const def = sq.query_definition || {};
    if (def.entity) setEntity(def.entity);
    if (def.time_range) setTimeRange(def.time_range);
    const f = def.filters || {};
    setSourceIp(f.source_ip || '');
    setDestinationIp(f.destination_ip || '');
    setAttackType(f.attack_type || '');
    setSeverity(f.severity || '');
    setKeyword(f.keyword || '');
    executeHunt(def);
  };

  const handleSaveCurrentQuery = async () => {
    if (!saveQueryName.trim()) return;
    try {
      const filters: any = {};
      if (sourceIp) filters.source_ip = sourceIp;
      if (destinationIp) filters.destination_ip = destinationIp;
      if (attackType) filters.attack_type = attackType;
      if (severity) filters.severity = severity;
      if (keyword) filters.keyword = keyword;

      await huntingService.saveQuery(saveQueryName, 'Custom threat hunting query', {
        entity,
        time_range: timeRange,
        filters
      });
      setShowSaveModal(false);
      setSaveQueryName('');
      loadSavedQueries();
    } catch (err) {
      console.error('Failed to save query', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center bg-slate-900/40 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-indigo-500/10 rounded-lg text-indigo-400 border border-indigo-500/20">
              <Search className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-wide">Threat Hunting Engine</h1>
          </div>
          <p className="text-slate-400 text-sm">
            Execute parameterized multi-signal threat hunts across flow alerts, incidents, and threat intelligence feeds.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowSaveModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-sm font-medium border border-slate-700 transition"
          >
            <Bookmark className="w-4 h-4 text-indigo-400" />
            Save Query
          </button>
          <button
            onClick={() => executeHunt()}
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-medium shadow-lg shadow-indigo-500/20 transition disabled:opacity-50"
          >
            <Play className="w-4 h-4 fill-current" />
            {loading ? 'Executing Hunt...' : 'Run Query'}
          </button>
        </div>
      </div>

      {/* Query Builder & Saved Queries */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Saved Queries Sidebar */}
        <div className="bg-slate-900/40 p-5 rounded-2xl border border-slate-800 space-y-4">
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <Bookmark className="w-4 h-4 text-indigo-400" />
            Saved Hunt Queries
          </h2>
          <div className="space-y-2">
            {savedQueries.length === 0 ? (
              <p className="text-xs text-slate-500 py-3">No saved queries found.</p>
            ) : (
              savedQueries.map((sq) => (
                <button
                  key={sq.id}
                  onClick={() => handleApplySavedQuery(sq)}
                  className="w-full text-left p-3 rounded-xl bg-slate-800/40 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 transition group"
                >
                  <div className="text-sm font-medium text-slate-200 group-hover:text-indigo-400 transition">{sq.name}</div>
                  <div className="text-xs text-slate-400 line-clamp-1 mt-0.5">{sq.description || 'Target: ' + sq.query_definition?.entity}</div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Filter Controls */}
        <div className="lg:col-span-3 bg-slate-900/40 p-5 rounded-2xl border border-slate-800 space-y-4">
          <div className="text-sm font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <Filter className="w-4 h-4 text-indigo-400" />
            Parameterized Filters
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1">Target Entity</label>
              <select
                value={entity}
                onChange={(e) => setEntity(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="alerts">Security Flow Alerts</option>
                <option value="incidents">Correlated Incidents</option>
                <option value="iocs">Threat Intel IOCs</option>
              </select>
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">Time Horizon</label>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="1h">Last 1 Hour</option>
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
              </select>
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">Attack Type / Category</label>
              <input
                type="text"
                placeholder="e.g. DDoS, PortScan, Infiltration"
                value={attackType}
                onChange={(e) => setAttackType(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 placeholder-slate-500"
              />
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">Source IP / CIDR</label>
              <input
                type="text"
                placeholder="e.g. 185.220.101.5"
                value={sourceIp}
                onChange={(e) => setSourceIp(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 placeholder-slate-500"
              />
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">Destination IP</label>
              <input
                type="text"
                placeholder="e.g. 198.51.100.10"
                value={destinationIp}
                onChange={(e) => setDestinationIp(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 placeholder-slate-500"
              />
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">Severity / Status</label>
              <select
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="">All Severities</option>
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Results Header & Stats */}
      <div className="flex items-center justify-between text-xs text-slate-400 px-1">
        <div className="flex items-center gap-4">
          <span className="font-semibold text-slate-200">{results.length} Match Results</span>
          <span>•</span>
          <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {durationMs} ms query latency</span>
        </div>
        <div className="text-slate-500">Parameterized SQLAlchemy Bound Query</div>
      </div>

      {/* Results Table & Detail Pane */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-900/40 rounded-2xl border border-slate-800 overflow-hidden">
          <div className="overflow-x-auto max-h-[520px]">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-800/80 text-slate-400 text-xs uppercase sticky top-0 backdrop-blur-md">
                <tr>
                  <th className="p-3.5">Entity / Type</th>
                  <th className="p-3.5">Source &rarr; Dest</th>
                  <th className="p-3.5">Severity / Risk</th>
                  <th className="p-3.5">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {results.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="p-8 text-center text-slate-500">
                      No matching records found for the specified hunting parameters.
                    </td>
                  </tr>
                ) : (
                  results.map((item) => (
                    <tr
                      key={item.id}
                      onClick={() => setSelectedItem(item)}
                      className={`hover:bg-slate-800/50 cursor-pointer transition ${selectedItem?.id === item.id ? 'bg-indigo-950/30 border-l-2 border-indigo-500' : ''}`}
                    >
                      <td className="p-3.5">
                        <div className="font-semibold text-slate-200">{item.title || item.attack_type || item.value}</div>
                        <div className="text-xs text-indigo-400 font-mono">{item.entity}</div>
                      </td>
                      <td className="p-3.5 text-xs text-slate-300 font-mono">
                        {item.source_ip || item.value || 'N/A'} {item.destination_ip ? `→ ${item.destination_ip}` : ''}
                      </td>
                      <td className="p-3.5">
                        <span className={`px-2 py-0.5 rounded text-xs font-semibold uppercase ${
                          item.severity === 'CRITICAL' || item.severity === 'High' ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
                          item.severity === 'HIGH' ? 'bg-orange-500/10 text-orange-400 border border-orange-500/20' :
                          'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        }`}>
                          {item.severity || 'INFO'} {item.risk_score ? `(${item.risk_score})` : ''}
                        </span>
                      </td>
                      <td className="p-3.5 text-xs text-slate-400">
                        {item.timestamp ? new Date(item.timestamp).toLocaleTimeString() : (item.created_at ? new Date(item.created_at).toLocaleTimeString() : 'N/A')}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Drilldown Evidence Pane */}
        <div className="bg-slate-900/40 p-5 rounded-2xl border border-slate-800 space-y-4">
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <Database className="w-4 h-4 text-indigo-400" />
            Inspection & Evidence
          </h2>

          {selectedItem ? (
            <div className="space-y-4 text-xs">
              <div className="p-3.5 bg-slate-800/60 rounded-xl border border-slate-700/60 space-y-2">
                <div className="text-slate-400">Target Identifier</div>
                <div className="font-mono text-indigo-300 break-all">{selectedItem.id}</div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-800">
                  <div className="text-slate-500">Attack Type</div>
                  <div className="font-semibold text-slate-200 mt-0.5">{selectedItem.attack_type || 'N/A'}</div>
                </div>
                <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-800">
                  <div className="text-slate-500">Risk Score</div>
                  <div className="font-semibold text-amber-400 mt-0.5">{selectedItem.risk_score || 'N/A'} / 100</div>
                </div>
              </div>

              {selectedItem.explanation && (
                <div className="p-3.5 bg-slate-800/40 rounded-xl border border-slate-800 space-y-1.5">
                  <div className="text-slate-400 font-medium">Context / Explanation:</div>
                  <pre className="text-[11px] text-slate-300 whitespace-pre-wrap font-mono">
                    {JSON.stringify(selectedItem.explanation, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-slate-500 py-10 text-center">Select any result row to inspect forensic evidence.</p>
          )}
        </div>
      </div>

      {/* Save Query Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4">
            <h3 className="text-lg font-semibold text-white">Save Threat Hunt Query</h3>
            <p className="text-xs text-slate-400">Store current filter parameters as a reusable search template.</p>
            <input
              type="text"
              placeholder="Query Name (e.g. Ingress SSH Scanners)"
              value={saveQueryName}
              onChange={(e) => setSaveQueryName(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
            />
            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={() => setShowSaveModal(false)}
                className="px-4 py-2 text-slate-400 hover:text-white text-sm"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveCurrentQuery}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-medium"
              >
                Save Template
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
