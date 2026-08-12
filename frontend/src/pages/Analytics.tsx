import React, { useState, useEffect } from 'react';
import { Cpu, RefreshCw, BarChart2, PieChart, GitCommit } from 'lucide-react';
import { ConfusionMatrixChart } from '../components/charts/ConfusionMatrixChart';
import { ROCCurveChart } from '../components/charts/ROCCurveChart';
import { FeatureImportanceChart } from '../components/charts/FeatureImportanceChart';
import { analyticsService } from '../services/analytics';
import { ModelPerformanceItem } from '../types';

export const Analytics: React.FC = () => {
  const [models, setModels] = useState<ModelPerformanceItem[]>([]);
  const [isRetraining, setIsRetraining] = useState<boolean>(false);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const data = await analyticsService.getModels();
        setModels(data);
      } catch (err) {
        console.error('Failed to fetch models:', err);
      }
    };
    fetchModels();
  }, []);

  const handleRetrain = async () => {
    setIsRetraining(true);
    try {
      await analyticsService.triggerTraining();
      alert('Model refresh started. You can keep using SentinelAI while it runs.');
    } catch (err) {
      alert('We could not start the model refresh. Please try again.');
    } finally {
      setIsRetraining(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-panel p-6 rounded-2xl">
        <div>
          <h1 className="text-xl font-mono font-bold text-white">Model performance</h1>
          <p className="text-xs text-slate-400 font-mono mt-1">
            Compare the detection models and see which one is currently being used.
          </p>
        </div>
        <button
          onClick={handleRetrain}
          disabled={isRetraining}
          className="px-4 py-2 bg-cyan-500/10 border border-cyan-500/30 hover:bg-cyan-500/20 text-cyan-400 font-mono text-xs font-bold rounded-xl flex items-center space-x-2 transition-all shadow-[0_0_15px_rgba(0,240,255,0.15)]"
        >
          <RefreshCw className={`w-4 h-4 ${isRetraining ? 'animate-spin' : ''}`} />
          <span>{isRetraining ? 'Refreshing models...' : 'Refresh model data'}</span>
        </button>
      </div>

      {/* Model comparison */}
      <div className="glass-panel p-5 rounded-xl space-y-4">
        <h2 className="text-xs font-mono text-slate-400 uppercase tracking-wider flex items-center space-x-2">
          <Cpu className="w-4 h-4 text-cyan-400" />
          <span>Compare detection models</span>
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/80 text-slate-400 uppercase">
                <th className="p-3">Model</th>
                <th className="p-3">Type</th>
                <th className="p-3">Accuracy</th>
                <th className="p-3">F1 score</th>
                <th className="p-3">Precision</th>
                <th className="p-3">Recall</th>
                <th className="p-3">ROC-AUC</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {models.map((m) => (
                <tr
                  key={m.model_name}
                  className={`hover:bg-slate-800/40 transition-colors ${
                    m.is_active ? 'bg-cyan-500/10 border-l-2 border-cyan-400' : ''
                  }`}
                >
                  <td className="p-3 font-bold text-slate-100">{m.model_name}</td>
                  <td className="p-3 text-cyan-400">{m.model_type}</td>
                  <td className="p-3 text-slate-200">{m.accuracy != null ? `${(m.accuracy * 100).toFixed(2)}%` : 'N/A'}</td>
                  <td className="p-3 font-bold text-emerald-400">{m.f1_score != null ? `${(m.f1_score * 100).toFixed(2)}%` : 'N/A'}</td>
                  <td className="p-3 text-slate-300">{m.precision_score != null ? `${(m.precision_score * 100).toFixed(2)}%` : 'N/A'}</td>
                  <td className="p-3 text-slate-300">{m.recall_score != null ? `${(m.recall_score * 100).toFixed(2)}%` : 'N/A'}</td>
                  <td className="p-3 text-slate-300">{m.roc_auc != null ? m.roc_auc.toFixed(3) : 'N/A'}</td>
                  <td className="p-3">
                    {m.is_active ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                        In use
                      </span>
                    ) : (
                      <span className="text-[10px] text-slate-500">Available</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="friendly-note text-xs text-slate-400 font-mono">
        <strong className="text-slate-200">How to read this:</strong> accuracy shows how often a model is right; precision and recall show how well it finds real threats without creating too many false alarms.
      </div>

      {/* Interactive evaluation charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel p-5 rounded-xl">
          <h2 className="text-xs font-mono text-slate-400 uppercase tracking-wider mb-4 flex items-center space-x-2">
            <BarChart2 className="w-4 h-4 text-cyan-400" />
            <span>Correct vs. missed predictions</span>
          </h2>
          <ConfusionMatrixChart />
        </div>

        <div className="glass-panel p-5 rounded-xl">
          <h2 className="text-xs font-mono text-slate-400 uppercase tracking-wider mb-4 flex items-center space-x-2">
            <GitCommit className="w-4 h-4 text-emerald-400" />
            <span>Model comparison curves</span>
          </h2>
          <ROCCurveChart />
        </div>
      </div>

      {/* Feature attribution chart */}
      <div className="glass-panel p-5 rounded-xl">
        <h2 className="text-xs font-mono text-slate-400 uppercase tracking-wider mb-4 flex items-center space-x-2">
          <PieChart className="w-4 h-4 text-purple-400" />
          <span>Signals that influence detections</span>
        </h2>
        <FeatureImportanceChart />
      </div>
    </div>
  );
};
