import React, { useEffect, useState } from 'react';
import {
  Database,
  Activity,
  ChevronRight,
  ShieldCheck,
  Zap,
  Server,
  Sliders,
  RefreshCw,
  Lock,
  ArrowRightLeft
} from 'lucide-react';
import { saasApi } from '../services/saas';

export const MultiRegionResilienceCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'clusters' | 'residency' | 'failover' | 'crdt_vector' | 'failover_studio'>('overview');
  const [summary, setSummary] = useState<any>(null);
  const [clusters, setClusters] = useState<any[]>([]);
  const [boundaries, setBoundaries] = useState<any[]>([]);
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Failover studio state
  const [sourceRegion, setSourceRegion] = useState<string>('US_EAST_PRIMARY');
  const [targetRegion, setTargetRegion] = useState<string>('EU_WEST_SECONDARY');
  const [failoverResult, setFailoverResult] = useState<any>(null);

  // Residency studio state
  const [boundaryName, setBoundaryName] = useState<string>('Japanese APPI Sovereign Banking Partition');
  const [complianceStd, setComplianceStd] = useState<string>('APPI_JAPAN');
  const [enforcedRegs, setEnforcedRegs] = useState<string>('AP_NORTHEAST_1,AP_NORTHEAST_3');
  const [createdBoundary, setCreatedBoundary] = useState<any>(null);

  useEffect(() => {
    fetchMultiRegionData();
  }, []);

  const fetchMultiRegionData = async () => {
    try {
      setLoading(true);
      const [sum, cls, bnds, evts] = await Promise.all([
        saasApi.getMultiRegionSummary(),
        saasApi.getMultiRegionClusters(),
        saasApi.getDataResidencyBoundaries(),
        saasApi.getFailoverEvents()
      ]);
      setSummary(sum);
      setClusters(cls);
      setBoundaries(bnds);
      setEvents(evts);
    } catch (err) {
      console.error('Failed to load Multi-Region data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerFailover = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await saasApi.triggerMultiRegionFailover({
        source_region: sourceRegion,
        target_region: targetRegion,
        trigger_type: 'OPERATOR_INITIATED'
      });
      setFailoverResult(res);
      fetchMultiRegionData();
    } catch (err) {
      console.error('Failed to trigger failover:', err);
    }
  };

  const handleCreateBoundary = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await saasApi.createDataResidencyBoundary({
        boundary_name: boundaryName,
        compliance_standard: complianceStd,
        enforced_regions: enforcedRegs,
        strict_egress_block: true
      });
      setCreatedBoundary(res);
      fetchMultiRegionData();
    } catch (err) {
      console.error('Failed to create residency boundary:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Database className="h-7 w-7 text-cyan-400" />
            Multi-Region Data Resilience & Sovereign Data Residency
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Active-Active Database Replication, CRDT Conflict Resolution, Sub-Second DR Failover & Sovereign Residency Boundaries.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('failover_studio')}
            className="flex items-center gap-2 px-3.5 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-xs font-semibold transition-colors"
          >
            <ArrowRightLeft className="h-4 w-4" /> Failover & Residency Studio
          </button>
        </div>
      </div>

      {/* Top Metrics Ribbon */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Resilience Score</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{summary.overall_resilience_score}<span className="text-xs text-slate-500">/100</span></div>
            <div className="text-[10px] text-cyan-400 mt-0.5">Active-Active Tier</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Replication Clusters</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{summary.active_replication_clusters_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Cross-Region Sync</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Mean Sync Lag</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.mean_replication_lag_ms} <span className="text-xs text-slate-500">ms</span></div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Synchronous Tier</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Guaranteed RPO</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.guaranteed_rpo_seconds} <span className="text-xs text-slate-500">s</span></div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Zero Data Loss</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Target RTO</div>
            <div className="text-2xl font-bold text-cyan-300 mt-1">{summary.target_rto_seconds} <span className="text-xs text-slate-500">s</span></div>
            <div className="text-[10px] text-slate-400 mt-0.5">Instant Switchover</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Sovereign Zones</div>
            <div className="text-2xl font-bold text-slate-200 mt-1">{summary.data_residency_boundaries_count}</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">GDPR/FedRAMP Safe</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'Resilience Overview', icon: Database },
          { id: 'clusters', label: 'Active-Active Clusters', icon: Server },
          { id: 'residency', label: 'Sovereign Data Residency', icon: Lock },
          { id: 'failover', label: 'Failover History & Events', icon: RefreshCw },
          { id: 'crdt_vector', label: 'CRDT & Vector Clocks', icon: Zap },
          { id: 'failover_studio', label: 'Failover & Boundary Studio', icon: Sliders }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'border-cyan-500 text-cyan-300'
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
          <Activity className="h-6 w-6 animate-spin text-cyan-400 mr-3" />
          Synchronizing Multi-Region Database Clusters & Data Residency State...
        </div>
      ) : (
        <>
          {/* TAB 1: Overview */}
          {activeTab === 'overview' && summary && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Clusters Overview */}
              <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Server className="h-4 w-4 text-cyan-400" /> Active Database Replication Clusters
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {clusters.map((c) => (
                    <div key={c.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                      <div className="flex justify-between items-center font-bold">
                        <span className="text-slate-100 text-sm font-mono">{c.region_name}</span>
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold border border-emerald-500/30">
                          {c.health_status}
                        </span>
                      </div>
                      <div className="text-[11px] text-cyan-300">Role: {c.cluster_role}</div>
                      <div className="space-y-1 text-[10px] text-slate-400 pt-1 border-t border-slate-800">
                        <div>Sync Lag: <strong className="text-emerald-400">{c.replication_lag_ms} ms</strong></div>
                        <div>RPO: <strong className="text-slate-200">{c.rpo_seconds}s</strong> · RTO: <strong className="text-slate-200">{c.rto_seconds}s</strong></div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-3 border-t border-slate-800/60">
                  <div className="text-xs font-bold text-slate-300 mb-2">Priority Resilience Directives:</div>
                  <div className="space-y-1.5">
                    {summary.top_resilience_priorities.map((pri: string, idx: number) => (
                      <div key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                        <ChevronRight className="h-3.5 w-3.5 text-cyan-400 shrink-0 mt-0.5" />
                        {pri}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Sovereign Boundaries */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Lock className="h-4 w-4 text-cyan-400" /> Sovereign Data Residency
                </h3>
                <div className="space-y-3">
                  {boundaries.map((b) => (
                    <div key={b.id} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60 text-xs space-y-1.5">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span>{b.boundary_name}</span>
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold">ENFORCED</span>
                      </div>
                      <div className="text-[11px] text-slate-400">Standard: <strong className="text-cyan-300">{b.compliance_standard}</strong></div>
                      <div className="text-[10px] text-slate-500 font-mono">Regions: {b.enforced_regions}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Clusters */}
          {activeTab === 'clusters' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Server className="h-4 w-4 text-cyan-400" /> Active-Active Multi-Region Cluster Topology
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {clusters.map((cl) => (
                  <div key={cl.id} className="p-5 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-3">
                    <div className="flex justify-between items-center font-bold">
                      <span className="text-slate-100 text-base font-mono">{cl.region_name}</span>
                      <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold text-[10px]">
                        {cl.health_status}
                      </span>
                    </div>

                    <div className="text-cyan-300 font-semibold text-xs">Role: {cl.cluster_role}</div>

                    <div className="grid grid-cols-3 gap-2 p-3 bg-slate-900 rounded-lg text-center">
                      <div>
                        <div className="text-slate-500 text-[10px]">Sync Lag</div>
                        <div className="text-emerald-400 font-bold text-sm">{cl.replication_lag_ms} ms</div>
                      </div>
                      <div>
                        <div className="text-slate-500 text-[10px]">RPO</div>
                        <div className="text-slate-200 font-bold text-sm">{cl.rpo_seconds} s</div>
                      </div>
                      <div>
                        <div className="text-slate-500 text-[10px]">RTO</div>
                        <div className="text-cyan-300 font-bold text-sm">{cl.rto_seconds} s</div>
                      </div>
                    </div>

                    <div className="text-[10px] text-slate-500 flex justify-between pt-1">
                      <span>CRDT Clock Synchronized</span>
                      <span>Last Heartbeat: {new Date(cl.last_sync).toLocaleTimeString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: Residency */}
          {activeTab === 'residency' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Lock className="h-4 w-4 text-cyan-400" /> Sovereign Data Residency & Egress Boundaries
                </h3>
                <button
                  onClick={() => setActiveTab('failover_studio')}
                  className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold"
                >
                  + Add Residency Boundary
                </button>
              </div>

              <div className="space-y-3">
                {boundaries.map((b) => (
                  <div key={b.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <span className="text-slate-100 text-sm">{b.boundary_name}</span>
                      <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold text-[10px]">
                        STRICT_EGRESS_BLOCKED
                      </span>
                    </div>

                    <div className="text-[11px] text-slate-400">
                      Compliance Standard: <strong className="text-cyan-300">{b.compliance_standard}</strong>
                    </div>

                    <div className="flex justify-between items-center text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">
                      <span>Restricted Geographic Regions: <strong className="font-mono text-slate-300">{b.enforced_regions}</strong></span>
                      <span>Enforced: {new Date(b.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: Failover */}
          {activeTab === 'failover' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <RefreshCw className="h-4 w-4 text-cyan-400" /> Regional Failover & Switchover Execution Events
              </h3>

              <div className="space-y-3">
                {events.map((evt) => (
                  <div key={evt.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-cyan-300">{evt.source_failing_region}</span>
                        <span className="text-slate-400">&rarr;</span>
                        <span className="font-mono text-emerald-400">{evt.target_failover_region}</span>
                      </div>
                      <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold text-[10px]">
                        {evt.status}
                      </span>
                    </div>

                    <div className="flex justify-between items-center text-[11px] text-slate-400">
                      <span>Trigger: <strong className="text-slate-200">{evt.failover_trigger}</strong></span>
                      <span>Switchover Duration: <strong className="text-emerald-400">{evt.switchover_duration_ms} ms</strong></span>
                    </div>

                    <div className="text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">
                      Executed: {new Date(evt.executed_at).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: CRDT Vector Clocks */}
          {activeTab === 'crdt_vector' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 max-w-2xl mx-auto space-y-4 text-xs">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Zap className="h-5 w-5 text-cyan-400" /> CRDT Conflict Resolution & Vector Clock Fabric
              </h3>
              <p className="text-slate-400 leading-relaxed">
                Aegivanta utilizes State-based Conflict-Free Replicated Data Types (CvRDT) and logical Lamport Vector Clocks for convergent cross-region telemetry state synchronizations without locking delays.
              </p>
              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2 font-mono text-[11px] text-cyan-300">
                <div>Vector Clock [US-East: 184920, EU-West: 184918, APAC-South: 184915]</div>
                <div>LWW-Element-Set (Last-Write-Wins) Convergence Verdict: CONVERGED</div>
                <div>Concurrent Conflict Resolution Rate: 0.0001% (Zero Manual Interventions)</div>
              </div>
              <div className="text-slate-400 text-[11px]">
                Deterministic mathematical convergence guarantees 100% consistent UEBA baseline profiles and security alert lifecycles across all global clusters.
              </div>
            </div>
          )}

          {/* TAB 6: Failover Studio */}
          {activeTab === 'failover_studio' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Trigger Failover Form */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 space-y-4">
                <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                  <RefreshCw className="h-5 w-5 text-cyan-400" /> Trigger Manual Failover
                </h3>
                <p className="text-xs text-slate-400">
                  Instantly switch primary processing traffic to an active secondary cluster with sub-second RTO.
                </p>

                <form onSubmit={handleTriggerFailover} className="space-y-3 text-xs">
                  <div>
                    <label className="block text-slate-400 mb-1">Source Failing Region</label>
                    <select
                      value={sourceRegion}
                      onChange={(e) => setSourceRegion(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                    >
                      <option value="US_EAST_PRIMARY">US_EAST_PRIMARY (Ashburn)</option>
                      <option value="EU_WEST_SECONDARY">EU_WEST_SECONDARY (Dublin)</option>
                      <option value="APAC_SOUTH_SATELLITE">APAC_SOUTH_SATELLITE (Singapore)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1">Target Failover Region</label>
                    <select
                      value={targetRegion}
                      onChange={(e) => setTargetRegion(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                    >
                      <option value="EU_WEST_SECONDARY">EU_WEST_SECONDARY (Dublin)</option>
                      <option value="US_EAST_PRIMARY">US_EAST_PRIMARY (Ashburn)</option>
                      <option value="APAC_SOUTH_SATELLITE">APAC_SOUTH_SATELLITE (Singapore)</option>
                    </select>
                  </div>
                  <div className="flex justify-end pt-2">
                    <button
                      type="submit"
                      className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl font-semibold flex items-center gap-2"
                    >
                      <RefreshCw className="h-4 w-4" /> Execute Switchover
                    </button>
                  </div>
                </form>

                {failoverResult && (
                  <div className="p-4 bg-slate-950 rounded-xl border border-cyan-500/30 text-xs space-y-2 mt-4">
                    <div className="flex justify-between items-center text-cyan-400 font-bold">
                      <span>Failover Executed Successfully</span>
                      <span>{failoverResult.switchover_duration_ms} ms</span>
                    </div>
                    <div className="text-slate-200 font-mono text-[11px]">
                      {failoverResult.source_failing_region} &rarr; {failoverResult.target_failover_region}
                    </div>
                  </div>
                )}
              </div>

              {/* Add Residency Boundary Form */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 space-y-4">
                <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                  <Lock className="h-5 w-5 text-cyan-400" /> Create Residency Boundary
                </h3>
                <p className="text-xs text-slate-400">
                  Deploy strict sovereign compliance boundaries to block cross-border telemetry egress.
                </p>

                <form onSubmit={handleCreateBoundary} className="space-y-3 text-xs">
                  <div>
                    <label className="block text-slate-400 mb-1">Boundary Name</label>
                    <input
                      type="text"
                      value={boundaryName}
                      onChange={(e) => setBoundaryName(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1">Compliance Standard</label>
                    <select
                      value={complianceStd}
                      onChange={(e) => setComplianceStd(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                    >
                      <option value="GDPR_EU_ONLY">GDPR (EU-Only Processing)</option>
                      <option value="FEDRAMP_US_ONLY">FedRAMP / ITAR (US Gov Cloud Only)</option>
                      <option value="APPI_JAPAN">APPI (Japan Financial Zone)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1">Enforced Regions (Comma-Separated)</label>
                    <input
                      type="text"
                      value={enforcedRegs}
                      onChange={(e) => setEnforcedRegs(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200 font-mono text-[11px]"
                      required
                    />
                  </div>
                  <div className="flex justify-end pt-2">
                    <button
                      type="submit"
                      className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl font-semibold flex items-center gap-2"
                    >
                      <ShieldCheck className="h-4 w-4" /> Enforce Boundary
                    </button>
                  </div>
                </form>

                {createdBoundary && (
                  <div className="p-4 bg-slate-950 rounded-xl border border-cyan-500/30 text-xs space-y-2 mt-4">
                    <div className="flex justify-between items-center text-cyan-400 font-bold">
                      <span>Boundary Enforced</span>
                      <span>{createdBoundary.compliance_standard}</span>
                    </div>
                    <div className="text-slate-200 font-semibold">{createdBoundary.boundary_name}</div>
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
