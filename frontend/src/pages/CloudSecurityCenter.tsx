import React, { useEffect, useState } from 'react';
import {
  Cloud,
  Server,
  Layers,
  ShieldAlert,
  CheckCircle2,
  FileCode,
  Box,
  Key,
  Network,
  Activity,
  Zap,
  Lock,
  ArrowRight,
  Cpu
} from 'lucide-react';

import { saasApi } from '../services/saas';

export const CloudSecurityCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'cspm' | 'inventory' | 'containers' | 'k8s' | 'iam' | 'attack_paths'>('cspm');
  const [assets, setAssets] = useState<any[]>([]);
  const [findings, setFindings] = useState<any[]>([]);
  const [containerScans, setContainerScans] = useState<any[]>([]);
  const [iamAnalysis, setIamAnalysis] = useState<any>(null);
  const [attackPaths, setAttackPaths] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [scanRunning, setScanRunning] = useState<boolean>(false);

  // K8s Manifest Auditor state
  const sampleInsecureManifest = `apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-worker-deployment
spec:
  template:
    spec:
      hostNetwork: true
      containers:
      - name: payment-processor
        image: aegivanta/payment-worker:v1.2.0
        securityContext:
          privileged: true
        env:
        - name: DB_PASSWORD
          value: "supersecretpassword123"`;

  const [manifestText, setManifestText] = useState<string>(sampleInsecureManifest);
  const [k8sAuditResult, setK8sAuditResult] = useState<any>(null);
  const [auditLoading, setAuditLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchCloudSecurityData();
  }, []);

  const fetchCloudSecurityData = async () => {
    try {
      setLoading(true);
      const [astList, fndList, cntList, iamData, pathList] = await Promise.all([
        saasApi.getCloudInventory(),
        saasApi.getCSPMFindings(),
        saasApi.listContainerScans(),
        saasApi.getCloudIAMAnalysis(),
        saasApi.getCloudAttackPaths()
      ]);
      setAssets(astList);
      setFindings(fndList);
      setContainerScans(cntList);
      setIamAnalysis(iamData);
      setAttackPaths(pathList);
    } catch (err) {
      console.error('Failed to load cloud security data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunCSPMScan = async () => {
    try {
      setScanRunning(true);
      await saasApi.runCSPMScan();
      await fetchCloudSecurityData();
    } catch (err) {
      console.error('CSPM scan execution error:', err);
    } finally {
      setScanRunning(false);
    }
  };

  const handleAuditManifest = async () => {
    try {
      setAuditLoading(true);
      const res = await saasApi.auditK8sManifest({ manifest_yaml: manifestText });
      setK8sAuditResult(res);
    } catch (err) {
      console.error('K8s audit error:', err);
    } finally {
      setAuditLoading(false);
    }
  };

  const criticalFindingsCount = findings.filter((f) => f.severity === 'CRITICAL').length;
  const complianceScore = Math.max(10, 100 - (criticalFindingsCount * 15 + findings.length * 4));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Cloud className="h-7 w-7 text-cyan-400" />
            Cloud & Container Security Command Center
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Multi-cloud posture (CSPM), container vulnerability scanning, SBOM, K8s workload audits, and attack-path graph analytics.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleRunCSPMScan}
            disabled={scanRunning}
            className="flex items-center gap-1.5 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-slate-950 text-xs font-bold rounded-lg transition-colors shadow-lg shadow-cyan-500/10"
          >
            {scanRunning ? <Activity className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
            Execute Full CSPM Scan
          </button>
        </div>
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Activity className="h-8 w-8 animate-spin text-cyan-400 mr-3" />
          Synchronizing multi-cloud assets and vulnerability catalogs...
        </div>
      ) : (
        <>
          {/* Key Posture Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">CIS Compliance Rating</div>
              <div className={`text-2xl font-bold mt-1 ${complianceScore >= 80 ? 'text-emerald-400' : 'text-amber-400'}`}>
                {complianceScore}%
              </div>
              <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3 text-emerald-400" /> Multi-Cloud Benchmark
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Inventoried Cloud Assets</div>
              <div className="text-2xl font-bold text-slate-100 mt-1">{assets.length}</div>
              <div className="text-[11px] text-cyan-400 mt-1 flex items-center gap-1">
                <Server className="h-3 w-3" /> AWS • GCP • Azure • K8s
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Open CSPM Misconfigurations</div>
              <div className="text-2xl font-bold text-rose-400 mt-1">
                {findings.length}{' '}
                <span className="text-xs text-slate-400 font-normal">({criticalFindingsCount} Critical)</span>
              </div>
              <div className="text-[11px] text-rose-400 mt-1 flex items-center gap-1">
                <ShieldAlert className="h-3 w-3" /> Action Required
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Cloud IAM Escalation Paths</div>
              <div className="text-2xl font-bold text-amber-400 mt-1">
                {iamAnalysis?.privilege_escalation_vectors_count || 0}
              </div>
              <div className="text-[11px] text-amber-400 mt-1 flex items-center gap-1">
                <Key className="h-3 w-3" /> Over-Privileged Roles
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex border-b border-slate-800 gap-2 overflow-x-auto">
            {[
              { id: 'cspm', label: 'CSPM Posture Findings', icon: ShieldAlert },
              { id: 'inventory', label: 'Cloud Asset Inventory', icon: Layers },
              { id: 'containers', label: 'Container Security & SBOM', icon: Box },
              { id: 'k8s', label: 'K8s Manifest Auditor', icon: FileCode },
              { id: 'iam', label: 'Cloud IAM (CIEM) Risks', icon: Key },
              { id: 'attack_paths', label: 'Attack Path Graph', icon: Network }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 whitespace-nowrap transition-colors ${
                    activeTab === tab.id
                      ? 'border-cyan-500 text-cyan-300'
                      : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Tab 1: CSPM Posture Findings */}
          {activeTab === 'cspm' && (
            <div className="space-y-4">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                  <ShieldAlert className="h-5 w-5 text-rose-400" />
                  Active Misconfigurations & Security Baseline Violations
                </h2>

                {findings.length === 0 ? (
                  <div className="p-8 text-center text-slate-500 text-xs">
                    No open misconfiguration findings detected. System is 100% compliant with CIS benchmarks.
                  </div>
                ) : (
                  <div className="space-y-3">
                    {findings.map((f) => (
                      <div key={f.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800/80 space-y-2">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                f.severity === 'CRITICAL'
                                  ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                                  : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                              }`}
                            >
                              {f.severity}
                            </span>
                            <span className="text-sm font-bold text-slate-100">{f.title}</span>
                            <span className="font-mono text-xs text-slate-400">({f.rule_id})</span>
                          </div>
                          <span className="text-[11px] font-mono text-cyan-400 bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-800/50">
                            {f.compliance_standard}
                          </span>
                        </div>

                        <p className="text-xs text-slate-300">{f.description}</p>

                        <div className="p-2.5 bg-slate-900/80 rounded-lg text-xs border border-slate-800 flex items-start gap-2">
                          <span className="text-cyan-400 font-bold">Remediation:</span>
                          <span className="text-slate-300">{f.remediation_guidance}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Tab 2: Cloud Asset Inventory */}
          {activeTab === 'inventory' && (
            <div className="space-y-4">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                  <Layers className="h-5 w-5 text-cyan-400" />
                  Multi-Cloud & Kubernetes Asset Registry
                </h2>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs text-slate-300">
                    <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px] border-b border-slate-800">
                      <tr>
                        <th className="p-3">Provider</th>
                        <th className="p-3">Type</th>
                        <th className="p-3">Resource Name</th>
                        <th className="p-3">Region</th>
                        <th className="p-3">Exposure</th>
                        <th className="p-3 text-right">Risk Score</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {assets.map((a) => (
                        <tr key={a.id} className="hover:bg-slate-800/30 transition-colors">
                          <td className="p-3 font-bold text-slate-100 flex items-center gap-1.5">
                            {a.provider === 'AWS' && <Cloud className="h-3.5 w-3.5 text-amber-400" />}
                            {a.provider === 'KUBERNETES' && <Cpu className="h-3.5 w-3.5 text-indigo-400" />}
                            {a.provider}
                          </td>
                          <td className="p-3 font-mono text-slate-400">{a.asset_type}</td>
                          <td className="p-3 font-medium text-slate-200">{a.resource_name}</td>
                          <td className="p-3 text-slate-400">{a.region}</td>
                          <td className="p-3">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                a.exposure_level === 'PUBLIC_INGRESS'
                                  ? 'bg-rose-500/10 text-rose-400'
                                  : 'bg-emerald-500/10 text-emerald-400'
                              }`}
                            >
                              {a.exposure_level}
                            </span>
                          </td>
                          <td className="p-3 text-right font-bold text-slate-100">{a.risk_score}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Tab 3: Container Security & SBOM */}
          {activeTab === 'containers' && (
            <div className="space-y-4">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                  <Box className="h-5 w-5 text-indigo-400" />
                  Container Vulnerability Scans & SBOM Catalog
                </h2>

                <div className="space-y-3">
                  {containerScans.map((cs) => (
                    <div key={cs.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800/80 space-y-3">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-bold text-slate-100">{cs.image_name}</span>
                            <span className="font-mono text-xs text-indigo-300">:{cs.image_tag}</span>
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                              <Lock className="h-2.5 w-2.5" /> {cs.signature_status}
                            </span>
                          </div>
                          <div className="text-[11px] text-slate-400 mt-1 font-mono">{cs.image_digest}</div>
                        </div>

                        <div className="flex items-center gap-2 text-xs">
                          <span className="px-2.5 py-1 bg-slate-900 rounded border border-slate-800 text-slate-300">
                            SBOM: <strong>{cs.sbom_components_count} packages</strong>
                          </span>
                          <span className="px-2.5 py-1 bg-rose-950/50 rounded border border-rose-800 text-rose-300">
                            <strong>{cs.critical_cve_count}</strong> Critical CVEs
                          </span>
                        </div>
                      </div>

                      {cs.vulnerabilities && cs.vulnerabilities.length > 0 && (
                        <div className="space-y-2 pt-2 border-t border-slate-900">
                          {cs.vulnerabilities.map((v: any) => (
                            <div key={v.cve_id} className="p-2.5 bg-slate-900 rounded-lg flex items-center justify-between text-xs">
                              <div>
                                <span className="font-bold text-rose-400 mr-2">{v.cve_id}</span>
                                <span className="text-slate-300">{v.title}</span>
                                <span className="text-slate-500 ml-2">({v.affected_package} {v.installed_version} → {v.fixed_version})</span>
                              </div>
                              <span className="font-bold text-slate-200">CVSS {v.cvss}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Tab 4: Kubernetes Manifest Auditor */}
          {activeTab === 'k8s' && (
            <div className="space-y-4">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                  <FileCode className="h-5 w-5 text-cyan-400" />
                  Kubernetes Workload & Manifest Security Auditor
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <label className="text-xs text-slate-400 block">Paste Kubernetes YAML Manifest for Compliance Audit:</label>
                    <textarea
                      rows={10}
                      value={manifestText}
                      onChange={(e) => setManifestText(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 font-mono text-xs text-slate-200"
                    />
                    <button
                      onClick={handleAuditManifest}
                      disabled={auditLoading}
                      className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs rounded-lg transition-colors flex items-center gap-2"
                    >
                      {auditLoading && <Activity className="h-4 w-4 animate-spin" />}
                      Audit Manifest Configuration
                    </button>
                  </div>

                  <div>
                    {k8sAuditResult ? (
                      <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3 text-xs">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-100">Workload Security Score:</span>
                          <span className={`text-base font-bold ${k8sAuditResult.workload_security_score >= 80 ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {k8sAuditResult.workload_security_score}/100
                          </span>
                        </div>

                        <div className="text-[11px] text-slate-400">
                          Identified {k8sAuditResult.violations_count} security misconfigurations.
                        </div>

                        <div className="space-y-2 pt-2 border-t border-slate-900">
                          {k8sAuditResult.violations.map((v: any) => (
                            <div key={v.rule} className="p-2.5 bg-slate-900 rounded-lg space-y-1">
                              <div className="flex items-center justify-between font-bold">
                                <span className="text-rose-400">{v.title}</span>
                                <span className="text-[10px] px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20">
                                  {v.severity}
                                </span>
                              </div>
                              <div className="text-slate-300 text-[11px]">{v.description}</div>
                              <div className="text-cyan-400 text-[10px] font-mono">Remediation: {v.remediation}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="h-full flex items-center justify-center p-8 text-center text-slate-500 text-xs border border-dashed border-slate-800 rounded-xl">
                        Click "Audit Manifest Configuration" to evaluate YAML for privileged flags, host sharing, and plaintext secrets.
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Tab 5: Cloud IAM (CIEM) Risks */}
          {activeTab === 'iam' && (
            <div className="space-y-4">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                  <Key className="h-5 w-5 text-amber-400" />
                  Cloud Infrastructure Entitlement Management (CIEM) Analysis
                </h2>

                <div className="space-y-3">
                  {iamAnalysis?.identities &&
                    iamAnalysis.identities.map((id: any) => (
                      <div key={id.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800/80 space-y-2">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-bold text-slate-100">{id.name}</span>
                            <span className="font-mono text-xs text-slate-400">({id.identity_type})</span>
                            {id.is_stale && (
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                                Stale ({id.last_activity_days}d inactive)
                              </span>
                            )}
                          </div>
                          <span className="text-xs font-bold text-slate-200">Risk Score: {id.risk_score}</span>
                        </div>

                        <div className="text-[11px] font-mono text-slate-400">{id.identity_arn}</div>

                        {id.privilege_escalation_vectors.length > 0 && (
                          <div className="p-2.5 bg-rose-950/30 border border-rose-500/20 rounded text-xs text-rose-300 flex items-center gap-2">
                            <ShieldAlert className="h-4 w-4" />
                            <span>Privilege Escalation Vector: {id.privilege_escalation_vectors.join(', ')}</span>
                          </div>
                        )}
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}

          {/* Tab 6: Attack Path Graph */}
          {activeTab === 'attack_paths' && (
            <div className="space-y-4">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                  <Network className="h-5 w-5 text-cyan-400" />
                  Multi-Hop Cloud & Container Attack Path Modeling
                </h2>

                <div className="space-y-4">
                  {attackPaths.map((p) => (
                    <div key={p.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800/80 space-y-4">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div>
                          <div className="text-sm font-bold text-rose-400">{p.title}</div>
                          <div className="text-xs text-slate-400 mt-0.5">Kill Chain: {p.kill_chain_phase}</div>
                        </div>
                        <span className="px-2.5 py-1 rounded text-xs font-bold bg-rose-500/10 text-rose-300 border border-rose-500/30">
                          Blast Radius: {p.blast_radius} ({p.risk_score} Score)
                        </span>
                      </div>

                      {/* Visual Hop Chain */}
                      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                        {p.hop_nodes.map((h: any, idx: number) => (
                          <React.Fragment key={h.step}>
                            <div className="flex-1 p-3 bg-slate-900 rounded-lg border border-slate-800 text-xs space-y-1">
                              <div className="text-[10px] font-bold text-cyan-400 uppercase">Step {h.step}: {h.node_type}</div>
                              <div className="font-bold text-slate-200 truncate">{h.name}</div>
                              <div className="text-[11px] text-slate-400">{h.detail}</div>
                            </div>
                            {idx < p.hop_nodes.length - 1 && (
                              <ArrowRight className="hidden sm:block h-5 w-5 text-slate-600 shrink-0" />
                            )}
                          </React.Fragment>
                        ))}
                      </div>

                      <div className="p-3 bg-slate-900/60 rounded-lg text-xs space-y-1 border border-slate-800">
                        <div className="font-bold text-slate-300">Prescribed Remediation Sequence:</div>
                        <ul className="list-disc list-inside text-slate-400 space-y-0.5">
                          {p.remediation_steps.map((rem: string, i: number) => (
                            <li key={i}>{rem}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
