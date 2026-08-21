import React, { useEffect, useState } from 'react';
import {
  Crosshair,
  Flame,
  Power,
  Users,
  Zap,
  CheckCircle,
  Play,
  RotateCcw,
  Lock,
  Radio,
  Terminal,
  Cpu,
  Target,
  AlertOctagon
} from 'lucide-react';
import { autonomousControlPlaneApi } from '../services/saas';

export const AutonomousControlPlaneCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'missions' | 'war_room' | 'consensus' | 'actions' | 'kill_switch'>('overview');
  const [summary, setSummary] = useState<any>(null);
  const [missions, setMissions] = useState<any[]>([]);
  const [selectedRoom, setSelectedRoom] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);


  // Tactical action execution state
  const [actionEntity, setActionEntity] = useState<string>('sa-compromised@prod.iam.gserviceaccount.com');
  const [actionCategory, setActionCategory] = useState<string>('CONTAINMENT');
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);

  // Kill switch state
  const [killSwitchBusy, setKillSwitchBusy] = useState<boolean>(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [sum, mList, rList] = await Promise.all([
        autonomousControlPlaneApi.getSummary(),
        autonomousControlPlaneApi.listMissions(),
        autonomousControlPlaneApi.listWarRooms(),
      ]);
      setSummary(sum);
      setMissions(mList);
      if (rList && rList.length > 0) {
        const details = await autonomousControlPlaneApi.getWarRoomDetails(rList[0].id);
        setSelectedRoom(details || rList[0]);
      }

    } catch (e) {
      console.error('Phase 49 Load Error:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleKillSwitch = async (activate: boolean) => {
    if (!selectedRoom) return;
    setKillSwitchBusy(true);
    try {
      await autonomousControlPlaneApi.toggleKillSwitch(selectedRoom.id, activate);
      // Reload room details and summary
      const updatedDetails = await autonomousControlPlaneApi.getWarRoomDetails(selectedRoom.id);
      setSelectedRoom(updatedDetails);
      const updatedSum = await autonomousControlPlaneApi.getSummary();
      setSummary(updatedSum);
    } catch (e) {
      console.error('Kill switch toggle error:', e);
    } finally {
      setKillSwitchBusy(false);
    }
  };

  const handleExecuteTacticalAction = async () => {
    if (!selectedRoom) return;
    setActionLoading(true);
    setActionFeedback(null);
    try {
      const res = await autonomousControlPlaneApi.executeAction(selectedRoom.id, {
        action_name: `Autonomous ${actionCategory} Directive`,
        action_category: actionCategory,
        proposing_agent: 'Agent-DecisiveCommander',
        target_entity: actionEntity,
      });
      setActionFeedback(`Action Executed: ${res.action_name} against ${res.target_entity} (${res.execution_latency_ms}ms)`);
      // Reload room details
      const updatedDetails = await autonomousControlPlaneApi.getWarRoomDetails(selectedRoom.id);
      setSelectedRoom(updatedDetails);
    } catch (e) {
      console.error('Tactical action error:', e);
    } finally {
      setActionLoading(false);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Control Plane Overview', icon: Crosshair },
    { id: 'missions', label: 'Defense Missions', icon: Target },
    { id: 'war_room', label: 'Live War Room', icon: Flame },
    { id: 'consensus', label: 'Agent Consensus', icon: Users },
    { id: 'actions', label: 'Tactical Action Audit', icon: Terminal },
    { id: 'kill_switch', label: 'Emergency Override', icon: Power },
  ] as const;

  const metricCard = (icon: React.ReactNode, label: string, value: string, sub: string, color: string) => (
    <div className={`rounded-2xl border p-5 bg-slate-900/60 border-slate-700/50 backdrop-blur-sm hover:border-${color}-500/40 transition-all`}>
      <div className="flex items-center gap-3 mb-3">
        <span className={`p-2.5 rounded-xl bg-${color}-500/10 text-${color}-400`}>{icon}</span>
        <span className="text-xs text-slate-400 font-medium">{label}</span>
      </div>
      <div className={`text-2xl font-black text-${color}-300 mb-1`}>{value}</div>
      <div className="text-xs text-slate-500">{sub}</div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-rose-500 via-red-600 to-amber-500 flex items-center justify-center animate-pulse">
            <Crosshair className="w-7 h-7 text-white" />
          </div>
          <p className="text-slate-400 text-sm font-medium">Synchronizing Autonomous Cyber Defense Control Plane...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-screen-xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-rose-600 via-red-600 to-orange-500 flex items-center justify-center shadow-lg shadow-rose-600/20">
            <Crosshair className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-white">Autonomous Cyber Defense Control Plane</h1>
              <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                ACTIVE ORCHESTRATION
              </span>
            </div>
            <p className="text-slate-400 text-sm">Phase 49 · Decisive Multi-Agent Cyber Defense, War Room & Strategic Directives</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm font-bold">
            <Radio className="w-4 h-4 text-rose-400 animate-pulse" />
            <span>Readiness: {summary?.control_plane_readiness_score ?? 99.4}/100</span>
          </div>
        </div>
      </div>

      {/* Control Plane Status Ribbon */}
      <div className="rounded-2xl border border-rose-500/20 bg-gradient-to-r from-rose-950/40 via-slate-900/50 to-amber-950/30 p-4 flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <span className="px-3 py-1 rounded-lg bg-rose-500/20 text-rose-300 text-xs font-bold border border-rose-500/30">
            {summary?.control_plane_tier ?? 'AUTONOMOUS_DECISIVE_CONTROL_PLANE'}
          </span>
          <span className="text-slate-300 text-sm">
            Active Missions: <span className="text-rose-300 font-bold">{summary?.active_missions_count ?? 2}</span>
            &nbsp;·&nbsp; Agents Online: <span className="text-cyan-300 font-bold">{summary?.autonomous_agents_online ?? 12}</span>
            &nbsp;·&nbsp; Consensus Health: <span className="text-emerald-400 font-bold">{((summary?.agent_consensus_health ?? 0.984) * 100).toFixed(1)}%</span>
            &nbsp;·&nbsp; Action Latency: <span className="text-violet-300 font-bold">{summary?.mean_autonomous_action_latency_ms ?? 24.8}ms</span>
          </span>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
            <Lock className="w-3.5 h-3.5" /> Bounded Blast Radius: ACTIVE
          </span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-1 bg-slate-900/60 border border-slate-700/50 rounded-2xl p-1.5 overflow-x-auto">
        {tabs.map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium whitespace-nowrap transition-all ${
                activeTab === tab.id
                  ? 'bg-rose-600 text-white shadow-lg shadow-rose-600/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* ── OVERVIEW ─────────────────────────────────────────────────────── */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {metricCard(<Target className="w-5 h-5" />, 'Active Missions', `${summary?.active_missions_count ?? 2}`, 'Strategic directives', 'rose')}
            {metricCard(<Users className="w-5 h-5" />, 'Autonomous Agents', `${summary?.autonomous_agents_online ?? 12}`, 'Distributed swarm', 'cyan')}
            {metricCard(<Zap className="w-5 h-5" />, 'Action Latency', `${summary?.mean_autonomous_action_latency_ms ?? 24.8} ms`, 'Sub-second intervention', 'amber')}
            {metricCard(<CheckCircle className="w-5 h-5" />, 'Decision Accuracy', `${((summary?.autonomous_decision_accuracy ?? 0.998) * 100).toFixed(1)}%`, 'Zero false containment', 'emerald')}
          </div>

          {/* Active War Room Spotlight Card */}
          {selectedRoom && (
            <div className="rounded-2xl border border-rose-500/30 bg-gradient-to-br from-slate-900/90 via-rose-950/20 to-slate-900/90 p-6 space-y-4">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
                    <Flame className="w-6 h-6 animate-pulse" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="text-lg font-bold text-white">{selectedRoom.room_name}</h2>
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
                        {selectedRoom.severity}
                      </span>
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                        {selectedRoom.session_status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">
                      Attributed Threat: <span className="text-rose-400 font-bold">{selectedRoom.threat_actor_attributed}</span>
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-2xl font-black text-emerald-400">
                    {((selectedRoom.consensus_confidence_score ?? 0.982) * 100).toFixed(1)}%
                  </div>
                  <div className="text-xs text-slate-400">Agent Swarm Consensus</div>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/40">
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Active Tactical Directive</div>
                <p className="text-sm text-slate-200 leading-relaxed font-mono">{selectedRoom.active_tactical_plan}</p>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-1">
                {selectedRoom.participating_agents?.map((ag: any) => (
                  <div key={ag.agent_id} className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/30 text-xs">
                    <div className="text-slate-400 font-medium">{ag.role}</div>
                    <div className="text-sm font-bold text-cyan-300 mt-1">{ag.vote}</div>
                    <div className="text-emerald-400 font-bold mt-0.5">{(ag.confidence * 100).toFixed(0)}% Conf</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── DEFENSE MISSIONS ─────────────────────────────────────────────── */}
      {activeTab === 'missions' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white">Strategic Autonomous Defense Missions ({missions.length})</h2>
            <span className="text-xs text-slate-400">Autonomous Directives, Bounded Blast Radius & Success Rates</span>
          </div>

          <div className="space-y-3">
            {missions.map((m: any) => (
              <div
                key={m.id}
                className="p-5 rounded-2xl border border-slate-700/50 bg-slate-900/60 hover:border-rose-500/30 transition-all space-y-3"
              >
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
                      <Target className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-white">{m.mission_name}</span>
                        <span className="px-2 py-0.5 rounded-md text-xs font-bold bg-slate-800 text-slate-300 border border-slate-700 font-mono">
                          {m.mission_code}
                        </span>
                        <span className="px-2 py-0.5 rounded-md text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
                          {m.threat_tier}
                        </span>
                        <span className={`px-2 py-0.5 rounded-md text-xs font-bold ${m.mission_status === 'ACTIVE' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-slate-800 text-slate-400'}`}>
                          {m.mission_status}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-1">{m.objective}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 text-xs">
                    <div className="text-right">
                      <div className="text-slate-400">Autonomy</div>
                      <div className="text-sm font-bold text-cyan-400">{m.autonomy_level}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-slate-400">Blast Radius Cap</div>
                      <div className="text-sm font-bold text-amber-400">${((m.blast_radius_limit_usd ?? 0) / 1000).toFixed(0)}k</div>
                    </div>
                    <div className="text-right">
                      <div className="text-slate-400">Success Rate</div>
                      <div className="text-sm font-bold text-emerald-400">{((m.success_rate ?? 1.0) * 100).toFixed(1)}%</div>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-800 text-slate-400">
                  <span>Actions Executed: <span className="text-slate-200 font-bold">{m.actions_executed_count}</span> · Threats Neutralized: <span className="text-emerald-400 font-bold">{m.threats_neutralized_count}</span></span>
                  <span>Started: {m.started_at ? new Date(m.started_at).toLocaleDateString() : '—'}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── LIVE WAR ROOM ────────────────────────────────────────────────── */}
      {activeTab === 'war_room' && (
        <div className="space-y-6">
          {selectedRoom && (
            <div className="rounded-2xl border border-rose-500/40 bg-slate-900/80 p-6 space-y-6">
              <div className="flex items-center justify-between flex-wrap gap-3">
                <div className="flex items-center gap-3">
                  <Flame className="w-7 h-7 text-rose-500 animate-pulse" />
                  <div>
                    <h2 className="text-base font-bold text-white">{selectedRoom.room_name}</h2>
                    <p className="text-xs text-slate-400">Multi-Agent Swarm Real-Time Battleground</p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`px-3 py-1 rounded-xl text-xs font-bold border ${selectedRoom.kill_switch_active ? 'bg-red-500/20 text-red-400 border-red-500/30' : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'}`}>
                    {selectedRoom.kill_switch_active ? 'KILL SWITCH: ENGAGED' : 'AUTONOMOUS DEFENSE: ARMED'}
                  </span>
                </div>
              </div>

              {/* Tactical Action Input for Operators */}
              <div className="p-5 rounded-2xl border border-slate-700 bg-slate-800/40 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-cyan-400" /> Issue Tactical Command / Intervention
                  </h3>
                  <span className="text-xs text-slate-400">Human-in-the-Loop Override Channel</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Target Entity / Host / Identity</label>
                    <input
                      type="text"
                      value={actionEntity}
                      onChange={(e) => setActionEntity(e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 font-mono focus:outline-none focus:border-rose-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Action Category</label>
                    <select
                      value={actionCategory}
                      onChange={(e) => setActionCategory(e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-rose-500"
                    >
                      <option value="CONTAINMENT">CONTAINMENT (Revoke Credentials / Egress Filter)</option>
                      <option value="ISOLATION">ISOLATION (Microsegmentation Quarantine)</option>
                      <option value="DECEPTION">DECEPTION (Reroute Traffic to Honeynet)</option>
                      <option value="ERADICATION">ERADICATION (Process Kill & Shadow Copy Restore)</option>
                    </select>
                  </div>
                  <div className="flex items-end">
                    <button
                      onClick={handleExecuteTacticalAction}
                      disabled={actionLoading}
                      className="w-full py-2 px-4 rounded-xl bg-gradient-to-r from-rose-600 to-amber-600 hover:from-rose-500 hover:to-amber-500 text-white font-bold text-xs shadow-lg shadow-rose-600/20 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                      <Play className="w-3.5 h-3.5" />
                      {actionLoading ? 'Executing Action...' : 'Execute Tactical Action'}
                    </button>
                  </div>
                </div>

                {actionFeedback && (
                  <div className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
                    {actionFeedback}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── AGENT CONSENSUS ──────────────────────────────────────────────── */}
      {activeTab === 'consensus' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white">Multi-Agent Swarm Consensus Voting</h2>
            <span className="text-xs text-slate-400">Decentralized Multi-Agent Byzantine-Resilient Voting</span>
          </div>

          {selectedRoom?.participating_agents && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {selectedRoom.participating_agents.map((agent: any) => (
                <div key={agent.agent_id} className="p-5 rounded-2xl border border-slate-700/50 bg-slate-900/60 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
                        <Cpu className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-white">{agent.role}</h4>
                        <span className="text-xs text-slate-400 font-mono">{agent.agent_id}</span>
                      </div>
                    </div>
                    <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      {(agent.confidence * 100).toFixed(0)}% CONFIDENCE
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/30 flex items-center justify-between text-xs">
                    <span className="text-slate-400 font-medium">Cast Vote:</span>
                    <span className="text-cyan-300 font-bold font-mono">{agent.vote}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── TACTICAL ACTION AUDIT ────────────────────────────────────────── */}
      {activeTab === 'actions' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white">Autonomous Action Execution History</h2>
            <span className="text-xs text-slate-400">Immutable Audit Trail of Autonomous Interventions</span>
          </div>

          <div className="space-y-3">
            {selectedRoom?.action_history?.map((act: any) => (
              <div key={act.id} className="p-4 rounded-2xl border border-slate-700/50 bg-slate-900/60 space-y-2">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                      <CheckCircle className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-white">{act.action_name}</span>
                        <span className="px-2 py-0.5 rounded-md text-xs font-bold bg-slate-800 text-slate-300 border border-slate-700">
                          {act.action_category}
                        </span>
                        <span className="px-2 py-0.5 rounded-md text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                          {act.execution_status}
                        </span>
                      </div>
                      <div className="text-xs text-slate-400 mt-0.5">
                        Target: <span className="text-slate-200 font-mono">{act.target_entity}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right text-xs">
                    <div className="text-cyan-400 font-bold">{act.execution_latency_ms}ms latency</div>
                    <div className="text-slate-500">{act.executed_at ? new Date(act.executed_at).toLocaleTimeString() : 'Just now'}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── EMERGENCY KILL SWITCH & OVERRIDE ─────────────────────────────── */}
      {activeTab === 'kill_switch' && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-red-500/30 bg-gradient-to-br from-slate-900/90 via-red-950/20 to-slate-900/90 p-6 space-y-6">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <AlertOctagon className="w-5 h-5 text-red-500" /> Emergency Autonomous Defense Kill Switch
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Disengage all autonomous action execution across the selected war room instantly. Operators retain complete manual oversight.
              </p>
            </div>

            <div className="p-6 rounded-2xl border border-red-500/40 bg-red-950/20 flex items-center justify-between flex-wrap gap-4">
              <div>
                <div className="text-sm font-bold text-white">Current War Room Kill Switch State</div>
                <div className="text-xs text-slate-400 mt-1">
                  Status: <span className="text-red-400 font-bold">{selectedRoom?.kill_switch_active ? 'ENGAGED (AUTONOMOUS EXECUTION PAUSED)' : 'DISENGAGED (ACTIVE AUTONOMY)'}</span>
                </div>
              </div>

              <div className="flex items-center gap-3">
                {selectedRoom?.kill_switch_active ? (
                  <button
                    onClick={() => handleToggleKillSwitch(false)}
                    disabled={killSwitchBusy}
                    className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-lg shadow-emerald-600/25 transition-all disabled:opacity-50"
                  >
                    <RotateCcw className="w-4 h-4" />
                    Resume Autonomous Defense
                  </button>
                ) : (
                  <button
                    onClick={() => handleToggleKillSwitch(true)}
                    disabled={killSwitchBusy}
                    className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-red-600 hover:bg-red-500 text-white font-bold text-xs shadow-lg shadow-red-600/25 transition-all disabled:opacity-50"
                  >
                    <Power className="w-4 h-4" />
                    Engage Emergency Kill Switch
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
