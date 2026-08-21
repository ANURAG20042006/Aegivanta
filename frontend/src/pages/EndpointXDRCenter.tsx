import React, { useEffect, useState } from 'react';
import {
  Shield,
  Laptop,
  Terminal,
  Activity,
  CheckCircle2,
  Zap,
  Network,
  ShieldAlert,
  Sliders,
  UserCheck
} from 'lucide-react';

import { saasApi } from '../services/saas';

export const EndpointXDRCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'zero_trust' | 'xdr' | 'detections' | 'telemetry' | 'response'>('zero_trust');
  const [postures, setPostures] = useState<any[]>([]);
  const [xdrIncidents, setXdrIncidents] = useState<any[]>([]);
  const [detections, setDetections] = useState<any[]>([]);
  const [telemetry, setTelemetry] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Response execution state
  const [selectedHost, setSelectedHost] = useState<string>('WKS-EXEC-FINANCE-04');
  const [responseAction, setResponseAction] = useState<string>('ISOLATE_ENDPOINT');
  const [responseReason, setResponseReason] = useState<string>('Contain active C2 beaconing and credential theft attempt.');
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  // Filter state for telemetry
  const [telemetryCategory, setTelemetryCategory] = useState<string>('');

  useEffect(() => {
    fetchEndpointXDRData();
  }, []);

  const fetchEndpointXDRData = async () => {
    try {
      setLoading(true);
      const [posList, xdrList, detList, telList] = await Promise.all([
        saasApi.getZeroTrustPostures(),
        saasApi.getXDRIncidents(),
        saasApi.getEndpointDetections(),
        saasApi.getEndpointTelemetry()
      ]);
      setPostures(posList);
      setXdrIncidents(xdrList);
      setDetections(detList);
      setTelemetry(telList);
    } catch (err) {
      console.error('Failed to load Endpoint XDR state:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteResponse = async () => {
    try {
      setActionLoading(true);
      setActionSuccess(null);
      await saasApi.executeEndpointResponse({
        sensor_id: 'sensor-edr-node-01',
        hostname: selectedHost,
        action_type: responseAction,
        target_entity: selectedHost,
        reason: responseReason
      });
      setActionSuccess(`Successfully executed ${responseAction} on host ${selectedHost}`);
      await fetchEndpointXDRData();
    } catch (err) {
      console.error('Response action error:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const avgTrustScore =
    postures.length > 0
      ? Math.round(postures.reduce((acc, p) => acc + p.device_trust_score, 0) / postures.length)
      : 82;

  const filteredTelemetry = telemetryCategory
    ? telemetry.filter((t) => t.event_category === telemetryCategory)
    : telemetry;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Shield className="h-7 w-7 text-indigo-400" />
            Endpoint XDR & Zero-Trust Command Center
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Unified Endpoint Detection & Response (EDR), continuous Zero-Trust device authorization, and cross-domain XDR incident correlation.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchEndpointXDRData}
            className="flex items-center gap-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-colors"
          >
            <Activity className="h-4 w-4 text-cyan-400" /> Refresh Telemetry
          </button>
        </div>
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Activity className="h-8 w-8 animate-spin text-indigo-400 mr-3" />
          Synchronizing endpoint sensor feeds and XDR correlation engines...
        </div>
      ) : (
        <>
          {/* Top Posture Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Fleet Zero-Trust Score</div>
              <div className={`text-2xl font-bold mt-1 ${avgTrustScore >= 80 ? 'text-emerald-400' : 'text-amber-400'}`}>
                {avgTrustScore}/100
              </div>
              <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
                <UserCheck className="h-3 w-3 text-emerald-400" /> Continuous Authorization Active
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Correlated XDR Incidents</div>
              <div className="text-2xl font-bold text-cyan-400 mt-1">{xdrIncidents.length}</div>
              <div className="text-[11px] text-cyan-400 mt-1 flex items-center gap-1">
                <Network className="h-3 w-3" /> 5-Domain Graph Fusion
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Active EDR Detections</div>
              <div className="text-2xl font-bold text-rose-400 mt-1">{detections.length}</div>
              <div className="text-[11px] text-rose-400 mt-1 flex items-center gap-1">
                <ShieldAlert className="h-3 w-3" /> Ransomware & Credential Theft
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Endpoint Event Stream</div>
              <div className="text-2xl font-bold text-slate-100 mt-1">{telemetry.length}</div>
              <div className="text-[11px] text-indigo-400 mt-1 flex items-center gap-1">
                <Sliders className="h-3 w-3" /> 8 Normalized Categories
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex border-b border-slate-800 gap-2 overflow-x-auto">
            {[
              { id: 'zero_trust', label: 'Zero-Trust Device Posture', icon: Laptop },
              { id: 'xdr', label: 'Cross-Domain XDR Investigation', icon: Network },
              { id: 'detections', label: 'EDR Behavioral Detections', icon: ShieldAlert },
              { id: 'telemetry', label: 'Endpoint Event Stream', icon: Terminal },
              { id: 'response', label: 'Gated Response & Containment', icon: Zap }
            ].map((tab) => {
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
                  <Icon className="h-4 w-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Tab 1: Zero-Trust Device Posture */}
          {activeTab === 'zero_trust' && (
            <div className="space-y-4">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                  <Laptop className="h-5 w-5 text-indigo-400" />
                  Device Trust Posture & Continuous Authorization Decisions
                </h2>

                <div className="space-y-3">
                  {postures.map((p) => (
                    <div key={p.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800/80 space-y-3">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-bold text-slate-100">{p.hostname}</span>
                            <span className="text-xs text-slate-400">({p.user_email})</span>
                          </div>
                          <div className="text-xs text-slate-400 mt-1 flex items-center gap-3">
                            <span>OS Patch: <strong className="text-slate-300">{p.os_patch_status}</strong></span>
                            <span>EDR Agent: <strong className="text-slate-300">{p.edr_agent_health}</strong></span>
                            <span>Encryption: <strong className="text-slate-300">{p.disk_encryption_status}</strong></span>
                          </div>
                        </div>

                        <div className="flex items-center gap-3">
                          <div className="text-right">
                            <div className="text-xs text-slate-400">Trust Score</div>
                            <div className={`text-lg font-bold ${p.device_trust_score >= 80 ? 'text-emerald-400' : 'text-amber-400'}`}>
                              {p.device_trust_score}/100
                            </div>
                          </div>

                          <span
                            className={`px-3 py-1.5 rounded-lg text-xs font-bold ${
                              p.access_decision === 'ALLOW'
                                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                : p.access_decision === 'STEP_UP_MFA'
                                ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                                : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                            }`}
                          >
                            Decision: {p.access_decision}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Tab 2: Cross-Domain XDR Investigation */}
          {activeTab === 'xdr' && (
            <div className="space-y-4">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                  <Network className="h-5 w-5 text-cyan-400" />
                  Multi-Domain XDR Correlation & Attack Graph
                </h2>

                <div className="space-y-4">
                  {xdrIncidents.map((inc) => (
                    <div key={inc.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800/80 space-y-4">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div>
                          <div className="text-sm font-bold text-slate-100">{inc.incident_title}</div>
                          <div className="flex items-center gap-2 mt-1">
                            {inc.correlated_domains.map((dom: string) => (
                              <span key={dom} className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950/60 text-cyan-400 border border-cyan-800/40">
                                {dom}
                              </span>
                            ))}
                          </div>
                        </div>
                        <span className="px-2.5 py-1 rounded text-xs font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                          {inc.severity} ({inc.status})
                        </span>
                      </div>

                      {/* Evidence Graph Nodes */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                        {inc.evidence_graph.nodes.map((n: any) => (
                          <div key={n.id} className="p-2.5 bg-slate-900 rounded-lg border border-slate-800 text-xs">
                            <div className="text-[10px] font-bold text-indigo-400 uppercase">{n.type}</div>
                            <div className="font-bold text-slate-200 truncate">{n.label}</div>
                            <div className="text-[11px] text-slate-400 mt-0.5">{n.detail}</div>
                          </div>
                        ))}
                      </div>

                      <div className="p-3 bg-slate-900/60 rounded-lg text-xs space-y-1.5 border border-slate-800">
                        <div className="font-bold text-slate-300">Root Cause Analysis:</div>
                        <p className="text-slate-400">{inc.root_cause_analysis}</p>
                        <div className="font-bold text-slate-300 pt-1">Recommended Response Actions:</div>
                        <ul className="list-disc list-inside text-slate-400 space-y-0.5">
                          {inc.recommended_actions.map((act: string, idx: number) => (
                            <li key={idx}>{act}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Tab 3: EDR Behavioral Detections */}
          {activeTab === 'detections' && (
            <div className="space-y-4">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                  <ShieldAlert className="h-5 w-5 text-rose-400" />
                  Active Endpoint Threat Detections
                </h2>

                <div className="space-y-3">
                  {detections.map((d) => (
                    <div key={d.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800/80 space-y-2">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                            {d.severity}
                          </span>
                          <span className="text-sm font-bold text-slate-100">{d.title}</span>
                          <span className="text-xs font-mono text-indigo-300">({d.mitre_technique_id} - {d.mitre_tactic})</span>
                        </div>
                        <span className="text-xs text-slate-400 font-mono">{d.hostname}</span>
                      </div>

                      <p className="text-xs text-slate-300">{d.description}</p>
                      {d.cmdline && (
                        <div className="p-2 bg-slate-900 rounded font-mono text-[11px] text-rose-300 border border-slate-800 overflow-x-auto">
                          {d.cmdline}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Tab 4: Endpoint Event Stream */}
          {activeTab === 'telemetry' && (
            <div className="space-y-4">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                    <Terminal className="h-5 w-5 text-cyan-400" />
                    Normalized Endpoint Event Stream
                  </h2>

                  <div className="flex items-center gap-2">
                    <label className="text-xs text-slate-400">Filter Category:</label>
                    <select
                      value={telemetryCategory}
                      onChange={(e) => setTelemetryCategory(e.target.value)}
                      className="bg-slate-950 border border-slate-800 rounded-lg p-1.5 text-xs text-slate-200"
                    >
                      <option value="">All Categories</option>
                      <option value="PROCESS">PROCESS</option>
                      <option value="FILE">FILE</option>
                      <option value="REGISTRY">REGISTRY</option>
                      <option value="AUTHENTICATION">AUTHENTICATION</option>
                      <option value="NETWORK">NETWORK</option>
                      <option value="PRIVILEGE">PRIVILEGE</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-2">
                  {filteredTelemetry.map((t) => (
                    <div key={t.id} className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between text-xs gap-2">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300">
                            {t.event_category}
                          </span>
                          <span className="font-bold text-slate-200">{t.process_name || t.user_account || 'System'}</span>
                          <span className="text-slate-400 font-mono text-[11px]">on {t.hostname}</span>
                        </div>
                        {t.process_cmdline && (
                          <div className="text-[11px] text-slate-400 font-mono mt-1 truncate max-w-xl">
                            {t.process_cmdline}
                          </div>
                        )}
                        {t.registry_key && (
                          <div className="text-[11px] text-indigo-300 font-mono mt-1">
                            Key: {t.registry_key}
                          </div>
                        )}
                        {t.target_ip && (
                          <div className="text-[11px] text-cyan-300 font-mono mt-1">
                            Outbound: {t.target_ip}:{t.target_port}
                          </div>
                        )}
                      </div>
                      <span className="text-[10px] text-slate-500 font-mono shrink-0">{t.timestamp}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Tab 5: Gated Response & Containment */}
          {activeTab === 'response' && (
            <div className="space-y-4">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                  <Zap className="h-5 w-5 text-indigo-400" />
                  Policy-Controlled & Human-Approved Response Center
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Target Endpoint Hostname</label>
                      <input
                        type="text"
                        value={selectedHost}
                        onChange={(e) => setSelectedHost(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200"
                      />
                    </div>

                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Response Action Type</label>
                      <select
                        value={responseAction}
                        onChange={(e) => setResponseAction(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200"
                      >
                        <option value="ISOLATE_ENDPOINT">ISOLATE_ENDPOINT (Host Network Containment)</option>
                        <option value="TERMINATE_PROCESS">TERMINATE_PROCESS (Kill Suspicious PID)</option>
                        <option value="REVOKE_SESSION">REVOKE_SESSION (Terminate Okta/Entra Token)</option>
                        <option value="RESET_CREDENTIALS">RESET_CREDENTIALS (Force Password Rotation)</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Reason / Justification</label>
                      <textarea
                        rows={3}
                        value={responseReason}
                        onChange={(e) => setResponseReason(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200"
                      />
                    </div>

                    <button
                      onClick={handleExecuteResponse}
                      disabled={actionLoading}
                      className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-lg transition-colors flex items-center gap-2"
                    >
                      {actionLoading && <Activity className="h-4 w-4 animate-spin" />}
                      Authorize & Execute Response
                    </button>

                    {actionSuccess && (
                      <div className="p-3 bg-emerald-950/40 border border-emerald-500/40 rounded-lg text-emerald-300 text-xs flex items-center gap-2">
                        <CheckCircle2 className="h-4 w-4" />
                        {actionSuccess}
                      </div>
                    )}
                  </div>

                  <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs space-y-3">
                    <div className="font-bold text-slate-200">Containment Safety Directives:</div>
                    <ul className="list-disc list-inside text-slate-400 space-y-1">
                      <li>Network isolation enforces host firewall rules blocking all ingress and egress except sensor C2.</li>
                      <li>Actions are logged with operator attribution and audit timestamps.</li>
                      <li>Rollback is supported for all isolation actions via the 1-click restore mechanism.</li>
                      <li>Integrated with SOAR 2.0 emergency kill switch for fail-closed safety.</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
