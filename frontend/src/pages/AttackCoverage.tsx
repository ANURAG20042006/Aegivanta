import React, { useState, useEffect } from 'react';
import { Target, RefreshCw, Shield, CheckCircle2, Eye, Layers } from 'lucide-react';
import { socMetricsService, AttackCoverageData } from '../services/socMetricsService';

export const AttackCoverage: React.FC = () => {
  const [coverage, setCoverage] = useState<AttackCoverageData | null>(null);
  const [recomputing, setRecomputing] = useState<boolean>(false);

  useEffect(() => {
    loadCoverage();
  }, []);

  const loadCoverage = async () => {
    try {
      const data = await socMetricsService.getAttackCoverage();
      setCoverage(data);
    } catch (err) {
      console.error('Failed to load ATT&CK coverage', err);
    }
  };

  const handleRecompute = async () => {
    setRecomputing(true);
    try {
      await socMetricsService.recomputeCoverage();
      await loadCoverage();
    } catch (err) {
      console.error('Failed to recompute ATT&CK coverage', err);
    } finally {
      setRecomputing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center bg-slate-900/40 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-indigo-500/10 rounded-lg text-indigo-400 border border-indigo-500/20">
              <Target className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-wide">MITRE ATT&CK Detection Matrix</h1>
          </div>
          <p className="text-slate-400 text-sm">
            Empirical visibility matrix mapping observed adversarial tactics against active ML and rule-based detectors.
          </p>
        </div>

        <button
          onClick={handleRecompute}
          disabled={recomputing}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-sm font-medium border border-slate-700 transition disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 text-indigo-400 ${recomputing ? 'animate-spin' : ''}`} />
          {recomputing ? 'Recomputing...' : 'Refresh Matrix'}
        </button>
      </div>

      {/* High-Level Metric Tiles */}
      {coverage && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-slate-900/40 p-5 rounded-2xl border border-slate-800 space-y-2">
            <div className="text-xs text-slate-400 font-semibold uppercase flex items-center gap-1.5">
              <Shield className="w-4 h-4 text-indigo-400" />
              Coverage Percentage
            </div>
            <div className="text-3xl font-bold text-indigo-300">{coverage.coverage_percentage}%</div>
            <div className="text-xs text-slate-500">Across monitored enterprise matrix</div>
          </div>

          <div className="bg-slate-900/40 p-5 rounded-2xl border border-slate-800 space-y-2">
            <div className="text-xs text-slate-400 font-semibold uppercase flex items-center gap-1.5">
              <Eye className="w-4 h-4 text-emerald-400" />
              Observed Stages
            </div>
            <div className="text-3xl font-bold text-white">{coverage.observed_techniques_count}</div>
            <div className="text-xs text-slate-500">Active attack tactics observed</div>
          </div>

          <div className="bg-slate-900/40 p-5 rounded-2xl border border-slate-800 space-y-2">
            <div className="text-xs text-slate-400 font-semibold uppercase flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-purple-400" />
              Covered Techniques
            </div>
            <div className="text-3xl font-bold text-purple-300">{coverage.detected_techniques_count}</div>
            <div className="text-xs text-slate-500">Supported by ML & IOC rules</div>
          </div>

          <div className="bg-slate-900/40 p-5 rounded-2xl border border-slate-800 space-y-2">
            <div className="text-xs text-slate-400 font-semibold uppercase flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-amber-400" />
              Total Matrix Scope
            </div>
            <div className="text-3xl font-bold text-white">{coverage.total_matrix_techniques}</div>
            <div className="text-xs text-slate-500">Enterprise attack techniques</div>
          </div>
        </div>
      )}

      {/* MITRE Tactic Heatmap Matrix */}
      <div className="bg-slate-900/40 p-6 rounded-2xl border border-slate-800 space-y-6">
        <h2 className="text-base font-bold text-white uppercase tracking-wider">
          Enterprise Matrix Tactic Coverage Breakdown
        </h2>

        {coverage?.tactic_breakdown ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {Object.entries(coverage.tactic_breakdown).map(([tactic, data]: [string, any]) => (
              <div
                key={tactic}
                className={`p-4 rounded-xl border transition ${
                  data.is_active_observation
                    ? 'bg-indigo-950/20 border-indigo-500/40 ring-1 ring-indigo-500/30'
                    : 'bg-slate-800/30 border-slate-800 opacity-60'
                }`}
              >
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold text-sm text-slate-200">{tactic}</span>
                  {data.is_active_observation && (
                    <span className="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 text-[10px] font-bold">
                      ACTIVE
                    </span>
                  )}
                </div>

                <div className="text-xs text-slate-400 space-y-1 mt-3 pt-2 border-t border-slate-800">
                  <div className="flex justify-between">
                    <span>Coverage:</span>
                    <span className="font-semibold text-slate-200">{data.coverage_pct}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Techniques:</span>
                    <span>{data.detected_count} / {data.total_techniques}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-500 text-center py-10">Loading matrix heatmap...</p>
        )}
      </div>
    </div>
  );
};
