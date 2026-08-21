import React, { useEffect, useState } from 'react';
import {
  Activity,
  ChevronRight,
  Sliders,
  Scale,
  Lock,
  UserCheck,
  CheckCircle2
} from 'lucide-react';
import { saasApi } from '../services/saas';


export const DataGovernanceCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'lineage' | 'legal_holds' | 'dsar' | 'retention_cert' | 'governance_studio'>('overview');
  const [summary, setSummary] = useState<any>(null);
  const [lineage, setLineage] = useState<any[]>([]);
  const [holds, setHolds] = useState<any[]>([]);
  const [requests, setRequests] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Legal Hold studio state
  const [matterRef, setMatterRef] = useState<string>('MATTER-2026-INTERNAL-AUDIT-08');
  const [custodian, setCustodian] = useState<string>('Director of Information Security');
  const [scopePattern, setScopePattern] = useState<string>('CASE_FORENSICS_INSIDER_*');
  const [createdHold, setCreatedHold] = useState<any>(null);

  // DSAR studio state
  const [requesterEmail, setRequesterEmail] = useState<string>('sar-inquiry@customer.com');
  const [requestType, setRequestType] = useState<string>('RIGHT_OF_ACCESS_EXPORT');
  const [processedDsar, setProcessedDsar] = useState<any>(null);

  useEffect(() => {
    fetchGovernanceData();
  }, []);

  const fetchGovernanceData = async () => {
    try {
      setLoading(true);
      const [sum, lin, hlds, reqs] = await Promise.all([
        saasApi.getDataGovernanceSummary(),
        saasApi.getDataLineage(),
        saasApi.getLegalHolds(),
        saasApi.getDSARRequests()
      ]);
      setSummary(sum);
      setLineage(lin);
      setHolds(hlds);
      setRequests(reqs);
    } catch (err) {
      console.error('Failed to load Data Governance data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateHold = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await saasApi.createLegalHold({
        matter_reference: matterRef,
        custodian_name: custodian,
        scope_pattern: scopePattern
      });
      setCreatedHold(res);
      fetchGovernanceData();
    } catch (err) {
      console.error('Failed to create legal hold:', err);
    }
  };

  const handleCreateDsar = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await saasApi.createDSARRequest({
        requester_email: requesterEmail,
        request_type: requestType
      });
      setProcessedDsar(res);
      fetchGovernanceData();
    } catch (err) {
      console.error('Failed to process DSAR request:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Scale className="h-7 w-7 text-amber-400" />
            Enterprise Data Governance, Lineage, Legal Hold & DSAR
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            End-to-End Telemetry Provenance, Immutable Forensic Legal Hold Custody & Automated GDPR/CCPA Privacy Workflows.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('governance_studio')}
            className="flex items-center gap-2 px-3.5 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-xs font-semibold transition-colors"
          >
            <Lock className="h-4 w-4" /> Legal Hold & DSAR Studio
          </button>
        </div>
      </div>

      {/* Top Metrics Ribbon */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Governance Score</div>
            <div className="text-2xl font-bold text-amber-400 mt-1">{summary.overall_governance_score}<span className="text-xs text-slate-500">/100</span></div>
            <div className="text-[10px] text-amber-400 mt-0.5">WORM Immutable</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Lineage Stages</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{summary.active_lineage_stages_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Sensor to Cold DAG</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Governed Records</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{(summary.total_governed_records_count / 1000000).toFixed(2)}M</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Cryptographically Audited</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Active Legal Holds</div>
            <div className="text-2xl font-bold text-red-400 mt-1">{summary.active_legal_holds_count}</div>
            <div className="text-[10px] text-red-400 mt-0.5">Forensic Frozen</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Completed DSARs</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.completed_dsar_requests_count}</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">100% Attested</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Mean DSAR Speed</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.mean_dsar_fulfillment_time_hours} <span className="text-xs text-slate-500">hrs</span></div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Instant Discovery</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'Governance Overview', icon: Scale },
          { id: 'lineage', label: 'Telemetry Provenance DAG', icon: Activity },
          { id: 'legal_holds', label: 'Forensic Legal Holds Vault', icon: Lock },
          { id: 'dsar', label: 'GDPR / CCPA DSAR Requests', icon: UserCheck },
          { id: 'retention_cert', label: 'Cryptographic Erasure Certificates', icon: CheckCircle2 },
          { id: 'governance_studio', label: 'Legal Hold & DSAR Studio', icon: Sliders }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'border-amber-500 text-amber-300'
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
          <Activity className="h-6 w-6 animate-spin text-amber-400 mr-3" />
          Synchronizing Data Governance, Lineage & Legal Hold Vault...
        </div>
      ) : (
        <>
          {/* TAB 1: Overview */}
          {activeTab === 'overview' && summary && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Lineage Overview */}
              <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Activity className="h-4 w-4 text-amber-400" /> Telemetry Provenance & Lineage Pipeline
                </h3>
                <div className="space-y-3">
                  {lineage.map((lin) => (
                    <div key={lin.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                      <div className="flex justify-between items-center font-bold">
                        <span className="text-slate-100">{lin.data_asset_name}</span>
                        <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 text-[10px] font-bold border border-cyan-500/30">
                          {lin.pipeline_stage}
                        </span>
                      </div>
                      <div className="p-2 bg-slate-900 rounded font-mono text-[10px] text-amber-300 break-all">
                        SHA-256 Transform: {lin.transform_hash}
                      </div>
                      <div className="flex justify-between items-center text-[10px] text-slate-400 pt-1 border-t border-slate-800/60">
                        <span>Governed Records: <strong className="text-emerald-400">{lin.record_count.toLocaleString()}</strong></span>
                        <span>Stage Timestamp: {new Date(lin.recorded_at).toLocaleTimeString()}</span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-3 border-t border-slate-800/60">
                  <div className="text-xs font-bold text-slate-300 mb-2">Priority Governance Directives:</div>
                  <div className="space-y-1.5">
                    {summary.top_governance_priorities.map((pri: string, idx: number) => (
                      <div key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                        <ChevronRight className="h-3.5 w-3.5 text-amber-400 shrink-0 mt-0.5" />
                        {pri}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Active Holds */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Lock className="h-4 w-4 text-amber-400" /> Active Legal Holds
                </h3>
                <div className="space-y-3">
                  {holds.map((h) => (
                    <div key={h.id} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60 text-xs space-y-1.5">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span className="font-mono text-red-400">{h.matter_reference}</span>
                        <span className="px-2 py-0.5 rounded bg-red-500/10 text-red-400 text-[10px] font-bold">{h.status}</span>
                      </div>
                      <div className="text-[11px] text-slate-400">Custodian: {h.custodian_name}</div>
                      <div className="text-[10px] text-slate-500 font-mono">Scope: {h.scope_pattern} ({h.frozen_artifact_count} frozen artifacts)</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Lineage */}
          {activeTab === 'lineage' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Activity className="h-4 w-4 text-amber-400" /> End-to-End Data Lineage & Cryptographic Provenance DAG
              </h3>

              <div className="space-y-4">
                {lineage.map((l, idx) => (
                  <div key={l.id} className="p-5 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-3">
                    <div className="flex justify-between items-center font-bold">
                      <div className="flex items-center gap-2">
                        <span className="w-6 h-6 rounded-full bg-amber-500/20 text-amber-300 flex items-center justify-center text-xs">{idx + 1}</span>
                        <span className="text-slate-100 text-base">{l.data_asset_name}</span>
                      </div>
                      <span className="px-2.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 font-bold text-[10px]">
                        STAGE: {l.pipeline_stage}
                      </span>
                    </div>

                    <div className="p-3 bg-slate-900 rounded font-mono text-[11px] text-amber-300 break-all">
                      Transform Provenance Hash: {l.transform_hash}
                    </div>

                    <div className="flex justify-between items-center text-[11px] text-slate-400">
                      <span>Records Processed: <strong className="text-emerald-400">{l.record_count.toLocaleString()}</strong></span>
                      <span>Lineage Timestamp: {new Date(l.recorded_at).toLocaleString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: Legal Holds */}
          {activeTab === 'legal_holds' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Lock className="h-4 w-4 text-amber-400" /> Forensic Evidence Legal Hold Custody Vault
                </h3>
                <button
                  onClick={() => setActiveTab('governance_studio')}
                  className="px-3 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-semibold"
                >
                  + Issue Legal Hold
                </button>
              </div>

              <div className="space-y-3">
                {holds.map((h) => (
                  <div key={h.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <span className="font-mono text-red-400 text-sm">{h.matter_reference}</span>
                      <span className="px-2.5 py-0.5 rounded bg-red-500/10 text-red-400 font-bold text-[10px]">
                        {h.status}
                      </span>
                    </div>

                    <div className="text-[11px] text-slate-300">
                      Legal Custodian: <strong>{h.custodian_name}</strong>
                    </div>

                    <div className="p-2 bg-slate-900 rounded font-mono text-[10px] text-cyan-300">
                      Freezing Scope Filter: {h.scope_pattern} ({h.frozen_artifact_count} Protected Evidence Items)
                    </div>

                    <div className="text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">
                      Issued At: {new Date(h.issued_at).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: DSAR Requests */}
          {activeTab === 'dsar' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <UserCheck className="h-4 w-4 text-amber-400" /> GDPR / CCPA Data Subject Access Requests (DSAR)
                </h3>
                <button
                  onClick={() => setActiveTab('governance_studio')}
                  className="px-3 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-semibold"
                >
                  + Submit DSAR Request
                </button>
              </div>

              <div className="space-y-3">
                {requests.map((r) => (
                  <div key={r.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <span className="text-slate-100">{r.requester_email}</span>
                      <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold text-[10px]">
                        {r.status}
                      </span>
                    </div>

                    <div className="text-[11px] text-slate-400">
                      Request Type: <strong className="text-cyan-300">{r.request_type}</strong> · Discovered Records: <strong className="text-slate-200">{r.discovered_records_count}</strong>
                    </div>

                    <div className="p-2 bg-slate-900 rounded font-mono text-[10px] text-amber-300 break-all">
                      Verification Certificate SHA-256: {r.completion_certificate_hash}
                    </div>

                    <div className="text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">
                      Completed: {new Date(r.requested_at).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: Retention & Certificates */}
          {activeTab === 'retention_cert' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 max-w-2xl mx-auto space-y-4 text-xs">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-amber-400" /> Cryptographic Erasure & Retention Certificates
              </h3>
              <p className="text-slate-400 leading-relaxed">
                All data purges, Right-to-be-Forgotten erasures, and automated WORM archive expiries produce immutable, cryptographically verifiable completion certificates.
              </p>
              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2 font-mono text-[11px] text-cyan-300">
                <div>WORM Retention Policy: 365 Days Mandatory Retention for Security Audits</div>
                <div>NIST 800-88 Compliant Cryptographic Erasure Verification: ACTIVE</div>
                <div>Zero Residual Forensic Leakage Guarantee: ATTESTED</div>
              </div>
            </div>
          )}

          {/* TAB 6: Governance Studio */}
          {activeTab === 'governance_studio' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Issue Legal Hold Form */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 space-y-4">
                <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                  <Lock className="h-5 w-5 text-amber-400" /> Issue Forensic Legal Hold
                </h3>
                <p className="text-xs text-slate-400">
                  Freeze telemetry, packet captures, and case evidence for litigation hold.
                </p>

                <form onSubmit={handleCreateHold} className="space-y-3 text-xs">
                  <div>
                    <label className="block text-slate-400 mb-1">Matter / Case Reference</label>
                    <input
                      type="text"
                      value={matterRef}
                      onChange={(e) => setMatterRef(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200 font-mono text-[11px]"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1">Legal Custodian Name</label>
                    <input
                      type="text"
                      value={custodian}
                      onChange={(e) => setCustodian(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1">Scope Pattern Filter</label>
                    <input
                      type="text"
                      value={scopePattern}
                      onChange={(e) => setScopePattern(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200 font-mono text-[11px]"
                      required
                    />
                  </div>
                  <div className="flex justify-end pt-2">
                    <button
                      type="submit"
                      className="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-xl font-semibold flex items-center gap-2"
                    >
                      <Lock className="h-4 w-4" /> Issue Hold Order
                    </button>
                  </div>
                </form>

                {createdHold && (
                  <div className="p-4 bg-slate-950 rounded-xl border border-amber-500/30 text-xs space-y-2 mt-4">
                    <div className="flex justify-between items-center text-amber-400 font-bold">
                      <span>Hold Order Issued</span>
                      <span>{createdHold.status}</span>
                    </div>
                    <div className="text-slate-200 font-semibold">{createdHold.matter_reference}</div>
                  </div>
                )}
              </div>

              {/* Submit DSAR Request Form */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 space-y-4">
                <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                  <UserCheck className="h-5 w-5 text-amber-400" /> Submit DSAR Privacy Request
                </h3>
                <p className="text-xs text-slate-400">
                  Execute automated GDPR/CCPA personal data discovery and right-to-be-forgotten erasure.
                </p>

                <form onSubmit={handleCreateDsar} className="space-y-3 text-xs">
                  <div>
                    <label className="block text-slate-400 mb-1">Data Subject Email Address</label>
                    <input
                      type="email"
                      value={requesterEmail}
                      onChange={(e) => setRequesterEmail(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1">Privacy Request Type</label>
                    <select
                      value={requestType}
                      onChange={(e) => setRequestType(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                    >
                      <option value="RIGHT_OF_ACCESS_EXPORT">Right of Access (Personal Data Export)</option>
                      <option value="RIGHT_TO_ERASURE_DELETE">Right to Erasure (Cryptographic Purge)</option>
                      <option value="RECTIFICATION">Data Rectification & Attribute Correction</option>
                    </select>
                  </div>
                  <div className="flex justify-end pt-2">
                    <button
                      type="submit"
                      className="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-xl font-semibold flex items-center gap-2"
                    >
                      <UserCheck className="h-4 w-4" /> Process DSAR
                    </button>
                  </div>
                </form>

                {processedDsar && (
                  <div className="p-4 bg-slate-950 rounded-xl border border-amber-500/30 text-xs space-y-2 mt-4">
                    <div className="flex justify-between items-center text-amber-400 font-bold">
                      <span>DSAR Processed</span>
                      <span>Discovered: {processedDsar.discovered_records_count}</span>
                    </div>
                    <div className="p-2 bg-slate-900 rounded font-mono text-[10px] text-cyan-300 break-all">
                      Certificate Hash: {processedDsar.completion_certificate_hash}
                    </div>
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
