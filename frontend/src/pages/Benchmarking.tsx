import React, { useEffect, useState } from 'react';
import {
  Cpu,
  Activity,
  BarChart3
} from 'lucide-react';

import { saasApi } from '../services/saas';

export const Benchmarking: React.FC = () => {
  const [benchmarks, setBenchmarks] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchBenchmarks();
  }, []);

  const fetchBenchmarks = async () => {
    try {
      setLoading(true);
      const bList = await saasApi.listBenchmarks(20);
      setBenchmarks(bList);
    } catch (err) {
      console.error('Failed to load benchmarks:', err);
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
            <Cpu className="h-7 w-7 text-cyan-400" />
            Detection Performance & Inference Benchmarking
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Reproducible benchmark executions with cryptographic hash verification, throughput (EPS), and latency percentiles.
          </p>
        </div>

        <button
          onClick={fetchBenchmarks}
          className="flex items-center gap-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-colors"
        >
          <Activity className="h-4 w-4 text-cyan-400" /> Refresh Benchmarks
        </button>
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Activity className="h-8 w-8 animate-spin text-cyan-400 mr-3" />
          Loading benchmark execution records...
        </div>
      ) : benchmarks.length === 0 ? (
        <div className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-12 text-center text-slate-400">
          <BarChart3 className="h-12 w-12 text-cyan-400 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-slate-200">No Benchmark Records Available</h3>
          <p className="text-xs text-slate-500 mt-1">Automated benchmark runs will be indexed here on completion.</p>
        </div>
      ) : (
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950/60 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="p-3">Dataset & Version</th>
                  <th className="p-3">Model Version</th>
                  <th className="p-3">Throughput</th>
                  <th className="p-3">P50 Latency</th>
                  <th className="p-3">P95 Latency</th>
                  <th className="p-3">Memory / CPU</th>
                  <th className="p-3">Result Hash</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {benchmarks.map((b) => (
                  <tr key={b.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="p-3 font-semibold text-slate-200">
                      {b.dataset} <span className="text-[10px] text-slate-500 block font-mono">{b.dataset_version}</span>
                    </td>
                    <td className="p-3 font-mono text-cyan-400">{b.model_version}</td>
                    <td className="p-3 font-bold text-emerald-400">{Math.round(b.throughput_eps).toLocaleString()} EPS</td>
                    <td className="p-3 text-slate-300">{b.p50_latency_ms.toFixed(2)} ms</td>
                    <td className="p-3 font-semibold text-indigo-400">{b.p95_latency_ms.toFixed(2)} ms</td>
                    <td className="p-3 text-slate-400">{b.memory_mb.toFixed(0)}MB / {b.cpu_percent.toFixed(1)}%</td>
                    <td className="p-3 font-mono text-[10px] text-slate-500">{b.result_hash.substring(0, 16)}...</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
