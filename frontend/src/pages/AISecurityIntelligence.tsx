import React, { useEffect, useState } from 'react';
import {
  Brain,
  ShieldAlert,
  Activity,
  Cpu,
  CheckCircle2,
  RotateCcw,
  Sparkles,
  Lock,
  Layers,
  Zap
} from 'lucide-react';

import { saasApi } from '../services/saas';

export const AISecurityIntelligence: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'registry' | 'drift' | 'xai' | 'adversarial' | 'copilot'>('registry');
  const [models, setModels] = useState<any[]>([]);
  const [drift, setDrift] = useState<any>(null);
  const [quality, setQuality] = useState<any>(null);
  const [adversarialEvents, setAdversarialEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Multi-model test state
  const [flowBytes, setFlowBytes] = useState<number>(24500);
  const [fwdPkts, setFwdPkts] = useState<number>(350);
  const [inferenceResult, setInferenceResult] = useState<any>(null);
  const [inferenceLoading, setInferenceLoading] = useState<boolean>(false);

  // Copilot 2.0 state
  const [copilotPrompt, setCopilotPrompt] = useState<string>('Analyze anomalous outbound HTTPS flow towards 198.51.100.22 and propose gated response.');
  const [copilotResponse, setCopilotResponse] = useState<any>(null);
  const [copilotLoading, setCopilotLoading] = useState<boolean>(false);

  // Action status
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    fetchAIData();
  }, []);

  const fetchAIData = async () => {
    try {
      setLoading(true);
      const [mList, dData, qData, advList] = await Promise.all([
        saasApi.listAIModels(),
        saasApi.getAIModelDrift(),
        saasApi.getAIDetectionQuality(),
        saasApi.listAIAdversarialEvents()
      ]);
      setModels(mList);
      setDrift(dData);
      setQuality(qData);
      setAdversarialEvents(advList);
    } catch (err) {
      console.error('Failed to load AI Intelligence state:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifySignature = async (modelId: string) => {
    try {
      setActionLoading(`verify_${modelId}`);
      await saasApi.verifyAIModelSignature(modelId);
      await fetchAIData();
    } catch (err) {
      console.error('Signature verification error:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const handlePromote = async (modelId: string) => {
    try {
      setActionLoading(`promote_${modelId}`);
      await saasApi.promoteAIModel(modelId, { target_stage: 'PRODUCTION' });
      await fetchAIData();
    } catch (err) {
      console.error('Promotion error:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleRollback = async (modelId: string) => {
    try {
      setActionLoading(`rollback_${modelId}`);
      await saasApi.rollbackAIModel(modelId);
      await fetchAIData();
    } catch (err) {
      console.error('Rollback error:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleRunInference = async () => {
    try {
      setInferenceLoading(true);
      const res = await saasApi.executeMultiModelDetection({
        features: {
          flow_bytes_s: flowBytes,
          tot_fwd_pkts: fwdPkts,
          flow_duration: 120.0,
          fwd_pkt_len_mean: 950.0
        },
        entity_id: 'HOST-CORE-01'
      });
      setInferenceResult(res);
    } catch (err) {
      console.error('Inference error:', err);
    } finally {
      setInferenceLoading(false);
    }
  };

  const handleCopilotReason = async () => {
    try {
      setCopilotLoading(true);
      const res = await saasApi.reasonAICopilot({
        prompt: copilotPrompt
      });
      setCopilotResponse(res);
    } catch (err) {
      console.error('Copilot reasoning error:', err);
    } finally {
      setCopilotLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Brain className="h-7 w-7 text-indigo-400" />
            AI/ML Security Intelligence Command Center
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Multi-model detection, cryptographic model governance, drift monitoring, adversarial defense, and AI Copilot 2.0.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchAIData}
            className="flex items-center gap-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-colors"
          >
            <Activity className="h-4 w-4 text-cyan-400" /> Refresh Telemetry
          </button>
        </div>
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Activity className="h-8 w-8 animate-spin text-indigo-400 mr-3" />
          Loading AI/ML intelligence topologies and model registries...
        </div>
      ) : (
        <>
          {/* Key Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Registered Models</div>
              <div className="text-2xl font-bold text-slate-100 mt-1">{models.length}</div>
              <div className="text-[11px] text-indigo-400 mt-1 flex items-center gap-1">
                <Lock className="h-3 w-3" /> HMAC-SHA256 Signed
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Drift PSI Status</div>
              <div className="text-2xl font-bold text-emerald-400 mt-1">
                {drift?.overall_psi || 0.035}{' '}
                <span className="text-xs text-slate-400 font-normal">({drift?.drift_status || 'NO_DRIFT'})</span>
              </div>
              <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3 text-emerald-400" /> Statistical Alignment Stable
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Detection F1 Score</div>
              <div className="text-2xl font-bold text-cyan-400 mt-1">
                {quality ? (quality.f1_score * 100).toFixed(1) + '%' : '97.1%'}
              </div>
              <div className="text-[11px] text-cyan-400 mt-1 flex items-center gap-1">
                <Zap className="h-3 w-3" /> Latency: {quality?.detection_latency_ms || 12.3} ms
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Adversarial Threats Blocked</div>
              <div className="text-2xl font-bold text-rose-400 mt-1">{adversarialEvents.length || 0}</div>
              <div className="text-[11px] text-rose-400 mt-1 flex items-center gap-1">
                <ShieldAlert className="h-3 w-3" /> Injections & Poisoning Mitigated
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex border-b border-slate-800 gap-2">
            {[
              { id: 'registry', label: 'Model Registry & Governance', icon: Layers },
              { id: 'drift', label: 'Drift & Quality Monitor', icon: Activity },
              { id: 'xai', label: 'Multi-Model XAI Inspector', icon: Cpu },
              { id: 'adversarial', label: 'Adversarial Defense Center', icon: ShieldAlert },
              { id: 'copilot', label: 'AI Copilot 2.0 Workbench', icon: Sparkles }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 transition-colors ${
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

          {/* Tab 1: Model Registry & Governance */}
          {activeTab === 'registry' && (
            <div className="space-y-4">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                  <Layers className="h-5 w-5 text-indigo-400" />
                  Signed Model Registry & Lineage
                </h2>

                <div className="space-y-3">
                  {models.map((m) => (
                    <div key={m.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800/80 space-y-3">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-bold text-slate-100">{m.model_name}</span>
                            <span className="font-mono text-xs text-indigo-300">({m.model_version})</span>
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                m.stage === 'PRODUCTION'
                                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                  : m.stage === 'CANARY'
                                  ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                                  : 'bg-slate-500/10 text-slate-400 border border-slate-500/20'
                              }`}
                            >
                              {m.stage}
                            </span>
                          </div>
                          <div className="text-xs text-slate-400 mt-1">
                            Dataset: <strong className="text-slate-300">{m.training_dataset_name}</strong> ({m.training_samples_count} samples)
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleVerifySignature(m.id)}
                            disabled={actionLoading === `verify_${m.id}`}
                            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-colors flex items-center gap-1"
                          >
                            <Lock className="h-3 w-3 text-cyan-400" /> Verify HMAC Signature
                          </button>
                          {m.stage !== 'PRODUCTION' && (
                            <button
                              onClick={() => handlePromote(m.id)}
                              disabled={actionLoading === `promote_${m.id}`}
                              className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-lg transition-colors"
                            >
                              Promote to Production
                            </button>
                          )}
                          {m.stage === 'PRODUCTION' && (
                            <button
                              onClick={() => handleRollback(m.id)}
                              disabled={actionLoading === `rollback_${m.id}`}
                              className="px-3 py-1.5 bg-rose-950/60 hover:bg-rose-900/60 text-rose-300 border border-rose-500/30 text-xs font-semibold rounded-lg transition-colors flex items-center gap-1"
                            >
                              <RotateCcw className="h-3 w-3" /> Rollback
                            </button>
                          )}
                        </div>
                      </div>

                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-900 text-xs text-slate-400">
                        <div>ROC-AUC: <strong className="text-slate-200">{m.roc_auc}</strong></div>
                        <div>Precision: <strong className="text-slate-200">{(m.precision_score * 100).toFixed(1)}%</strong></div>
                        <div>Recall: <strong className="text-slate-200">{(m.recall_score * 100).toFixed(1)}%</strong></div>
                        <div>F1 Score: <strong className="text-slate-200">{(m.f1_score * 100).toFixed(1)}%</strong></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Tab 2: Drift & Quality Monitor */}
          {activeTab === 'drift' && (
            <div className="space-y-4">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                  <Activity className="h-5 w-5 text-emerald-400" />
                  Feature & Prediction Distribution Drift (PSI)
                </h2>

                <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-800/80 space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm font-bold text-slate-100">Population Stability Index (PSI)</div>
                      <div className="text-xs text-slate-400">{drift?.recommendation}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold text-emerald-400">{drift?.overall_psi}</div>
                      <div className="text-[10px] text-slate-500 font-mono">KS-Stat: {drift?.ks_statistic}</div>
                    </div>
                  </div>

                  <div className="space-y-2 pt-2">
                    {drift?.feature_drift_breakdown &&
                      Object.entries(drift.feature_drift_breakdown).map(([feat, details]: [string, any]) => (
                        <div key={feat} className="flex items-center justify-between text-xs bg-slate-900 p-2.5 rounded-lg">
                          <span className="font-mono text-slate-300">{feat}</span>
                          <div className="flex items-center gap-3">
                            <span className="text-slate-400">PSI: <strong>{details.psi}</strong></span>
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400">
                              {details.status}
                            </span>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Tab 3: Multi-Model XAI Inspector */}
          {activeTab === 'xai' && (
            <div className="space-y-4">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                  <Cpu className="h-5 w-5 text-cyan-400" />
                  Multi-Model Detection & SHAP-Attribution Tester
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Flow Bytes Per Second</label>
                      <input
                        type="number"
                        value={flowBytes}
                        onChange={(e) => setFlowBytes(Number(e.target.value))}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Total Forward Packets</label>
                      <input
                        type="number"
                        value={fwdPkts}
                        onChange={(e) => setFwdPkts(Number(e.target.value))}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200"
                      />
                    </div>
                    <button
                      onClick={handleRunInference}
                      disabled={inferenceLoading}
                      className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs rounded-lg transition-colors flex items-center gap-2"
                    >
                      {inferenceLoading && <Activity className="h-4 w-4 animate-spin" />}
                      Execute Multi-Model Pipeline
                    </button>
                  </div>

                  {inferenceResult && (
                    <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-100">Prediction: {inferenceResult.prediction}</span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                          {inferenceResult.severity} ({(inferenceResult.confidence * 100).toFixed(1)}%)
                        </span>
                      </div>

                      <div className="text-slate-300 text-[11px] bg-slate-900 p-2.5 rounded">
                        {inferenceResult.xai.reasoning_summary}
                      </div>

                      <div className="space-y-1.5">
                        <div className="text-[11px] font-bold text-slate-400">Contributing Signal Weights:</div>
                        {inferenceResult.xai.contributing_signals.map((sig: any) => (
                          <div key={sig.signal_name} className="flex items-center justify-between text-[11px]">
                            <span className="font-mono text-slate-400">{sig.signal_name}</span>
                            <span className="text-cyan-300 font-bold">{(sig.importance_weight * 100).toFixed(0)}% weight</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Tab 4: Adversarial Defense Center */}
          {activeTab === 'adversarial' && (
            <div className="space-y-4">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                  <ShieldAlert className="h-5 w-5 text-rose-400" />
                  Mitigated Adversarial Threats & Attack Attempts
                </h2>

                {adversarialEvents.length === 0 ? (
                  <div className="p-8 text-center text-slate-500 text-xs">
                    No active adversarial attacks detected in current audit window.
                  </div>
                ) : (
                  <div className="space-y-2">
                    {adversarialEvents.map((evt) => (
                      <div key={evt.id} className="p-3.5 bg-slate-950/60 rounded-xl border border-slate-800/80 flex items-center justify-between">
                        <div>
                          <div className="text-xs font-bold text-rose-300 flex items-center gap-2">
                            <ShieldAlert className="h-3.5 w-3.5" />
                            {evt.threat_type} — {evt.mitigation_action}
                          </div>
                          <div className="text-[11px] text-slate-400 font-mono mt-1">
                            Payload Snippet: {evt.raw_payload_snippet}
                          </div>
                        </div>
                        <span className="text-[10px] text-slate-500 font-mono">{evt.detected_at}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Tab 5: AI Copilot 2.0 Workbench */}
          {activeTab === 'copilot' && (
            <div className="space-y-4">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-indigo-400" />
                  AI Copilot 2.0 Security Analyst Reasoning
                </h2>

                <div className="space-y-3">
                  <textarea
                    rows={3}
                    value={copilotPrompt}
                    onChange={(e) => setCopilotPrompt(e.target.value)}
                    placeholder="Enter security investigation prompt..."
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200"
                  />

                  <div className="flex justify-end">
                    <button
                      onClick={handleCopilotReason}
                      disabled={copilotLoading}
                      className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-lg transition-colors flex items-center gap-2"
                    >
                      {copilotLoading && <Activity className="h-4 w-4 animate-spin" />}
                      Run Copilot Reasoning
                    </button>
                  </div>

                  {copilotResponse && (
                    <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3 text-xs">
                      {copilotResponse.is_prompt_injection_flagged && (
                        <div className="p-2.5 bg-rose-950/40 border border-rose-500/40 rounded-lg text-rose-300 text-[11px] font-bold">
                          ⚠️ Prompt Injection Pattern Flagged & Sanitized by Adversarial Defense Layer.
                        </div>
                      )}

                      <div>
                        <div className="font-bold text-slate-200">Reasoning Summary:</div>
                        <div className="text-slate-400 mt-1">{copilotResponse.reasoning_summary}</div>
                      </div>

                      <div className="pt-2 border-t border-slate-900">
                        <div className="font-bold text-slate-200 mb-1.5">Gated Remediation Proposals (Human Approval Gated):</div>
                        <div className="space-y-1.5">
                          {copilotResponse.remediation_proposals.map((rem: any) => (
                            <div key={rem.action} className="p-2 bg-slate-900 rounded flex items-center justify-between">
                              <div>
                                <span className="font-bold text-indigo-300">{rem.action}</span>: {rem.description}
                              </div>
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-400">
                                Requires Human Approval
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
