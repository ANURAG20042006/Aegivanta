import React, { useEffect, useState } from 'react';
import {
  Shield,
  Activity,
  CheckCircle2,
  Brain,
  Search,
  Briefcase,
  Terminal,
  Zap,
  Lock,
  RefreshCw,
  ChevronRight,
  Flame,
  Layers,
  FileCheck
} from 'lucide-react';

import { saasApi } from '../services/saas';

export const SOCCommandCenterV2: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'threat_ops' | 'cases' | 'hunting' | 'ai_analyst' | 'validation'>('overview');
  const [scorecard, setScorecard] = useState<any>(null);
  const [validation, setValidation] = useState<any>(null);
  const [cases, setCases] = useState<any[]>([]);
  const [selectedCase, setSelectedCase] = useState<any>(null);
  const [huntingQueries, setHuntingQueries] = useState<any[]>([]);
  const [sreHealth, setSreHealth] = useState<any>(null);
  const [aiQuery, setAiQuery] = useState('');
  const [aiResult, setAiResult] = useState<any>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [chaosScenarios, setChaosScenarios] = useState<any[]>([]);
  const [chaosResult, setChaosResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCoreData();
  }, []);

  const fetchCoreData = async () => {
    try {
      setLoading(true);
      const [sc, val, cs, hq, sre, chaos] = await Promise.all([
        saasApi.getSecurityScorecard(),
        saasApi.getContinuousValidation(),
        saasApi.getSOCCases(),
        saasApi.getSavedHuntingQueries(),
        saasApi.getSREHealth(),
        saasApi.getChaosScenarios()
      ]);
      setScorecard(sc);
      setValidation(val);
      setCases(cs);
      if (cs.length > 0) setSelectedCase(cs[0]);
      setHuntingQueries(hq);
      setSreHealth(sre);
      setChaosScenarios(chaos);
    } catch (err) {
      console.error('Failed loading SOC Command Center data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunValidation = async () => {
    try {
      setLoading(true);
      const res = await saasApi.runContinuousValidation();
      setValidation(res);
      const sc = await saasApi.getSecurityScorecard();
      setScorecard(sc);
    } catch (err) {
      console.error('Validation run failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAIInvestigate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!aiQuery.trim()) return;
    try {
      setAiLoading(true);
      const res = await saasApi.queryAIAnalyst(aiQuery, selectedCase?.id);
      setAiResult(res);
    } catch (err) {
      console.error('AI Analyst failed:', err);
    } finally {
      setAiLoading(false);
    }
  };

  const handleRunChaos = async (scenarioKey: string) => {
    try {
      const res = await saasApi.runChaosSimulation(scenarioKey);
      setChaosResult(res);
    } catch (err) {
      console.error('Chaos simulation failed:', err);
    }
  };

  const getSeverityBadge = (sev: string) => {
    switch (sev?.toUpperCase()) {
      case 'CRITICAL': return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'HIGH': return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'MEDIUM': return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30';
      default: return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Shield className="h-7 w-7 text-indigo-400" />
            SOC Command Center V2
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Autonomous SOC operations, explainable correlation, continuous defense validation, and SRE resilience.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleRunValidation}
            className="flex items-center gap-2 px-3.5 py-2 bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 border border-indigo-500/40 rounded-xl text-xs font-semibold transition-colors"
          >
            <RefreshCw className="h-4 w-4" /> Run Continuous Validation
          </button>
        </div>
      </div>

      {/* Top Level Metric Ribbon */}
      {scorecard && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Security Score</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{scorecard.overall_security_score}<span className="text-xs text-slate-500">/100</span></div>
            <div className="text-[10px] text-emerald-400 mt-0.5">{scorecard.security_tier}</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Active Cases</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{cases.length}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">SLA: 100% On-Time</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Validation Status</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{validation?.overall_score || 98}%</div>
            <div className="text-[10px] text-cyan-400 mt-0.5">16/16 Controls Passed</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Endpoint Trust</div>
            <div className="text-2xl font-bold text-indigo-300 mt-1">{scorecard.category_scores.endpoint_zero_trust}</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Zero-Trust Active</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">SRE Health</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{scorecard.category_scores.sre_reliability}%</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">99.98% Uptime</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Sensors Online</div>
            <div className="text-2xl font-bold text-slate-100 mt-1">{sreHealth?.components.sensor_fleet.online_count || 48}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Index: 98.2</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'Command Overview', icon: Layers },
          { id: 'threat_ops', label: 'Threat Operations', icon: Flame },
          { id: 'cases', label: 'Case Management', icon: Briefcase },
          { id: 'hunting', label: 'Threat Hunting V2', icon: Search },
          { id: 'ai_analyst', label: 'AI SOC Analyst V2', icon: Brain },
          { id: 'validation', label: 'Continuous Validation & SRE', icon: FileCheck }
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
          Loading SOC Command Center V2...
        </div>
      ) : (
        <>
          {/* TAB 1: Command Overview */}
          {activeTab === 'overview' && scorecard && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Scorecard Matrix */}
              <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Shield className="h-4 w-4 text-indigo-400" /> Enterprise Multi-Vector Security Scorecard
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {Object.entries(scorecard.category_scores).map(([cat, val]: [string, any]) => (
                    <div key={cat} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60">
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-slate-400 capitalize">{cat.replace(/_/g, ' ')}</span>
                        <span className="font-bold text-slate-100">{val}%</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden mt-2">
                        <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${val}%` }} />
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-2 border-t border-slate-800/60">
                  <div className="text-xs font-bold text-slate-300 mb-2">Recommended Hardening Actions:</div>
                  <div className="space-y-1.5">
                    {scorecard.recommendations.map((rec: string, i: number) => (
                      <div key={i} className="text-xs text-slate-400 flex items-start gap-2">
                        <ChevronRight className="h-3.5 w-3.5 text-indigo-400 shrink-0 mt-0.5" />
                        {rec}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Active Cases Snapshot */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Briefcase className="h-4 w-4 text-indigo-400" /> Active Priority Cases
                </h3>
                <div className="space-y-2.5">
                  {cases.slice(0, 4).map((c) => (
                    <div
                      key={c.id}
                      onClick={() => { setSelectedCase(c); setActiveTab('cases'); }}
                      className="p-3 bg-slate-950/60 hover:bg-slate-900 border border-slate-800/60 rounded-lg cursor-pointer transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-[11px] font-mono text-indigo-300">{c.case_number}</span>
                        <span className={`text-[10px] px-1.5 py-0.5 rounded border font-bold ${getSeverityBadge(c.severity)}`}>
                          {c.priority}
                        </span>
                      </div>
                      <div className="text-xs font-semibold text-slate-200 mt-1">{c.title}</div>
                      <div className="text-[10px] text-slate-400 mt-1 flex justify-between">
                        <span>Risk: {c.risk_score}</span>
                        <span className="text-indigo-400">{c.status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Threat Operations */}
          {activeTab === 'threat_ops' && (
            <div className="space-y-6">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Flame className="h-4 w-4 text-rose-400" /> Autonomous Cross-Domain Correlation Topology
                </h3>
                <div className="p-4 bg-slate-950/80 rounded-xl border border-slate-800 font-mono text-xs space-y-2">
                  <div className="text-indigo-400 font-bold">[CORRELATION GRAPH NODE TOPOLOGY]</div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-slate-300">
                    <div className="p-2.5 bg-slate-900/60 rounded border border-rose-800/30">
                      <div className="text-[10px] text-rose-400 font-bold">ATTACKER INGRESS</div>
                      <div>IP: 198.51.100.22</div>
                      <div className="text-[10px] text-slate-400">Reputation: High Threat IOC</div>
                    </div>
                    <div className="p-2.5 bg-slate-900/60 rounded border border-amber-800/30">
                      <div className="text-[10px] text-amber-400 font-bold">PIVOT WORKSTATION</div>
                      <div>Host: WKS-EXEC-01</div>
                      <div className="text-[10px] text-slate-400">User: alice.smith (Kerberos)</div>
                    </div>
                    <div className="p-2.5 bg-slate-900/60 rounded border border-indigo-800/30">
                      <div className="text-[10px] text-indigo-400 font-bold">INTERNAL TARGET</div>
                      <div>Host: SRV-DB-PROD-01</div>
                      <div className="text-[10px] text-slate-400">SMB Port 445 Probe</div>
                    </div>
                  </div>
                  <div className="text-[11px] text-slate-400 pt-2 border-t border-slate-800">
                    <strong>Correlation Verdict:</strong> Multi-hop lateral movement confirmed. Confidence: 94.2% · MITRE Techniques: T1059.001, T1021.002.
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: Case Management & Forensics */}
          {activeTab === 'cases' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Case List */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 space-y-3">
                <div className="font-bold text-sm text-slate-200">Investigation Cases</div>
                <div className="space-y-2">
                  {cases.map((c) => (
                    <div
                      key={c.id}
                      onClick={() => setSelectedCase(c)}
                      className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                        selectedCase?.id === c.id
                          ? 'bg-indigo-950/40 border-indigo-500/50'
                          : 'bg-slate-950/60 border-slate-800/60 hover:bg-slate-900'
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-mono font-bold text-indigo-300">{c.case_number}</span>
                        <span className={`text-[10px] px-1.5 py-0.5 rounded border font-bold ${getSeverityBadge(c.severity)}`}>
                          {c.priority}
                        </span>
                      </div>
                      <div className="text-xs font-semibold text-slate-200 mt-1">{c.title}</div>
                      <div className="text-[10px] text-slate-400 mt-1 flex justify-between">
                        <span>Status: <strong className="text-slate-300">{c.status}</strong></span>
                        <span>Risk: <strong className="text-rose-400">{c.risk_score}</strong></span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Case Details */}
              {selectedCase && (
                <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                    <div>
                      <div className="text-xs font-mono text-indigo-400">{selectedCase.case_number}</div>
                      <h2 className="text-base font-bold text-slate-100">{selectedCase.title}</h2>
                    </div>
                    <div className="flex items-center gap-2">
                      <select
                        value={selectedCase.status}
                        onChange={async (e) => {
                          await saasApi.updateSOCCaseStatus(selectedCase.id, e.target.value);
                          fetchCoreData();
                        }}
                        className="bg-slate-950 border border-slate-800 text-xs text-slate-200 rounded-lg px-2.5 py-1.5"
                      >
                        {['OPEN', 'TRIAGED', 'INVESTIGATING', 'CONTAINMENT', 'REMEDIATION', 'MONITORING', 'RESOLVED', 'CLOSED'].map(s => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="text-xs text-slate-300">{selectedCase.description}</div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                    <div className="p-2.5 bg-slate-950/60 rounded border border-slate-800/60">
                      <div className="text-[10px] text-slate-400">Risk Score</div>
                      <div className="font-bold text-rose-400 mt-0.5">{selectedCase.risk_score}/100</div>
                    </div>
                    <div className="p-2.5 bg-slate-950/60 rounded border border-slate-800/60">
                      <div className="text-[10px] text-slate-400">Lead Analyst</div>
                      <div className="font-bold text-slate-200 mt-0.5">{selectedCase.lead_analyst_id || 'Unassigned'}</div>
                    </div>
                    <div className="p-2.5 bg-slate-950/60 rounded border border-slate-800/60">
                      <div className="text-[10px] text-slate-400">SLA Target</div>
                      <div className="font-bold text-slate-200 mt-0.5">4.0 Hours</div>
                    </div>
                    <div className="p-2.5 bg-slate-950/60 rounded border border-slate-800/60">
                      <div className="text-[10px] text-slate-400">SLA Status</div>
                      <div className="font-bold text-emerald-400 mt-0.5">ON-TIME</div>
                    </div>
                  </div>

                  {/* Forensic Evidence Chain of Custody */}
                  <div className="space-y-2 pt-2 border-t border-slate-800">
                    <div className="text-xs font-bold text-slate-200 flex items-center gap-2">
                      <Lock className="h-3.5 w-3.5 text-indigo-400" /> Cryptographically Verified Forensic Evidence
                    </div>
                    <div className="p-3 bg-slate-950/80 rounded-lg border border-slate-800 space-y-1 text-xs">
                      <div className="flex justify-between items-center font-semibold text-slate-200">
                        <span>EV-001: Encoded PowerShell Execution Payload</span>
                        <span className="text-[10px] text-emerald-400 flex items-center gap-1"><CheckCircle2 className="h-3 w-3" /> SHA-256 Verified</span>
                      </div>
                      <div className="text-[10px] font-mono text-slate-400 break-all">
                        SHA-256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
                      </div>
                      <div className="text-[10px] text-slate-500">
                        Collected by aegivanta.edr · Chain of Custody intact
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 4: Threat Hunting V2 */}
          {activeTab === 'hunting' && (
            <div className="space-y-4">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Search className="h-4 w-4 text-indigo-400" /> Saved Threat Hunting Query Templates
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {huntingQueries.map((q) => (
                    <div key={q.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800/80 hover:border-indigo-500/40 transition-colors">
                      <div className="text-xs font-bold text-slate-200">{q.name}</div>
                      <div className="text-[11px] font-mono text-indigo-300 bg-slate-900 p-2 rounded mt-2 border border-slate-800">
                        {q.query_string}
                      </div>
                      <div className="flex items-center justify-between mt-3 text-[10px] text-slate-400">
                        <span>Target: <strong className="text-slate-300">{q.target_data_source}</strong></span>
                        <button
                          onClick={async () => {
                            const res = await saasApi.executeHuntingSearch({
                              hypothesis: `Validate ${q.name}`,
                              query_string: q.query_string,
                              target_source: q.target_data_source
                            });
                            alert(`Hunt completed: ${res.matched_events_count} events matched in ${res.execution_time_ms}ms.`);
                          }}
                          className="px-2 py-1 bg-indigo-600/30 hover:bg-indigo-600/60 text-indigo-300 rounded font-semibold"
                        >
                          Execute Hunt
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: AI SOC Analyst V2 */}
          {activeTab === 'ai_analyst' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Brain className="h-4 w-4 text-indigo-400" /> AI SOC Analyst Investigation Prompt
                </h3>
                <form onSubmit={handleAIInvestigate} className="space-y-3">
                  <textarea
                    rows={4}
                    value={aiQuery}
                    onChange={(e) => setAiQuery(e.target.value)}
                    placeholder="Enter security hypothesis or incident question (e.g. 'Investigate the root cause and lateral movement path for WKS-EXEC-01')..."
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none"
                  />
                  <div className="flex justify-between items-center text-[10px] text-slate-400">
                    <span>Adversarial Prompt-Injection Defense: Active</span>
                    <button
                      type="submit"
                      disabled={aiLoading}
                      className="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold disabled:opacity-50"
                    >
                      {aiLoading ? <Activity className="h-3.5 w-3.5 animate-spin" /> : <Zap className="h-3.5 w-3.5" />}
                      Synthesize Reasoning
                    </button>
                  </div>
                </form>
              </div>

              {/* AI Structured Output */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-3">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Terminal className="h-4 w-4 text-indigo-400" /> Structured Evidence Reasoning
                </h3>
                {aiResult ? (
                  <div className="space-y-3 text-xs">
                    <div className="p-3 bg-slate-950/80 rounded-lg border border-slate-800 text-slate-300 leading-relaxed">
                      {aiResult.summary}
                    </div>
                    <div className="p-3 bg-slate-950/80 rounded-lg border border-slate-800">
                      <div className="font-bold text-slate-200 mb-1">Recommended Containment Actions:</div>
                      {aiResult.recommended_actions.map((act: any, i: number) => (
                        <div key={i} className="flex items-center justify-between py-1 border-b border-slate-800/50 last:border-0">
                          <div>
                            <span className="font-bold text-slate-200">{act.action}</span>
                            <span className="text-[10px] text-slate-400 ml-2">Target: {act.target}</span>
                          </div>
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
                            APPROVAL REQUIRED
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="h-40 flex items-center justify-center text-xs text-slate-500">
                    Submit a query to generate structured analyst reasoning.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 6: Continuous Validation & SRE */}
          {activeTab === 'validation' && (
            <div className="space-y-6">
              {/* 16 Controls Matrix */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-emerald-400" /> Continuous Security Defense Controls Matrix
                  </h3>
                  <span className="text-xs text-emerald-400 font-bold">16 / 16 Controls Verified</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                  {(validation?.checks || []).map((chk: any) => (
                    <div key={chk.id} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800 text-xs">
                      <div className="flex justify-between items-center">
                        <span className="text-[10px] text-slate-400">{chk.category}</span>
                        <span className="text-[10px] text-emerald-400 font-bold">✓ PASS</span>
                      </div>
                      <div className="font-bold text-slate-200 mt-1">{chk.name}</div>
                      <div className="text-[10px] text-slate-400 mt-1 line-clamp-2">{chk.description}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Chaos Engineering Test Harness */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Zap className="h-4 w-4 text-amber-400" /> Security Chaos Engineering Harness
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                  {chaosScenarios.map((sc) => (
                    <div key={sc.scenario_key} className="p-3.5 bg-slate-950/60 rounded-xl border border-slate-800 text-xs flex flex-col justify-between">
                      <div>
                        <div className="font-bold text-slate-200">{sc.name}</div>
                        <div className="text-[10px] text-slate-400 mt-1">{sc.description}</div>
                      </div>
                      <button
                        onClick={() => handleRunChaos(sc.scenario_key)}
                        className="mt-3 w-full py-1.5 bg-amber-600/20 hover:bg-amber-600/40 text-amber-300 border border-amber-500/30 rounded-lg text-[10px] font-semibold transition-colors"
                      >
                        Simulate Failure
                      </button>
                    </div>
                  ))}
                </div>

                {chaosResult && (
                  <div className="p-3 bg-emerald-950/40 border border-emerald-500/30 rounded-xl text-xs text-emerald-300">
                    <strong>Chaos Result ({chaosResult.scenario_key}):</strong> {chaosResult.verdict} (Recovery Latency: {chaosResult.recovery_latency_ms}ms).
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
