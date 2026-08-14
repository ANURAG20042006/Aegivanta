import React, { useState, useEffect } from 'react';
import { Database, Search, RefreshCw } from 'lucide-react';
import api from '../services/api';

interface ThreatIndicatorItem {
  id: string;
  ioc_type: string;
  raw_value: string;
  normalized_value: string;
  threat_type: string;
  severity: string;
  confidence: number;
  source: string;
  description: string;
  tags: string[];
  hit_count: number;
  last_seen: string | null;
}

export const ThreatIntelView: React.FC = () => {
  const [indicators, setIndicators] = useState<ThreatIndicatorItem[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [lookupQuery, setLookupQuery] = useState<string>('');
  const [lookupResult, setLookupResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchIndicators = async (search?: string) => {
    try {
      const params = search ? { search } : {};
      const res = await api.get('/threat-intel/indicators', { params });
      const list = Array.isArray(res.data) ? res.data : (res.data?.items || []);
      setIndicators(list);
    } catch (err) {
      console.error('Failed to load threat indicators', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchIndicators();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchIndicators(searchQuery);
  };

  const handleLookup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!lookupQuery) return;
    try {
      const res = await api.post('/threat-intel/lookup', { value: lookupQuery });
      setLookupResult(res.data);
    } catch (err) {
      console.error('Lookup failed', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2.5">
          <Database className="w-7 h-7 text-indigo-400" />
          Threat Intelligence & IOC Repository
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Normalized Indicators of Compromise (IOCs), pluggable threat feed ingestion, and live event enrichment.
        </p>
      </div>

      {/* Quick Lookup Card */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
        <div className="text-xs font-semibold text-slate-300 flex items-center gap-2">
          <Search className="w-4 h-4 text-indigo-400" />
          Live Threat Intel IP / Domain Lookup
        </div>
        <form onSubmit={handleLookup} className="flex gap-2">
          <input
            type="text"
            placeholder="Enter IP (e.g. 198.51.100.22) or domain to check reputation..."
            value={lookupQuery}
            onChange={(e) => setLookupQuery(e.target.value)}
            className="flex-1 bg-slate-950/80 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500 transition"
          />
          <button
            type="submit"
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition"
          >
            Check IOC
          </button>
        </form>

        {lookupResult && (
          <div className={`p-3 rounded-lg border text-xs font-mono mt-2 ${
            lookupResult.is_match
              ? 'bg-rose-950/30 border-rose-500/30 text-rose-300'
              : 'bg-emerald-950/30 border-emerald-500/30 text-emerald-300'
          }`}>
            {lookupResult.is_match ? (
              <div>
                <span className="font-bold text-rose-400">[MATCH FOUND]</span> Known malicious indicator! Severity: {lookupResult.top_severity}. Matched {lookupResult.match_count} indicator(s).
              </div>
            ) : (
              <div>
                <span className="font-bold text-emerald-400">[CLEAN]</span> No matching threat intelligence records found for this indicator.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Search & Filter Bar */}
      <div className="flex items-center justify-between gap-4">
        <form onSubmit={handleSearch} className="flex-1 relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Filter indicators by IP, domain, or hash..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900/60 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500 transition"
          />
        </form>
        <button
          onClick={() => fetchIndicators()}
          className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-300 hover:bg-slate-700 transition flex items-center gap-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Reset
        </button>
      </div>

      {/* Indicators Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="text-sm font-semibold text-slate-200">Normalized Indicators of Compromise</div>
          <div className="text-xs font-mono text-slate-500">{indicators.length} Active Records</div>
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-xs font-mono text-slate-500 animate-pulse">
            QUERYING IOC DATABASE...
          </div>
        ) : indicators.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500">
            No threat indicators found matching query.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/40 text-slate-400 font-mono border-b border-slate-800">
                <tr>
                  <th className="p-3">Normalized Indicator</th>
                  <th className="p-3">Type</th>
                  <th className="p-3">Threat Type</th>
                  <th className="p-3">Severity</th>
                  <th className="p-3">Confidence</th>
                  <th className="p-3">Source Attribution</th>
                  <th className="p-3">Hits</th>
                  <th className="p-3">Last Seen</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {indicators.map(ind => (
                  <tr key={ind.id} className="hover:bg-slate-800/30 transition">
                    <td className="p-3 font-mono text-indigo-300 font-medium">
                      {ind.normalized_value}
                    </td>
                    <td className="p-3 font-mono text-slate-400">{ind.ioc_type.toUpperCase()}</td>
                    <td className="p-3 font-mono text-slate-300">{ind.threat_type}</td>
                    <td className="p-3">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold ${
                        ind.severity === 'CRITICAL'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : ind.severity === 'HIGH'
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          : 'bg-slate-700 text-slate-300'
                      }`}>
                        {ind.severity}
                      </span>
                    </td>
                    <td className="p-3 font-mono text-slate-300">{Math.round(ind.confidence * 100)}%</td>
                    <td className="p-3 font-mono text-slate-400">{ind.source}</td>
                    <td className="p-3 font-mono text-cyan-400 font-semibold">{ind.hit_count}</td>
                    <td className="p-3 font-mono text-slate-500">
                      {ind.last_seen ? new Date(ind.last_seen).toLocaleDateString() : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default ThreatIntelView;
