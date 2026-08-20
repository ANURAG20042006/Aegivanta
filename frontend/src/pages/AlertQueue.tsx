import React, { useEffect, useState } from 'react';
import {
  Layers,
  ShieldAlert,
  Flame,
  CheckCircle2,
  Eye,
  Activity,
  Zap,
  Server
} from 'lucide-react';

import { saasApi } from '../services/saas';

export const AlertQueue: React.FC = () => {
  const [alertGroups, setAlertGroups] = useState<any[]>([]);
  const [selectedAlertPriority, setSelectedAlertPriority] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [modalOpen, setModalOpen] = useState<boolean>(false);

  useEffect(() => {
    fetchAlertGroups();
  }, []);

  const fetchAlertGroups = async () => {
    try {
      setLoading(true);
      const groups = await saasApi.listAlertGroups();
      setAlertGroups(groups);
    } catch (err) {
      console.error('Failed to load alert groups:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInspectPriority = async (alertId: string) => {
    try {
      const pData = await saasApi.getAlertPriority(alertId);
      setSelectedAlertPriority(pData);
      setModalOpen(true);
    } catch (err) {
      console.error('Failed to load alert priority:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Layers className="h-7 w-7 text-indigo-400" />
            Intelligent Alert Queue & Deduplication
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Correlated alert clusters grouped by attack campaign, entity topology, and explainable 0–100 priority.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchAlertGroups}
            className="flex items-center gap-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-colors"
          >
            <Activity className="h-4 w-4 text-cyan-400" /> Refresh Queue
          </button>
        </div>
      </div>

      {/* Alert Groups List */}
      {loading ? (
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Activity className="h-8 w-8 animate-spin text-indigo-400 mr-3" />
          Correlating alert groups...
        </div>
      ) : alertGroups.length === 0 ? (
        <div className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-12 text-center text-slate-400">
          <CheckCircle2 className="h-12 w-12 text-emerald-400 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-slate-200">Zero Uncorrelated Alert Backlog</h3>
          <p className="text-xs text-slate-500 mt-1">All incoming alerts are cleanly correlated into managed incidents.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {alertGroups.map((grp) => (
            <div
              key={grp.id}
              className="bg-slate-900/60 border border-slate-800/80 hover:border-indigo-500/50 rounded-xl p-5 backdrop-blur-sm transition-all"
            >
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    <span className="px-2.5 py-1 rounded-md text-xs font-mono font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                      {grp.group_code}
                    </span>
                    <h3 className="text-base font-bold text-slate-100">{grp.title}</h3>
                    <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                      {grp.alert_count} Alerts Correlated
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-xs text-slate-400 pt-1">
                    <span className="flex items-center gap-1.5">
                      <ShieldAlert className="h-4 w-4 text-amber-400" /> Vector: <strong className="text-slate-200">{grp.root_attack_type}</strong>
                    </span>
                    <span className="flex items-center gap-1.5">
                      <Server className="h-4 w-4 text-indigo-400" /> Entities: <strong className="text-slate-200">{(grp.source_ips || []).join(', ') || 'Internal Asset'}</strong>
                    </span>
                    <span className="flex items-center gap-1.5">
                      <Zap className="h-4 w-4 text-cyan-400" /> Confidence: <strong className="text-slate-200">{Math.round(grp.confidence_score * 100)}%</strong>
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    onClick={() => handleInspectPriority(grp.incident_id || grp.id)}
                    className="flex items-center gap-1.5 px-3.5 py-2 bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-xs font-semibold rounded-lg transition-all"
                  >
                    <Eye className="h-4 w-4" /> Why High Priority?
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Priority Explainability Modal */}
      {modalOpen && selectedAlertPriority && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <Flame className="h-6 w-6 text-amber-400" />
                Alert Priority Score: {selectedAlertPriority.priority_score}/100 ({selectedAlertPriority.priority_level})
              </h3>
              <button
                onClick={() => setModalOpen(false)}
                className="text-slate-400 hover:text-slate-200 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 text-xs text-slate-300">
                <strong className="text-slate-100 block mb-1">Explainable Reasoning:</strong>
                {selectedAlertPriority.explanation}
              </div>

              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Contributing Factors:</h4>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {Object.entries(selectedAlertPriority.contributing_factors || {}).map(([k, v]) => (
                    <div key={k} className="p-2.5 bg-slate-950/40 rounded-lg border border-slate-800 flex justify-between">
                      <span className="text-slate-400 capitalize">{k.replace('_', ' ')}</span>
                      <span className="font-bold text-indigo-400">+{String(v)} pts</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Detected Indicators:</h4>
                <ul className="space-y-1 text-xs text-slate-300">
                  {(selectedAlertPriority.reasons || []).map((r: string, idx: number) => (
                    <li key={idx} className="flex items-center gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-cyan-400" />
                      {r}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => setModalOpen(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg"
              >
                Close Explanation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
