import React, { useEffect, useState } from 'react';
import {
  Crosshair,
  Shield,
  Activity,
  ChevronRight,
  Database,
  Radio,
  Zap,
  Flame,
  Search,
  Copy,
  Check
} from 'lucide-react';
import { saasApi } from '../services/saas';

export const ThreatIntelCenterV2: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'actors' | 'feeds' | 'indicators' | 'heatmaps' | 'hunting_dispatcher'>('overview');
  const [summary, setSummary] = useState<any>(null);
  const [actors, setActors] = useState<any[]>([]);
  const [feeds, setFeeds] = useState<any[]>([]);
  const [indicators, setIndicators] = useState<any[]>([]);
  const [heatmaps, setHeatmaps] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Hunting query dispatcher state
  const [selectedActor, setSelectedActor] = useState<string>('Volt Typhoon');
  const [generatedQueries, setGeneratedQueries] = useState<any[]>([]);
  const [dispatchLoading, setDispatchLoading] = useState<boolean>(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  useEffect(() => {
    fetchCTIData();
  }, []);

  const fetchCTIData = async () => {
    try {
      setLoading(true);
      const [sum, act, fd, ind, hm] = await Promise.all([
        saasApi.getCTISummary(),
        saasApi.getThreatActors(),
        saasApi.getSTIXFeeds(),
        saasApi.getCTIIndicators(),
        saasApi.getCampaignHeatmaps()
      ]);
      setSummary(sum);
      setActors(act);
      setFeeds(fd);
      setIndicators(ind);
      setHeatmaps(hm);
    } catch (err) {
      console.error('Failed to load CTI 2.0 data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePollFeed = async (feedId: string) => {
    try {
      await saasApi.pollSTIXFeed(feedId);
      fetchCTIData();
    } catch (err) {
      console.error('Failed to poll TAXII feed:', err);
    }
  };

  const handleGenerateQueries = async () => {
    try {
      setDispatchLoading(true);
      const queries = await saasApi.generateThreatHuntingQueries({ actor_name: selectedActor });
      setGeneratedQueries(queries);
    } catch (err) {
      console.error('Query generation failed:', err);
    } finally {
      setDispatchLoading(false);
    }
  };

  const handleCopyQuery = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Crosshair className="h-7 w-7 text-indigo-400" />
            Cyber Threat Intelligence (CTI) 2.0 & STIX/TAXII Engine
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            STIX 2.1 Feeds, Diamond Model Threat Attribution, Dynamic IOC Decay & MITRE ATT&CK Campaign Heatmaps.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('hunting_dispatcher')}
            className="flex items-center gap-2 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-colors"
          >
            <Zap className="h-4 w-4" /> Dispatch Hunting Queries
          </button>
        </div>
      </div>

      {/* Top Metric Ribbon */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">CTI Posture Score</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.overall_cti_posture_score}<span className="text-xs text-slate-500">/100</span></div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Strategic Grade</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">TAXII 2.1 Feeds</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{summary.active_stix_feeds_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Auto-Polling Active</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Active Indicators</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{summary.total_active_indicators_count.toLocaleString()}</div>
            <div className="text-[10px] text-cyan-400 mt-0.5">Time-Decayed IOCs</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Profiled Actors</div>
            <div className="text-2xl font-bold text-amber-400 mt-1">{summary.profiled_threat_actors_count}</div>
            <div className="text-[10px] text-amber-400 mt-0.5">Diamond Model Mapped</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Campaign Heatmaps</div>
            <div className="text-2xl font-bold text-rose-400 mt-1">{summary.high_heat_campaign_techniques_count}</div>
            <div className="text-[10px] text-rose-400 mt-0.5">Critical MITRE TTPs</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">STIX 2.1 Parser</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">ONLINE</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Continuous Sync</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'CTI 2.0 Overview', icon: Crosshair },
          { id: 'actors', label: 'Threat Actor Profiles', icon: Shield },
          { id: 'feeds', label: 'STIX/TAXII Feeds', icon: Radio },
          { id: 'indicators', label: 'IOC Ledger & Decay', icon: Database },
          { id: 'heatmaps', label: 'ATT&CK Heatmaps', icon: Flame },
          { id: 'hunting_dispatcher', label: 'Hunting Query Dispatcher', icon: Search }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'border-indigo-500 text-indigo-300'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Icon className="h-4 w-4" />{tab.label}
            </button>
          );
        })}
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Activity className="h-6 w-6 animate-spin text-indigo-400 mr-3" />
          Loading Cyber Threat Intelligence 2.0 Engine...
        </div>
      ) : (
        <>
          {/* TAB 1: Overview */}
          {activeTab === 'overview' && summary && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Threat Landscape */}
              <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Flame className="h-4 w-4 text-rose-400" /> Active Global Campaign Heat Matrix
                </h3>
                <div className="space-y-3">
                  {heatmaps.map((hm) => (
                    <div key={hm.id} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60 text-xs flex justify-between items-center">
                      <div>
                        <div className="font-bold text-slate-200">{hm.campaign_name}</div>
                        <div className="text-[10px] text-slate-400 mt-0.5">Actor: <span className="text-indigo-300 font-semibold">{hm.threat_actor}</span> · Technique: {hm.mitre_technique_id} ({hm.technique_name})</div>
                      </div>
                      <span className="px-2.5 py-1 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 text-[10px] font-bold">
                        HEAT LEVEL: {hm.heat_level}/5
                      </span>
                    </div>
                  ))}
                </div>

                <div className="pt-3 border-t border-slate-800/60">
                  <div className="text-xs font-bold text-slate-300 mb-2">Priority Proactive Threat Hunts:</div>
                  <div className="space-y-1.5">
                    {summary.recommended_hunting_priorities.map((hunt: string, idx: number) => (
                      <div key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                        <ChevronRight className="h-3.5 w-3.5 text-indigo-400 shrink-0 mt-0.5" />
                        {hunt}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Quick Threat Actor List */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Shield className="h-4 w-4 text-indigo-400" /> Tracked Threat Actors
                </h3>
                <div className="space-y-2.5">
                  {actors.map((act) => (
                    <div key={act.id} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60 text-xs space-y-1">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span>{act.actor_name}</span>
                        <span className={`text-[10px] font-bold ${act.actor_type === 'NATION_STATE' ? 'text-rose-400' : 'text-amber-400'}`}>
                          {act.actor_type}
                        </span>
                      </div>
                      <div className="text-[10px] text-slate-400">Origin: {act.country_of_origin} · Sophistication: {act.sophistication_level}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Threat Actor Profiles */}
          {activeTab === 'actors' && (
            <div className="space-y-4">
              {actors.map((act) => (
                <div key={act.id} className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-3 text-xs">
                  <div className="flex justify-between items-center font-bold text-slate-100">
                    <div className="flex items-center gap-2">
                      <span className="text-base text-indigo-300">{act.actor_name}</span>
                      <span className="text-slate-500 font-normal">({act.aliases.join(', ')})</span>
                    </div>
                    <span className="px-2.5 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 text-[10px]">
                      {act.actor_type} · {act.country_of_origin}
                    </span>
                  </div>

                  {/* Diamond Model Grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 pt-2">
                    <div className="p-3 bg-slate-950/80 rounded-lg border border-slate-800/60">
                      <div className="text-[10px] font-bold text-indigo-400 uppercase">1. Adversary</div>
                      <div className="text-slate-300 mt-1 font-semibold">{act.diamond_model.adversary}</div>
                    </div>
                    <div className="p-3 bg-slate-950/80 rounded-lg border border-slate-800/60">
                      <div className="text-[10px] font-bold text-cyan-400 uppercase">2. Capability</div>
                      <div className="text-slate-300 mt-1">{act.diamond_model.capability}</div>
                    </div>
                    <div className="p-3 bg-slate-950/80 rounded-lg border border-slate-800/60">
                      <div className="text-[10px] font-bold text-amber-400 uppercase">3. Infrastructure</div>
                      <div className="text-slate-300 mt-1">{act.diamond_model.infrastructure}</div>
                    </div>
                    <div className="p-3 bg-slate-950/80 rounded-lg border border-slate-800/60">
                      <div className="text-[10px] font-bold text-rose-400 uppercase">4. Victimology</div>
                      <div className="text-slate-300 mt-1">{act.diamond_model.victimology}</div>
                    </div>
                  </div>

                  <div className="flex justify-between items-center text-[11px] text-slate-400 pt-2 border-t border-slate-800/60">
                    <div><strong>Targeted Sectors:</strong> {act.targeted_sectors.join(', ')}</div>
                    <div><strong>Primary MITRE TTPs:</strong> {act.primary_mitre_techniques.join(', ')}</div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* TAB 3: STIX Feeds */}
          {activeTab === 'feeds' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Radio className="h-4 w-4 text-indigo-400" /> STIX 2.1 & TAXII 2.1 Threat Intelligence Feeds
              </h3>
              <div className="space-y-3">
                {feeds.map((fd) => (
                  <div key={fd.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs flex justify-between items-center">
                    <div className="space-y-1">
                      <div className="font-bold text-slate-200 text-sm">{fd.feed_name}</div>
                      <div className="text-slate-400 font-mono text-[10px]">{fd.taxii_server_url} ({fd.collection_id})</div>
                      <div className="text-[10px] text-slate-500">
                        Format: {fd.feed_format} · Interval: {fd.poll_interval_minutes}m · Reputation: {fd.feed_reputation_score}% · Total Ingested: {fd.total_indicators_ingested.toLocaleString()}
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-[10px] text-emerald-400 font-bold bg-emerald-500/10 px-2 py-1 rounded">
                        {fd.last_poll_status}
                      </span>
                      <button
                        onClick={() => handlePollFeed(fd.id)}
                        className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold"
                      >
                        Poll Now
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: IOC Ledger & Decay */}
          {activeTab === 'indicators' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Database className="h-4 w-4 text-cyan-400" /> Dynamic IOC Ledger with Exponential Time Decay
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                    <tr>
                      <th className="p-3">Type</th>
                      <th className="p-3">Indicator Value</th>
                      <th className="p-3">Threat Actor</th>
                      <th className="p-3">Malware Family</th>
                      <th className="p-3">Initial Score</th>
                      <th className="p-3">Decayed Confidence</th>
                      <th className="p-3">Sightings</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50 text-slate-200">
                    {indicators.map((ind) => (
                      <tr key={ind.id} className="hover:bg-slate-950/40">
                        <td className="p-3">
                          <span className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] font-mono">{ind.indicator_type}</span>
                        </td>
                        <td className="p-3 font-mono text-indigo-300 truncate max-w-xs">{ind.indicator_value}</td>
                        <td className="p-3">{ind.threat_actor}</td>
                        <td className="p-3 text-slate-400">{ind.malware_family}</td>
                        <td className="p-3 text-slate-400">{ind.initial_confidence_score}%</td>
                        <td className="p-3 font-bold text-emerald-400">
                          {ind.current_confidence_score}%
                        </td>
                        <td className="p-3 text-cyan-300 font-bold">{ind.sighting_count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 5: ATT&CK Campaign Heatmaps */}
          {activeTab === 'heatmaps' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Flame className="h-4 w-4 text-rose-400" /> MITRE ATT&CK Campaign Technique Heatmap
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {heatmaps.map((hm) => (
                  <div key={hm.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold text-slate-200">
                      <span>{hm.technique_name}</span>
                      <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 text-[10px]">
                        HEAT: {hm.heat_level}/5
                      </span>
                    </div>
                    <div className="text-[10px] text-slate-400">
                      Technique ID: <strong className="text-indigo-300">{hm.mitre_technique_id}</strong> · Tactic: {hm.tactic_name}
                    </div>
                    <div className="text-[10px] text-slate-500">
                      Campaign: {hm.campaign_name} · Threat Actor: {hm.threat_actor} · Confidence: {hm.confidence_score}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 6: Hunting Query Dispatcher */}
          {activeTab === 'hunting_dispatcher' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Search className="h-4 w-4 text-indigo-400" /> Automated Threat Hunting Query Dispatcher
              </h3>
              <div className="flex gap-3 text-xs">
                <div className="flex-1">
                  <label className="block text-slate-400 mb-1">Target Threat Actor</label>
                  <select
                    value={selectedActor}
                    onChange={(e) => setSelectedActor(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                  >
                    <option value="Volt Typhoon">Volt Typhoon (Vanguard Panda)</option>
                    <option value="APT29">APT29 (Midnight Blizzard / Cozy Bear)</option>
                    <option value="LockBit 3.0">LockBit 3.0 (LockBit Black)</option>
                    <option value="Lazarus Group">Lazarus Group (HIDDEN COBRA)</option>
                  </select>
                </div>
                <div className="flex items-end">
                  <button
                    onClick={handleGenerateQueries}
                    disabled={dispatchLoading}
                    className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold"
                  >
                    {dispatchLoading ? 'Synthesizing...' : 'Generate Hunting Queries'}
                  </button>
                </div>
              </div>

              {generatedQueries.length > 0 && (
                <div className="space-y-3 pt-3">
                  {generatedQueries.map((q) => (
                    <div key={q.query_id} className="p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs space-y-2">
                      <div className="flex justify-between items-center font-bold">
                        <span className="text-slate-200">{q.title} ({q.technique_id})</span>
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 text-[10px]">{q.syntax}</span>
                          <button
                            onClick={() => handleCopyQuery(q.query_id, q.query_string)}
                            className="p-1 text-slate-400 hover:text-slate-200"
                          >
                            {copiedId === q.query_id ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                          </button>
                        </div>
                      </div>
                      <div className="p-2.5 bg-slate-900 rounded font-mono text-[11px] text-emerald-300 overflow-x-auto">
                        {q.query_string}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};
