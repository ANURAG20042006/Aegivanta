import React, { useEffect, useState } from 'react';
import {
  TrendingDown,
  ShieldCheck,
  Activity,
  ShieldAlert,
  Server,
  Lock,
  PlusCircle
} from 'lucide-react';

import { saasApi } from '../services/saas';

export const SecurityValue: React.FC = () => {
  const [valueData, setValueData] = useState<any>(null);
  const [improvements, setImprovements] = useState<any>(null);
  const [lookbackDays, setLookbackDays] = useState<number>(30);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchValueData();
  }, [lookbackDays]);

  const fetchValueData = async () => {
    try {
      setLoading(true);
      const [vMetrics, pImprov] = await Promise.all([
        saasApi.getSecurityValue(lookbackDays),
        saasApi.getPostureImprovements()
      ]);
      setValueData(vMetrics);
      setImprovements(pImprov);
    } catch (err) {
      console.error('Failed to load security value metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <ShieldCheck className="h-7 w-7 text-emerald-400" />
            Customer Security Value & ROI Center
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Quantifiable threat mitigation metrics, operational risk reduction, and actionable posture improvements.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-slate-900/80 p-1.5 rounded-lg border border-slate-800">
          {[7, 30, 90].map((days) => (
            <button
              key={days}
              onClick={() => setLookbackDays(days)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
                lookbackDays === days
                  ? 'bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/20'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {days} Days
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Activity className="h-8 w-8 animate-spin text-emerald-400 mr-3" />
          Calculating cybersecurity value & ROI...
        </div>
      ) : (
        <>
          {/* Top ROI Highlights */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium uppercase tracking-wider text-slate-400">Threats Blocked</span>
                <ShieldCheck className="h-5 w-5 text-emerald-400" />
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-3xl font-bold text-slate-100">{valueData?.threats_blocked || 0}</span>
                <span className="text-xs font-medium text-emerald-400">Autonomous SOAR</span>
              </div>
              <p className="text-xs text-slate-500 mt-2">Attacks stopped before perimeter penetration</p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium uppercase tracking-wider text-slate-400">Risk Reduction</span>
                <TrendingDown className="h-5 w-5 text-cyan-400" />
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-3xl font-bold text-slate-100">-{valueData?.risk_reduction_percentage || 0}%</span>
                <span className="text-xs font-medium text-cyan-400">Enterprise Risk</span>
              </div>
              <p className="text-xs text-slate-500 mt-2">Overall exposure reduction from automated containment</p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium uppercase tracking-wider text-slate-400">Threats Detected</span>
                <ShieldAlert className="h-5 w-5 text-amber-400" />
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-3xl font-bold text-slate-100">{valueData?.threats_detected || 0}</span>
                <span className="text-xs font-medium text-slate-400">Total Incidents</span>
              </div>
              <p className="text-xs text-slate-500 mt-2">{valueData?.critical_incidents || 0} critical incidents triaged</p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium uppercase tracking-wider text-slate-400">Monitored Fleet</span>
                <Server className="h-5 w-5 text-indigo-400" />
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-3xl font-bold text-slate-100">{valueData?.sensors_healthy || 0}/{valueData?.total_sensors || 0}</span>
                <span className="text-xs font-medium text-emerald-400">Healthy</span>
              </div>
              <p className="text-xs text-slate-500 mt-2">Distributed endpoint & network sensor coverage</p>
            </div>
          </div>

          {/* Security Posture Improvement Recommendations */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                <Lock className="h-5 w-5 text-emerald-400" />
                Security Posture Score
              </h2>
              <div className="p-6 bg-slate-950/60 rounded-xl border border-slate-800 text-center space-y-2">
                <div className="text-5xl font-extrabold text-emerald-400">{improvements?.current_score || 82}</div>
                <div className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Current Readiness Score</div>
                <div className="text-xs text-cyan-400 pt-2 font-medium">
                  Potential to reach <strong>{improvements?.potential_score || 92}</strong> (+{improvements?.score_delta_available || 10} pts)
                </div>
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 lg:col-span-2 space-y-4">
              <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                <PlusCircle className="h-5 w-5 text-cyan-400" />
                Explainable Posture Improvement Recommendations
              </h2>
              <div className="space-y-3">
                {(improvements?.recommendations || []).map((rec: any) => (
                  <div
                    key={rec.id}
                    className="p-4 bg-slate-950/40 rounded-xl border border-slate-800/80 hover:border-slate-700 transition-all flex items-center justify-between gap-4"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                          {rec.category}
                        </span>
                        <h4 className="text-sm font-bold text-slate-200">{rec.title}</h4>
                      </div>
                      <p className="text-xs text-slate-400">{rec.description}</p>
                    </div>

                    <div className="text-right whitespace-nowrap">
                      <span className="inline-flex items-center gap-1 text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">
                        +{rec.estimated_impact_points} Score Pts
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
