import React, { useEffect, useState } from 'react';
import {
  Globe,
  Shield,
  Activity,
  ChevronRight,
  Key,
  Server,
  Lock,
  Plus,
  Compass
} from 'lucide-react';

import { saasApi } from '../services/saas';

export const AttackSurfaceCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'inventory' | 'dangling_dns' | 'darkweb' | 'brand_protection' | 'ctem_matrix'>('overview');
  const [summary, setSummary] = useState<any>(null);
  const [assets, setAssets] = useState<any[]>([]);
  const [danglingDNS, setDanglingDNS] = useState<any[]>([]);
  const [darkwebLeaks, setDarkwebLeaks] = useState<any[]>([]);
  const [brandAlerts, setBrandAlerts] = useState<any[]>([]);
  const [ctemExposures, setCtemExposures] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Enroll domain modal state
  const [showEnrollModal, setShowEnrollModal] = useState<boolean>(false);
  const [enrollDomain, setEnrollDomain] = useState<string>('staging-auth.aegivanta.io');
  const [enrollCloud, setEnrollCloud] = useState<string>('AWS');

  useEffect(() => {
    fetchASMData();
  }, []);

  const fetchASMData = async () => {
    try {
      setLoading(true);
      const [sum, ast, dd, dw, ba, ctem] = await Promise.all([
        saasApi.getASMSummary(),
        saasApi.getExternalAssets(),
        saasApi.getDanglingDNS(),
        saasApi.getDarkWebCredentials(),
        saasApi.getBrandTyposquats(),
        saasApi.getCTEMPrioritizedExposures()
      ]);
      setSummary(sum);
      setAssets(ast);
      setDanglingDNS(dd);
      setDarkwebLeaks(dw);
      setBrandAlerts(ba);
      setCtemExposures(ctem);
    } catch (err) {
      console.error('Failed to load Attack Surface data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleEnrollDomain = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await saasApi.discoverExternalDomain({
        domain_name: enrollDomain,
        cloud_provider: enrollCloud
      });
      setShowEnrollModal(false);
      fetchASMData();
    } catch (err) {
      console.error('Domain enrollment failed:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Globe className="h-7 w-7 text-indigo-400" />
            Attack Surface Management (ASM) & Threat Exposure (CTEM)
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            External Asset Reconnaissance, Dangling DNS Takeovers, Dark Web Breach Intel & Gartner 5-Stage CTEM Prioritization.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowEnrollModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-colors"
          >
            <Plus className="h-4 w-4" /> Enroll External Asset
          </button>
        </div>
      </div>

      {/* Top Metric Ribbon */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">ASM Posture Score</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.overall_asm_posture_score}<span className="text-xs text-slate-500">/100</span></div>
            <div className="text-[10px] text-emerald-400 mt-0.5">{summary.security_tier}</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">External Assets</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{summary.total_external_assets_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Domains & Endpoints</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Dangling DNS Risks</div>
            <div className="text-2xl font-bold text-rose-400 mt-1">{summary.dangling_dns_vulnerabilities_count}</div>
            <div className="text-[10px] text-rose-400 mt-0.5">Takeover Risks</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Dark Web Leaks</div>
            <div className="text-2xl font-bold text-amber-400 mt-1">{summary.unremediated_credential_leaks_count}</div>
            <div className="text-[10px] text-amber-400 mt-0.5">Leaked Credentials</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Brand Typosquats</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{summary.active_brand_phishing_lures_count}</div>
            <div className="text-[10px] text-cyan-400 mt-0.5">Active Lookalikes</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">CTEM Framework</div>
            <div className="text-2xl font-bold text-indigo-300 mt-1">ACTIVE</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">5-Stage Prioritized</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'CTEM & ASM Overview', icon: Globe },
          { id: 'inventory', label: 'External Asset Inventory', icon: Server },
          { id: 'dangling_dns', label: 'Dangling DNS & Takeover', icon: Shield },
          { id: 'darkweb', label: 'Dark Web Breach Intel', icon: Key },
          { id: 'brand_protection', label: 'Brand & Typosquatting', icon: Lock },
          { id: 'ctem_matrix', label: 'CTEM Prioritization Matrix', icon: Compass }
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
          Loading Attack Surface Management & CTEM Engine...
        </div>
      ) : (
        <>
          {/* TAB 1: Overview */}
          {activeTab === 'overview' && summary && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Architecture & Exposure */}
              <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Compass className="h-4 w-4 text-indigo-400" /> Gartner 5-Stage CTEM Exposure Lifecycle
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-5 gap-2 text-xs">
                  <div className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800/60 text-center">
                    <div className="text-[10px] text-slate-500 font-bold">1. SCOPING</div>
                    <div className="text-emerald-400 font-semibold mt-1">Defined</div>
                  </div>
                  <div className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800/60 text-center">
                    <div className="text-[10px] text-slate-500 font-bold">2. DISCOVERY</div>
                    <div className="text-indigo-400 font-semibold mt-1">Continuous</div>
                  </div>
                  <div className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800/60 text-center">
                    <div className="text-[10px] text-slate-500 font-bold">3. PRIORITIZE</div>
                    <div className="text-amber-400 font-semibold mt-1">EPSS + KEV</div>
                  </div>
                  <div className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800/60 text-center">
                    <div className="text-[10px] text-slate-500 font-bold">4. VALIDATION</div>
                    <div className="text-cyan-400 font-semibold mt-1">Reachable</div>
                  </div>
                  <div className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800/60 text-center">
                    <div className="text-[10px] text-slate-500 font-bold">5. MOBILIZE</div>
                    <div className="text-rose-400 font-semibold mt-1">SOAR Ready</div>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800/60">
                  <div className="text-xs font-bold text-slate-300 mb-2">Priority CTEM Mobilization Actions:</div>
                  <div className="space-y-1.5">
                    {summary.top_mobilization_actions.map((act: string, idx: number) => (
                      <div key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                        <ChevronRight className="h-3.5 w-3.5 text-indigo-400 shrink-0 mt-0.5" />
                        {act}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Quick Dangling DNS List */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Shield className="h-4 w-4 text-rose-400" /> Dangling DNS Takeovers
                </h3>
                <div className="space-y-2.5">
                  {danglingDNS.slice(0, 2).map((dd) => (
                    <div key={dd.id} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60 text-xs">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span className="truncate">{dd.subdomain}</span>
                        <span className="text-rose-400 text-[10px] font-bold">VULNERABLE</span>
                      </div>
                      <div className="text-[10px] text-slate-400 mt-1">Target: {dd.cname_target}</div>
                      <div className="text-[10px] text-amber-400 mt-0.5">Service: {dd.target_service}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Asset Inventory */}
          {activeTab === 'inventory' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Server className="h-4 w-4 text-indigo-400" /> External Asset Inventory & Exposed Ports Map
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                    <tr>
                      <th className="p-3">Asset / FQDN</th>
                      <th className="p-3">Type</th>
                      <th className="p-3">Primary IP</th>
                      <th className="p-3">ASN Organization</th>
                      <th className="p-3">Cloud</th>
                      <th className="p-3">Open Ports</th>
                      <th className="p-3">SSL Days</th>
                      <th className="p-3">Risk Score</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50 text-slate-200">
                    {assets.map((a) => (
                      <tr key={a.id} className="hover:bg-slate-950/40">
                        <td className="p-3 font-semibold text-indigo-300">{a.fqdn_or_ip}</td>
                        <td className="p-3 text-[10px] text-slate-400">{a.asset_type}</td>
                        <td className="p-3 font-mono text-slate-400">{a.primary_ip}</td>
                        <td className="p-3 text-[10px] text-slate-400">{a.asn_organization}</td>
                        <td className="p-3 text-cyan-300 font-bold">{a.cloud_provider}</td>
                        <td className="p-3">
                          <div className="flex gap-1 flex-wrap">
                            {a.open_ports.map((p: number) => (
                              <span key={p} className={`px-1.5 py-0.5 rounded text-[10px] font-mono ${[3389, 22, 6443].includes(p) ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'bg-slate-800 text-slate-300'}`}>
                                {p}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td className="p-3">
                          <span className={a.ssl_days_until_expiry <= 15 ? 'text-rose-400 font-bold' : 'text-slate-300'}>
                            {a.ssl_days_until_expiry}d
                          </span>
                        </td>
                        <td className="p-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${a.risk_score >= 70 ? 'bg-rose-500/10 text-rose-400' : 'bg-emerald-500/10 text-emerald-400'}`}>
                            {a.risk_score}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 3: Dangling DNS */}
          {activeTab === 'dangling_dns' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Shield className="h-4 w-4 text-rose-400" /> Dangling DNS & Subdomain Takeover Guard
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {danglingDNS.map((dd) => (
                  <div key={dd.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold text-slate-200">
                      <span>{dd.subdomain}</span>
                      <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 text-[10px] font-bold">
                        TAKEOVER RISK: {dd.takeover_risk_score}
                      </span>
                    </div>
                    <div className="text-[11px] font-mono text-slate-400 bg-slate-900/60 p-2 rounded">
                      CNAME: {dd.cname_target}
                    </div>
                    <div className="flex justify-between text-[10px] text-slate-400">
                      <span>Service: {dd.target_service}</span>
                      <span className="text-emerald-400 font-bold">{dd.is_takeover_verified ? '✓ Verified Reachable' : 'Pending'}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: Dark Web */}
          {activeTab === 'darkweb' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Key className="h-4 w-4 text-amber-400" /> Dark Web Credential Breach Intelligence
              </h3>
              <div className="space-y-3">
                {darkwebLeaks.map((dw) => (
                  <div key={dw.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold text-slate-200">
                      <span className="text-indigo-300">{dw.employee_email}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${dw.severity === 'CRITICAL' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30' : 'bg-amber-500/10 text-amber-400'}`}>
                        {dw.severity}
                      </span>
                    </div>
                    <div className="text-slate-400 text-[11px]">
                      <strong>Breach Source:</strong> {dw.breach_source} · <strong>Plaintext Exposed:</strong> {dw.is_plaintext_exposed ? 'YES (High Risk)' : 'Hashed'}
                    </div>
                    <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                      <span>Hash Sample: {dw.password_hash_sample}</span>
                      <span className={dw.is_remediated ? 'text-emerald-400' : 'text-rose-400'}>
                        {dw.is_remediated ? '✓ Password Reset Enforced' : 'Action Required: Force Reset'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: Brand Protection */}
          {activeTab === 'brand_protection' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Lock className="h-4 w-4 text-cyan-400" /> Brand Protection & Typosquatting Monitor
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                    <tr>
                      <th className="p-3">Impersonating Domain</th>
                      <th className="p-3">Similarity</th>
                      <th className="p-3">Registrar</th>
                      <th className="p-3">Active MX</th>
                      <th className="p-3">Live Web Server</th>
                      <th className="p-3">Threat Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50 text-slate-200">
                    {brandAlerts.map((ba) => (
                      <tr key={ba.id} className="hover:bg-slate-950/40">
                        <td className="p-3 font-semibold text-rose-300 font-mono">{ba.impersonating_domain}</td>
                        <td className="p-3 text-indigo-300 font-bold">{(ba.levenshtein_similarity_score * 100).toFixed(0)}% Match</td>
                        <td className="p-3 text-slate-400">{ba.registrar_name}</td>
                        <td className="p-3">
                          <span className={ba.has_active_mx_records ? 'text-rose-400 font-bold' : 'text-slate-500'}>
                            {ba.has_active_mx_records ? 'Active (Phishing)' : 'No MX'}
                          </span>
                        </td>
                        <td className="p-3">
                          <span className={ba.has_live_web_server ? 'text-rose-400 font-bold' : 'text-slate-500'}>
                            {ba.has_live_web_server ? 'Live Site' : 'Offline'}
                          </span>
                        </td>
                        <td className="p-3">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">
                            {ba.threat_status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 6: CTEM Matrix */}
          {activeTab === 'ctem_matrix' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Compass className="h-4 w-4 text-indigo-400" /> CTEM Exposure Prioritization Matrix
              </h3>
              <div className="space-y-3">
                {ctemExposures.map((exp) => (
                  <div key={exp.exposure_id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold text-slate-200">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 font-mono text-[10px]">
                          {exp.exposure_id}
                        </span>
                        <span>{exp.title}</span>
                      </div>
                      <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 text-[10px] font-bold border border-rose-500/30">
                        {exp.urgency}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[10px] bg-slate-900/60 p-2.5 rounded">
                      <div><span className="text-slate-500">CVSS v3.1:</span> <strong className="text-rose-400">{exp.cvss_score}</strong></div>
                      <div><span className="text-slate-500">EPSS Percentile:</span> <strong className="text-amber-400">{exp.epss_percentile}%</strong></div>
                      <div><span className="text-slate-500">CISA KEV:</span> <strong className={exp.cisa_kev_weaponized ? 'text-rose-400' : 'text-slate-400'}>{exp.cisa_kev_weaponized ? 'YES' : 'NO'}</strong></div>
                      <div><span className="text-slate-500">CTEM Stage:</span> <strong className="text-indigo-300">{exp.ctem_stage}</strong></div>
                    </div>
                    <div className="text-slate-400 text-[11px] pt-1">
                      <strong>Recommended Mobilization:</strong> {exp.recommended_action}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Enroll Domain Modal */}
      {showEnrollModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Globe className="h-5 w-5 text-indigo-400" /> Enroll External Asset
            </h2>
            <form onSubmit={handleEnrollDomain} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Domain Name or IP Address</label>
                <input
                  type="text"
                  value={enrollDomain}
                  onChange={(e) => setEnrollDomain(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                  required
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Cloud Provider</label>
                <select
                  value={enrollCloud}
                  onChange={(e) => setEnrollCloud(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                >
                  <option value="AWS">Amazon Web Services (AWS)</option>
                  <option value="AZURE">Microsoft Azure</option>
                  <option value="GCP">Google Cloud Platform</option>
                  <option value="CLOUDFLARE">Cloudflare Edge</option>
                  <option value="ON_PREM">On-Premises DMZ</option>
                </select>
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowEnrollModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold"
                >
                  Start Discovery
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
