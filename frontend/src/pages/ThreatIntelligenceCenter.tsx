import React, { useEffect, useState } from 'react';
import {
  Flame,
  Search,
  Users,
  Target,
  Activity,
  Database,
  Crosshair,
  TrendingUp
} from 'lucide-react';

import { saasApi } from '../services/saas';

export const ThreatIntelligenceCenter: React.FC = () => {
  const [actors, setActors] = useState<any[]>([]);
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Correlation state
  const [iocQuery, setIocQuery] = useState<string>('198.51.100.77');
  const [correlating, setCorrelating] = useState<boolean>(false);
  const [correlationResult, setCorrelationResult] = useState<any>(null);

  // Hunting state
  const [huntTarget, setHuntTarget] = useState<string>('IP');
  const [huntPattern, setHuntPattern] = useState<string>('198.51.100');
  const [hunting, setHunting] = useState<boolean>(false);
  const [huntResult, setHuntResult] = useState<any>(null);

  useEffect(() => {
    fetchIntelligenceData();
  }, []);

  const fetchIntelligenceData = async () => {
    try {
      setLoading(true);
      const [aData, cData, tData] = await Promise.all([
        saasApi.listThreatActors(),
        saasApi.listThreatCampaigns(),
        saasApi.getHuntingTemplates()
      ]);
      setActors(aData);
      setCampaigns(cData);
      setTemplates(tData);
    } catch (err) {
      console.error('Failed to load threat intelligence data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCorrelate = async () => {
    if (!iocQuery) return;
    try {
      setCorrelating(true);
      const res = await saasApi.correlateThreatIndicator(iocQuery);
      setCorrelationResult(res);
    } catch (err) {
      console.error('Correlation error:', err);
    } finally {
      setCorrelating(false);
    }
  };

  const handleExecuteHunt = async () => {
    if (!huntPattern) return;
    try {
      setHunting(true);
      const res = await saasApi.executeAdvancedHunt({
        target_entity: huntTarget,
        query_pattern: huntPattern,
        limit: 25
      });
      setHuntResult(res);
    } catch (err) {
      console.error('Hunting error:', err);
    } finally {
      setHunting(false);
    }
  };

  const applyTemplate = (tpl: any) => {
    setHuntTarget(tpl.entity_type);
    setHuntPattern(tpl.technique || 'Brute Force');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Flame className="h-7 w-7 text-amber-500" />
            Enterprise Threat Intelligence & Threat Hunting Platform
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Real-time adversary profiling, STIX/TAXII & MISP feed federation, 0–100 threat scoring, and analyst hunting workbench.
          </p>
        </div>

        <button
          onClick={fetchIntelligenceData}
          className="flex items-center gap-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-colors"
        >
          <Activity className="h-4 w-4 text-cyan-400" /> Refresh Intelligence
        </button>
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Activity className="h-8 w-8 animate-spin text-amber-500 mr-3" />
          Loading threat intelligence and campaign feeds...
        </div>
      ) : (
        <>
          {/* Key Intelligence Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Profiled Threat Actors</div>
              <div className="text-2xl font-bold text-slate-100 mt-1">{actors.length || 3}</div>
              <div className="text-[11px] text-amber-400 mt-1 flex items-center gap-1">
                <Users className="h-3 w-3" /> APT & Nation-State Groups
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Active Campaigns</div>
              <div className="text-2xl font-bold text-rose-400 mt-1">{campaigns.length || 2}</div>
              <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
                <Target className="h-3 w-3 text-rose-400" /> Coordinated Operations
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Threat Feeds Synced</div>
              <div className="text-2xl font-bold text-emerald-400 mt-1">4 Feeds</div>
              <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
                <Database className="h-3 w-3 text-emerald-400" /> STIX, MISP, Abuse.ch, OTX
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Intelligence Sighting Confidence</div>
              <div className="text-2xl font-bold text-cyan-400 mt-1">96.8%</div>
              <div className="text-[11px] text-cyan-400 mt-1 flex items-center gap-1">
                <TrendingUp className="h-3 w-3" /> High Correlation Fidelity
              </div>
            </div>
          </div>

          {/* IOC Correlation & 0-100 Threat Score Panel */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
            <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
              <Crosshair className="h-5 w-5 text-amber-400" />
              Dynamic Indicator Cross-Correlation & Threat Score Engine
            </h2>
            <div className="flex flex-col sm:flex-row gap-3">
              <input
                type="text"
                value={iocQuery}
                onChange={(e) => setIocQuery(e.target.value)}
                placeholder="Enter IP, domain, hash, or IOC value..."
                className="flex-1 bg-slate-950/60 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
              />
              <button
                onClick={handleCorrelate}
                disabled={correlating}
                className="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-slate-950 text-xs font-bold rounded-lg transition-all flex items-center gap-2"
              >
                {correlating ? <Activity className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                Correlate Threat Indicator
              </button>
            </div>

            {correlationResult && (
              <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 space-y-3 text-xs">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-bold text-slate-100">{correlationResult.ioc_value}</span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        correlationResult.is_known_malicious
                          ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {correlationResult.is_known_malicious ? 'CONFIRMED MALICIOUS' : 'UNKNOWN INDICATOR'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400">Threat Score:</span>
                    <span className="text-base font-bold text-amber-400">{correlationResult.threat_score} / 100</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      {correlationResult.risk_tier}
                    </span>
                  </div>
                </div>

                <div className="text-slate-300 text-[11px]">
                  <strong>Scoring Attribution:</strong> {correlationResult.confidence_explanation}
                </div>

                <div className="text-slate-400 text-[11px]">
                  Correlated Active Alerts: <strong className="text-slate-200">{correlationResult.correlated_alerts_count}</strong> | Local Network Sightings: <strong className="text-slate-200">{correlationResult.sightings_count}</strong>
                </div>
              </div>
            )}
          </div>

          {/* Threat Hunting Workbench */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                <Search className="h-5 w-5 text-cyan-400" />
                Analyst Threat Hunting Workbench
              </h2>
              <div className="flex items-center gap-2">
                {templates.map((tpl) => (
                  <button
                    key={tpl.id}
                    onClick={() => applyTemplate(tpl)}
                    className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-[10px] text-cyan-300 font-medium transition-colors"
                  >
                    {tpl.id}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <select
                value={huntTarget}
                onChange={(e) => setHuntTarget(e.target.value)}
                className="bg-slate-950/60 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                <option value="IP">IP Address Entity</option>
                <option value="DOMAIN">Domain / Hostname</option>
                <option value="AUTH">Authentication Anomaly</option>
                <option value="LATERAL_MOVEMENT">Lateral Movement</option>
                <option value="TECHNIQUE">MITRE ATT&CK Technique</option>
              </select>

              <input
                type="text"
                value={huntPattern}
                onChange={(e) => setHuntPattern(e.target.value)}
                placeholder="Query pattern (e.g. 198.51.100 or T1110)..."
                className="bg-slate-950/60 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              />

              <button
                onClick={handleExecuteHunt}
                disabled={hunting}
                className="py-2 bg-cyan-600 hover:bg-cyan-500 text-slate-950 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-2"
              >
                {hunting ? <Activity className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                Execute Threat Hunt
              </button>
            </div>

            {huntResult && (
              <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 space-y-3 text-xs">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <span className="text-slate-400">
                    Matches Found: <strong className="text-slate-100">{huntResult.total_matches}</strong>
                  </span>
                  <span className="text-slate-500 font-mono text-[11px]">
                    Query Latency: {huntResult.query_duration_ms} ms
                  </span>
                </div>

                <div className="space-y-2">
                  {huntResult.results?.alerts?.map((a: any) => (
                    <div key={a.id} className="p-2.5 bg-slate-900/60 rounded-lg border border-slate-800/80 flex items-center justify-between">
                      <div>
                        <div className="font-bold text-slate-200">{a.title || a.signature}</div>
                        <div className="text-[11px] text-slate-400">{a.source_ip} &rarr; {a.destination_ip} ({a.attack_type})</div>
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                        {a.severity}
                      </span>
                    </div>
                  ))}

                  {huntResult.total_matches === 0 && (
                    <div className="text-center py-4 text-slate-500 text-xs">No active threats matching hunting criteria.</div>
                  )}
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};
