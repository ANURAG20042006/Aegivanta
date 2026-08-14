import React, { useState, useEffect } from 'react';
import { SearchCode, Play } from 'lucide-react';
import api from '../services/api';

interface IncidentItem {
  id: string;
  incident_code: string;
  attack_type: string;
  severity: string;
  risk_score: number;
  status: string;
  created_at: string;
}

export const InvestigationsView: React.FC = () => {
  const [incidents, setIncidents] = useState<IncidentItem[]>([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const [investigation, setInvestigation] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [playbookResult, setPlaybookResult] = useState<any>(null);

  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        const res = await api.get('/incidents');
        const list = res.data || [];
        setIncidents(list);
        if (list.length > 0) {
          setSelectedIncidentId(list[0].id);
        }
      } catch (err) {
        console.error('Failed to load incidents', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchIncidents();
  }, []);

  useEffect(() => {
    if (!selectedIncidentId) return;
    const fetchInvestigation = async () => {
      setIsAnalyzing(true);
      try {
        const res = await api.get(`/investigations/${selectedIncidentId}`);
        setInvestigation(res.data);
      } catch (err) {
        console.error('Failed to load investigation', err);
        setInvestigation(null);
      } finally {
        setIsAnalyzing(false);
      }
    };
    fetchInvestigation();
  }, [selectedIncidentId]);

  const handleSimulatePlaybook = async (actionType: string) => {
    if (!selectedIncidentId || !investigation) return;
    try {
      const res = await api.post('/playbooks/execute', {
        incident_id: selectedIncidentId,
        playbook_name: `${actionType}_SIMULATION_PLAYBOOK`,
        action_type: actionType,
        target_entity: investigation.findings?.source_ip || '198.51.100.22',
        is_dry_run: true
      });
      setPlaybookResult(res.data);
    } catch (err) {
      console.error('Playbook execution failed', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2.5">
          <SearchCode className="w-7 h-7 text-purple-400" />
          Automated Incident Investigation & ATT&CK Chain Analysis
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Evidence aggregation across alerts, IOC matches, behavioral anomalies, and dry-run playbook execution.
        </p>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Incident Selector */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 space-y-3">
          <div className="text-sm font-semibold text-slate-200">Select Incident to Investigate</div>
          {isLoading ? (
            <div className="text-xs font-mono text-slate-500 animate-pulse">LOADING INCIDENTS...</div>
          ) : (
            <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
              {incidents.map(inc => (
                <button
                  key={inc.id}
                  onClick={() => setSelectedIncidentId(inc.id)}
                  className={`w-full text-left p-3 rounded-lg border transition text-xs ${
                    selectedIncidentId === inc.id
                      ? 'bg-purple-950/40 border-purple-500/40 text-purple-200'
                      : 'bg-slate-950/40 border-slate-800/80 hover:bg-slate-800/40 text-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-purple-300">{inc.incident_code || inc.id.slice(0, 8)}</span>
                    <span className="text-[10px] font-mono text-slate-400">Risk: {inc.risk_score?.toFixed(1)}</span>
                  </div>
                  <div className="text-slate-200 mt-1 font-medium">{inc.attack_type}</div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Investigation Details */}
        <div className="lg:col-span-2 space-y-4">
          {isAnalyzing ? (
            <div className="p-12 text-center text-xs font-mono text-slate-500 animate-pulse rounded-xl border border-slate-800 bg-slate-900/60">
              AGGREGATING TRACEABLE EVIDENCE & EVALUATING ATT&CK STAGES...
            </div>
          ) : !investigation ? (
            <div className="p-8 text-center text-xs text-slate-500 rounded-xl border border-slate-800 bg-slate-900/60">
              Select an incident to view automated investigation findings.
            </div>
          ) : (
            <>
              {/* Stage & Summary Card */}
              <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="text-xs font-mono text-slate-400">MITRE ATT&CK Framework Stage</div>
                  <span className="px-3 py-1 rounded-full text-xs font-bold font-mono bg-purple-500/20 text-purple-300 border border-purple-500/30">
                    STAGE: {investigation.attack_chain_stage}
                  </span>
                </div>
                <p className="text-xs font-mono text-slate-200 leading-relaxed bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
                  {investigation.summary}
                </p>
              </div>

              {/* Evidence Items */}
              <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                <div className="text-xs font-semibold text-slate-200">Correlated Traceable Evidence Items</div>
                {investigation.evidence?.length === 0 ? (
                  <div className="text-xs text-slate-500">No explicit evidence items attached.</div>
                ) : (
                  <div className="space-y-2">
                    {investigation.evidence.map((ev: any) => (
                      <div key={ev.id} className="p-2.5 rounded bg-slate-950/40 border border-slate-800/60 text-xs flex items-center justify-between">
                        <div className="flex items-center gap-2 font-mono">
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-cyan-400">{ev.evidence_type}</span>
                          <span className="text-slate-300">{ev.description}</span>
                        </div>
                        <span className="text-[10px] font-mono text-slate-500">
                          {ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString() : ''}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Recommended Actions & Safe Playbook Simulation */}
              <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                <div className="text-xs font-semibold text-slate-200">Recommended Analyst Actions</div>
                <ul className="space-y-1 text-xs text-slate-300 list-disc list-inside font-mono">
                  {investigation.recommended_actions?.map((act: string, idx: number) => (
                    <li key={idx}>{act}</li>
                  ))}
                </ul>

                <div className="pt-3 border-t border-slate-800/80 flex flex-wrap gap-2">
                  <button
                    onClick={() => handleSimulatePlaybook('BLOCK_IP')}
                    className="px-3 py-1.5 rounded-lg bg-purple-600/20 text-purple-300 border border-purple-500/30 hover:bg-purple-600/30 transition text-xs font-mono flex items-center gap-1.5"
                  >
                    <Play className="w-3.5 h-3.5" /> Simulate IP Containment Playbook (Dry Run)
                  </button>
                  <button
                    onClick={() => handleSimulatePlaybook('QUARANTINE_VLAN')}
                    className="px-3 py-1.5 rounded-lg bg-cyan-600/20 text-cyan-300 border border-cyan-500/30 hover:bg-cyan-600/30 transition text-xs font-mono flex items-center gap-1.5"
                  >
                    <Play className="w-3.5 h-3.5" /> Simulate VLAN Quarantine Playbook (Dry Run)
                  </button>
                </div>

                {playbookResult && (
                  <div className="p-3 rounded-lg bg-slate-950/80 border border-purple-500/30 text-xs font-mono text-purple-300 mt-2">
                    <div className="font-bold text-purple-400">[PLAYBOOK SIMULATION EXECUTED]</div>
                    <div className="mt-1 text-slate-300">{playbookResult.log}</div>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default InvestigationsView;
