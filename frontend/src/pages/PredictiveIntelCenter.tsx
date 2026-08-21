import React, { useEffect, useState } from 'react';
import {
  BrainCircuit,
  Activity,
  ChevronRight,
  TrendingUp,
  ShieldAlert,
  Flame,
  Globe,
  Sliders,
  Crosshair
} from 'lucide-react';
import { saasApi } from '../services/saas';

export const PredictiveIntelCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'forecasts' | 'simulations' | 'horizon_trends' | 'risk_projections' | 'forecast_generator'>('overview');
  const [summary, setSummary] = useState<any>(null);
  const [forecasts, setForecasts] = useState<any[]>([]);
  const [simulations, setSimulations] = useState<any[]>([]);
  const [indicators, setIndicators] = useState<any[]>([]);
  const [selectedHorizon, setSelectedHorizon] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  // Generator form
  const [genVectorTitle, setGenVectorTitle] = useState<string>('Shadow AI Endpoint Prompt Exfiltration');
  const [genAssetCat, setGenAssetCat] = useState<string>('Engineering Workstations & SaaS Apps');
  const [genHorizon, setGenHorizon] = useState<string>('30_DAYS');
  const [generatedForecast, setGeneratedForecast] = useState<any>(null);

  useEffect(() => {
    fetchPredictiveData();
  }, [selectedHorizon]);

  const fetchPredictiveData = async () => {
    try {
      setLoading(true);
      const [sum, fcs, sims, inds] = await Promise.all([
        saasApi.getPredictiveIntelSummary(),
        saasApi.getPredictiveForecasts(selectedHorizon || undefined),
        saasApi.getAdversarialSimulations(),
        saasApi.getThreatHorizonIndicators()
      ]);
      setSummary(sum);
      setForecasts(fcs);
      setSimulations(sims);
      setIndicators(inds);
    } catch (err) {
      console.error('Failed to load Predictive Security Intelligence data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateForecast = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await saasApi.generatePredictiveForecast({
        threat_vector_title: genVectorTitle,
        target_asset_category: genAssetCat,
        forecast_horizon: genHorizon
      });
      setGeneratedForecast(res);
      fetchPredictiveData();
    } catch (err) {
      console.error('Failed to generate predictive forecast:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <BrainCircuit className="h-7 w-7 text-cyan-400" />
            Predictive Security Intelligence & Threat Forecasting
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Machine Learning Threat Probability Horizon Modeling, Adversarial Blast Radius Simulation & Emerging Vector Anticipation.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('forecast_generator')}
            className="flex items-center gap-2 px-3.5 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-xs font-semibold transition-colors"
          >
            <BrainCircuit className="h-4 w-4" /> Synthesize Forecast
          </button>
        </div>
      </div>

      {/* Top Metrics Ribbon */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Predictive Posture</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{summary.overall_predictive_posture_score}<span className="text-xs text-slate-500">/100</span></div>
            <div className="text-[10px] text-cyan-400 mt-0.5">Adaptive Defense</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Active Forecasts</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{summary.active_threat_forecasts_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">30/60/90-Day Vector</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Adversarial Sims</div>
            <div className="text-2xl font-bold text-rose-400 mt-1">{summary.adversarial_simulations_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Escalation Trees</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Horizon Indicators</div>
            <div className="text-2xl font-bold text-amber-400 mt-1">{summary.global_horizon_indicators_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Global Trends</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Mean Probability</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{Math.round(summary.average_forecast_probability_score * 100)}%</div>
            <div className="text-[10px] text-cyan-400 mt-0.5">Confidence: 92%</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Avg Blast Radius</div>
            <div className="text-2xl font-bold text-slate-200 mt-1">{summary.average_blast_radius_nodes}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Nodes at Risk</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'Predictive Intelligence Overview', icon: BrainCircuit },
          { id: 'forecasts', label: 'Threat Forecasts (30/60/90d)', icon: TrendingUp },
          { id: 'simulations', label: 'Adversarial Blast Radius Sims', icon: ShieldAlert },
          { id: 'horizon_trends', label: 'Global Threat Horizon', icon: Globe },
          { id: 'risk_projections', label: 'Probabilistic Projections', icon: Crosshair },
          { id: 'forecast_generator', label: 'Forecast Synthesizer', icon: Sliders }
        ].map(tab => {
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
              <Icon className="h-4 w-4" />{tab.label}
            </button>
          );
        })}
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Activity className="h-6 w-6 animate-spin text-cyan-400 mr-3" />
          Synthesizing Emerging Threat Vectors & Predictive Horizons...
        </div>
      ) : (
        <>
          {/* TAB 1: Overview */}
          {activeTab === 'overview' && summary && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Emerging Threat Forecasts */}
              <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-cyan-400" /> High-Probability Threat Vector Projections
                </h3>
                <div className="space-y-3">
                  {forecasts.map((fc) => (
                    <div key={fc.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                      <div className="flex justify-between items-center font-bold">
                        <div className="flex items-center gap-2">
                          <span className="text-slate-100 text-sm">{fc.threat_vector_title}</span>
                          <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 text-[10px]">Horizon: {fc.forecast_horizon.replace('_', ' ')}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${fc.predicted_impact_severity === 'CRITICAL' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30' : 'bg-amber-500/10 text-amber-400'}`}>
                            {fc.predicted_impact_severity}
                          </span>
                          <span className="text-cyan-300 font-mono font-bold">{Math.round(fc.probability_score * 100)}% Prob</span>
                        </div>
                      </div>
                      <div className="text-slate-400 text-[11px]">
                        Target Asset: <strong className="text-slate-200">{fc.target_asset_category}</strong>
                      </div>
                      <div className="text-slate-300 text-[11px] leading-relaxed">
                        <strong className="text-cyan-400">Evidence & Model Rationale: </strong>{fc.evidence_features_summary}
                      </div>
                      <div className="flex justify-between items-center text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">
                        <span>Confidence: <strong className="text-emerald-400">{Math.round(fc.confidence_score * 100)}%</strong></span>
                        <span>Model: {fc.model_version}</span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-3 border-t border-slate-800/60">
                  <div className="text-xs font-bold text-slate-300 mb-2">Priority Predictive Actions:</div>
                  <div className="space-y-1.5">
                    {summary.top_predictive_priorities.map((pri: string, idx: number) => (
                      <div key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                        <ChevronRight className="h-3.5 w-3.5 text-cyan-400 shrink-0 mt-0.5" />
                        {pri}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Global Threat Horizon */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Globe className="h-4 w-4 text-cyan-400" /> Global Threat Horizon Surges
                </h3>
                <div className="space-y-3">
                  {indicators.map((ind) => (
                    <div key={ind.id} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60 text-xs space-y-1.5">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span>{ind.indicator_name}</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${ind.trajectory_trend === 'SURGING' ? 'bg-rose-500/10 text-rose-400' : 'bg-slate-800 text-slate-300'}`}>
                          {ind.trajectory_trend}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-400">Category: {ind.category}</div>
                      <div className="text-[10px] text-cyan-300 font-mono">Observed Sightings: {ind.observed_global_sightings.toLocaleString()}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Forecasts */}
          {activeTab === 'forecasts' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-cyan-400" /> Emerging Threat Forecast Registry
                </h3>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400">Filter Horizon:</span>
                  <select
                    value={selectedHorizon}
                    onChange={(e) => setSelectedHorizon(e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-lg p-1.5 text-xs text-slate-200"
                  >
                    <option value="">All Horizons</option>
                    <option value="30_DAYS">30 Days</option>
                    <option value="60_DAYS">60 Days</option>
                    <option value="90_DAYS">90 Days</option>
                  </select>
                </div>
              </div>

              <div className="space-y-3">
                {forecasts.map((f) => (
                  <div key={f.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <span className="text-slate-100 text-base">{f.threat_vector_title}</span>
                      <div className="flex items-center gap-2">
                        <span className="px-2.5 py-0.5 rounded bg-cyan-500/10 text-cyan-300 text-[10px] font-bold">Probability: {Math.round(f.probability_score * 100)}%</span>
                        <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${f.predicted_impact_severity === 'CRITICAL' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30' : 'bg-amber-500/10 text-amber-400'}`}>
                          {f.predicted_impact_severity}
                        </span>
                      </div>
                    </div>

                    <div className="text-slate-300 text-[11px] leading-relaxed">
                      <strong className="text-cyan-400">Rationale: </strong>{f.evidence_features_summary}
                    </div>

                    <div className="flex justify-between items-center text-[10px] text-slate-400 pt-1">
                      <span>Target Category: <strong className="text-slate-200">{f.target_asset_category}</strong> · Horizon: <strong className="text-cyan-300">{f.forecast_horizon.replace('_', ' ')}</strong></span>
                      <span>Model Version: {f.model_version}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: Simulations */}
          {activeTab === 'simulations' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <ShieldAlert className="h-4 w-4 text-rose-400" /> Adversarial Attack Vector Simulations & Blast Radius Analysis
              </h3>

              <div className="space-y-4">
                {simulations.map((s) => (
                  <div key={s.id} className="p-5 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-3">
                    <div className="flex justify-between items-center font-bold">
                      <div className="flex items-center gap-2">
                        <Flame className="h-4 w-4 text-rose-400" />
                        <span className="text-slate-100 text-base">{s.threat_scenario_title}</span>
                      </div>
                      <span className="px-3 py-1 rounded-full bg-rose-500/10 text-rose-400 font-mono text-[11px] font-bold border border-rose-500/30">
                        Blast Radius: {s.estimated_blast_radius_nodes} Nodes
                      </span>
                    </div>

                    <div className="p-3 bg-slate-900 rounded-lg text-[11px] space-y-1">
                      <div className="text-slate-400 font-semibold">Initial Access Vector: <span className="text-cyan-300 font-normal">{s.initial_access_vector}</span></div>
                      <div className="text-slate-300 font-mono text-[10px] mt-1 pt-1 border-t border-slate-800">{s.predicted_escalation_pathway}</div>
                    </div>

                    <div className="p-3 bg-emerald-950/20 border border-emerald-500/20 rounded-lg text-[11px] text-emerald-300">
                      <strong>Prescribed Pre-emptive Mitigation: </strong>{s.mitigation_directive}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: Horizon Trends */}
          {activeTab === 'horizon_trends' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Globe className="h-4 w-4 text-cyan-400" /> Global Threat Trajectory Indicators
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {indicators.map((ind) => (
                  <div key={ind.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <span className="text-slate-100">{ind.indicator_name}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${ind.trajectory_trend === 'SURGING' ? 'bg-rose-500/10 text-rose-400' : 'bg-slate-800 text-slate-300'}`}>
                        {ind.trajectory_trend}
                      </span>
                    </div>
                    <div className="text-slate-400 text-[11px]">Threat Category: {ind.category}</div>
                    <div className="text-2xl font-bold text-cyan-400 font-mono">{ind.observed_global_sightings.toLocaleString()}</div>
                    <div className="text-[10px] text-slate-500">Observed in Global Telemetry</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: Risk Projections */}
          {activeTab === 'risk_projections' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Crosshair className="h-4 w-4 text-cyan-400" /> Probabilistic Risk Projection Models
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 space-y-2">
                  <div className="font-bold text-slate-200 text-sm">30-Day Exposure Horizon</div>
                  <div className="text-slate-400 text-[11px] leading-relaxed">
                    Forecast model estimates a <strong>89% probability</strong> of automated dependency confusion / typosquatting campaigns targeting Python CI/CD runners based on upstream PyPI threat intelligence velocity.
                  </div>
                  <div className="p-2 bg-slate-900 rounded font-mono text-[10px] text-cyan-300">
                    Confidence Interval: [0.82 - 0.96] · EPSS Percentile: 94.2%
                  </div>
                </div>

                <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 space-y-2">
                  <div className="font-bold text-slate-200 text-sm">60 to 90-Day Attack Path Forecast</div>
                  <div className="text-slate-400 text-[11px] leading-relaxed">
                    Long-term projection models anticipate increased credential dumping against dormant cloud IAM keys across developer machines, with an average blast radius of <strong>15 workloads</strong>.
                  </div>
                  <div className="p-2 bg-slate-900 rounded font-mono text-[10px] text-cyan-300">
                    Confidence Interval: [0.75 - 0.91] · Blast Mitigation: ZTNA L4/L7 Active
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 6: Forecast Generator */}
          {activeTab === 'forecast_generator' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 max-w-2xl mx-auto space-y-4">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Sliders className="h-5 w-5 text-cyan-400" /> Threat Vector Forecast Synthesizer
              </h3>
              <p className="text-xs text-slate-400">
                Execute predictive ML models to compute hypothetical attack probability and horizon exposure for emerging vectors.
              </p>

              <form onSubmit={handleGenerateForecast} className="space-y-3 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Threat Vector Scenario Title</label>
                  <input
                    type="text"
                    value={genVectorTitle}
                    onChange={(e) => setGenVectorTitle(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-slate-400 mb-1">Target Asset Category</label>
                    <input
                      type="text"
                      value={genAssetCat}
                      onChange={(e) => setGenAssetCat(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1">Forecast Horizon</label>
                    <select
                      value={genHorizon}
                      onChange={(e) => setGenHorizon(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                    >
                      <option value="30_DAYS">30 Days</option>
                      <option value="60_DAYS">60 Days</option>
                      <option value="90_DAYS">90 Days</option>
                    </select>
                  </div>
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl font-semibold"
                  >
                    Synthesize Predictive Vector
                  </button>
                </div>
              </form>

              {generatedForecast && (
                <div className="p-4 bg-slate-950 rounded-xl border border-cyan-500/30 text-xs space-y-2 mt-4">
                  <div className="flex justify-between items-center text-cyan-400 font-bold">
                    <span>Forecast Synthesized</span>
                    <span>Probability: {Math.round(generatedForecast.probability_score * 100)}%</span>
                  </div>
                  <div className="text-slate-200 font-semibold">{generatedForecast.threat_vector_title}</div>
                  <div className="text-[10px] text-slate-400">Severity: <strong className="text-amber-400">{generatedForecast.predicted_impact_severity}</strong> · Horizon: <strong className="text-cyan-300">{generatedForecast.forecast_horizon}</strong></div>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};
