import React, { useEffect, useState } from 'react';
import {
  Shield,
  Key,
  Lock,
  UserCheck,
  Clock,
  Fingerprint,
  Users,
  Activity,
  ChevronRight,
  Flame,
  Plus
} from 'lucide-react';

import { saasApi } from '../services/saas';

export const EnterpriseIAMCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'pam' | 'itdr' | 'zero_trust' | 'passkeys' | 'governance'>('overview');
  const [iamSummary, setIamSummary] = useState<any>(null);
  const [elevations, setElevations] = useState<any[]>([]);
  const [itdrDetections, setItdrDetections] = useState<any[]>([]);
  const [passkeys, setPasskeys] = useState<any[]>([]);
  const [scorecards, setScorecards] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // PAM JIT Request modal state
  const [showJITModal, setShowJITModal] = useState<boolean>(false);
  const [targetUsername, setTargetUsername] = useState<string>('sarah.connor@aegivanta.io');
  const [targetRole, setTargetRole] = useState<string>('CLUSTER_ADMIN');
  const [targetResource, setTargetResource] = useState<string>('PROD_K8S_PRIMARY');
  const [justification, setJustification] = useState<string>('');
  const [durationMinutes, setDurationMinutes] = useState<number>(60);

  // Zero Trust Continuous Auth Simulator state
  const [ztUsername, setZtUsername] = useState<string>('sarah.connor@aegivanta.io');
  const [ztIdentityRisk, setZtIdentityRisk] = useState<number>(20);
  const [ztDeviceTrust, setZtDeviceTrust] = useState<number>(95);
  const [ztCriticality, setZtCriticality] = useState<string>('HIGH');
  const [ztKnownLocation, setZtKnownLocation] = useState<boolean>(true);
  const [ztManagedDevice, setZtManagedDevice] = useState<boolean>(true);
  const [ztResult, setZtResult] = useState<any>(null);
  const [ztLoading, setZtLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchIAMData();
  }, []);

  const fetchIAMData = async () => {
    try {
      setLoading(true);
      const [sum, elv, itdr, keys, cards] = await Promise.all([
        saasApi.getIAMSummary(),
        saasApi.getPAMElevations(),
        saasApi.getITDRDetections(),
        saasApi.getRegisteredPasskeys(),
        saasApi.getIdentityScorecards()
      ]);
      setIamSummary(sum);
      setElevations(elv);
      setItdrDetections(itdr);
      setPasskeys(keys);
      setScorecards(cards);
    } catch (err) {
      console.error('Failed to load Enterprise IAM data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRequestElevation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!justification) return;
    try {
      await saasApi.requestJITElevation({
        username: targetUsername,
        target_role: targetRole,
        target_resource: targetResource,
        justification: justification,
        duration_minutes: durationMinutes
      });
      setShowJITModal(false);
      setJustification('');
      fetchIAMData();
    } catch (err) {
      console.error('JIT Elevation request failed:', err);
    }
  };

  const handleEvaluateZeroTrust = async () => {
    try {
      setZtLoading(true);
      const res = await saasApi.evaluateZeroTrustSession({
        username: ztUsername,
        identity_risk_score: ztIdentityRisk,
        device_trust_score: ztDeviceTrust,
        resource_criticality: ztCriticality,
        is_known_location: ztKnownLocation,
        is_managed_device: ztManagedDevice
      });
      setZtResult(res);
    } catch (err) {
      console.error('Zero trust evaluation failed:', err);
    } finally {
      setZtLoading(false);
    }
  };

  const getVerdictBadge = (verdict: string) => {
    switch (verdict) {
      case 'ALLOW': return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'STEP_UP_MFA': return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'RESTRICTED_MODE': return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30';
      default: return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Shield className="h-7 w-7 text-indigo-400" />
            Enterprise IAM, PAM & Zero Trust 2.0
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Privileged Access Management (JIT), Identity Threat Detection (ITDR), FIDO2 Passkeys & Continuous Adaptive Authorization.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowJITModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-colors"
          >
            <Plus className="h-4 w-4" /> Request JIT Elevation
          </button>
        </div>
      </div>

      {/* Top Metric Ribbon */}
      {iamSummary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Identity Trust Index</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{iamSummary.overall_identity_trust_score}<span className="text-xs text-slate-500">/100</span></div>
            <div className="text-[10px] text-emerald-400 mt-0.5">{iamSummary.security_tier}</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Active JIT Elevations</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{iamSummary.active_jit_elevations_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Time-Bounded Access</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Pending Approvals</div>
            <div className="text-2xl font-bold text-amber-400 mt-1">{iamSummary.pending_jit_approvals_count}</div>
            <div className="text-[10px] text-amber-400 mt-0.5">Awaiting Peer Review</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">ITDR Threat Alerts</div>
            <div className="text-2xl font-bold text-rose-400 mt-1">{iamSummary.active_itdr_threats_count}</div>
            <div className="text-[10px] text-rose-400 mt-0.5">MFA Fatigue / Spray</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">FIDO2 Passkeys</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{iamSummary.registered_passkeys_count}</div>
            <div className="text-[10px] text-cyan-400 mt-0.5">Hardware Keys Active</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">SCIM Directory</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">HEALTHY</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Auto-Lifecycle Synced</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'Identity Overview', icon: Shield },
          { id: 'pam', label: 'PAM & JIT Elevations', icon: Key },
          { id: 'itdr', label: 'ITDR Threat Defense', icon: Flame },
          { id: 'zero_trust', label: 'Continuous Zero Trust Auth', icon: Lock },
          { id: 'passkeys', label: 'FIDO2 / Passkeys', icon: Fingerprint },
          { id: 'governance', label: 'Identity Governance & SCIM', icon: Users }
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
          Loading Enterprise IAM & Zero Trust Platform...
        </div>
      ) : (
        <>
          {/* TAB 1: Overview */}
          {activeTab === 'overview' && iamSummary && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Scorecard & Priorities */}
              <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <UserCheck className="h-4 w-4 text-indigo-400" /> Identity Posture & Zero Trust Governance
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60">
                    <div className="text-xs text-slate-400">Continuous Adaptive Auth</div>
                    <div className="text-sm font-bold text-emerald-400 mt-1">ENFORCED</div>
                    <div className="text-[10px] text-slate-500 mt-0.5">Real-time dynamic session verdicts</div>
                  </div>
                  <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60">
                    <div className="text-xs text-slate-400">Privileged Session Recording</div>
                    <div className="text-sm font-bold text-indigo-400 mt-1">ACTIVE</div>
                    <div className="text-[10px] text-slate-500 mt-0.5">Audit ledgers cryptographically verified</div>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800/60">
                  <div className="text-xs font-bold text-slate-300 mb-2">Priority Governance Actions:</div>
                  <div className="space-y-1.5">
                    {iamSummary.top_governance_priorities.map((act: string, idx: number) => (
                      <div key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                        <ChevronRight className="h-3.5 w-3.5 text-indigo-400 shrink-0 mt-0.5" />
                        {act}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Active High-Privilege Users */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Key className="h-4 w-4 text-indigo-400" /> Active High-Privilege Users
                </h3>
                <div className="space-y-2.5">
                  {scorecards.slice(0, 3).map((u) => (
                    <div key={u.id} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60 text-xs">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span>{u.username}</span>
                        <span className={u.risk_tier === 'LOW' ? 'text-emerald-400' : 'text-rose-400'}>{u.risk_tier}</span>
                      </div>
                      <div className="text-[10px] text-slate-400 mt-1">Roles: {u.assigned_roles.join(', ')}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: PAM & JIT Elevations */}
          {activeTab === 'pam' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Key className="h-4 w-4 text-indigo-400" /> Just-in-Time (JIT) Privilege Elevation Queue
                </h3>
                <span className="text-xs text-slate-400">{elevations.length} Requests</span>
              </div>
              <div className="space-y-3">
                {elevations.map((elv) => (
                  <div key={elv.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-0.5 rounded border text-[10px] font-bold ${elv.status === 'ACTIVE' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : (elv.status === 'PENDING' ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' : 'bg-slate-800 text-slate-400 border-slate-700')}`}>
                          {elv.status}
                        </span>
                        <span className="font-bold text-slate-200">{elv.username}</span>
                        <span className="text-indigo-400 font-mono">→ {elv.target_role} ({elv.target_resource})</span>
                      </div>
                      <span className="text-slate-400 text-[10px] flex items-center gap-1">
                        <Clock className="h-3 w-3" /> {elv.duration_minutes} mins
                      </span>
                    </div>
                    <div className="text-slate-400">{elv.justification}</div>
                    <div className="flex justify-end gap-2 pt-2 border-t border-slate-800/60">
                      {elv.status === 'PENDING' && (
                        <button
                          onClick={async () => {
                            await saasApi.approveJITElevation(elv.id);
                            fetchIAMData();
                          }}
                          className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold"
                        >
                          Approve JIT Elevation
                        </button>
                      )}
                      {elv.status === 'ACTIVE' && (
                        <button
                          onClick={async () => {
                            await saasApi.revokeJITElevation(elv.id);
                            fetchIAMData();
                          }}
                          className="px-3 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold"
                        >
                          Emergency Revoke
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: ITDR Threat Defense */}
          {activeTab === 'itdr' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Flame className="h-4 w-4 text-rose-400" /> Identity Threat Detection & Response (ITDR) Alerts
                </h3>
                <button
                  onClick={async () => {
                    await saasApi.simulateITDREvent({ threat_type: 'MFA_FATIGUE' });
                    fetchIAMData();
                  }}
                  className="px-3 py-1.5 bg-rose-600/20 hover:bg-rose-600/40 text-rose-300 border border-rose-500/30 rounded-lg text-xs font-semibold"
                >
                  Simulate MFA Fatigue Attack
                </button>
              </div>
              <div className="space-y-3">
                {itdrDetections.map((det) => (
                  <div key={det.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 bg-rose-500/10 text-rose-400 border border-rose-500/30 rounded text-[10px] font-bold">
                          {det.threat_type}
                        </span>
                        <span className="font-bold text-slate-200">{det.target_username}</span>
                      </div>
                      <span className="font-mono text-[10px] text-slate-400">MITRE: {det.mitre_attack_id}</span>
                    </div>
                    <div className="text-slate-400">Source: {det.source_ip} ({det.geo_location}) · Action: <strong className="text-indigo-300">{det.action_taken}</strong></div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: Continuous Zero Trust Auth */}
          {activeTab === 'zero_trust' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Lock className="h-4 w-4 text-indigo-400" /> Continuous Zero Trust Adaptive Authorization Simulator
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">User Principal</label>
                  <input
                    type="text"
                    value={ztUsername}
                    onChange={(e) => setZtUsername(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Identity Risk Score (0–100): {ztIdentityRisk}</label>
                  <input
                    type="range"
                    min={0}
                    max={100}
                    value={ztIdentityRisk}
                    onChange={(e) => setZtIdentityRisk(Number(e.target.value))}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Endpoint Device Trust Score (0–100): {ztDeviceTrust}</label>
                  <input
                    type="range"
                    min={0}
                    max={100}
                    value={ztDeviceTrust}
                    onChange={(e) => setZtDeviceTrust(Number(e.target.value))}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Target Resource Criticality</label>
                  <select
                    value={ztCriticality}
                    onChange={(e) => setZtCriticality(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                  >
                    <option value="LOW">LOW</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="HIGH">HIGH</option>
                    <option value="CRITICAL">CRITICAL</option>
                  </select>
                </div>
                <div className="flex items-center gap-2 pt-6">
                  <input
                    type="checkbox"
                    checked={ztKnownLocation}
                    onChange={(e) => setZtKnownLocation(e.target.checked)}
                    id="knownLoc"
                  />
                  <label htmlFor="knownLoc" className="text-slate-300">Known Geolocation</label>
                </div>
                <div className="flex items-center gap-2 pt-6">
                  <input
                    type="checkbox"
                    checked={ztManagedDevice}
                    onChange={(e) => setZtManagedDevice(e.target.checked)}
                    id="managedDev"
                  />
                  <label htmlFor="managedDev" className="text-slate-300">MDM Managed Device</label>
                </div>
              </div>

              <div className="pt-2">
                <button
                  onClick={handleEvaluateZeroTrust}
                  disabled={ztLoading}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-colors"
                >
                  {ztLoading ? 'Evaluating...' : 'Evaluate Dynamic Session Verdict'}
                </button>
              </div>

              {ztResult && (
                <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs space-y-2">
                  <div className="flex justify-between items-center font-bold">
                    <span className="text-slate-200">Composite Session Risk: {ztResult.composite_session_risk}/100</span>
                    <span className={`px-2.5 py-1 rounded border text-[11px] font-bold ${getVerdictBadge(ztResult.verdict)}`}>
                      VERDICT: {ztResult.verdict}
                    </span>
                  </div>
                  <div className="text-slate-400">{ztResult.reason}</div>
                  <div className="text-[10px] text-indigo-300 font-mono">Action Code: {ztResult.action_code}</div>
                </div>
              )}
            </div>
          )}

          {/* TAB 5: Passkeys */}
          {activeTab === 'passkeys' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Fingerprint className="h-4 w-4 text-cyan-400" /> FIDO2 / WebAuthn Hardware Security Keys & Biometrics
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {passkeys.map((pk) => (
                  <div key={pk.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="font-bold text-slate-200">{pk.device_nickname}</div>
                    <div className="text-[10px] text-slate-400 font-mono">{pk.credential_id}</div>
                    <div className="flex justify-between items-center pt-2 border-t border-slate-800 text-[10px]">
                      <span className="text-slate-400">Sign Count: {pk.sign_count}</span>
                      <span className="text-emerald-400 font-bold">✓ Hardware Bound</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 6: Governance */}
          {activeTab === 'governance' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Users className="h-4 w-4 text-indigo-400" /> Identity Posture Scorecards & Dormant Account Reaper
                </h3>
                <button
                  onClick={async () => {
                    await saasApi.reapDormantIdentities({ inactivity_days_threshold: 90 });
                    fetchIAMData();
                  }}
                  className="px-3 py-1.5 bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-300 border border-indigo-500/30 rounded-lg text-xs font-semibold"
                >
                  Run Dormant Identity Reaper (&gt;90d)
                </button>

              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                    <tr>
                      <th className="p-3">User Principal</th>
                      <th className="p-3">Risk Tier</th>
                      <th className="p-3">Risk Score</th>
                      <th className="p-3">Last Login</th>
                      <th className="p-3">MFA Status</th>
                      <th className="p-3">Dormant</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50 text-slate-200">
                    {scorecards.map((sc) => (
                      <tr key={sc.id} className="hover:bg-slate-950/40">
                        <td className="p-3 font-semibold text-indigo-300">{sc.username}</td>
                        <td className="p-3"><span className={`px-2 py-0.5 rounded text-[10px] font-bold ${sc.risk_tier === 'LOW' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>{sc.risk_tier}</span></td>
                        <td className="p-3 font-bold">{sc.identity_risk_score}/100</td>
                        <td className="p-3 text-slate-400">{sc.last_login_days_ago} days ago</td>
                        <td className="p-3 text-emerald-400 font-bold">{sc.mfa_enabled ? '✓ Enabled' : '✗ Disabled'}</td>
                        <td className="p-3">{sc.is_dormant ? <span className="text-rose-400 font-bold">DORMANT</span> : <span className="text-slate-400">ACTIVE</span>}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {/* JIT Elevation Modal */}
      {showJITModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Key className="h-5 w-5 text-indigo-400" /> Request JIT Privilege Elevation
            </h2>
            <form onSubmit={handleRequestElevation} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">User Principal</label>
                <input
                  type="text"
                  value={targetUsername}
                  onChange={(e) => setTargetUsername(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Requested Target Role</label>
                <select
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                >
                  <option value="CLUSTER_ADMIN">CLUSTER_ADMIN (Kubernetes Root)</option>
                  <option value="SEC_OPS_ADMIN">SEC_OPS_ADMIN (Security Operations)</option>
                  <option value="SUPER_ADMIN">SUPER_ADMIN (Tenant Super Admin)</option>
                  <option value="BREAK_GLASS_ADMIN">BREAK_GLASS_ADMIN (Emergency Incident)</option>
                </select>
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Target Resource</label>
                <input
                  type="text"
                  value={targetResource}
                  onChange={(e) => setTargetResource(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Elevation Duration (Minutes)</label>
                <input
                  type="number"
                  min={5}
                  max={480}
                  value={durationMinutes}
                  onChange={(e) => setDurationMinutes(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Operational Justification</label>
                <textarea
                  rows={3}
                  value={justification}
                  onChange={(e) => setJustification(e.target.value)}
                  placeholder="Provide detailed justification for auditing..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                />
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowJITModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold"
                >
                  Submit Request
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
