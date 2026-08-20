import React, { useEffect, useState } from 'react';
import {
  Zap,
  Play,
  Activity,
  Sliders,
  Network,
  AlertCircle
} from 'lucide-react';
import { saasApi } from '../services/saas';

export const SecurityAutomation: React.FC = () => {
  const [policy, setPolicy] = useState<any>(null);
  const [attackPaths, setAttackPaths] = useState<any[]>([]);
  const [coverageGaps, setCoverageGaps] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [simulating, setSimulating] = useState<boolean>(false);
  const [simResult, setSimResult] = useState<any>(null);


  useEffect(() => {
    fetchAutomationData();
  }, []);

  const fetchAutomationData = async () => {
    try {
      setLoading(true);
      const [pData, apData, cgData] = await Promise.all([
        saasApi.getAutonomousPolicy(),
        saasApi.getAttackPaths(),
        saasApi.getCoverageGaps()
      ]);
      setPolicy(pData);
      setAttackPaths(apData);
      setCoverageGaps(cgData);
    } catch (err) {
      console.error('Failed to load security automation data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAutonomyChange = async (level: string) => {
    try {
      await saasApi.updateAutonomousPolicy({ autonomy_level: level });
      setPolicy((prev: any) => ({ ...prev, autonomy_level: level }));
    } catch (err) {
      console.error('Failed to update autonomy level:', err);
    }
  };

  const handleSimulate = async () => {
    try {
      setSimulating(true);
      const res = await saasApi.simulateResponse({
        incident_id: 'INC-DEMO-01',
        action_type: 'ISOLATE_ENDPOINT',
        target_entity: '198.51.100.25'
      });
      setSimResult(res);
    } catch (err) {
      console.error('Failed to simulate response:', err);
    } finally {
      setSimulating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Zap className="h-7 w-7 text-cyan-400" />
            Autonomous Threat Response & Automation Center
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Policy-governed risk-based autonomy levels (0–4), blast-radius guards, and non-destructive simulation.
          </p>
        </div>

        <button
          onClick={fetchAutomationData}
          className="flex items-center gap-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-colors"
        >
          <Activity className="h-4 w-4 text-cyan-400" /> Refresh State
        </button>
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Activity className="h-8 w-8 animate-spin text-cyan-400 mr-3" />
          Loading security automation policies...
        </div>
      ) : (
        <>
          {/* Autonomy Level Slider / Switcher */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 backdrop-blur-sm space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sliders className="h-5 w-5 text-indigo-400" />
                <h2 className="text-base font-semibold text-slate-100">Enterprise Autonomy Level Configuration</h2>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                Active: {policy?.autonomy_level}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
              {[
                { id: 'LEVEL_0_OBSERVE', name: 'Level 0: Observe', desc: 'Telemetry ingestion only; zero active remediation.' },
                { id: 'LEVEL_1_RECOMMEND', name: 'Level 1: Recommend', desc: 'Generate AI proposals for analyst review.' },
                { id: 'LEVEL_2_APPROVAL_REQUIRED', name: 'Level 2: Approval Gated', desc: 'Mandate human sign-off for all actions.' },
                { id: 'LEVEL_3_LIMITED_AUTONOMOUS', name: 'Level 3: Limited Auto', desc: 'Auto-isolate non-critical assets; gate core.' },
                { id: 'LEVEL_4_FULL_AUTONOMOUS', name: 'Level 4: Full Auto', desc: 'Full automated high-velocity containment.' }
              ].map((lvl) => (
                <button
                  key={lvl.id}
                  onClick={() => handleAutonomyChange(lvl.id)}
                  className={`p-3.5 rounded-xl border text-left transition-all ${
                    policy?.autonomy_level === lvl.id
                      ? 'bg-indigo-600/20 border-indigo-500 shadow-md shadow-indigo-500/10'
                      : 'bg-slate-950/40 border-slate-800/80 hover:border-slate-700'
                  }`}
                >
                  <div className="text-xs font-bold text-slate-200 mb-1">{lvl.name}</div>
                  <p className="text-[11px] text-slate-400">{lvl.desc}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Response Simulation Sandbox & Attack Paths */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Simulation Runner */}
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                <Play className="h-5 w-5 text-emerald-400" />
                Response Simulation & Blast-Radius Sandbox
              </h2>
              <p className="text-xs text-slate-400">
                Execute safe dry-run containment to evaluate policy decisions and downstream dependency risk.
              </p>

              <button
                onClick={handleSimulate}
                disabled={simulating}
                className="w-full flex items-center justify-center gap-2 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold rounded-lg transition-all"
              >
                {simulating ? <Activity className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                Simulate ISOLATE_ENDPOINT on 198.51.100.25
              </button>

              {simResult && (
                <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 space-y-3 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Policy Decision:</span>
                    <span className="font-bold text-emerald-400">{simResult.decision}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Human Approval Required:</span>
                    <span className={`font-bold ${simResult.requires_approval ? 'text-amber-400' : 'text-emerald-400'}`}>
                      {simResult.requires_approval ? 'YES (Gated)' : 'NO (Autonomous)'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Estimated Business Impact:</span>
                    <span className="font-bold text-cyan-400">{simResult.blast_radius?.estimated_business_impact}</span>
                  </div>
                  <div className="p-2.5 bg-slate-900/80 rounded-lg text-slate-300 text-[11px] border border-slate-800">
                    {simResult.explanation}
                  </div>
                </div>
              )}
            </div>

            {/* Attack Paths & Lateral Exposure */}
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                <Network className="h-5 w-5 text-indigo-400" />
                Active Attack Path Traversal & Cut-Points
              </h2>
              <div className="space-y-3">
                {attackPaths.map((ap) => (
                  <div
                    key={ap.path_id}
                    className="p-3.5 bg-slate-950/40 rounded-xl border border-slate-800 space-y-2 text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-indigo-400">{ap.path_id}</span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                        {ap.path_likelihood_pct}% Likelihood
                      </span>
                    </div>
                    <div className="text-slate-200">
                      <strong>Entry:</strong> {ap.entry_point} &rarr; <strong>Target:</strong> {ap.target_asset}
                    </div>
                    <div className="p-2 bg-slate-900/60 rounded text-[11px] text-cyan-400 font-medium">
                      Recommended Containment Cut-Point: {ap.recommended_cut_point}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* ATT&CK Coverage Gaps */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
            <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-amber-400" />
              MITRE ATT&CK Detection Coverage Gaps
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {coverageGaps.map((gap) => (
                <div
                  key={gap.id || gap.technique_id}
                  className="p-4 bg-slate-950/40 rounded-xl border border-slate-800 space-y-2 text-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-amber-400">{gap.technique_id}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                      {gap.risk_level} Risk
                    </span>
                  </div>
                  <div className="font-bold text-slate-100">{gap.technique_name}</div>
                  <p className="text-slate-400 text-[11px]">{gap.recommended_detection}</p>
                  <div className="p-2 bg-slate-900/80 rounded text-[10px] text-slate-300">
                    <strong>Telemetry:</strong> {gap.recommended_telemetry}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

