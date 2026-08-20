import React, { useEffect, useState } from 'react';
import {
  Zap,
  Activity,
  Play,
  CheckCircle2,
  Server,
  Layers,
  PowerOff
} from 'lucide-react';

import { saasApi } from '../services/saas';

export const SOARCommandCenter: React.FC = () => {
  const [playbooks, setPlaybooks] = useState<any[]>([]);
  const [executions, setExecutions] = useState<any[]>([]);
  const [connectors, setConnectors] = useState<any[]>([]);
  const [killSwitchActive, setKillSwitchActive] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [togglingKs, setTogglingKs] = useState<boolean>(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    fetchSOARData();
  }, []);

  const fetchSOARData = async () => {
    try {
      setLoading(true);
      const [pData, eData, cData, ksData] = await Promise.all([
        saasApi.listSOARPlaybooks(),
        saasApi.listSOARExecutions(),
        saasApi.listSOARConnectors(),
        saasApi.getSOARKillSwitch()
      ]);
      setPlaybooks(pData);
      setExecutions(eData);
      setConnectors(cData);
      setKillSwitchActive(ksData?.is_active || false);
    } catch (err) {
      console.error('Failed to load SOAR 2.0 data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleKillSwitch = async () => {
    try {
      setTogglingKs(true);
      const res = await saasApi.toggleSOARKillSwitch({
        is_active: !killSwitchActive,
        reason: !killSwitchActive ? 'Emergency containment lock requested by SOC analyst' : 'Manual kill switch release'
      });
      setKillSwitchActive(res.is_active);
    } catch (err) {
      console.error('Kill switch toggle error:', err);
    } finally {
      setTogglingKs(false);
    }
  };

  const handleDryRun = async (playbookId: string) => {
    try {
      setActionLoading(`dry_${playbookId}`);
      await saasApi.dryRunSOARPlaybook(playbookId, {});
      await fetchSOARData();
    } catch (err) {
      console.error('Dry-run error:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleExecute = async (playbookId: string) => {
    try {
      setActionLoading(`exec_${playbookId}`);
      await saasApi.executeSOARPlaybook(playbookId, {});
      await fetchSOARData();
    } catch (err) {
      console.error('Execution error:', err);
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Zap className="h-7 w-7 text-cyan-400" />
            Autonomous SOC & SOAR 2.0 Command Center
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Declarative playbook orchestration, automated containment workflows, connector ecosystem, and emergency kill-switch.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchSOARData}
            className="flex items-center gap-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-colors"
          >
            <Activity className="h-4 w-4 text-cyan-400" /> Refresh State
          </button>
        </div>
      </div>

      {/* Emergency Kill Switch Banner */}
      <div
        className={`p-4 rounded-xl border flex flex-col sm:flex-row items-center justify-between gap-4 ${
          killSwitchActive
            ? 'bg-rose-950/40 border-rose-500/50 text-rose-200'
            : 'bg-slate-900/60 border-slate-800/80 text-slate-300'
        }`}
      >
        <div className="flex items-center gap-3">
          <PowerOff className={`h-6 w-6 ${killSwitchActive ? 'text-rose-400 animate-pulse' : 'text-slate-500'}`} />
          <div>
            <div className="text-sm font-bold">
              Emergency Containment Kill Switch:{' '}
              <span className={killSwitchActive ? 'text-rose-400' : 'text-emerald-400'}>
                {killSwitchActive ? 'ACTIVE (AUTOMATED ACTIONS BLOCKED)' : 'DISARMED (AUTONOMOUS OPS ACTIVE)'}
              </span>
            </div>
            <div className="text-xs text-slate-400 mt-0.5">
              {killSwitchActive
                ? 'All automated and autonomous remediation workflows are halted. Manual approval required for all actions.'
                : 'Automated containment workflows execute normally according to tenant autonomy policy.'}
            </div>
          </div>
        </div>

        <button
          onClick={handleToggleKillSwitch}
          disabled={togglingKs}
          className={`px-4 py-2 text-xs font-bold rounded-lg transition-all flex items-center gap-2 ${
            killSwitchActive
              ? 'bg-emerald-600 hover:bg-emerald-500 text-slate-950'
              : 'bg-rose-600 hover:bg-rose-500 text-white'
          }`}
        >
          {togglingKs && <Activity className="h-4 w-4 animate-spin" />}
          {killSwitchActive ? 'Disarm Kill Switch' : 'ENGAGE EMERGENCY KILL SWITCH'}
        </button>
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Activity className="h-8 w-8 animate-spin text-cyan-400 mr-3" />
          Loading SOAR playbooks and connector topologies...
        </div>
      ) : (
        <>
          {/* Key Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Declarative Playbooks</div>
              <div className="text-2xl font-bold text-slate-100 mt-1">{playbooks.length}</div>
              <div className="text-[11px] text-cyan-400 mt-1 flex items-center gap-1">
                <Layers className="h-3 w-3" /> Version-controlled Workflows
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Execution Sessions</div>
              <div className="text-2xl font-bold text-emerald-400 mt-1">{executions.length}</div>
              <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3 text-emerald-400" /> Containment Audited
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">SOAR Connectors</div>
              <div className="text-2xl font-bold text-amber-400 mt-1">{connectors.length}</div>
              <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
                <Server className="h-3 w-3 text-amber-400" /> Firewall, EDR, IAM, SIEM
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Average Action Latency</div>
              <div className="text-2xl font-bold text-indigo-400 mt-1">16.4 ms</div>
              <div className="text-[11px] text-indigo-400 mt-1 flex items-center gap-1">
                <Zap className="h-3 w-3" /> High-Velocity Containment
              </div>
            </div>
          </div>

          {/* Playbooks Catalog */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
            <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
              <Layers className="h-5 w-5 text-cyan-400" />
              Declarative SOAR Playbook Library
            </h2>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {playbooks.map((pb) => (
                <div key={pb.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800/80 space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm font-bold text-slate-100">{pb.name}</div>
                      <div className="text-[11px] text-slate-400 mt-0.5">{pb.description}</div>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                      v{pb.version} {pb.category}
                    </span>
                  </div>

                  <div className="bg-slate-900/80 p-3 rounded-lg text-xs space-y-1">
                    <div className="text-slate-400">
                      Steps Configured: <strong className="text-slate-200">{pb.steps_count} actions</strong>
                    </div>
                    <div className="text-slate-400">
                      Trigger: <span className="font-mono text-cyan-300">{pb.trigger_type}</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
                    <button
                      onClick={() => handleDryRun(pb.id)}
                      disabled={actionLoading === `dry_${pb.id}`}
                      className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-colors flex items-center gap-1.5"
                    >
                      {actionLoading === `dry_${pb.id}` ? <Activity className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5 text-amber-400" />}
                      Simulate Dry-Run
                    </button>
                    <button
                      onClick={() => handleExecute(pb.id)}
                      disabled={actionLoading === `exec_${pb.id}` || killSwitchActive}
                      className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-800 disabled:text-slate-500 text-slate-950 text-xs font-bold rounded-lg transition-all flex items-center gap-1.5"
                    >
                      {actionLoading === `exec_${pb.id}` ? <Activity className="h-3.5 w-3.5 animate-spin" /> : <Zap className="h-3.5 w-3.5" />}
                      Execute Containment
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Connectors Health Grid */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
            <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
              <Server className="h-5 w-5 text-amber-400" />
              SOAR Security Tool Connectors
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {connectors.map((c) => (
                <div key={c.id} className="p-3.5 bg-slate-950/60 rounded-xl border border-slate-800/80 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-200">{c.connector_type}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {c.health_status}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-300 font-medium">{c.connector_name}</div>
                  <div className="text-[10px] text-slate-500 font-mono">Latency: {c.latency_ms} ms</div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};
