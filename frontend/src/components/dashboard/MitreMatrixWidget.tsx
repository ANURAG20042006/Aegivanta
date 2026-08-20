import React, { useState, useEffect } from 'react';
import { 
  Layers, 
  RefreshCw, 
  X
} from 'lucide-react';
import { dashboardService, MitreDashboardData } from '../../services/dashboard';

export const MitreMatrixWidget: React.FC = () => {
  const [mitreData, setMitreData] = useState<MitreDashboardData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [selectedTechnique, setSelectedTechnique] = useState<any | null>(null);

  const fetchMitreData = async () => {
    setIsLoading(true);
    try {
      const data = await dashboardService.getMitre();
      setMitreData(data);
    } catch (err) {
      console.error('Failed to load MITRE matrix data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMitreData();
  }, []);

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-2xl backdrop-blur-md space-y-4 font-mono">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-purple-500/10 border border-purple-500/30 rounded-xl text-purple-400">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              Enterprise MITRE ATT&CK Matrix Coverage
            </h3>
            <p className="text-xs text-slate-400">
              Active detection rules & incident observation mappings
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="text-right">
            <span className="text-xs text-slate-400">Coverage: </span>
            <span className="text-sm font-black text-cyan-400">
              {mitreData?.coverage_percentage ?? 0}%
            </span>
          </div>
          <button
            onClick={fetchMitreData}
            className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl"
            title="Refresh MITRE Matrix"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
          <span className="text-[10px] text-slate-500 block">TOTAL TECHNIQUES</span>
          <span className="text-base font-bold text-slate-200">
            {mitreData?.total_catalog_techniques ?? 25}
          </span>
        </div>
        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
          <span className="text-[10px] text-slate-500 block">COVERED BY RULES</span>
          <span className="text-base font-bold text-emerald-400">
            {mitreData?.covered_techniques_count ?? 0}
          </span>
        </div>
        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
          <span className="text-[10px] text-slate-500 block">UNCOVERED GAPS</span>
          <span className="text-base font-bold text-rose-400">
            {mitreData?.uncovered_techniques_count ?? 0}
          </span>
        </div>
        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
          <span className="text-[10px] text-slate-500 block">ACTIVE MAPPINGS</span>
          <span className="text-base font-bold text-purple-400">
            {mitreData?.highest_frequency_detected?.length ?? 0} Observed
          </span>
        </div>
      </div>

      {/* Matrix Techniques Grid */}
      <div>
        <h4 className="text-xs font-bold text-slate-300 mb-2">Covered & Detected Techniques</h4>
        {isLoading ? (
          <div className="py-8 text-center text-slate-500 text-xs flex items-center justify-center">
            <RefreshCw className="w-4 h-4 animate-spin mr-2" />
            COMPUTING MITRE COVERAGE MATRIX...
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2 max-h-[220px] overflow-y-auto pr-1">
            {mitreData?.covered_techniques.map((t) => (
              <div
                key={t.technique_id}
                onClick={() => setSelectedTechnique(t)}
                className="p-2 rounded-xl bg-slate-950/80 hover:bg-slate-800 border border-purple-500/20 hover:border-purple-500/50 cursor-pointer transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-purple-400 font-bold text-[11px]">{t.technique_id}</span>
                    {t.incident_observation_count > 0 && (
                      <span className="px-1 py-0.2 bg-red-500/20 text-red-400 rounded text-[9px] font-bold">
                        {t.incident_observation_count} Hits
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-slate-300 font-medium truncate mt-0.5">{t.name}</p>
                </div>
                <div className="text-[9px] text-slate-500 truncate mt-1">
                  {t.tactic}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Technique Drilldown Modal */}
      {selectedTechnique && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-5 shadow-2xl space-y-4 font-mono">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <span className="text-purple-400 font-bold text-xs">{selectedTechnique.technique_id}</span>
                <h3 className="text-sm font-bold text-slate-100">{selectedTechnique.name}</h3>
              </div>
              <button onClick={() => setSelectedTechnique(null)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-slate-500">Tactic:</span>
                <p className="text-slate-200 font-bold">{selectedTechnique.tactic}</p>
              </div>

              <div>
                <span className="text-slate-500">Mapped Detection Rules:</span>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {selectedTechnique.mapped_rules && selectedTechnique.mapped_rules.length > 0 ? (
                    selectedTechnique.mapped_rules.map((r: string, idx: number) => (
                      <span key={idx} className="px-2 py-0.5 bg-slate-950 border border-slate-800 text-cyan-400 rounded text-[11px]">
                        {r}
                      </span>
                    ))
                  ) : (
                    <span className="text-slate-500">No specific rules mapped</span>
                  )}
                </div>
              </div>

              <div>
                <span className="text-slate-500">Incident Observation Count:</span>
                <p className="text-slate-200 font-bold">{selectedTechnique.incident_observation_count} occurrences</p>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedTechnique(null)}
                className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
