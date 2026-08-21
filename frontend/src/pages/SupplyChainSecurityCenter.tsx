import React, { useEffect, useState } from 'react';
import {
  FileCode,
  Layers,
  GitBranch,
  ShieldCheck,
  Lock,
  Download,
  Plus,
  Terminal,
  Activity,
  ChevronRight,
  Key
} from 'lucide-react';

import { saasApi } from '../services/saas';

export const SupplyChainSecurityCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'sbom' | 'vex' | 'slsa' | 'gates' | 'secrets'>('overview');
  const [summary, setSummary] = useState<any>(null);
  const [components, setComponents] = useState<any[]>([]);
  const [vexStatements, setVexStatements] = useState<any[]>([]);
  const [attestations, setAttestations] = useState<any[]>([]);
  const [gates, setGates] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Publish VEX modal state
  const [showVEXModal, setShowVEXModal] = useState<boolean>(false);
  const [vexCVE, setVexCVE] = useState<string>('CVE-2026-9012');
  const [vexPURL, setVexPURL] = useState<string>('pkg:npm/example-lib@1.0.0');
  const [vexStatus, setVexStatus] = useState<string>('NOT_AFFECTED');
  const [vexJustification, setVexJustification] = useState<string>('Vulnerable code is not reachable via active entry points');
  const [vexImpact, setVexImpact] = useState<string>('Feature flag disabled in production builds.');

  // Gate evaluation simulator state
  const [simEnv, setSimEnv] = useState<string>('PRODUCTION');
  const [simCritCVEs, setSimCritCVEs] = useState<number>(0);
  const [simHighCVEs, setSimHighCVEs] = useState<number>(1);
  const [simSLSA, setSimSLSA] = useState<boolean>(true);
  const [simCopyleft, setSimCopyleft] = useState<boolean>(false);
  const [simSecrets, setSimSecrets] = useState<boolean>(false);
  const [gateResult, setGateResult] = useState<any>(null);
  const [gateLoading, setGateLoading] = useState<boolean>(false);

  // Secret scanner state
  const [scanCodeText, setScanCodeText] = useState<string>(
    'const awsKey = "AKIA1234567890EXAMPLE";\nconst secretToken = "ghp_1234567890abcdefghijklmnopqrstuvwxyz";'
  );
  const [scanResult, setScanResult] = useState<any>(null);
  const [scanLoading, setScanLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchSupplyChainData();
  }, []);

  const fetchSupplyChainData = async () => {
    try {
      setLoading(true);
      const [sum, comps, vex, att, gt] = await Promise.all([
        saasApi.getSupplyChainSummary(),
        saasApi.getSBOMComponents(),
        saasApi.getVEXStatements(),
        saasApi.getSLSAAttestations(),
        saasApi.getPipelineGates()
      ]);
      setSummary(sum);
      setComponents(comps);
      setVexStatements(vex);
      setAttestations(att);
      setGates(gt);
    } catch (err) {
      console.error('Failed to load supply chain data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePublishVEX = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await saasApi.publishVEXStatement({
        vulnerability_id: vexCVE,
        product_purl: vexPURL,
        status: vexStatus,
        justification: vexJustification,
        impact_statement: vexImpact
      });
      setShowVEXModal(false);
      fetchSupplyChainData();
    } catch (err) {
      console.error('Failed to publish VEX statement:', err);
    }
  };

  const handleEvaluateGate = async () => {
    try {
      setGateLoading(true);
      const res = await saasApi.evaluatePipelineGate({
        target_environment: simEnv,
        critical_cves: simCritCVEs,
        high_cves: simHighCVEs,
        has_slsa_level_3: simSLSA,
        has_copyleft_license: simCopyleft,
        has_secrets_detected: simSecrets
      });
      setGateResult(res);
    } catch (err) {
      console.error('Gate evaluation failed:', err);
    } finally {
      setGateLoading(false);
    }
  };

  const handleScanSecrets = async () => {
    try {
      setScanLoading(true);
      const res = await saasApi.scanCodeSecrets({ file_content: scanCodeText });
      setScanResult(res);
    } catch (err) {
      console.error('Secret scan failed:', err);
    } finally {
      setScanLoading(false);
    }
  };

  const handleExportSBOM = async (fmt: string) => {
    try {
      const data = await saasApi.generateSBOMExport({ format_type: fmt });
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sbom-${fmt.toLowerCase()}-${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Layers className="h-7 w-7 text-indigo-400" />
            Supply Chain Security & SBOM 2.0
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            End-to-End Code-to-Cloud Governance: CycloneDX/SPDX SBOMs, OpenVEX Exploitability, SLSA Level 3 & CI/CD Gates.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => handleExportSBOM('CYCLONEDX_1_5')}
            className="flex items-center gap-2 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl text-xs font-semibold transition-colors"
          >
            <Download className="h-4 w-4" /> Export CycloneDX
          </button>
          <button
            onClick={() => setShowVEXModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-colors"
          >
            <Plus className="h-4 w-4" /> Publish OpenVEX
          </button>
        </div>
      </div>

      {/* Top Metric Ribbon */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Supply Chain Score</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.overall_supply_chain_score}<span className="text-xs text-slate-500">/100</span></div>
            <div className="text-[10px] text-emerald-400 mt-0.5">{summary.security_tier}</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">SLSA Build Level</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">LEVEL 3</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Hermetic & Signed</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">SBOM Packages</div>
            <div className="text-2xl font-bold text-slate-100 mt-1">{components.length}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Direct & Transitive</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">OpenVEX Records</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{vexStatements.length}</div>
            <div className="text-[10px] text-cyan-400 mt-0.5">Exploitability Filtered</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Pipeline Gates</div>
            <div className="text-2xl font-bold text-indigo-300 mt-1">{gates.length} Active</div>
            <div className="text-[10px] text-indigo-400 mt-0.5">CI/CD Gatekeeper</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Secret Scanner</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">CLEAN</div>
            <div className="text-[10px] text-slate-400 mt-0.5">High-Entropy Checked</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'Supply Chain Overview', icon: Layers },
          { id: 'sbom', label: 'SBOM 2.0 Catalog', icon: FileCode },
          { id: 'vex', label: 'OpenVEX Exploitability', icon: ShieldCheck },
          { id: 'slsa', label: 'SLSA Level 3 Provenance', icon: GitBranch },
          { id: 'gates', label: 'CI/CD Gatekeeper Policies', icon: Lock },
          { id: 'secrets', label: 'Secret Scanner & Licenses', icon: Key }
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
          Loading Supply Chain & SBOM Security Center...
        </div>
      ) : (
        <>
          {/* TAB 1: Overview */}
          {activeTab === 'overview' && summary && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Architecture & Scorecard */}
              <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 text-indigo-400" /> SLSA Level 3 & Code-to-Cloud Governance
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60">
                    <div className="text-slate-400">Provenance Attestation</div>
                    <div className="text-sm font-bold text-emerald-400 mt-1">COSIGN VERIFIED</div>
                    <div className="text-[10px] text-slate-500 mt-0.5">Signed by GitHub Actions Builder</div>
                  </div>
                  <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60">
                    <div className="text-slate-400">VEX Exploitability Filtering</div>
                    <div className="text-sm font-bold text-cyan-400 mt-1">ACTIVE</div>
                    <div className="text-[10px] text-slate-500 mt-0.5">Suppresses non-reachable CVE alerts</div>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800/60">
                  <div className="text-xs font-bold text-slate-300 mb-2">Priority Supply Chain Actions:</div>
                  <div className="space-y-1.5">
                    {summary.top_remediation_actions.map((act: string, idx: number) => (
                      <div key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                        <ChevronRight className="h-3.5 w-3.5 text-indigo-400 shrink-0 mt-0.5" />
                        {act}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Quick Pipeline Gates */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Lock className="h-4 w-4 text-indigo-400" /> Active Pipeline Gates
                </h3>
                <div className="space-y-2.5">
                  {gates.map((g) => (
                    <div key={g.id} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60 text-xs">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span>{g.gate_name}</span>
                        <span className="text-indigo-400">{g.enforcement_mode}</span>
                      </div>
                      <div className="text-[10px] text-slate-400 mt-1">Env: {g.target_environment} · Max Critical: {g.max_critical_cves}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: SBOM 2.0 */}
          {activeTab === 'sbom' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <FileCode className="h-4 w-4 text-indigo-400" /> Software Bill of Materials (SBOM 2.0) Inventory
                </h3>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleExportSBOM('CYCLONEDX_1_5')}
                    className="px-3 py-1 bg-indigo-600/30 text-indigo-300 rounded text-xs font-semibold"
                  >
                    CycloneDX 1.5
                  </button>
                  <button
                    onClick={() => handleExportSBOM('SPDX_2_3')}
                    className="px-3 py-1 bg-indigo-600/30 text-indigo-300 rounded text-xs font-semibold"
                  >
                    SPDX 2.3
                  </button>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                    <tr>
                      <th className="p-3">Package Name</th>
                      <th className="p-3">Version</th>
                      <th className="p-3">Ecosystem</th>
                      <th className="p-3">License</th>
                      <th className="p-3">Dependency Type</th>
                      <th className="p-3">Vulnerabilities</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50 text-slate-200">
                    {components.map((c) => (
                      <tr key={c.id} className="hover:bg-slate-950/40">
                        <td className="p-3 font-semibold text-indigo-300">{c.package_name}</td>
                        <td className="p-3 font-mono text-slate-400">{c.version}</td>
                        <td className="p-3"><span className="px-2 py-0.5 bg-slate-800 rounded text-[10px] font-bold">{c.ecosystem}</span></td>
                        <td className="p-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${c.is_copyleft ? 'bg-amber-500/10 text-amber-400' : 'text-slate-300'}`}>
                            {c.license_spdx_id}
                          </span>
                        </td>
                        <td className="p-3">{c.is_direct_dependency ? 'Direct' : 'Transitive'}</td>
                        <td className="p-3">
                          {c.vulnerability_count === 0 ? (
                            <span className="text-emerald-400 font-bold">✓ 0 CVEs</span>
                          ) : (
                            <span className="text-rose-400 font-bold">{c.vulnerability_count} CVEs</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 3: OpenVEX */}
          {activeTab === 'vex' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 text-emerald-400" /> OpenVEX Exploitability Statements Ledger
                </h3>
                <span className="text-xs text-slate-400">{vexStatements.length} Active Records</span>
              </div>
              <div className="space-y-3">
                {vexStatements.map((v) => (
                  <div key={v.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-0.5 rounded border text-[10px] font-bold ${v.status === 'NOT_AFFECTED' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : (v.status === 'FIXED' ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30' : 'bg-amber-500/10 text-amber-400 border-amber-500/30')}`}>
                          {v.status}
                        </span>
                        <span className="font-bold text-slate-200">{v.vulnerability_id}</span>
                        <span className="text-slate-400 font-mono text-[10px]">({v.product_purl})</span>
                      </div>
                      <span className="text-[10px] text-slate-500">{v.published_at}</span>
                    </div>
                    <div className="text-slate-400"><strong>Justification:</strong> {v.justification}</div>
                    <div className="text-indigo-300 text-[11px] bg-slate-900/80 p-2 rounded">
                      <strong>Impact Assessment:</strong> {v.impact_statement}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: SLSA Provenance */}
          {activeTab === 'slsa' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <GitBranch className="h-4 w-4 text-indigo-400" /> SLSA Level 3 Provenance & Build Attestations
              </h3>
              <div className="space-y-3">
                {attestations.map((a) => (
                  <div key={a.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold text-slate-200">
                      <span>{a.artifact_name}</span>
                      <span className="text-emerald-400 text-[10px]">✓ {a.slsa_level} (Cosign Verified)</span>
                    </div>
                    <div className="text-slate-400 font-mono text-[11px]">Digest: {a.artifact_digest}</div>
                    <div className="text-slate-400 text-[10px]">Builder: {a.builder_id} · Commit: {a.source_commit_sha}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: CI/CD Gates */}
          {activeTab === 'gates' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Lock className="h-4 w-4 text-indigo-400" /> CI/CD Pipeline Gatekeeper Simulator
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Target Deployment Environment</label>
                  <select
                    value={simEnv}
                    onChange={(e) => setSimEnv(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                  >
                    <option value="PRODUCTION">PRODUCTION</option>
                    <option value="STAGING">STAGING</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Critical CVEs: {simCritCVEs}</label>
                  <input
                    type="number"
                    min={0}
                    value={simCritCVEs}
                    onChange={(e) => setSimCritCVEs(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">High CVEs: {simHighCVEs}</label>
                  <input
                    type="number"
                    min={0}
                    value={simHighCVEs}
                    onChange={(e) => setSimHighCVEs(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                  />
                </div>
                <div className="flex items-center gap-2 pt-4">
                  <input
                    type="checkbox"
                    checked={simSLSA}
                    onChange={(e) => setSimSLSA(e.target.checked)}
                    id="simSLSA"
                  />
                  <label htmlFor="simSLSA" className="text-slate-300">Has SLSA Level 3 Signature</label>
                </div>
                <div className="flex items-center gap-2 pt-4">
                  <input
                    type="checkbox"
                    checked={simCopyleft}
                    onChange={(e) => setSimCopyleft(e.target.checked)}
                    id="simCopyleft"
                  />
                  <label htmlFor="simCopyleft" className="text-slate-300">Copyleft License Present</label>
                </div>
                <div className="flex items-center gap-2 pt-4">
                  <input
                    type="checkbox"
                    checked={simSecrets}
                    onChange={(e) => setSimSecrets(e.target.checked)}
                    id="simSec"
                  />
                  <label htmlFor="simSec" className="text-slate-300">Secrets Found in Commits</label>
                </div>
              </div>

              <button
                onClick={handleEvaluateGate}
                disabled={gateLoading}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-colors"
              >
                {gateLoading ? 'Evaluating...' : 'Evaluate Deployment Gate'}
              </button>

              {gateResult && (
                <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs space-y-2">
                  <div className="flex justify-between items-center font-bold">
                    <span className="text-slate-200">Evaluation Status: {gateResult.target_environment}</span>
                    <span className={`px-2.5 py-1 rounded border text-[11px] font-bold ${gateResult.is_passed ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-rose-500/10 text-rose-400 border-rose-500/30'}`}>
                      {gateResult.gate_status}
                    </span>
                  </div>
                  {gateResult.violations.map((v: string, i: number) => (
                    <div key={i} className="text-rose-400 border-l-2 border-rose-500 pl-3">{v}</div>
                  ))}
                  {gateResult.is_passed && (
                    <div className="text-emerald-400">All supply chain gating criteria satisfied. Authorized for release.</div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* TAB 6: Secret Scanner */}
          {activeTab === 'secrets' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Terminal className="h-4 w-4 text-indigo-400" /> High-Entropy Secret Scanner & Token Detector
              </h3>
              <textarea
                rows={6}
                value={scanCodeText}
                onChange={(e) => setScanCodeText(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-slate-300 focus:outline-none focus:border-indigo-500"
              />
              <button
                onClick={handleScanSecrets}
                disabled={scanLoading}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-colors"
              >
                {scanLoading ? 'Scanning...' : 'Scan for Secrets & API Keys'}
              </button>

              {scanResult && (
                <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs space-y-2">
                  <div className="flex justify-between items-center font-bold">
                    <span className="text-slate-200">Scan Status</span>
                    <span className={scanResult.is_clean ? 'text-emerald-400' : 'text-rose-400'}>
                      {scanResult.is_clean ? 'CLEAN (0 Secrets)' : `${scanResult.secrets_detected_count} Secrets Detected`}
                    </span>
                  </div>
                  {scanResult.findings.map((f: any, i: number) => (
                    <div key={i} className="text-rose-400 border-l-2 border-rose-500 pl-3">
                      <strong>{f.secret_type}:</strong> Pattern {f.matched_prefix} (Entropy: {f.entropy})
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Publish OpenVEX Modal */}
      {showVEXModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-indigo-400" /> Publish OpenVEX Statement
            </h2>
            <form onSubmit={handlePublishVEX} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Vulnerability CVE ID</label>
                <input
                  type="text"
                  value={vexCVE}
                  onChange={(e) => setVexCVE(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Product / Package PURL</label>
                <input
                  type="text"
                  value={vexPURL}
                  onChange={(e) => setVexPURL(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Exploitability Status</label>
                <select
                  value={vexStatus}
                  onChange={(e) => setVexStatus(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                >
                  <option value="NOT_AFFECTED">NOT_AFFECTED (Non-Exploitable)</option>
                  <option value="FIXED">FIXED (Patched in Current Release)</option>
                  <option value="UNDER_INVESTIGATION">UNDER_INVESTIGATION (In Triage)</option>
                  <option value="AFFECTED">AFFECTED (Actionable Vulnerability)</option>
                </select>
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Standard Justification</label>
                <input
                  type="text"
                  value={vexJustification}
                  onChange={(e) => setVexJustification(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Impact Assessment Statement</label>
                <textarea
                  rows={3}
                  value={vexImpact}
                  onChange={(e) => setVexImpact(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                />
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowVEXModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold"
                >
                  Publish Statement
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
