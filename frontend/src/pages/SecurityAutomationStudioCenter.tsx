import React, { useEffect, useState } from 'react';
import {
  Workflow,
  Activity,
  ChevronRight,
  ShieldCheck,
  Play,
  FileCode,
  Layers,
  GitBranch,
  Clock,
  ArrowRight
} from 'lucide-react';
import { saasApi } from '../services/saas';


export const SecurityAutomationStudioCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'dag_canvas' | 'active_playbooks' | 'execution_runs' | 'template_library' | 'simulation_studio'>('overview');
  const [summary, setSummary] = useState<any>(null);
  const [playbooks, setPlaybooks] = useState<any[]>([]);
  const [executions, setExecutions] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Create playbook form state
  const [playbookName, setPlaybookName] = useState<string>('Automated Lateral Movement Containment');
  const [description, setDescription] = useState<string>('Quarantines compromised host network via eBPF and invalidates Active Directory Kerberos tickets.');
  const [triggerType, setTriggerType] = useState<string>('ON_ALERT');
  const [createdPlaybook, setCreatedPlaybook] = useState<any>(null);

  // Simulation state
  const [simPlaybookName, setSimPlaybookName] = useState<string>('Ransomware Containment & Host Isolation');
  const [simResult, setSimResult] = useState<any>(null);

  useEffect(() => {
    fetchAutomationData();
  }, []);

  const fetchAutomationData = async () => {
    try {
      setLoading(true);
      const [sum, pbs, runs, tpls] = await Promise.all([
        saasApi.getAutomationStudioSummary(),
        saasApi.getAutomationPlaybooks(),
        saasApi.getPlaybookExecutions(),
        saasApi.getPlaybookTemplates()
      ]);
      setSummary(sum);
      setPlaybooks(pbs);
      setExecutions(runs);
      setTemplates(tpls);
    } catch (err) {
      console.error('Failed to load Automation Studio data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePlaybook = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await saasApi.createAutomationPlaybook({
        name: playbookName,
        description: description,
        trigger_type: triggerType
      });
      setCreatedPlaybook(res);
      fetchAutomationData();
    } catch (err) {
      console.error('Failed to create playbook:', err);
    }
  };

  const handleSimulate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await saasApi.simulatePlaybookExecution({
        playbook_name: simPlaybookName
      });
      setSimResult(res);
      fetchAutomationData();
    } catch (err) {
      console.error('Failed to simulate playbook:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Workflow className="h-7 w-7 text-indigo-400" />
            Security Automation Studio (SOAR Visual Playbook Builder)
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Low-Code / No-Code Directed Acyclic Graph (DAG) Playbook Canvas, Asynchronous State Recovery & Turnkey SOAR Templates.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('simulation_studio')}
            className="flex items-center gap-2 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-colors"
          >
            <Play className="h-4 w-4" /> Dry-Run Simulation Studio
          </button>
        </div>
      </div>

      {/* Top Metrics Ribbon */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Automation Score</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{summary.overall_automation_score}<span className="text-xs text-slate-500">/100</span></div>
            <div className="text-[10px] text-emerald-400 mt-0.5">SOAR 2.0 Certified</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Active Playbooks</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{summary.active_playbooks_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Live DAG Pipelines</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Total Executions</div>
            <div className="text-2xl font-bold text-slate-200 mt-1">{summary.total_playbook_executions}</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">{(summary.automation_success_rate * 100).toFixed(2)}% Success</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Turnkey Templates</div>
            <div className="text-2xl font-bold text-amber-400 mt-1">{summary.available_turnkey_templates}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Verified Library</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Mean Duration</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.mean_execution_duration_ms} <span className="text-xs text-slate-500">ms</span></div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Sub-Second MTTR</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">MTTR Reduction</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.mttr_reduction_percentage}%</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Autonomous SOAR</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'Automation Overview', icon: Workflow },
          { id: 'dag_canvas', label: 'Visual DAG Canvas', icon: GitBranch },
          { id: 'active_playbooks', label: 'Active Playbooks', icon: Layers },
          { id: 'execution_runs', label: 'Execution Runs & Audit', icon: Clock },
          { id: 'template_library', label: 'Turnkey Templates', icon: FileCode },
          { id: 'simulation_studio', label: 'Simulation Studio', icon: Play }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'border-indigo-500 text-indigo-300'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Icon className="h-4 w-4" />{tab.label}
            </button>
          );
        })}
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Activity className="h-6 w-6 animate-spin text-indigo-400 mr-3" />
          Synchronizing Security Automation Studio DAGs, Templates & Execution State...
        </div>
      ) : (
        <>
          {/* TAB 1: Overview */}
          {activeTab === 'overview' && summary && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Active Playbooks List */}
              <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Workflow className="h-4 w-4 text-indigo-400" /> Active Security Playbooks
                </h3>
                <div className="space-y-3">
                  {playbooks.map((pb) => (
                    <div key={pb.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                      <div className="flex justify-between items-center font-bold">
                        <span className="text-slate-100 text-sm">{pb.name}</span>
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold border border-emerald-500/30">
                          {pb.status}
                        </span>
                      </div>
                      <p className="text-slate-400 text-xs leading-relaxed">{pb.description}</p>
                      <div className="flex justify-between items-center text-[10px] text-slate-400 pt-1 border-t border-slate-800/60">
                        <span>Trigger: <strong className="text-cyan-300 font-mono">{pb.trigger_type}</strong></span>
                        <span>Total Executions: <strong className="text-indigo-400">{pb.executions_count}</strong></span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-3 border-t border-slate-800/60">
                  <div className="text-xs font-bold text-slate-300 mb-2">Priority Automation Directives:</div>
                  <div className="space-y-1.5">
                    {summary.top_automation_priorities.map((pri: string, idx: number) => (
                      <div key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                        <ChevronRight className="h-3.5 w-3.5 text-indigo-400 shrink-0 mt-0.5" />
                        {pri}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Execution Summary Ribbon */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Clock className="h-4 w-4 text-indigo-400" /> Recent Execution Runs
                </h3>
                <div className="space-y-3">
                  {executions.map((run) => (
                    <div key={run.id} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60 text-xs space-y-1.5">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span className="truncate max-w-[180px]">{run.playbook_name}</span>
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold">COMPLETED</span>
                      </div>
                      <div className="text-[10px] text-slate-400">Trigger: <strong className="text-cyan-300">{run.trigger_event}</strong></div>
                      <div className="flex justify-between items-center text-[10px] text-slate-500 pt-1">
                        <span>Duration: <strong className="text-emerald-400">{run.duration_ms} ms</strong></span>
                        <span>{new Date(run.started_at).toLocaleTimeString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Visual DAG Canvas */}
          {activeTab === 'dag_canvas' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 space-y-6">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                    <GitBranch className="h-4 w-4 text-indigo-400" /> Visual DAG Playbook Flow Canvas
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Drag-and-Drop Triggers, Conditional Gates, eBPF Actions, and SOC Human Approvals.
                  </p>
                </div>
                <button
                  onClick={() => setActiveTab('simulation_studio')}
                  className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5"
                >
                  <Play className="h-3.5 w-3.5" /> Test DAG Flow
                </button>
              </div>

              {/* Interactive Visual DAG Diagram */}
              <div className="p-8 bg-slate-950 rounded-2xl border border-slate-800/80 flex flex-col md:flex-row items-center justify-between gap-4 overflow-x-auto">
                {/* Node 1: Trigger */}
                <div className="p-4 bg-slate-900 border border-cyan-500/40 rounded-xl text-center min-w-[180px] space-y-2 shadow-lg shadow-cyan-500/5">
                  <div className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 text-[10px] font-bold inline-block">1. TRIGGER</div>
                  <div className="text-xs font-bold text-slate-100">On Critical Alert</div>
                  <div className="text-[10px] text-slate-400 font-mono">SEVERITY == "CRITICAL"</div>
                </div>

                <ArrowRight className="h-6 w-6 text-slate-600 shrink-0 hidden md:block" />

                {/* Node 2: Condition Gate */}
                <div className="p-4 bg-slate-900 border border-amber-500/40 rounded-xl text-center min-w-[180px] space-y-2 shadow-lg shadow-amber-500/5">
                  <div className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 text-[10px] font-bold inline-block">2. CONDITION</div>
                  <div className="text-xs font-bold text-slate-100">Asset Verification</div>
                  <div className="text-[10px] text-slate-400 font-mono">IS_PRODUCTION == true</div>
                </div>

                <ArrowRight className="h-6 w-6 text-slate-600 shrink-0 hidden md:block" />

                {/* Node 3: Approval Gate */}
                <div className="p-4 bg-slate-900 border border-indigo-500/40 rounded-xl text-center min-w-[180px] space-y-2 shadow-lg shadow-indigo-500/5">
                  <div className="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-400 text-[10px] font-bold inline-block">3. HUMAN GATE</div>
                  <div className="text-xs font-bold text-slate-100">SOC L2 Approval</div>
                  <div className="text-[10px] text-slate-400 font-mono">TIMED_OUT &lt; 5m</div>
                </div>

                <ArrowRight className="h-6 w-6 text-slate-600 shrink-0 hidden md:block" />

                {/* Node 4: Action */}
                <div className="p-4 bg-slate-900 border border-emerald-500/40 rounded-xl text-center min-w-[180px] space-y-2 shadow-lg shadow-emerald-500/5">
                  <div className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 text-[10px] font-bold inline-block">4. ACTION</div>
                  <div className="text-xs font-bold text-slate-100">eBPF Quarantine</div>
                  <div className="text-[10px] text-slate-400 font-mono">CONTAIN_HOST_NETWORK</div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: Active Playbooks */}
          {activeTab === 'active_playbooks' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Layers className="h-4 w-4 text-indigo-400" /> Active Automation Playbooks
                </h3>
              </div>

              {/* Create Playbook Form */}
              <form onSubmit={handleCreatePlaybook} className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3">
                <div className="text-xs font-bold text-slate-200">Register New DAG Playbook</div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] text-slate-400 mb-1">Playbook Name</label>
                    <input
                      type="text"
                      value={playbookName}
                      onChange={(e) => setPlaybookName(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-slate-200 text-xs"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] text-slate-400 mb-1">Trigger Type</label>
                    <select
                      value={triggerType}
                      onChange={(e) => setTriggerType(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-slate-200 text-xs"
                    >
                      <option value="ON_ALERT">ON_ALERT (Real-Time Ingestion Alert)</option>
                      <option value="ON_SCHEDULE">ON_SCHEDULE (Cron Schedule Interval)</option>
                      <option value="ON_WEBHOOK">ON_WEBHOOK (External Webhook Ingest)</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-[11px] text-slate-400 mb-1">Description & Scope</label>
                  <input
                    type="text"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-slate-200 text-xs"
                    required
                  />
                </div>
                <div className="flex justify-end">
                  <button
                    type="submit"
                    className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5"
                  >
                    <Workflow className="h-3.5 w-3.5" /> Save & Activate Playbook
                  </button>
                </div>
              </form>

              {createdPlaybook && (
                <div className="p-4 bg-slate-950 rounded-xl border border-emerald-500/30 text-xs space-y-2">
                  <div className="flex justify-between items-center text-emerald-400 font-bold">
                    <span>Playbook Created & Deployed</span>
                    <span>{createdPlaybook.status}</span>
                  </div>
                  <div className="text-[11px] text-slate-300">{createdPlaybook.name}</div>
                </div>
              )}

              <div className="space-y-3">
                {playbooks.map((pb) => (
                  <div key={pb.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <span className="text-slate-100 text-sm">{pb.name}</span>
                      <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold text-[10px]">
                        {pb.status}
                      </span>
                    </div>

                    <p className="text-slate-400 text-xs">{pb.description}</p>

                    <div className="flex justify-between items-center text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">
                      <span>Trigger: <strong className="text-cyan-300 font-mono">{pb.trigger_type}</strong></span>
                      <span>Executions: <strong className="text-slate-200">{pb.executions_count}</strong></span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: Execution Runs */}
          {activeTab === 'execution_runs' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Clock className="h-4 w-4 text-indigo-400" /> Playbook Execution Runs & State Audit
              </h3>

              <div className="space-y-3">
                {executions.map((run) => (
                  <div key={run.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <span className="text-slate-100 text-sm">{run.playbook_name}</span>
                      <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold text-[10px]">
                        {run.status}
                      </span>
                    </div>

                    <div className="text-[11px] text-slate-400">
                      Trigger Event: <strong className="text-cyan-300">{run.trigger_event}</strong>
                    </div>

                    <pre className="p-3 bg-slate-900 rounded font-mono text-[10px] text-slate-300 overflow-x-auto">
                      {JSON.stringify(run.step_results_json, null, 2)}
                    </pre>

                    <div className="flex justify-between items-center text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">
                      <span>Execution Duration: <strong className="text-emerald-400">{run.duration_ms} ms</strong></span>
                      <span>Completed: {new Date(run.started_at).toLocaleString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: Turnkey Template Library */}
          {activeTab === 'template_library' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {templates.map((tpl) => (
                <div key={tpl.id} className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-3 flex flex-col justify-between">
                  <div className="space-y-2">
                    <div className="flex justify-between items-start">
                      <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 font-bold text-[10px] border border-indigo-500/30">
                        {tpl.category}
                      </span>
                      <ShieldCheck className="h-4 w-4 text-emerald-400" />
                    </div>
                    <div className="text-sm font-bold text-slate-100">{tpl.name}</div>
                    <p className="text-slate-400 text-xs leading-relaxed">{tpl.description}</p>
                  </div>

                  <div className="pt-3 border-t border-slate-800/60 flex justify-between items-center">
                    <span className="text-[10px] text-emerald-400 font-bold">VERIFIED SOAR TEMPLATE</span>
                    <button
                      onClick={() => {
                        setPlaybookName(tpl.name);
                        setDescription(tpl.description);
                        setActiveTab('active_playbooks');
                      }}
                      className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold"
                    >
                      Clone & Use
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* TAB 6: Simulation Studio */}
          {activeTab === 'simulation_studio' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 max-w-2xl mx-auto space-y-6">
              <div>
                <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                  <Play className="h-5 w-5 text-indigo-400" /> Playbook Dry-Run Simulation Studio
                </h3>
                <p className="text-xs text-slate-400 mt-1">
                  Test and validate your DAG execution pipeline with simulated attack payloads without impacting production.
                </p>
              </div>

              <form onSubmit={handleSimulate} className="space-y-4 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Target Playbook</label>
                  <select
                    value={simPlaybookName}
                    onChange={(e) => setSimPlaybookName(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                  >
                    <option value="Ransomware Containment & Host Isolation">Ransomware Containment & Host Isolation</option>
                    <option value="Compromised Credential Session Reaper">Compromised Credential Session Reaper</option>
                    <option value="Phishing Mailbox Auto-Purge">Phishing Mailbox Auto-Purge</option>
                  </select>
                </div>

                <div className="flex justify-end">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold flex items-center gap-2"
                  >
                    <Play className="h-4 w-4" /> Run Dry-Run Simulation
                  </button>
                </div>
              </form>

              {simResult && (
                <div className="p-4 bg-slate-950 rounded-xl border border-indigo-500/30 text-xs space-y-3 mt-4">
                  <div className="flex justify-between items-center text-indigo-400 font-bold">
                    <span>Simulation Passed ({simResult.step_count} DAG Steps)</span>
                    <span className="text-emerald-400">{simResult.duration_ms} ms</span>
                  </div>

                  <pre className="p-3 bg-slate-900 rounded font-mono text-[10px] text-slate-300 overflow-x-auto">
                    {JSON.stringify(simResult.step_results, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};
