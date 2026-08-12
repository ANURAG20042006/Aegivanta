import React, { useState } from 'react';
import { Upload } from 'lucide-react';
import { PacketTable } from '../components/tables/PacketTable';
import { predictService } from '../services/predict';
import { PacketFeatureVector, PredictionResult, BatchPredictionResponse } from '../types';

export const Prediction: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'single' | 'csv'>('csv');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>(() => localStorage.getItem('sentinel_default_model') || 'Random Forest');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  // Single Flow Form state
  const [formVector, setFormVector] = useState<PacketFeatureVector>({
    source_ip: '192.168.1.105',
    destination_ip: '10.0.0.1',
    source_port: 443,
    destination_port: 80,
    protocol: 'TCP',
    flow_duration: 120500,
    total_fwd_packets: 10,
    total_backward_packets: 8,
    packet_length_mean: 512,
    packet_length_std: 128,
    flow_bytes_s: 10240,
    flow_packets_s: 150,
    syn_flag_count: 1,
    rst_flag_count: 0,
    psh_flag_count: 1,
    ack_flag_count: 1,
    urg_flag_count: 0,
  });

  const [singleResult, setSingleResult] = useState<PredictionResult | null>(null);
  const [batchResult, setBatchResult] = useState<BatchPredictionResponse | null>(null);

  const handleSingleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsProcessing(true);
    try {
      const res = await predictService.predictSingle(formVector as any, selectedModel);
      setSingleResult(res);
    } catch (err) {
      alert('We could not check this connection. Please review the values and try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCSVUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      alert('Choose a CSV file before starting the analysis.');
      return;
    }
    setIsProcessing(true);
    try {
      const rawRes = await predictService.predictCsv(selectedFile, selectedModel);
      const formattedBatch: BatchPredictionResponse = {
        total_packets_inspected: rawRes.total_records,
        malicious_packets_count: rawRes.malicious_count,
        benign_packets_count: rawRes.total_records - rawRes.malicious_count,
        threat_ratio_percentage: Math.round((rawRes.malicious_count / (rawRes.total_records || 1)) * 1000) / 10,
        results: rawRes.predictions
      };
      setBatchResult(formattedBatch);
    } catch (err) {
      alert('We could not read that CSV file. Please check the format and try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel p-6 rounded-2xl">
        <h1 className="text-xl font-mono font-bold text-white">Inspect network traffic</h1>
        <p className="text-xs text-slate-400 font-mono mt-1">
          Upload a traffic file or enter one connection below. SentinelAI will look for activity that may be harmful.
        </p>

        {/* Tab Controls */}
        <div className="flex space-x-2 mt-4">
          <button
            onClick={() => setActiveTab('csv')}
            className={`px-4 py-2 rounded-lg font-mono text-xs font-bold transition-all ${
              activeTab === 'csv'
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-[0_0_15px_rgba(0,240,255,0.15)]'
                : 'bg-slate-900 text-slate-400 border border-slate-800'
            }`}
          >
            Upload a traffic file
          </button>
          <button
            onClick={() => setActiveTab('single')}
            className={`px-4 py-2 rounded-lg font-mono text-xs font-bold transition-all ${
              activeTab === 'single'
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-[0_0_15px_rgba(0,240,255,0.15)]'
                : 'bg-slate-900 text-slate-400 border border-slate-800'
            }`}
          >
            Check one connection
          </button>
        </div>
      </div>

      {/* Model Selection Dropdown */}
      <div className="glass-panel p-4 rounded-xl flex items-center justify-between">
        <div>
          <label className="text-xs font-mono text-slate-400 block">Detection model</label>
          <span className="text-[10px] text-slate-500">The default model is a good choice for most checks.</span>
        </div>
        <select
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          className="bg-slate-900 border border-slate-700 text-cyan-400 font-mono text-xs px-3 py-1.5 rounded-lg focus:outline-none focus:border-cyan-400"
        >
          <option value="Random Forest">Random Forest (Ensemble)</option>
          <option value="XGBoost">XGBoost (Boosting)</option>
          <option value="LightGBM">LightGBM (Boosting)</option>
          <option value="CatBoost">CatBoost (Boosting)</option>
          <option value="1D-CNN">1D-CNN (Deep Learning)</option>
          <option value="LSTM">LSTM (Recurrent DeepNet)</option>
          <option value="Autoencoder">Autoencoder (Zero-Day Anomaly)</option>
        </select>
      </div>

      {/* CSV Batch Upload Mode */}
      {activeTab === 'csv' && (
        <div className="space-y-6">
          <form onSubmit={handleCSVUpload} className="glass-panel p-8 rounded-xl border-dashed border-2 border-slate-700 text-center space-y-4">
            <Upload className="w-10 h-10 text-cyan-400 mx-auto" />
            <div>
              <div className="text-sm font-mono font-bold text-slate-200">Upload a network traffic CSV</div>
              <div className="text-xs text-slate-500 font-mono mt-1">Use a standard CICIDS2017-style file with one traffic flow per row.</div>
            </div>
            <input
              type="file"
              accept=".csv"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              className="block mx-auto text-xs font-mono text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-mono file:bg-cyan-500/10 file:text-cyan-400 hover:file:bg-cyan-500/20"
            />
            {selectedFile && <div className="text-[10px] text-cyan-400 font-mono">Selected: {selectedFile.name}</div>}
            <button
              type="submit"
              disabled={isProcessing || !selectedFile}
              className="px-6 py-2.5 bg-gradient-to-r from-cyan-500 to-teal-500 text-slate-950 font-mono font-bold text-xs rounded-lg shadow-[0_0_20px_rgba(0,240,255,0.3)] disabled:opacity-50"
            >
              {isProcessing ? 'Checking traffic...' : 'Analyze traffic'}
            </button>
          </form>

          {/* Batch Prediction Results */}
          {batchResult && (
            <div className="glass-panel p-5 rounded-xl space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-center font-mono">
                <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                  <div className="text-[10px] text-slate-400">CHECKED</div>
                  <div className="text-lg font-bold text-white">{batchResult.total_packets_inspected}</div>
                </div>
                <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                  <div className="text-[10px] text-slate-400">NORMAL</div>
                  <div className="text-lg font-bold text-emerald-400">{batchResult.benign_packets_count}</div>
                </div>
                <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                  <div className="text-[10px] text-slate-400">POSSIBLE THREATS</div>
                  <div className="text-lg font-bold text-rose-400">{batchResult.malicious_packets_count}</div>
                </div>
                <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                  <div className="text-[10px] text-slate-400">THREAT RATE</div>
                  <div className="text-lg font-bold text-cyan-400">{batchResult.threat_ratio_percentage}%</div>
                </div>
              </div>

              <h2 className="text-xs font-mono text-slate-400 uppercase tracking-wider">
                Results (possible threats are highlighted)
              </h2>
              <PacketTable packets={batchResult.results} />
            </div>
          )}
        </div>
      )}

      {/* Manual Vector Form Mode */}
      {activeTab === 'single' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <form onSubmit={handleSingleSubmit} className="glass-panel p-5 rounded-xl space-y-4">
            <h2 className="text-xs font-mono text-slate-400 uppercase tracking-wider">
              Enter connection details
            </h2>
            <p className="text-[10px] text-slate-500">Use this form for a quick test. For many connections, upload a CSV instead.</p>
            <div className="grid grid-cols-2 gap-3 text-xs font-mono">
              <div>
                <label className="text-slate-400">Source IP:</label>
                <input
                  type="text"
                  value={formVector.source_ip}
                  onChange={(e) => setFormVector({ ...formVector, source_ip: e.target.value })}
                  className="w-full mt-1 p-2 bg-slate-900 border border-slate-700 rounded text-slate-200"
                />
              </div>
              <div>
                <label className="text-slate-400">Destination IP:</label>
                <input
                  type="text"
                  value={formVector.destination_ip}
                  onChange={(e) => setFormVector({ ...formVector, destination_ip: e.target.value })}
                  className="w-full mt-1 p-2 bg-slate-900 border border-slate-700 rounded text-slate-200"
                />
              </div>
              <div>
                <label className="text-slate-400">Flow Packets/s:</label>
                <input
                  type="number"
                  value={formVector.flow_packets_s}
                  onChange={(e) => setFormVector({ ...formVector, flow_packets_s: parseFloat(e.target.value) })}
                  className="w-full mt-1 p-2 bg-slate-900 border border-slate-700 rounded text-slate-200"
                />
              </div>
              <div>
                <label className="text-slate-400">Packet Length Mean:</label>
                <input
                  type="number"
                  value={formVector.packet_length_mean}
                  onChange={(e) => setFormVector({ ...formVector, packet_length_mean: parseFloat(e.target.value) })}
                  className="w-full mt-1 p-2 bg-slate-900 border border-slate-700 rounded text-slate-200"
                />
              </div>
              <div>
                <label className="text-slate-400">SYN Flag Count:</label>
                <input
                  type="number"
                  value={formVector.syn_flag_count}
                  onChange={(e) => setFormVector({ ...formVector, syn_flag_count: parseFloat(e.target.value) })}
                  className="w-full mt-1 p-2 bg-slate-900 border border-slate-700 rounded text-slate-200"
                />
              </div>
              <div>
                <label className="text-slate-400">URG Flag Count:</label>
                <input
                  type="number"
                  value={formVector.urg_flag_count}
                  onChange={(e) => setFormVector({ ...formVector, urg_flag_count: parseFloat(e.target.value) })}
                  className="w-full mt-1 p-2 bg-slate-900 border border-slate-700 rounded text-slate-200"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isProcessing}
              className="w-full py-2.5 bg-cyan-500 text-slate-950 font-mono font-bold text-xs rounded-lg cursor-pointer"
            >
              Check this connection
            </button>
          </form>

          {/* Single Result Viewer */}
          {singleResult && (
            <div className="glass-panel p-5 rounded-xl space-y-4 font-mono">
              <h2 className="text-xs text-slate-400 uppercase tracking-wider">What we found</h2>
              <div className={`p-4 rounded-xl border ${
                singleResult.is_malicious ? 'bg-rose-500/10 border-rose-500/40 text-rose-400' : 'bg-emerald-500/10 border-emerald-500/40 text-emerald-400'
              }`}>
                <div className="text-xl font-bold">{singleResult.attack_type}</div>
                <div className="text-xs text-slate-300 mt-1">
                  Confidence: {singleResult.confidence_score !== null && singleResult.confidence_score !== undefined
                    ? `${(singleResult.confidence_score * 100).toFixed(1)}%`
                    : 'N/A'} · Priority: {singleResult.severity}
                </div>
              </div>

              {/* SHAP Explanation Attribution */}
              {singleResult.shap_explanation && (
                <div className="space-y-2">
                  <div className="text-xs text-slate-400 uppercase">Why the model reached this result</div>
                  {Object.entries(singleResult.shap_explanation).map(([feat, score]) => (
                    <div key={feat} className="flex justify-between items-center text-xs p-2 bg-slate-900 rounded">
                      <span className="text-slate-300">{feat}</span>
                      <span className={score > 0 ? 'text-rose-400 font-bold' : 'text-emerald-400'}>{score}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
