import React, { useEffect, useState } from 'react';
import {
  Cloud,
  Server,
  Layers,
  FileCode,
  Box,
  Key,
  Network,
  Activity,
  Zap,
  Plus,
  RefreshCw,
  Flame,
  Terminal,
  ShieldCheck,
  ChevronRight
} from 'lucide-react';

import { saasApi } from '../services/saas';

export const CloudSecurityCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'cnapp_overview' | 'inventory' | 'cspm' | 'cwpp' | 'kspm_serverless' | 'ciem_attack_paths'>('cnapp_overview');
  const [cnappSummary, setCnappSummary] = useState<any>(null);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [assets, setAssets] = useState<any[]>([]);
  const [findings, setFindings] = useState<any[]>([]);
  const [cwppFindings, setCwppFindings] = useState<any[]>([]);
  const [serverlessFindings, setServerlessFindings] = useState<any[]>([]);
  const [k8sClusters, setK8sClusters] = useState<any[]>([]);
  const [containerScans, setContainerScans] = useState<any[]>([]);
  const [iamAnalysis, setIamAnalysis] = useState<any>(null);
  const [attackPaths, setAttackPaths] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [scanRunning, setScanRunning] = useState<boolean>(false);

  // Connect Account Form state
  const [showConnectModal, setShowConnectModal] = useState<boolean>(false);
  const [accountProvider, setAccountProvider] = useState<string>('AWS');
  const [accountName, setAccountName] = useState<string>('');
  const [accountIdentifier, setAccountIdentifier] = useState<string>('');

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
      const [summary, accList, astList, fndList, cwppList, srvList, clsList, cntList, iamData, pathList] = await Promise.all([
        saasApi.getCNAPPSummary(),
        saasApi.getCloudAccounts(),
        saasApi.getCloudInventory(),
        saasApi.getCSPMFindings(),
        saasApi.getCWPPFindings(),
        saasApi.getServerlessFindings(),
        saasApi.getK8sClusters(),
        saasApi.listContainerScans(),
        saasApi.getCloudIAMAnalysis(),
        saasApi.getCloudAttackPaths()
      ]);
      setCnappSummary(summary);
      setAccounts(accList);
      setAssets(astList);
      setFindings(fndList);
      setCwppFindings(cwppList);
      setServerlessFindings(srvList);
      setK8sClusters(clsList);
      setContainerScans(cntList);
      setIamAnalysis(iamData);
      setAttackPaths(pathList);
    } catch (err) {
      console.error('Failed to load CNAPP cloud security data:', err);
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
      console.error('CSPM scan failed:', err);
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

      console.error('Manifest audit failed:', err);
    } finally {
      setAuditLoading(false);
    }
  };

  const handleConnectAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accountName || !accountIdentifier) return;
    try {
      await saasApi.connectCloudAccount({
        provider: accountProvider,
        account_name: accountName,
        account_identifier: accountIdentifier,
        auth_type: accountProvider === 'AWS' ? 'ASSUME_ROLE' : (accountProvider === 'AZURE' ? 'SERVICE_PRINCIPAL' : 'SERVICE_ACCOUNT_KEY')
      });
      setShowConnectModal(false);
      setAccountName('');
      setAccountIdentifier('');
      fetchCloudSecurityData();
    } catch (err) {
      console.error('Account connection failed:', err);
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
            <Cloud className="h-7 w-7 text-indigo-400" />
            CNAPP & Cloud Security Center
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Cloud-Native Application Protection across AWS, Azure, GCP & Kubernetes (CSPM, CWPP, CIEM, KSPM).
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowConnectModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-colors"
          >
            <Plus className="h-4 w-4" /> Connect Cloud Account
          </button>
          <button
            onClick={handleRunCSPMScan}
            disabled={scanRunning}
            className="flex items-center gap-2 px-3.5 py-2 bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-300 border border-indigo-500/30 rounded-xl text-xs font-semibold transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${scanRunning ? 'animate-spin' : ''}`} />
            Run CSPM Scan
          </button>
        </div>
      </div>

      {/* Top Metric Ribbon */}
      {cnappSummary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">CNAPP Score</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{cnappSummary.overall_cnapp_score}<span className="text-xs text-slate-500">/100</span></div>
            <div className="text-[10px] text-emerald-400 mt-0.5">{cnappSummary.security_tier}</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Connected Accounts</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{accounts.length}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">AWS · Azure · GCP · K8s</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Cloud Assets</div>
            <div className="text-2xl font-bold text-slate-100 mt-1">{assets.length}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Protected Resources</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">CSPM Posture</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{cnappSummary.pillar_scores.cspm_posture}%</div>
            <div className="text-[10px] text-cyan-400 mt-0.5">CIS Benchmark Status</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">CWPP Workloads</div>
            <div className="text-2xl font-bold text-amber-400 mt-1">{cnappSummary.pillar_scores.cwpp_workload_defense}%</div>
            <div className="text-[10px] text-amber-400 mt-0.5">{cwppFindings.length} Active Detections</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">KSPM Clusters</div>
            <div className="text-2xl font-bold text-indigo-300 mt-1">{k8sClusters.length}</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Restricted PSS Enforced</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-1 overflow-x-auto">
        {[
          { id: 'cnapp_overview', label: 'CNAPP Overview', icon: Layers },
          { id: 'inventory', label: 'Multi-Cloud Inventory', icon: Server },
          { id: 'cspm', label: 'CSPM & Compliance', icon: ShieldCheck },
          { id: 'cwpp', label: 'CWPP & Containers', icon: Box },
          { id: 'kspm_serverless', label: 'KSPM & Serverless', icon: FileCode },
          { id: 'ciem_attack_paths', label: 'CIEM & Attack Paths', icon: Key }
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
          Loading CNAPP Security Center...
        </div>
      ) : (
        <>
          {/* TAB 1: CNAPP Overview */}
          {activeTab === 'cnapp_overview' && cnappSummary && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Pillar Scorecard */}
              <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Layers className="h-4 w-4 text-indigo-400" /> CNAPP Multi-Pillar Posture Index
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {Object.entries(cnappSummary.pillar_scores).map(([pillar, score]: [string, any]) => (
                    <div key={pillar} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60">
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-slate-400 capitalize">{pillar.replace(/_/g, ' ')}</span>
                        <span className="font-bold text-slate-100">{score}%</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden mt-2">
                        <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${score}%` }} />
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-2 border-t border-slate-800/60">
                  <div className="text-xs font-bold text-slate-300 mb-2">Priority Remediation Actions:</div>
                  <div className="space-y-1.5">
                    {cnappSummary.top_remediation_actions.map((act: string, idx: number) => (
                      <div key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                        <ChevronRight className="h-3.5 w-3.5 text-indigo-400 shrink-0 mt-0.5" />
                        {act}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Connected Cloud Accounts */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                    <Cloud className="h-4 w-4 text-indigo-400" /> Connected Accounts
                  </h3>
                  <span className="text-[10px] text-slate-400">{accounts.length} Active</span>
                </div>
                <div className="space-y-2.5">
                  {accounts.map((acc) => (
                    <div key={acc.id} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60 flex items-center justify-between text-xs">
                      <div>
                        <div className="font-bold text-slate-200">{acc.account_name}</div>
                        <div className="text-[10px] text-slate-400 font-mono">{acc.provider} · {acc.account_identifier}</div>
                      </div>
                      <button
                        onClick={async () => {
                          await saasApi.syncCloudAccount(acc.id);
                          fetchCloudSecurityData();
                        }}
                        className="px-2.5 py-1 bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 rounded text-[10px] font-semibold"
                      >
                        Sync
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Multi-Cloud Inventory */}
          {activeTab === 'inventory' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Server className="h-4 w-4 text-indigo-400" /> Discovered Multi-Cloud & Kubernetes Assets
                </h3>
                <span className="text-xs text-slate-400">{assets.length} Total Resources</span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                    <tr>
                      <th className="p-3">Resource Name</th>
                      <th className="p-3">Provider</th>
                      <th className="p-3">Asset Type</th>
                      <th className="p-3">Region</th>
                      <th className="p-3">Exposure</th>
                      <th className="p-3">Risk Score</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50 text-slate-200">
                    {assets.map((ast) => (
                      <tr key={ast.id} className="hover:bg-slate-950/40">
                        <td className="p-3 font-semibold text-indigo-300">{ast.resource_name}</td>
                        <td className="p-3"><span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] font-bold">{ast.provider}</span></td>
                        <td className="p-3 font-mono text-[11px] text-slate-400">{ast.asset_type}</td>
                        <td className="p-3 text-slate-400">{ast.region}</td>
                        <td className="p-3">
                          <span className={`px-2 py-0.5 rounded border text-[10px] font-bold ${ast.exposure_level === 'PUBLIC_INGRESS' ? 'bg-rose-500/10 text-rose-400 border-rose-500/30' : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'}`}>
                            {ast.exposure_level}
                          </span>
                        </td>
                        <td className="p-3 font-bold text-slate-100">{ast.risk_score}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 3: CSPM & Compliance */}
          {activeTab === 'cspm' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 text-emerald-400" /> CSPM Misconfiguration Findings & CIS Benchmarks
                </h3>
                <span className="text-xs text-rose-400 font-bold">{findings.length} Open Findings</span>
              </div>
              <div className="space-y-3">
                {findings.map((fnd) => (
                  <div key={fnd.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-0.5 rounded border font-bold text-[10px] ${getSeverityBadge(fnd.severity)}`}>
                          {fnd.severity}
                        </span>
                        <span className="font-bold text-slate-200 text-sm">{fnd.title}</span>
                      </div>
                      <span className="font-mono text-[10px] text-slate-400">{fnd.rule_id}</span>
                    </div>
                    <div className="text-slate-400 leading-relaxed">{fnd.description}</div>
                    <div className="p-2.5 bg-slate-900/70 rounded-lg border border-slate-800/80 text-[11px] text-indigo-300">
                      <strong>Remediation:</strong> {fnd.remediation_guidance}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: CWPP & Containers */}
          {activeTab === 'cwpp' && (
            <div className="space-y-6">
              {/* CWPP Workload Threats */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                    <Flame className="h-4 w-4 text-rose-400" /> CWPP Runtime Workload Threat Detections
                  </h3>
                  <button
                    onClick={async () => {
                      await saasApi.simulateCWPPThreat({ workload_type: 'K8S_POD', threat_type: 'REVERSE_SHELL' });
                      fetchCloudSecurityData();
                    }}
                    className="px-3 py-1.5 bg-rose-600/20 hover:bg-rose-600/40 text-rose-300 border border-rose-500/30 rounded-lg text-xs font-semibold"
                  >
                    Simulate Workload Threat
                  </button>
                </div>
                <div className="space-y-2.5">
                  {cwppFindings.map((cw) => (
                    <div key={cw.id} className="p-3.5 bg-slate-950/60 rounded-xl border border-slate-800 text-xs flex items-center justify-between">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-0.5 rounded border text-[10px] font-bold ${getSeverityBadge(cw.severity)}`}>
                            {cw.threat_type}
                          </span>
                          <span className="font-bold text-slate-200">{cw.workload_name}</span>
                          <span className="text-[10px] text-slate-400 font-mono">({cw.workload_type})</span>
                        </div>
                        <div className="font-mono text-[11px] text-rose-300 bg-slate-900 p-1.5 rounded border border-slate-800">
                          {cw.command_line}
                        </div>
                      </div>
                      <button
                        onClick={async () => {
                          await saasApi.containWorkload(cw.id);
                          fetchCloudSecurityData();
                        }}
                        disabled={cw.is_contained}
                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${cw.is_contained ? 'bg-slate-800 text-slate-500' : 'bg-rose-600 text-white hover:bg-rose-500'}`}
                      >
                        {cw.is_contained ? 'Contained' : 'Quarantine Workload'}
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Container Scans & SBOMs */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Box className="h-4 w-4 text-indigo-400" /> Container Image Vulnerability Scans & SBOM Manifests
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {containerScans.map((cs) => (
                    <div key={cs.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span>{cs.image_name}:{cs.image_tag}</span>
                        <span className="text-emerald-400 text-[10px]">✓ Cosign Verified</span>
                      </div>
                      <div className="text-[11px] text-slate-400">SBOM Components: {cs.sbom_components_count} packages</div>
                      <div className="flex gap-2 text-[10px]">
                        <span className="px-2 py-0.5 bg-rose-500/10 text-rose-400 rounded">Critical: {cs.critical_cve_count}</span>
                        <span className="px-2 py-0.5 bg-amber-500/10 text-amber-400 rounded">High: {cs.high_cve_count}</span>
                        <span className="px-2 py-0.5 bg-indigo-500/10 text-indigo-400 rounded">Medium: {cs.medium_cve_count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: KSPM & Serverless */}
          {activeTab === 'kspm_serverless' && (
            <div className="space-y-6">
              {/* K8s Clusters */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <FileCode className="h-4 w-4 text-indigo-400" /> Kubernetes Cluster Posture & Pod Security Standards
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {k8sClusters.map((cls) => (
                    <div key={cls.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                      <div className="font-bold text-slate-200">{cls.cluster_name}</div>
                      <div className="text-slate-400 text-[10px]">{cls.distribution} · {cls.k8s_version} ({cls.node_count} Nodes)</div>
                      <div className="flex justify-between items-center pt-2 border-t border-slate-800">
                        <span className="text-slate-400">PSS: <strong className="text-indigo-300">{cls.pod_security_standard}</strong></span>
                        <span className="text-emerald-400 font-bold">{cls.kspm_health_score}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Serverless Function Risks */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Zap className="h-4 w-4 text-amber-400" /> Serverless Function Security Posture (Lambda / Cloud Functions)
                </h3>
                <div className="space-y-2.5">
                  {serverlessFindings.map((sf) => (
                    <div key={sf.id} className="p-3.5 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-1">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span>{sf.function_name} ({sf.runtime})</span>
                        <span className="text-amber-400">Risk: {sf.risk_score}/100</span>
                      </div>
                      <div className="text-[11px] text-slate-400">{sf.remediation_advice}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* K8s Manifest Auditor */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Terminal className="h-4 w-4 text-indigo-400" /> Interactive Kubernetes YAML Manifest Auditor
                </h3>
                <textarea
                  rows={8}
                  value={manifestText}
                  onChange={(e) => setManifestText(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-slate-300 focus:outline-none focus:border-indigo-500"
                />
                <button
                  onClick={handleAuditManifest}
                  disabled={auditLoading}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-colors"
                >
                  {auditLoading ? 'Auditing...' : 'Audit Manifest Context'}
                </button>
                {k8sAuditResult && (
                  <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <span className="text-slate-200">Audit Score: {k8sAuditResult.workload_security_score}/100</span>
                      <span className={k8sAuditResult.is_compliant ? 'text-emerald-400' : 'text-rose-400'}>
                        {k8sAuditResult.is_compliant ? 'COMPLIANT' : `${k8sAuditResult.violations_count} Violations Found`}
                      </span>
                    </div>
                    {k8sAuditResult.violations.map((v: any, i: number) => (
                      <div key={i} className="text-slate-400 border-l-2 border-rose-500 pl-3">
                        <strong className="text-rose-400">{v.title}:</strong> {v.description}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 6: CIEM & Attack Paths */}
          {activeTab === 'ciem_attack_paths' && (
            <div className="space-y-6">
              {/* CIEM Identity Analysis */}
              {iamAnalysis && (
                <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                  <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                    <Key className="h-4 w-4 text-indigo-400" /> Cloud IAM (CIEM) Entitlement & Privilege Escalation Analysis
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {iamAnalysis.identities.map((idnt: any, idx: number) => (
                      <div key={idx} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800 text-xs space-y-1">
                        <div className="font-bold text-slate-200">{idnt.name} ({idnt.identity_type})</div>
                        <div className="text-[10px] text-slate-400 font-mono break-all">{idnt.identity_arn}</div>
                        {idnt.privilege_escalation_vectors.length > 0 && (
                          <div className="text-[10px] text-rose-400">
                            Escalation Vector: {idnt.privilege_escalation_vectors.join(', ')}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Attack Path Graph */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Network className="h-4 w-4 text-rose-400" /> Graph-Synthesized Cloud Attack Paths
                </h3>
                <div className="space-y-3">
                  {attackPaths.map((ap) => (
                    <div key={ap.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span>{ap.title}</span>
                        <span className="text-rose-400">Blast Radius: {ap.blast_radius}</span>
                      </div>
                      <div className="text-slate-400">{ap.source_entity} → {ap.target_critical_asset}</div>
                      <div className="text-indigo-300 text-[11px]">
                        <strong>Kill Chain Phase:</strong> {ap.kill_chain_phase}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* Connect Cloud Account Modal */}
      {showConnectModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Cloud className="h-5 w-5 text-indigo-400" /> Connect Cloud Provider
            </h2>
            <form onSubmit={handleConnectAccount} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Provider</label>
                <select
                  value={accountProvider}
                  onChange={(e) => setAccountProvider(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                >
                  <option value="AWS">Amazon Web Services (AWS)</option>
                  <option value="AZURE">Microsoft Azure</option>
                  <option value="GCP">Google Cloud Platform (GCP)</option>
                  <option value="KUBERNETES">Kubernetes Cluster (K8s)</option>
                </select>
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Account / Environment Name</label>
                <input
                  type="text"
                  value={accountName}
                  onChange={(e) => setAccountName(e.target.value)}
                  placeholder="e.g. AWS-Production-Core"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Account ID / Subscription ID / Project ID</label>
                <input
                  type="text"
                  value={accountIdentifier}
                  onChange={(e) => setAccountIdentifier(e.target.value)}
                  placeholder="e.g. 123456789012"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                />
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowConnectModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold"
                >
                  Connect & Sync
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
