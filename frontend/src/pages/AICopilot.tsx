import React, { useState } from 'react';
import { saasApi } from '../services/saas';

export const AICopilotPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [incidentId, setIncidentId] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [chatResponse, setChatResponse] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await saasApi.queryCopilot(query, incidentId ? incidentId : undefined);
      if (res.executive_summary) {
        setAnalysisResult(res);
        setChatResponse(null);
      } else {
        setChatResponse(res);
        setAnalysisResult(null);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to communicate with AI Copilot.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeSpecificIncident = async () => {
    if (!incidentId.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await saasApi.explainIncident(incidentId);
      setAnalysisResult(res);
      setChatResponse(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to explain incident.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 font-mono">
      <div className="flex justify-between items-center border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-cyan-400 tracking-wider">AEGIVANTA AI SECURITY COPILOT</h1>
          <p className="text-xs text-gray-400">Explainable Attack Path Reasoning, Evidence Correlation & Gated SOAR Remediation</p>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-950/40 border border-red-500/50 rounded text-red-300 text-xs">
          {error}
        </div>
      )}

      {/* Query Bar */}
      <div className="bg-gray-900/60 border border-gray-800 rounded p-4 space-y-3">
        <form onSubmit={handleQuery} className="space-y-3">
          <div className="flex flex-col md:flex-row gap-3">
            <div className="flex-1">
              <label className="block text-[10px] text-gray-400 uppercase mb-1">Analyst Prompt / Inquiry</label>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g. Explain attack path, blast radius, and recommend containment steps"
                className="w-full bg-black/60 border border-gray-700 rounded p-2.5 text-xs text-white"
              />
            </div>
            <div className="w-full md:w-64">
              <label className="block text-[10px] text-gray-400 uppercase mb-1">Target Incident ID (Optional)</label>
              <input
                type="text"
                value={incidentId}
                onChange={(e) => setIncidentId(e.target.value)}
                placeholder="inc-1234-uuid"
                className="w-full bg-black/60 border border-gray-700 rounded p-2.5 text-xs text-white"
              />
            </div>
          </div>
          <div className="flex flex-col md:flex-row justify-between items-center pt-2 gap-2">
            <div className="flex gap-2 flex-wrap">
              <button
                type="button"
                onClick={handleAnalyzeSpecificIncident}
                className="px-2.5 py-1 bg-cyan-950 hover:bg-cyan-900 text-[10px] text-cyan-300 border border-cyan-500/30 rounded"
              >
                Analyze Incident ID
              </button>
              <button
                type="button"
                onClick={() => setQuery("What happened during this attack and what MITRE techniques are involved?")}
                className="px-2.5 py-1 bg-gray-800 hover:bg-gray-700 text-[10px] text-gray-300 rounded"
              >
                Attack Summary
              </button>
              <button
                type="button"
                onClick={() => setQuery("What evidence supports this threat detection?")}
                className="px-2.5 py-1 bg-gray-800 hover:bg-gray-700 text-[10px] text-gray-300 rounded"
              >
                Evidence Verification
              </button>
              <button
                type="button"
                onClick={() => setQuery("What gated containment actions are recommended?")}
                className="px-2.5 py-1 bg-gray-800 hover:bg-gray-700 text-[10px] text-gray-300 rounded"
              >
                Containment Actions
              </button>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 bg-cyan-600 hover:bg-cyan-500 text-black font-bold text-xs rounded transition-colors"
            >
              {loading ? 'ANALYZING...' : 'RUN COPILOT'}
            </button>
          </div>
        </form>
      </div>

      {/* Structured Analysis Result */}
      {analysisResult && (
        <div className="space-y-4">
          {/* Executive Summary */}
          <div className="bg-gray-900/60 border border-cyan-500/30 rounded p-5 space-y-2">
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-bold text-cyan-300 uppercase">{analysisResult.title || 'Incident Analysis'}</h3>
              <span className="px-2.5 py-0.5 bg-red-950 text-red-400 border border-red-500/30 rounded text-[10px] font-bold">
                RISK SCORE: {analysisResult.risk_score}/100
              </span>
            </div>
            <p className="text-xs text-gray-200 leading-relaxed">{analysisResult.executive_summary}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Attack Path */}
            <div className="bg-gray-900/60 border border-gray-800 rounded p-4 space-y-3">
              <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Derived Multi-Hop Attack Path</h4>
              <div className="space-y-2">
                {analysisResult.attack_path?.map((step: any, idx: number) => (
                  <div key={idx} className="p-2.5 bg-black/40 border border-gray-800 rounded text-xs space-y-1">
                    <div className="flex justify-between text-[10px] font-bold text-cyan-300">
                      <span>STEP {step.step}: {step.phase}</span>
                    </div>
                    <p className="text-gray-300 text-[11px]">{step.detail}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* MITRE ATT&CK & Supporting Evidence */}
            <div className="bg-gray-900/60 border border-gray-800 rounded p-4 space-y-3">
              <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider">MITRE ATT&CK & Correlated Evidence</h4>
              <div className="flex flex-wrap gap-1.5 mb-3">
                {analysisResult.mitre_tactics?.map((t: string, idx: number) => (
                  <span key={idx} className="px-2 py-0.5 bg-purple-950/60 text-purple-300 border border-purple-500/30 rounded text-[10px]">
                    {t}
                  </span>
                ))}
              </div>
              <div className="space-y-2">
                {analysisResult.evidence?.map((ev: any, idx: number) => (
                  <div key={idx} className="p-2 bg-black/40 border border-gray-800 rounded text-[11px]">
                    <span className="font-bold text-amber-400">{ev.type}: </span>
                    <span className="text-gray-300">{ev.description}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Gated SOAR Containment Actions */}
          <div className="bg-gray-900/60 border border-emerald-500/30 rounded p-4 space-y-3">
            <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider">🔒 Gated SOAR Remediation Proposals (Human Approval Required)</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {analysisResult.response_proposals?.map((prop: any, idx: number) => (
                <div key={idx} className="p-3 bg-black/50 border border-gray-800 rounded space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-emerald-300">{prop.action}</span>
                    <span className="text-[10px] text-gray-400">Target: {prop.target}</span>
                  </div>
                  <p className="text-[11px] text-gray-300">{prop.description}</p>
                  <div className="flex justify-between items-center pt-1 border-t border-gray-800 text-[10px]">
                    <span className="text-cyan-400">Policy: {prop.policy_check}</span>
                    <span className="text-amber-400 font-semibold">Requires Approval</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Conversational guidance output */}
      {chatResponse && (
        <div className="bg-gray-900/60 border border-cyan-500/30 rounded p-5 space-y-3">
          <div className="text-xs text-gray-400">PROMPT: "{chatResponse.query}"</div>
          <p className="text-xs text-gray-200 leading-relaxed">{chatResponse.response}</p>
          {chatResponse.suggested_actions && (
            <div className="pt-2 border-t border-gray-800 space-y-1">
              <div className="text-[10px] text-gray-400 uppercase">Suggested Next Steps:</div>
              <ul className="list-disc list-inside text-xs text-cyan-300 space-y-0.5">
                {chatResponse.suggested_actions.map((act: string, idx: number) => (
                  <li key={idx}>{act}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
