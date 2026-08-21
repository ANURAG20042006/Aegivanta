import React, { useEffect, useState } from 'react';
import {
  Brain,
  Activity,
  ChevronRight,
  AlertTriangle,
  UserCheck,
  Zap,
  Sliders,
  CheckCircle2,
  Users
} from 'lucide-react';
import { saasApi } from '../services/saas';

export const AISOCCommandCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'investigations' | 'ueba_profiles' | 'insider_threats' | 'decision_audits' | 'investigation_sandbox'>('overview');
  const [summary, setSummary] = useState<any>(null);
  const [investigations, setInvestigations] = useState<any[]>([]);
  const [profiles, setProfiles] = useState<any[]>([]);
  const [insiderThreats, setInsiderThreats] = useState<any[]>([]);
  const [decisionAudits, setDecisionAudits] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Trigger modal / sandbox state
  const [triggerAlertId, setTriggerAlertId] = useState<string>('ALT-99412');
  const [triggerAlertTitle, setTriggerAlertTitle] = useState<string>('Anomalous High-Volume S3 Bucket Dump & Tor Pivot');
  const [triggerResult, setTriggerResult] = useState<any>(null);

  // Approve action modal state
  const [showApproveModal, setShowApproveModal] = useState<boolean>(false);
  const [selectedInvId, setSelectedInvId] = useState<string>('');
  const [actionText, setActionText] = useState<string>('');
  const [actorName, setActorName] = useState<string>('lead_soc_commander');

  useEffect(() => {
    fetchAISOCData();
  }, []);

  const fetchAISOCData = async () => {
    try {
      setLoading(true);
      const [sum, invs, profs, threats, audits] = await Promise.all([
        saasApi.getAISOCSummary(),
        saasApi.getAISOCInvestigations(),
        saasApi.getUEBAProfiles(),
        saasApi.getInsiderThreats(),
        saasApi.getAISOCDecisionAudits()
      ]);
      setSummary(sum);
      setInvestigations(invs);
      setProfiles(profs);
      setInsiderThreats(threats);
      setDecisionAudits(audits);
    } catch (err) {
      console.error('Failed to load AI SOC & UEBA data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerInvestigation = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await saasApi.triggerAISOCInvestigation({
        alert_id: triggerAlertId,
        alert_title: triggerAlertTitle
      });
      setTriggerResult(res);
      fetchAISOCData();
    } catch (err) {
      console.error('Failed to trigger autonomous investigation:', err);
    }
  };

  const handleApproveAction = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await saasApi.approveAISOCAction({
        investigation_id: selectedInvId,
        action: actionText,
        acted_by: actorName
      });
      setShowApproveModal(false);
      fetchAISOCData();
    } catch (err) {
      console.error('Failed to approve AI SOC action:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Brain className="h-7 w-7 text-indigo-500" />
            AI SOC Autonomy, Insider Threat Defense & UEBA 2.0
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Autonomous Incident Triage, Forensic Evidence Correlation, User & Entity Behavior Profiling (URS) & Human-Gated Containment.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('investigation_sandbox')}
            className="flex items-center gap-2 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-colors"
          >
            <Zap className="h-4 w-4" /> Trigger Autonomous Triage
          </button>
        </div>
      </div>

      {/* Top Metrics Ribbon */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">AI Autonomy Score</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.overall_ai_soc_autonomy_score}<span className="text-xs text-slate-500">/100</span></div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Governed Engine</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Mean Triage Time</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{summary.mean_time_to_triage_seconds}s</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Automated Triaging</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Mean Respond Time</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{summary.mean_time_to_respond_minutes}m</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Human-Gated Contain</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Active Cases</div>
            <div className="text-2xl font-bold text-slate-200 mt-1">{summary.active_ai_investigations_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Autonomous Triaged</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Insider Threats</div>
            <div className="text-2xl font-bold text-rose-400 mt-1">{summary.detected_insider_threats_count}</div>
            <div className="text-[10px] text-rose-400 mt-0.5">Data Hoarding Alerts</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">AI Accuracy</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.ai_autonomous_investigation_accuracy_pct}%</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">True-Positive Rate</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'AI SOC Overview', icon: Brain },
          { id: 'investigations', label: 'Autonomous Investigations', icon: Zap },
          { id: 'ueba_profiles', label: 'UEBA Profiles (URS)', icon: Users },
          { id: 'insider_threats', label: 'Insider Threat Matrix', icon: AlertTriangle },
          { id: 'decision_audits', label: 'Decision Traces & Audits', icon: UserCheck },
          { id: 'investigation_sandbox', label: 'Investigation Sandbox', icon: Sliders }
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
          Loading AI SOC Autonomy & UEBA Behavioral Intelligence Engine...
        </div>
      ) : (
        <>
          {/* TAB 1: Overview */}
          {activeTab === 'overview' && summary && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Active Investigations */}
              <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Zap className="h-4 w-4 text-indigo-400" /> Active Autonomous Investigations
                </h3>
                <div className="space-y-3">
                  {investigations.map((inv) => (
                    <div key={inv.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2.5">
                      <div className="flex justify-between items-center font-bold">
                        <span className="text-slate-100 text-sm">{inv.investigation_title}</span>
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 text-[10px]">{inv.triage_verdict}</span>
                          <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 text-[10px]">Confidence: {Math.round(inv.confidence_score * 100)}%</span>
                        </div>
                      </div>
                      <div className="text-slate-300 text-[11px] leading-relaxed">
                        <strong className="text-indigo-400">AI Hypothesis: </strong>{inv.lead_hypothesis}
                      </div>
                      <div className="p-2.5 bg-slate-900/80 rounded-lg space-y-1">
                        <div className="text-[10px] font-bold text-slate-400">Key Evidence Gathered:</div>
                        {inv.collected_evidence_items.map((ev: string, idx: number) => (
                          <div key={idx} className="text-[10px] text-slate-300 font-mono flex items-center gap-1.5">
                            <span className="text-cyan-400">›</span> {ev}
                          </div>
                        ))}
                      </div>
                      <div className="flex justify-between items-center pt-2 border-t border-slate-800/60">
                        <span className="text-[10px] text-slate-500">Root Alert: {inv.root_alert_id} · State: {inv.investigation_state}</span>
                        {inv.investigation_state === 'HUMAN_REVIEW_REQUIRED' && (
                          <button
                            onClick={() => {
                              setSelectedInvId(inv.id);
                              setActionText(inv.proposed_actions[0] || 'Enforce containment');
                              setShowApproveModal(true);
                            }}
                            className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-[10px] font-semibold"
                          >
                            Review & Approve Action
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-3 border-t border-slate-800/60">
                  <div className="text-xs font-bold text-slate-300 mb-2">Priority Autonomous Directives:</div>
                  <div className="space-y-1.5">
                    {summary.top_ai_soc_priorities.map((pri: string, idx: number) => (
                      <div key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                        <ChevronRight className="h-3.5 w-3.5 text-indigo-400 shrink-0 mt-0.5" />
                        {pri}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* High-Risk UEBA Profiles */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Users className="h-4 w-4 text-cyan-400" /> High-Risk Identities (URS)
                </h3>
                <div className="space-y-3">
                  {profiles.map((p) => (
                    <div key={p.id} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60 text-xs space-y-2">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span className="font-semibold text-slate-200">{p.user_email}</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${p.risk_level === 'CRITICAL' ? 'bg-rose-500/10 text-rose-400' : p.risk_level === 'HIGH' ? 'bg-amber-500/10 text-amber-400' : 'bg-emerald-500/10 text-emerald-400'}`}>
                          URS: {p.user_risk_score}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-400">
                        Dept: <strong className="text-slate-300">{p.department}</strong> · Peer Group: <span className="text-indigo-400">{p.peer_group}</span>
                      </div>
                      <div className="text-[10px] text-slate-500 flex justify-between">
                        <span>Anomalies: {p.anomalous_indicators_count}</span>
                        <span>Daily Egress: {p.baseline_daily_egress_mb} MB</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Investigations */}
          {activeTab === 'investigations' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Zap className="h-4 w-4 text-indigo-400" /> Autonomous AI SOC Investigation Ledger
                </h3>
                <button
                  onClick={() => setActiveTab('investigation_sandbox')}
                  className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold"
                >
                  + Trigger New Investigation
                </button>
              </div>

              <div className="space-y-4">
                {investigations.map((inv) => (
                  <div key={inv.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-3">
                    <div className="flex justify-between items-center font-bold">
                      <div className="flex items-center gap-2">
                        <span className="text-slate-100 text-base">{inv.investigation_title}</span>
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">{inv.root_alert_id}</span>
                      </div>
                      <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${inv.triage_verdict === 'TRUE_POSITIVE_MALICIOUS' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30' : 'bg-amber-500/10 text-amber-400'}`}>
                        {inv.triage_verdict} ({Math.round(inv.confidence_score * 100)}% Conf)
                      </span>
                    </div>

                    <div className="p-3 bg-slate-900/60 rounded-lg text-slate-300 leading-relaxed text-[11px]">
                      <strong className="text-indigo-400">Lead Hypothesis: </strong>{inv.lead_hypothesis}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-1.5">
                        <div className="text-[11px] font-bold text-cyan-400">Collected Evidence Items:</div>
                        {inv.collected_evidence_items.map((ev: string, idx: number) => (
                          <div key={idx} className="text-[10px] text-slate-300 font-mono">› {ev}</div>
                        ))}
                      </div>
                      <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-1.5">
                        <div className="text-[11px] font-bold text-emerald-400">Proposed Containment Actions:</div>
                        {inv.proposed_actions.map((act: string, idx: number) => (
                          <div key={idx} className="text-[10px] text-slate-300 font-mono">› {act}</div>
                        ))}
                      </div>
                    </div>

                    <div className="flex justify-between items-center text-[10px] text-slate-500 pt-2 border-t border-slate-800">
                      <span>Created At: {new Date(inv.created_at).toLocaleString()}</span>
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-bold">{inv.investigation_state}</span>
                        {inv.investigation_state === 'HUMAN_REVIEW_REQUIRED' && (
                          <button
                            onClick={() => {
                              setSelectedInvId(inv.id);
                              setActionText(inv.proposed_actions[0] || 'Enforce containment');
                              setShowApproveModal(true);
                            }}
                            className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded font-bold"
                          >
                            Approve Action
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: UEBA Profiles */}
          {activeTab === 'ueba_profiles' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Users className="h-4 w-4 text-cyan-400" /> User & Entity Behavior Analytics (UEBA 2.0) Risk Profiles
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                    <tr>
                      <th className="p-3">User Identity</th>
                      <th className="p-3">Department</th>
                      <th className="p-3">Peer Group</th>
                      <th className="p-3">Baseline Hours</th>
                      <th className="p-3">Daily Egress</th>
                      <th className="p-3">Anomalies</th>
                      <th className="p-3">User Risk Score (URS)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50 text-slate-200">
                    {profiles.map((p) => (
                      <tr key={p.id} className="hover:bg-slate-950/40">
                        <td className="p-3 font-semibold text-slate-100">{p.user_email}</td>
                        <td className="p-3 text-slate-300">{p.department}</td>
                        <td className="p-3 text-indigo-400 font-medium">{p.peer_group}</td>
                        <td className="p-3 font-mono text-slate-400">{p.baseline_login_hours}</td>
                        <td className="p-3 font-mono text-cyan-300">{p.baseline_daily_egress_mb} MB</td>
                        <td className="p-3 font-bold text-amber-400">{p.anomalous_indicators_count}</td>
                        <td className="p-3">
                          <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${p.risk_level === 'CRITICAL' ? 'bg-rose-500/10 text-rose-400' : p.risk_level === 'HIGH' ? 'bg-amber-500/10 text-amber-400' : 'bg-emerald-500/10 text-emerald-400'}`}>
                            {p.user_risk_score} / 100 ({p.risk_level})
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 4: Insider Threat Matrix */}
          {activeTab === 'insider_threats' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-rose-400" /> Insider Threat & Data Hoarding Matrix
              </h3>
              <div className="space-y-3">
                {insiderThreats.map((threat) => (
                  <div key={threat.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <div className="flex items-center gap-2">
                        <span className="text-slate-100 text-sm">{threat.suspect_identity}</span>
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">{threat.anomaly_category}</span>
                      </div>
                      <span className="px-2.5 py-0.5 rounded bg-rose-500/10 text-rose-400 font-bold text-[10px]">
                        Magnitude: {threat.anomaly_magnitude_score}/100
                      </span>
                    </div>

                    <div className="text-slate-300 leading-relaxed text-[11px]">
                      {threat.evidence_summary}
                    </div>

                    <div className="text-[10px] text-slate-500 pt-1 border-t border-slate-800/60 flex justify-between">
                      <span>Category: Flight Risk & Anomalous Hoarding</span>
                      <span>{new Date(threat.detected_at).toLocaleString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: Decision Traces & Audits */}
          {activeTab === 'decision_audits' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <UserCheck className="h-4 w-4 text-emerald-400" /> Human-in-the-Loop AI Decision Traces & Action Audits
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                    <tr>
                      <th className="p-3">Investigation ID</th>
                      <th className="p-3">Proposed Action</th>
                      <th className="p-3">Impact Tier</th>
                      <th className="p-3">Approval Status</th>
                      <th className="p-3">Reasoning Trace</th>
                      <th className="p-3">Acted By</th>
                      <th className="p-3">Audited At</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50 text-slate-200">
                    {decisionAudits.map((a) => (
                      <tr key={a.id} className="hover:bg-slate-950/40">
                        <td className="p-3 font-mono text-slate-400">{a.investigation_id}</td>
                        <td className="p-3 font-semibold text-slate-100">{a.proposed_action}</td>
                        <td className="p-3">
                          <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 font-bold text-[10px]">{a.impact_tier}</span>
                        </td>
                        <td className="p-3">
                          <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold text-[10px]">{a.approval_status}</span>
                        </td>
                        <td className="p-3 text-slate-300 text-[11px] max-w-xs truncate">{a.decision_reasoning_trace}</td>
                        <td className="p-3 font-mono text-cyan-300">{a.acted_by}</td>
                        <td className="p-3 text-[10px] text-slate-500">{new Date(a.audited_at).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 6: Investigation Sandbox */}
          {activeTab === 'investigation_sandbox' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 max-w-2xl mx-auto space-y-4">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Sliders className="h-5 w-5 text-indigo-400" /> Autonomous AI SOC Investigation Sandbox
              </h3>
              <p className="text-xs text-slate-400">
                Simulate ingestion of high-priority security telemetry and launch instant autonomous investigation, multi-domain correlation, and evidence synthesis.
              </p>

              <form onSubmit={handleTriggerInvestigation} className="space-y-3 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Trigger Alert ID</label>
                  <input
                    type="text"
                    value={triggerAlertId}
                    onChange={(e) => setTriggerAlertId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                    required
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Alert Title & Telemetry Sighting</label>
                  <input
                    type="text"
                    value={triggerAlertTitle}
                    onChange={(e) => setTriggerAlertTitle(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                    required
                  />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold flex items-center gap-2"
                  >
                    <Zap className="h-4 w-4" /> Launch AI Autonomous Triage
                  </button>
                </div>
              </form>

              {triggerResult && (
                <div className="p-4 bg-slate-950 rounded-xl border border-emerald-500/30 text-xs space-y-2 mt-4">
                  <div className="flex justify-between items-center text-emerald-400 font-bold">
                    <span className="flex items-center gap-1.5"><CheckCircle2 className="h-4 w-4" /> Autonomous Investigation Initialized</span>
                    <span>Confidence: {Math.round(triggerResult.confidence_score * 100)}%</span>
                  </div>
                  <div className="text-slate-200 font-semibold">{triggerResult.investigation_title}</div>
                  <div className="text-[10px] text-slate-400">Verdict: <strong className="text-rose-400">{triggerResult.triage_verdict}</strong> · State: <strong className="text-cyan-300">{triggerResult.investigation_state}</strong></div>
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Action Approval Modal */}
      {showApproveModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4">
            <h3 className="text-base font-bold text-slate-100">Approve AI Containment Action</h3>
            <form onSubmit={handleApproveAction} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Proposed Containment Action</label>
                <input
                  type="text"
                  value={actionText}
                  onChange={(e) => setActionText(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                  required
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Approving SOC Commander</label>
                <input
                  type="text"
                  value={actorName}
                  onChange={(e) => setActorName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                  required
                />
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowApproveModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold"
                >
                  Grant Approval & Enforce
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
