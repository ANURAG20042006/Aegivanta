import React, { useEffect, useState } from 'react';
import {
  FileText,
  Activity,
  ChevronRight,
  AlertTriangle,
  Lock,
  Eye,
  Key,
  Search,
  Sliders,
  Database
} from 'lucide-react';
import { saasApi } from '../services/saas';


export const DLPCommandCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'policies' | 'incidents' | 'tokens' | 'shadow_data' | 'sandbox'>('overview');
  const [summary, setSummary] = useState<any>(null);
  const [policies, setPolicies] = useState<any[]>([]);
  const [incidents, setIncidents] = useState<any[]>([]);
  const [tokens, setTokens] = useState<any[]>([]);
  const [shadowData, setShadowData] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Tokenize modal state
  const [showTokenizeModal, setShowTokenizeModal] = useState<boolean>(false);
  const [rawInput, setRawInput] = useState<string>('4111-9824-7712-1111');
  const [tokenFormat, setTokenFormat] = useState<string>('FPE_CREDIT_CARD');

  // Detokenize modal state
  const [detokenizeResult, setDetokenizeResult] = useState<any>(null);

  // Live sandbox state
  const [sandboxInput, setSandboxInput] = useState<string>(
    'Sending customer order record: Customer John Doe, Card 4111-2222-3333-4444, SSN 123-45-6789, using AWS Key AKIAIOSFODNN7EXAMPLE for ingest.'
  );
  const [sandboxResult, setSandboxResult] = useState<any>(null);
  const [inspecting, setInspecting] = useState<boolean>(false);

  useEffect(() => {
    fetchDLPData();
  }, []);

  const fetchDLPData = async () => {
    try {
      setLoading(true);
      const [sum, pols, incs, tkns, shdw] = await Promise.all([
        saasApi.getDLPSummary(),
        saasApi.getDLPPolicies(),
        saasApi.getDLPIncidents(),
        saasApi.getTokenVault(),
        saasApi.getShadowData()
      ]);
      setSummary(sum);
      setPolicies(pols);
      setIncidents(incs);
      setTokens(tkns);
      setShadowData(shdw);
    } catch (err) {
      console.error('Failed to load DLP data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTokenize = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await saasApi.tokenizeData({
        raw_value: rawInput,
        token_format: tokenFormat,
        authorized_roles: ['admin', 'compliance_officer']
      });
      setShowTokenizeModal(false);
      fetchDLPData();
    } catch (err) {
      console.error('Failed to tokenize data:', err);
    }
  };

  const handleDetokenize = async (tokenId: string) => {
    try {
      const res = await saasApi.detokenizeData({
        token_identifier: tokenId,
        requestor_role: 'admin'
      });
      setDetokenizeResult(res);
    } catch (err) {
      console.error('Failed to detokenize data:', err);
    }
  };

  const handleInspectSandbox = async () => {
    try {
      setInspecting(true);
      const res = await saasApi.inspectPayload({
        payload_text: sandboxInput
      });
      setSandboxResult(res);
    } catch (err) {
      console.error('Failed to inspect sandbox payload:', err);
    } finally {
      setInspecting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <FileText className="h-7 w-7 text-indigo-500" />
            Data Loss Prevention (DLP), Enterprise Classification & Tokenization
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Real-Time Sensitive Data Classification, Multi-Channel Exfiltration Prevention, FPE Cryptographic Vault & DSPM Shadow Data Discovery.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowTokenizeModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-colors"
          >
            <Lock className="h-4 w-4" /> Cryptographic Tokenize
          </button>
        </div>
      </div>

      {/* Top Metrics Ribbon */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">DLP Posture</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.overall_dlp_posture_score}<span className="text-xs text-slate-500">/100</span></div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Enforcing Active</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Inspection Policies</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{summary.active_inspection_policies_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Multi-Channel Active</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Exfiltrations Blocked</div>
            <div className="text-2xl font-bold text-rose-400 mt-1">{summary.total_exfiltrations_blocked_count}</div>
            <div className="text-[10px] text-rose-400 mt-0.5">Intercepted Incidents</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Tokenized Vault</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{summary.tokenized_vault_records_count}</div>
            <div className="text-[10px] text-cyan-400 mt-0.5">FPE Surrogates</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Shadow Data Stores</div>
            <div className="text-2xl font-bold text-amber-400 mt-1">{summary.discovered_shadow_data_stores_count}</div>
            <div className="text-[10px] text-amber-400 mt-0.5">DSPM Discovered</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Success Rate</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.dlp_interception_success_rate_pct}%</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Zero Data Loss</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'DLP Overview', icon: FileText },
          { id: 'policies', label: 'Inspection Policies', icon: Sliders },
          { id: 'incidents', label: 'Exfiltration Incidents', icon: AlertTriangle },
          { id: 'tokens', label: 'Tokenization Vault (FPE)', icon: Lock },
          { id: 'shadow_data', label: 'Shadow Data (DSPM)', icon: Database },
          { id: 'sandbox', label: 'Live Payload Scanner', icon: Search }
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
          Loading Enterprise Data Loss Prevention & Tokenization Engine...
        </div>
      ) : (
        <>
          {/* TAB 1: Overview */}
          {activeTab === 'overview' && summary && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Intercepted Incidents Card */}
              <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-rose-400" /> Recent Intercepted Exfiltrations
                </h3>
                <div className="space-y-3">
                  {incidents.map((inc) => (
                    <div key={inc.id} className="p-3.5 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                      <div className="flex justify-between items-center font-bold">
                        <span className="text-indigo-300">{inc.matched_policy_name}</span>
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 text-[10px]">{inc.enforcement_action_taken}</span>
                          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">{inc.channel}</span>
                        </div>
                      </div>
                      <div className="text-slate-300">Source: <strong className="text-indigo-400">{inc.source_identity}</strong> → Destination: <strong className="font-mono text-slate-400">{inc.target_destination}</strong></div>
                      <div className="text-[11px] text-slate-400 font-mono">Masked Payload Sample: {inc.masked_sample_snippet}</div>
                      <div className="text-[10px] text-slate-500 flex justify-between pt-1 border-t border-slate-800/60">
                        <span>Category: {inc.data_category}</span>
                        <span>{new Date(inc.occurred_at).toLocaleString()}</span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-3 border-t border-slate-800/60">
                  <div className="text-xs font-bold text-slate-300 mb-2">Priority Data Protection Directives:</div>
                  <div className="space-y-1.5">
                    {summary.top_dlp_priorities.map((pri: string, idx: number) => (
                      <div key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                        <ChevronRight className="h-3.5 w-3.5 text-indigo-400 shrink-0 mt-0.5" />
                        {pri}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Shadow Data Summary */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Database className="h-4 w-4 text-amber-400" /> High-Risk Shadow Data Stores
                </h3>
                <div className="space-y-3">
                  {shadowData.map((store) => (
                    <div key={store.id} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60 text-xs space-y-2">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span className="font-mono text-indigo-300">{store.resource_uri}</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${store.risk_level === 'CRITICAL' ? 'bg-rose-500/10 text-rose-400' : 'bg-amber-500/10 text-amber-400'}`}>
                          {store.risk_level}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-400">
                        Records: <strong className="text-rose-400">{store.discovered_sensitive_records_count.toLocaleString()}</strong> · Encryption: <span className="font-mono text-slate-300">{store.encryption_state}</span>
                      </div>
                      <div className="text-[10px] text-slate-500">
                        Categories: {store.detected_data_categories.join(', ')}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Inspection Policies */}
          {activeTab === 'policies' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Sliders className="h-4 w-4 text-indigo-400" /> Active DLP Inspection Policies & Classification Rules
                </h3>
              </div>

              <div className="space-y-3">
                {policies.map((p) => (
                  <div key={p.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2.5">
                    <div className="flex justify-between items-center font-bold">
                      <div className="flex items-center gap-2">
                        <span className="text-slate-100 text-sm">{p.policy_name}</span>
                        <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 text-[10px]">{p.data_category}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="px-2.5 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 text-[10px]">
                          {p.enforcement_action}
                        </span>
                      </div>
                    </div>

                    <div className="p-2.5 bg-slate-900 rounded font-mono text-[11px] text-cyan-300 overflow-x-auto">
                      Regex: {p.regex_pattern}
                    </div>

                    <div className="flex justify-between items-center text-[10px] text-slate-400 pt-1">
                      <span>Keywords: <strong className="text-slate-300">{p.context_keywords.join(', ')}</strong></span>
                      <span>Total Interceptions: <strong className="text-emerald-400 font-bold">{p.total_violations_intercepted.toLocaleString()}</strong></span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: Exfiltration Incidents */}
          {activeTab === 'incidents' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-rose-400" /> Intercepted Sensitive Data Exfiltration Ledger
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                    <tr>
                      <th className="p-3">Source User / Service</th>
                      <th className="p-3">Channel</th>
                      <th className="p-3">Target Destination</th>
                      <th className="p-3">Matched Policy</th>
                      <th className="p-3">Masked Sample</th>
                      <th className="p-3">Action Taken</th>
                      <th className="p-3">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50 text-slate-200">
                    {incidents.map((inc) => (
                      <tr key={inc.id} className="hover:bg-slate-950/40">
                        <td className="p-3 font-semibold text-indigo-300">{inc.source_identity}</td>
                        <td className="p-3">
                          <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px]">{inc.channel}</span>
                        </td>
                        <td className="p-3 font-mono text-[11px] text-slate-400">{inc.target_destination}</td>
                        <td className="p-3 text-slate-200">{inc.matched_policy_name}</td>
                        <td className="p-3 font-mono text-amber-400">{inc.masked_sample_snippet}</td>
                        <td className="p-3">
                          <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 font-bold text-[10px]">
                            {inc.enforcement_action_taken}
                          </span>
                        </td>
                        <td className="p-3 text-slate-400 text-[10px]">{new Date(inc.occurred_at).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 4: Tokenization Vault */}
          {activeTab === 'tokens' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Lock className="h-4 w-4 text-cyan-400" /> Format-Preserving Cryptographic Tokenization Vault
                </h3>
                <button
                  onClick={() => setShowTokenizeModal(true)}
                  className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold"
                >
                  + Tokenize Sensitive Asset
                </button>
              </div>

              <div className="space-y-3">
                {tokens.map((t) => (
                  <div key={t.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-cyan-400 text-sm">{t.token_identifier}</span>
                        <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 text-[10px]">{t.token_format}</span>
                      </div>
                      <button
                        onClick={() => handleDetokenize(t.token_identifier)}
                        className="flex items-center gap-1 px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-[10px] font-semibold"
                      >
                        <Eye className="h-3 w-3" /> Detokenize
                      </button>
                    </div>

                    <div className="flex justify-between text-[11px] text-slate-300">
                      <span>Surrogate Token Value: <strong className="font-mono text-emerald-400">{t.surrogate_token_value}</strong></span>
                      <span>Cipher: <strong className="font-mono text-slate-400">{t.cipher_algorithm}</strong></span>
                    </div>

                    <div className="text-[10px] text-slate-500 flex justify-between pt-1 border-t border-slate-800/60">
                      <span>Authorized Roles: {t.authorized_roles.join(', ')}</span>
                      <span>Detokenized: {t.times_detokenized} times</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: Shadow Data Discovery */}
          {activeTab === 'shadow_data' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Database className="h-4 w-4 text-amber-400" /> Discovered Shadow Data Stores & DSPM Exposure Map
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {shadowData.map((s) => (
                  <div key={s.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-3">
                    <div className="flex justify-between items-center font-bold">
                      <span className="text-sm font-mono text-indigo-300">{s.resource_uri}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${s.risk_level === 'CRITICAL' ? 'bg-rose-500/10 text-rose-400' : 'bg-amber-500/10 text-amber-400'}`}>
                        {s.risk_level}
                      </span>
                    </div>
                    <div className="text-slate-400">Provider: <strong>{s.storage_provider}</strong></div>
                    <div className="text-slate-300">Sensitive Records: <strong className="text-rose-400">{s.discovered_sensitive_records_count.toLocaleString()}</strong></div>
                    <div className="text-slate-400">Encryption State: <span className="font-mono text-slate-200">{s.encryption_state}</span></div>
                    <div className="text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">
                      Categories: {s.detected_data_categories.join(', ')}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 6: Live Sandbox Scanner */}
          {activeTab === 'sandbox' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Search className="h-4 w-4 text-indigo-400" /> Real-Time DLP Payload Inspection & Sanitizer Sandbox
              </h3>
              <p className="text-xs text-slate-400">
                Input any raw payload, log entry, or message payload to test real-time PCI-DSS Luhn validation, PII identification, and secret redaction.
              </p>

              <div className="space-y-3">
                <textarea
                  rows={4}
                  value={sandboxInput}
                  onChange={(e) => setSandboxInput(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-slate-200"
                />

                <button
                  onClick={handleInspectSandbox}
                  disabled={inspecting}
                  className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-colors"
                >
                  <Search className="h-4 w-4" /> {inspecting ? 'Inspecting Payload...' : 'Inspect & Sanitize Payload'}
                </button>
              </div>

              {sandboxResult && (
                <div className="mt-4 p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs space-y-3">
                  <div className="flex justify-between items-center font-bold">
                    <span className="text-slate-100">Inspection Verdict:</span>
                    <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${sandboxResult.is_violating ? 'bg-rose-500/10 text-rose-400' : 'bg-emerald-500/10 text-emerald-400'}`}>
                      {sandboxResult.recommended_action}
                    </span>
                  </div>

                  <div className="space-y-1.5">
                    <div className="text-slate-400 font-bold">Identified Violations ({sandboxResult.findings_count}):</div>
                    {sandboxResult.findings.map((f: any, idx: number) => (
                      <div key={idx} className="p-2 bg-slate-900 rounded text-[11px] flex justify-between text-slate-300">
                        <span><strong>{f.rule}</strong> ({f.data_category})</span>
                        <span className="font-mono text-amber-400">{f.matched_snippet}</span>
                      </div>
                    ))}
                  </div>

                  <div className="pt-2 border-t border-slate-800/60">
                    <div className="text-slate-400 font-bold mb-1">Sanitized Egress Output:</div>
                    <div className="p-2.5 bg-slate-900 rounded font-mono text-[11px] text-emerald-400">
                      {sandboxResult.sanitized_payload}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Tokenize Modal */}
      {showTokenizeModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4">
            <h3 className="text-base font-bold text-slate-100">Tokenize Sensitive Asset</h3>
            <form onSubmit={handleTokenize} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Raw Sensitive Value</label>
                <input
                  type="text"
                  value={rawInput}
                  onChange={(e) => setRawInput(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200 font-mono"
                  required
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Format-Preserving Token Strategy</label>
                <select
                  value={tokenFormat}
                  onChange={(e) => setTokenFormat(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                >
                  <option value="FPE_CREDIT_CARD">FPE Credit Card PAN</option>
                  <option value="FPE_SSN">FPE US Social Security Number</option>
                  <option value="HASH_EMAIL">Cryptographic Hash Email</option>
                </select>
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowTokenizeModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold"
                >
                  Generate Surrogate Token
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Detokenize Result Modal */}
      {detokenizeResult && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4">
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Key className="h-5 w-5 text-indigo-400" /> Detokenization Audit Result
            </h3>
            <div className="space-y-2 text-xs">
              <div className="text-slate-400">Token ID: <strong className="text-slate-200 font-mono">{detokenizeResult.token_identifier}</strong></div>
              <div className="text-slate-400">Surrogate: <strong className="text-cyan-400 font-mono">{detokenizeResult.surrogate_token_value}</strong></div>
              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-emerald-400 font-mono font-bold text-sm">
                Decrypted Raw Value: {detokenizeResult.raw_detokenized_value}
              </div>
              <div className="text-[10px] text-slate-500">
                Audited Detokenizations: {detokenizeResult.times_detokenized}
              </div>
            </div>
            <div className="flex justify-end pt-3">
              <button
                type="button"
                onClick={() => setDetokenizeResult(null)}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold text-xs"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
