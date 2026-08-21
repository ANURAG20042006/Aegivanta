import React, { useEffect, useState } from 'react';
import {
  Brain,
  Cpu,
  Shield,
  ShieldAlert,
  Activity,
  GitBranch,
  RefreshCw,
  Play,
  CheckCircle2,
  Zap,
  Server,
  Sparkles,
  Check
} from 'lucide-react';
import { mlModelPlatformApi } from '../services/saas';


export const MLModelPlatformCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'registry' | 'drift' | 'adversarial' | 'lineage' | 'simulator'>('overview');
  const [summary, setSummary] = useState<any>(null);
  const [models, setModels] = useState<any[]>([]);
  const [champion, setChampion] = useState<any>(null);
  const [driftRecords, setDriftRecords] = useState<any[]>([]);
  const [driftSummary, setDriftSummary] = useState<any>(null);
  const [adversarialEvents, setAdversarialEvents] = useState<any[]>([]);
  const [adversarialSummary, setAdversarialSummary] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Simulator state
  const [simModelId, setSimModelId] = useState<string>('cat-001');
  const [simAttackType, setSimAttackType] = useState<string>('EVASION');
  const [simLoading, setSimLoading] = useState<boolean>(false);
  const [simResult, setSimResult] = useState<any>(null);

  useEffect(() => {
    loadAll();
  }, []);

  const loadAll = async () => {
    try {
      const [sum, mdls, champ, driftRecs, driftSum, advEvts, advSum] = await Promise.all([
        mlModelPlatformApi.getSummary(),
        mlModelPlatformApi.listModels(),
        mlModelPlatformApi.getChampionModel(),
        mlModelPlatformApi.listDriftRecords(),
        mlModelPlatformApi.getDriftSummary(),
        mlModelPlatformApi.listAdversarialEvents(),
        mlModelPlatformApi.getAdversarialSummary(),
      ]);
      setSummary(sum);
      setModels(mdls);
      setChampion(champ);
      setDriftRecords(driftRecs);
      setDriftSummary(driftSum);
      setAdversarialEvents(advEvts);
      setAdversarialSummary(advSum);
    } catch (e) {
      console.error('Phase 48 ML Platform load error:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleSimulate = async () => {
    setSimLoading(true);
    setSimResult(null);
    try {
      const res = await mlModelPlatformApi.simulateAdversarialDefense({
        model_id: simModelId,
        attack_type: simAttackType,
        attack_payload: {
          technique: simAttackType === 'EVASION' ? 'feature_gradient_perturbation' : 'oracle_query_extraction',
          perturbation_epsilon: 0.045,
          timestamp: new Date().toISOString()
        }
      });
      setSimResult(res);
      // Reload events
      const updatedEvts = await mlModelPlatformApi.listAdversarialEvents();
      setAdversarialEvents(updatedEvts);
    } catch (e) {
      console.error('Simulation error:', e);
    } finally {
      setSimLoading(false);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Platform Overview', icon: Brain },
    { id: 'registry', label: 'Model Registry', icon: Server },
    { id: 'drift', label: 'Drift Monitoring', icon: Activity },
    { id: 'adversarial', label: 'Adversarial Defenses', icon: ShieldAlert },
    { id: 'lineage', label: 'Lineage & Governance', icon: GitBranch },
    { id: 'simulator', label: 'Defense Simulator', icon: Zap },
  ] as const;

  const metricCard = (icon: React.ReactNode, label: string, value: string, sub: string, color: string) => (
    <div className={`rounded-2xl border p-5 bg-slate-900/60 border-slate-700/50 backdrop-blur-sm hover:border-${color}-500/40 transition-all`}>
      <div className="flex items-center gap-3 mb-3">
        <span className={`p-2.5 rounded-xl bg-${color}-500/10 text-${color}-400`}>{icon}</span>
        <span className="text-xs text-slate-400 font-medium">{label}</span>
      </div>
      <div className={`text-2xl font-black text-${color}-300 mb-1`}>{value}</div>
      <div className="text-xs text-slate-500">{sub}</div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center animate-pulse">
            <Brain className="w-7 h-7 text-white" />
          </div>
          <p className="text-slate-400 text-sm font-medium">Initializing Global AI/ML Model Platform...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-screen-xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Global AI/ML Model Platform</h1>
            <p className="text-slate-400 text-sm">Phase 48 · Enterprise Model Registry, Drift Telemetry & Adversarial Shields</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadAll}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-all border border-slate-700"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh
          </button>
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-sm font-bold">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <span>Platform Score: {summary?.platform_intelligence_score ?? 98.4}/100</span>
          </div>
        </div>
      </div>

      {/* Tier Badge */}
      <div className="rounded-2xl border border-indigo-500/20 bg-gradient-to-r from-indigo-950/40 via-slate-900/40 to-cyan-950/40 p-4 flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <span className="px-3 py-1 rounded-lg bg-indigo-500/20 text-indigo-300 text-xs font-bold border border-indigo-500/30">
            {summary?.platform_tier ?? 'GLOBAL_AUTONOMOUS_AI_PLATFORM'}
          </span>
          <span className="text-slate-300 text-sm">
            Champion: <span className="text-cyan-300 font-bold">{summary?.champion_model ?? 'CatBoost-ThreatClassifier@v3.2.1'}</span>
            &nbsp;·&nbsp; ROC-AUC: <span className="text-emerald-400 font-bold">{summary?.champion_roc_auc ?? 0.9994}</span>
            &nbsp;·&nbsp; P99 Latency: <span className="text-violet-300 font-bold">{summary?.champion_inference_p99_ms ?? 3.2}ms</span>
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="flex items-center gap-1 px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
            <Check className="w-3 h-3" /> Drift Watch: Active
          </span>
          <span className="flex items-center gap-1 px-2.5 py-1 rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-medium">
            <Shield className="w-3 h-3" /> Adversarial Shield: Active
          </span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-1 bg-slate-900/60 border border-slate-700/50 rounded-2xl p-1.5 overflow-x-auto">
        {tabs.map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium whitespace-nowrap transition-all ${
                activeTab === tab.id
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* ── OVERVIEW ─────────────────────────────────────────────────────── */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {metricCard(<Server className="w-5 h-5" />, 'Models Registered', `${summary?.total_models_registered ?? 5}`, 'Versioned artifacts', 'indigo')}
            {metricCard(<Zap className="w-5 h-5" />, 'Champion Accuracy', `${((summary?.champion_accuracy ?? 0.9971) * 100).toFixed(2)}%`, 'CatBoost production model', 'emerald')}
            {metricCard(<Activity className="w-5 h-5" />, 'Drift Monitored', `${summary?.models_under_drift_watch ?? 5} Models`, 'PSI & KS-Test real-time', 'cyan')}
            {metricCard(<ShieldAlert className="w-5 h-5" />, 'Attacks Blocked (30d)', `${summary?.adversarial_attacks_blocked_30d ?? 312}`, '100% block rate', 'rose')}
          </div>

          {/* Champion Model Deep Dive Card */}
          {champion && (
            <div className="rounded-2xl border border-cyan-500/30 bg-gradient-to-br from-slate-900/90 via-indigo-950/30 to-cyan-950/20 p-6">
              <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
                    <Sparkles className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="text-lg font-bold text-white">{champion.model_name}</h2>
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                        {champion.model_version}
                      </span>
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                        CHAMPION
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-0.5">Framework: {champion.framework.toUpperCase()} · Family: {champion.model_family}</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-black text-cyan-300">{(champion.accuracy * 100).toFixed(2)}%</div>
                  <div className="text-xs text-slate-400">Validation Accuracy</div>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-4">
                {[
                  ['F1-Score', `${(champion.f1_score * 100).toFixed(2)}%`, 'text-indigo-400'],
                  ['Precision', `${(champion.precision_score * 100).toFixed(2)}%`, 'text-emerald-400'],
                  ['Recall', `${(champion.recall_score * 100).toFixed(2)}%`, 'text-cyan-400'],
                  ['ROC-AUC', `${champion.roc_auc.toFixed(4)}`, 'text-purple-400'],
                  ['P99 Latency', `${champion.inference_p99_ms} ms`, 'text-amber-400'],
                ].map(([label, val, cls]) => (
                  <div key={label} className="bg-slate-800/60 rounded-xl p-3 border border-slate-700/40">
                    <div className="text-xs text-slate-400 mb-1">{label}</div>
                    <div className={`text-base font-bold ${cls}`}>{val}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Dual Column Status Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Drift Health Summary */}
            <div className="rounded-2xl border border-slate-700/50 bg-slate-900/60 p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Activity className="w-4 h-4 text-cyan-400" /> Drift Monitoring Status
                </h3>
                <span className="text-xs text-emerald-400 font-bold">Score: {driftSummary?.drift_monitoring_score ?? 96.2}%</span>
              </div>
              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="bg-slate-800/40 p-3 rounded-xl border border-slate-700/30">
                  <div className="text-lg font-bold text-emerald-400">{driftSummary?.models_with_no_drift ?? 3}</div>
                  <div className="text-xs text-slate-400">Zero Drift</div>
                </div>
                <div className="bg-slate-800/40 p-3 rounded-xl border border-slate-700/30">
                  <div className="text-lg font-bold text-amber-400">{driftSummary?.models_with_low_drift ?? 1}</div>
                  <div className="text-xs text-slate-400">Low Drift</div>
                </div>
                <div className="bg-slate-800/40 p-3 rounded-xl border border-slate-700/30">
                  <div className="text-lg font-bold text-rose-400">{driftSummary?.models_with_medium_drift ?? 1}</div>
                  <div className="text-xs text-slate-400">Medium Drift</div>
                </div>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Statistical thresholds: Alert at PSI &gt; 0.05 · Trigger auto-retraining pipeline at PSI &gt; 0.07. 1 model currently queued for automated retraining.
              </p>
            </div>

            {/* Adversarial Defense Posture */}
            <div className="rounded-2xl border border-slate-700/50 bg-slate-900/60 p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-rose-400" /> Adversarial Shield Posture
                </h3>
                <span className="text-xs text-emerald-400 font-bold">100% Neutralization</span>
              </div>
              <div className="space-y-2">
                {adversarialSummary?.defense_mechanisms_active?.slice(0, 3).map((mech: string, i: number) => (
                  <div key={i} className="flex items-center justify-between p-2.5 rounded-xl bg-slate-800/40 border border-slate-700/30 text-xs">
                    <span className="text-slate-300 font-mono">{mech}</span>
                    <span className="text-emerald-400 font-bold">ACTIVE</span>
                  </div>
                ))}
              </div>
              <p className="text-xs text-slate-400">Average mitigation latency: {adversarialSummary?.avg_defense_latency_ms ?? 1.2} ms</p>
            </div>
          </div>
        </div>
      )}

      {/* ── MODEL REGISTRY ───────────────────────────────────────────────── */}
      {activeTab === 'registry' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white">Registered ML Models ({models.length})</h2>
            <span className="text-xs text-slate-400">Standardized Model Metadata, Lineage & Performance Metrics</span>
          </div>

          <div className="space-y-3">
            {models.map((m: any) => (
              <div
                key={m.id}
                className="p-5 rounded-2xl border border-slate-700/50 bg-slate-900/60 hover:border-indigo-500/40 transition-all space-y-3"
              >
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                      <Cpu className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-white">{m.model_name}</span>
                        <span className="px-2 py-0.5 rounded-md text-xs font-bold bg-slate-800 text-slate-300 border border-slate-700">
                          {m.model_version}
                        </span>
                        {m.is_champion && (
                          <span className="px-2 py-0.5 rounded-md text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                            CHAMPION
                          </span>
                        )}
                        <span className={`px-2 py-0.5 rounded-md text-xs font-bold ${m.status === 'ACTIVE' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' : 'bg-slate-700/40 text-slate-400'}`}>
                          {m.status}
                        </span>
                      </div>
                      <div className="text-xs text-slate-400 mt-1">
                        Framework: <span className="text-slate-300 font-medium">{m.framework}</span> · Family: <span className="text-slate-300 font-medium">{m.model_family}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-xs">
                    <div className="text-right">
                      <div className="text-slate-400">Accuracy</div>
                      <div className="text-sm font-bold text-emerald-400">{m.accuracy ? `${(m.accuracy * 100).toFixed(2)}%` : '—'}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-slate-400">ROC-AUC</div>
                      <div className="text-sm font-bold text-cyan-400">{m.roc_auc ? m.roc_auc.toFixed(4) : '—'}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-slate-400">P99 Latency</div>
                      <div className="text-sm font-bold text-indigo-400">{m.inference_p99_ms ? `${m.inference_p99_ms}ms` : '—'}</div>
                    </div>
                  </div>
                </div>

                {m.tags && m.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-2 border-t border-slate-800">
                    {m.tags.map((t: string) => (
                      <span key={t} className="text-xs px-2 py-0.5 rounded-md bg-slate-800 text-slate-400 border border-slate-700/50">
                        #{t}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── DRIFT MONITORING ─────────────────────────────────────────────── */}
      {activeTab === 'drift' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white">Model Drift Telemetry ({driftRecords.length})</h2>
            <span className="text-xs text-slate-400">Population Stability Index (PSI) & Kolmogorov-Smirnov (KS) Statistical Tests</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {driftRecords.map((r: any) => (
              <div
                key={r.id}
                className="p-5 rounded-2xl border border-slate-700/50 bg-slate-900/60 hover:border-cyan-500/40 transition-all space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-white">{r.model_name}</h3>
                    <span className="text-xs text-slate-400">{r.model_version} · Method: {r.drift_method}</span>
                  </div>
                  <span className={`px-2.5 py-1 rounded-lg text-xs font-bold border ${
                    r.drift_severity === 'NONE'
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      : r.drift_severity === 'LOW'
                      ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                      : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                  }`}>
                    {r.drift_severity} DRIFT
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-2 pt-2">
                  <div className="bg-slate-800/40 p-2.5 rounded-xl border border-slate-700/30 text-center">
                    <div className="text-xs text-slate-400">Data Drift</div>
                    <div className="text-sm font-bold text-cyan-300">{r.data_drift_score}</div>
                  </div>
                  <div className="bg-slate-800/40 p-2.5 rounded-xl border border-slate-700/30 text-center">
                    <div className="text-xs text-slate-400">Concept Drift</div>
                    <div className="text-sm font-bold text-indigo-300">{r.concept_drift_score}</div>
                  </div>
                  <div className="bg-slate-800/40 p-2.5 rounded-xl border border-slate-700/30 text-center">
                    <div className="text-xs text-slate-400">Pred Drift</div>
                    <div className="text-sm font-bold text-purple-300">{r.prediction_drift_score}</div>
                  </div>
                </div>

                {r.feature_drift_breakdown && (
                  <div className="pt-2 border-t border-slate-800">
                    <div className="text-xs text-slate-400 mb-1.5 font-medium">Top Feature Drift Contributors:</div>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(r.feature_drift_breakdown).map(([feat, score]) => (
                        <span key={feat} className="text-xs px-2 py-1 rounded-md bg-slate-800/80 text-slate-300 border border-slate-700 font-mono">
                          {feat}: <span className="text-cyan-400 font-bold">{(score as number).toFixed(3)}</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between text-xs pt-1">
                  <span className="text-slate-500">Alert: {r.alert_triggered ? '🚨 Triggered' : '✅ Nominal'}</span>
                  <span className="text-slate-500">Auto-Retrain: {r.auto_retrain_triggered ? '⚡ Triggered' : 'Inactive'}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── ADVERSARIAL DEFENSES ─────────────────────────────────────────── */}
      {activeTab === 'adversarial' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white">Adversarial Attack & Defense Events ({adversarialEvents.length})</h2>
            <span className="text-xs text-slate-400">Real-time Model Hardening, Evasion Defense & Query Rate Limiting</span>
          </div>

          <div className="space-y-3">
            {adversarialEvents.map((e: any) => (
              <div
                key={e.id}
                className="p-4 rounded-2xl border border-slate-700/50 bg-slate-900/60 hover:border-rose-500/30 transition-all space-y-2"
              >
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
                      <ShieldAlert className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-white">{e.attack_type} Attack</span>
                        <span className="px-2 py-0.5 rounded-md text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
                          {e.attack_severity}
                        </span>
                        <span className="px-2 py-0.5 rounded-md text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                          BLOCKED
                        </span>
                      </div>
                      <div className="text-xs text-slate-400 mt-0.5">Target: <span className="text-slate-300">{e.model_name}</span></div>
                    </div>
                  </div>
                  <div className="text-right text-xs">
                    <div className="text-slate-400">Confidence: <span className="text-rose-400 font-bold">{((e.confidence_score ?? 0.95) * 100).toFixed(0)}%</span></div>
                    <div className="text-slate-400">Latency: <span className="text-cyan-400 font-bold">{e.defense_latency_ms ?? 1.2}ms</span></div>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-800/80 text-slate-400">
                  <span>Defense Mechanism: <span className="text-indigo-300 font-mono font-medium">{e.defense_mechanism}</span></span>
                  <span>{e.detected_at ? new Date(e.detected_at).toLocaleString() : 'Just now'}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── LINEAGE & GOVERNANCE ─────────────────────────────────────────── */}
      {activeTab === 'lineage' && (
        <div className="space-y-4">
          <div className="rounded-2xl border border-slate-700/50 bg-slate-900/60 p-6 space-y-6">
            <div>
              <h2 className="text-base font-bold text-white mb-1">Model Lineage & Provenance Graph</h2>
              <p className="text-xs text-slate-400">Immutable audit trails from raw telemetry datasets to trained weights and containerized endpoints</p>
            </div>

            <div className="space-y-4">
              {[
                { stage: '1. Ingestion & Feature Store', desc: 'Real-time telemetry stream normalized into 128 cybersecurity feature vectors (Feast & Redis).', status: 'SYNCHRONIZED' },
                { stage: '2. Continuous Retraining Pipeline', desc: 'Airflow/Prefect orchestrates weekly automated fine-tuning against verified threat labels.', status: 'HEALTHY' },
                { stage: '3. Pre-Deployment Validation', desc: 'Rigorous benchmark validation against 100K synthetic adversarial samples and drift benchmarks.', status: 'PASSED' },
                { stage: '4. Production Serving & Hardening', desc: 'Triton inference server with sub-4ms P99 latency and differential privacy defense filters.', status: 'SERVING' },
              ].map((item, idx) => (
                <div key={idx} className="flex items-start gap-4 p-4 rounded-xl bg-slate-800/40 border border-slate-700/40">
                  <div className="w-8 h-8 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-sm shrink-0">
                    {idx + 1}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-bold text-white">{item.stage}</h4>
                      <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">
                        {item.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── ADVERSARIAL DEFENSE SIMULATOR ────────────────────────────────── */}
      {activeTab === 'simulator' && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-indigo-500/30 bg-gradient-to-br from-slate-900/90 via-indigo-950/20 to-purple-950/20 p-6 space-y-6">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Zap className="w-5 h-5 text-indigo-400" /> Adversarial Attack Defense Simulator
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Trigger simulated adversarial attack vectors (Evasion, Model Extraction, Poisoning) against production models to test active defense layers.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-slate-400 font-medium mb-1.5">Target Production Model</label>
                <select
                  value={simModelId}
                  onChange={(e) => setSimModelId(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="cat-001">CatBoost-ThreatClassifier (Champion)</option>
                  <option value="xgb-001">XGBoost-AnomalyDetector (Shadow)</option>
                  <option value="trans-001">Transformer-NLP-PhishingDetector</option>
                  <option value="gnn-001">PyTorch-GNN-LateralMovement</option>
                  <option value="iso-001">IsolationForest-ExfiltrationDetector</option>
                </select>
              </div>

              <div>
                <label className="block text-xs text-slate-400 font-medium mb-1.5">Adversarial Vector Type</label>
                <select
                  value={simAttackType}
                  onChange={(e) => setSimAttackType(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="EVASION">Evasion (Feature Gradient Perturbation)</option>
                  <option value="MODEL_EXTRACTION">Model Extraction (High-Volume Oracle Probing)</option>
                  <option value="MEMBERSHIP_INFERENCE">Membership Inference (Privacy Extraction)</option>
                  <option value="POISONING">Poisoning (Synthetic Label Injection)</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleSimulate}
              disabled={simLoading}
              className="flex items-center justify-center gap-2 w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-sm shadow-lg shadow-indigo-500/25 transition-all disabled:opacity-50"
            >
              {simLoading ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              {simLoading ? 'Simulating Adversarial Attack...' : 'Execute Defense Simulation'}
            </button>

            {simResult && (
              <div className="p-5 rounded-2xl border border-emerald-500/30 bg-emerald-950/20 space-y-3 animate-fade-in">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
                    <CheckCircle2 className="w-5 h-5" />
                    <span>SIMULATION OUTCOME: {simResult.outcome}</span>
                  </div>
                  <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono font-bold">
                    LATENCY: {simResult.defense_latency_ms}ms
                  </span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs pt-2">
                  <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
                    <div className="text-slate-400">Simulation ID</div>
                    <div className="text-slate-200 font-mono mt-0.5 truncate">{simResult.simulation_id}</div>
                  </div>
                  <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
                    <div className="text-slate-400">Attack Type</div>
                    <div className="text-slate-200 font-bold mt-0.5">{simResult.attack_type}</div>
                  </div>
                  <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
                    <div className="text-slate-400">Defense Mechanism</div>
                    <div className="text-cyan-300 font-mono mt-0.5">{simResult.defense_mechanism}</div>
                  </div>
                  <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
                    <div className="text-slate-400">Detection Confidence</div>
                    <div className="text-emerald-400 font-bold mt-0.5">{(simResult.confidence_score * 100).toFixed(0)}%</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
