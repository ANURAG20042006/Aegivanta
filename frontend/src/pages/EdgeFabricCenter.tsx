import React, { useEffect, useState } from 'react';
import {
  Globe,
  Activity,
  ChevronRight,
  ShieldCheck,
  Zap,
  Server,
  Sliders,
  ShieldAlert,
  Radio
} from 'lucide-react';
import { saasApi } from '../services/saas';

export const EdgeFabricCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'pops' | 'policies' | 'routes' | 'geo_topology' | 'policy_deployer'>('overview');
  const [summary, setSummary] = useState<any>(null);
  const [pops, setPops] = useState<any[]>([]);
  const [policies, setPolicies] = useState<any[]>([]);
  const [routes, setRoutes] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Policy Deployer state
  const [policyName, setPolicyName] = useState<string>('Edge TLS 1.3 Anti-Replay Inspection');
  const [inspectionMode, setInspectionMode] = useState<string>('INLINE_BLOCK');
  const [rateLimitRps, setRateLimitRps] = useState<number>(75000);
  const [geoAction, setGeoAction] = useState<string>('CHALLENGE');
  const [deployedPolicy, setDeployedPolicy] = useState<any>(null);

  useEffect(() => {
    fetchEdgeFabricData();
  }, []);

  const fetchEdgeFabricData = async () => {
    try {
      setLoading(true);
      const [sum, ps, pols, rts] = await Promise.all([
        saasApi.getEdgeFabricSummary(),
        saasApi.getEdgePoPs(),
        saasApi.getEdgeInspectionPolicies(),
        saasApi.getRegionalIngestionRoutes()
      ]);
      setSummary(sum);
      setPops(ps);
      setPolicies(pols);
      setRoutes(rts);
    } catch (err) {
      console.error('Failed to load Edge Security Fabric data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeployPolicy = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await saasApi.createEdgeInspectionPolicy({
        policy_name: policyName,
        inspection_mode: inspectionMode,
        edge_rate_limit_rps: rateLimitRps,
        geo_fence_action: geoAction
      });
      setDeployedPolicy(res);
      fetchEdgeFabricData();
    } catch (err) {
      console.error('Failed to deploy edge policy:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Globe className="h-7 w-7 text-emerald-400" />
            Global Distributed Edge Security & Regional Ingestion Fabric
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Global Edge Point of Presence (PoP) Mesh, Edge-Side DDoS Scrubbing, TLS 1.3 Termination & Low-Latency Regional Ingestion.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('policy_deployer')}
            className="flex items-center gap-2 px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold transition-colors"
          >
            <ShieldCheck className="h-4 w-4" /> Deploy Edge Policy
          </button>
        </div>
      </div>

      {/* Top Metrics Ribbon */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Edge Fabric Health</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.overall_edge_fabric_score}<span className="text-xs text-slate-500">/100</span></div>
            <div className="text-[10px] text-emerald-400 mt-0.5">High Availability</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Active Edge PoPs</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{summary.active_edge_pops_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Global Locations</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Edge Throughput</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{summary.aggregate_edge_throughput_gbps} <span className="text-xs text-slate-500">Gbps</span></div>
            <div className="text-[10px] text-slate-400 mt-0.5">Line Rate Ingestion</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Active Connections</div>
            <div className="text-2xl font-bold text-slate-200 mt-1">{(summary.active_edge_connections_count / 1000).toFixed(0)}k</div>
            <div className="text-[10px] text-slate-400 mt-0.5">TLS 1.3 Terminated</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Mean Latency</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.mean_edge_termination_latency_ms} <span className="text-xs text-slate-500">ms</span></div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Sub-5ms Edge</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">WAN Routes</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{summary.regional_wan_routes_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">WireGuard mTLS</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'Edge Fabric Overview', icon: Globe },
          { id: 'pops', label: 'Global PoP Fleet', icon: Server },
          { id: 'policies', label: 'Edge Inspection & DDoS Policies', icon: ShieldAlert },
          { id: 'routes', label: 'Regional Ingestion WAN Routes', icon: Radio },
          { id: 'geo_topology', label: 'Geo-Routing & Latency Map', icon: Zap },
          { id: 'policy_deployer', label: 'Deploy Edge Policy', icon: Sliders }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'border-emerald-500 text-emerald-300'
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
          <Activity className="h-6 w-6 animate-spin text-emerald-400 mr-3" />
          Synchronizing Global Edge Ingestion Fabric & PoP Nodes...
        </div>
      ) : (
        <>
          {/* TAB 1: Overview */}
          {activeTab === 'overview' && summary && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Worldwide PoPs */}
              <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Server className="h-4 w-4 text-emerald-400" /> Active Global Ingestion Points of Presence (PoPs)
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {pops.map((pop) => (
                    <div key={pop.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                      <div className="flex justify-between items-center font-bold">
                        <span className="text-slate-100 text-sm">{pop.pop_location_name}</span>
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold border border-emerald-500/30">
                          {pop.edge_status}
                        </span>
                      </div>
                      <div className="font-mono text-[11px] text-cyan-300">Region: {pop.region_code}</div>
                      <div className="grid grid-cols-3 gap-2 pt-1 border-t border-slate-800 text-[10px] text-slate-400">
                        <div>
                          <div className="text-slate-500">Throughput</div>
                          <div className="text-emerald-400 font-bold">{pop.throughput_gbps} Gbps</div>
                        </div>
                        <div>
                          <div className="text-slate-500">Connections</div>
                          <div className="text-slate-200 font-bold">{pop.active_connections.toLocaleString()}</div>
                        </div>
                        <div>
                          <div className="text-slate-500">Latency</div>
                          <div className="text-cyan-300 font-bold">{pop.latency_ms} ms</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-3 border-t border-slate-800/60">
                  <div className="text-xs font-bold text-slate-300 mb-2">Priority Edge Operational Directives:</div>
                  <div className="space-y-1.5">
                    {summary.top_edge_priorities.map((pri: string, idx: number) => (
                      <div key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                        <ChevronRight className="h-3.5 w-3.5 text-emerald-400 shrink-0 mt-0.5" />
                        {pri}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Regional WAN Routes */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Radio className="h-4 w-4 text-emerald-400" /> WAN Ingestion Routes
                </h3>
                <div className="space-y-3">
                  {routes.map((route) => (
                    <div key={route.id} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60 text-xs space-y-1.5">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span className="font-mono text-cyan-300">{route.source_region} &rarr; {route.target_core_cluster}</span>
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold">PRIMARY</span>
                      </div>
                      <div className="text-[11px] text-slate-400">Protocol: {route.routing_protocol}</div>
                      <div className="text-[10px] text-emerald-400 font-mono">Replication Lag: {route.replication_lag_ms} ms</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: PoPs */}
          {activeTab === 'pops' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Server className="h-4 w-4 text-emerald-400" /> Global Point of Presence Fleet Registry
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {pops.map((p) => (
                  <div key={p.id} className="p-5 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-3">
                    <div className="flex justify-between items-center font-bold">
                      <span className="text-slate-100 text-base">{p.pop_location_name}</span>
                      <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold text-[10px]">
                        {p.edge_status}
                      </span>
                    </div>

                    <div className="text-cyan-300 font-mono text-xs">Region Identifier: {p.region_code}</div>

                    <div className="grid grid-cols-3 gap-2 p-3 bg-slate-900 rounded-lg text-center">
                      <div>
                        <div className="text-slate-500 text-[10px]">Throughput</div>
                        <div className="text-emerald-400 font-bold text-sm">{p.throughput_gbps} Gbps</div>
                      </div>
                      <div>
                        <div className="text-slate-500 text-[10px]">Active Conns</div>
                        <div className="text-slate-200 font-bold text-sm">{p.active_connections.toLocaleString()}</div>
                      </div>
                      <div>
                        <div className="text-slate-500 text-[10px]">Edge Latency</div>
                        <div className="text-cyan-300 font-bold text-sm">{p.latency_ms} ms</div>
                      </div>
                    </div>

                    <div className="text-[10px] text-slate-500 flex justify-between pt-1">
                      <span>TLS 1.3 / QUIC Ready</span>
                      <span>Heartbeat: {new Date(p.last_heartbeat).toLocaleTimeString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: Policies */}
          {activeTab === 'policies' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <ShieldAlert className="h-4 w-4 text-emerald-400" /> Edge-Side Inspection & DDoS Scrubbing Policies
                </h3>
                <button
                  onClick={() => setActiveTab('policy_deployer')}
                  className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold"
                >
                  + Deploy Edge Policy
                </button>
              </div>

              <div className="space-y-3">
                {policies.map((pol) => (
                  <div key={pol.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <span className="text-slate-100 text-sm">{pol.policy_name}</span>
                      <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold text-[10px]">
                        {pol.inspection_mode}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-400">
                      <div>Rate Limit: <strong className="text-slate-200">{pol.edge_rate_limit_rps.toLocaleString()} RPS</strong></div>
                      <div>Geo-Fence Action: <strong className="text-cyan-300">{pol.geo_fence_action}</strong></div>
                    </div>

                    <div className="flex justify-between items-center text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">
                      <span>Status: ACTIVE_AT_ALL_POPS</span>
                      <span>Deployed: {new Date(pol.created_at).toLocaleString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: Routes */}
          {activeTab === 'routes' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Radio className="h-4 w-4 text-emerald-400" /> Regional Ingestion & WAN Replication Routing
              </h3>

              <div className="space-y-3">
                {routes.map((r) => (
                  <div key={r.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-cyan-300">{r.source_region}</span>
                        <span className="text-slate-400">&rarr;</span>
                        <span className="text-slate-100">{r.target_core_cluster}</span>
                      </div>
                      <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold text-[10px]">
                        PRIMARY ROUTE
                      </span>
                    </div>

                    <div className="flex justify-between items-center text-[11px] text-slate-300">
                      <span>Encrypted Protocol: <strong className="font-mono text-indigo-300">{r.routing_protocol}</strong></span>
                      <span>Replication Lag: <strong className="text-emerald-400">{r.replication_lag_ms} ms</strong></span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: Geo Topology */}
          {activeTab === 'geo_topology' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 max-w-2xl mx-auto space-y-4 text-xs">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Zap className="h-5 w-5 text-emerald-400" /> Global Geo-Routing & Latency Topology
              </h3>
              <p className="text-slate-400 leading-relaxed">
                Sensor agents and customer API clients are automatically routed via Anycast DNS and BGP geo-proximity to the nearest Edge Point of Presence.
              </p>
              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2 font-mono text-[11px] text-cyan-300">
                <div>North America (US-East / US-West): Mean 3.8 ms Latency &rarr; Ashburn PoP</div>
                <div>Europe (EU-Central / EU-West): Mean 4.1 ms Latency &rarr; Frankfurt PoP</div>
                <div>Asia-Pacific (APAC / East Asia): Mean 5.2 ms Latency &rarr; Singapore PoP</div>
                <div>Latin America (SA-East): Mean 8.4 ms Latency &rarr; S&atilde;o Paulo PoP</div>
              </div>
              <div className="text-slate-400 text-[11px]">
                Cross-region telemetry replication traverses encrypted WireGuard mTLS overlay tunnels with guaranteed zero data loss buffer failover.
              </div>
            </div>
          )}

          {/* TAB 6: Policy Deployer */}
          {activeTab === 'policy_deployer' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 max-w-2xl mx-auto space-y-4">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Sliders className="h-5 w-5 text-emerald-400" /> Deploy Edge Inspection Policy
              </h3>
              <p className="text-xs text-slate-400">
                Configure line-rate packet inspection, DDoS scrubbing thresholds, and geo-fencing actions across all global edge PoPs.
              </p>

              <form onSubmit={handleDeployPolicy} className="space-y-3 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Policy Name</label>
                  <input
                    type="text"
                    value={policyName}
                    onChange={(e) => setPolicyName(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-slate-400 mb-1">Inspection Mode</label>
                    <select
                      value={inspectionMode}
                      onChange={(e) => setInspectionMode(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                    >
                      <option value="INLINE_BLOCK">Inline Packet Inspection & Block</option>
                      <option value="SCRUB_DDOS">Autonomous L7 DDoS Scrubbing</option>
                      <option value="PASS_THROUGH">Passive Telemetry Ingestion Only</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1">Edge Rate Limit (RPS)</label>
                    <input
                      type="number"
                      value={rateLimitRps}
                      onChange={(e) => setRateLimitRps(parseInt(e.target.value))}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200 font-mono"
                      required
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Geo-Fence Action</label>
                  <select
                    value={geoAction}
                    onChange={(e) => setGeoAction(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                  >
                    <option value="CHALLENGE">Challenge (Proof of Work / mTLS)</option>
                    <option value="BLOCK">Strict Block Non-Compliant Geographies</option>
                    <option value="ALLOW">Allow All Geographies</option>
                  </select>
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-semibold flex items-center gap-2"
                  >
                    <ShieldCheck className="h-4 w-4" /> Deploy Policy to Edge Fleet
                  </button>
                </div>
              </form>

              {deployedPolicy && (
                <div className="p-4 bg-slate-950 rounded-xl border border-emerald-500/30 text-xs space-y-2 mt-4">
                  <div className="flex justify-between items-center text-emerald-400 font-bold">
                    <span>Policy Deployed to 4 Global PoPs</span>
                    <span>Mode: {deployedPolicy.inspection_mode}</span>
                  </div>
                  <div className="text-slate-200 font-semibold">{deployedPolicy.policy_name}</div>
                  <div className="text-[10px] text-slate-400">Rate Limit: {deployedPolicy.edge_rate_limit_rps} RPS · Geo Action: {deployedPolicy.geo_fence_action}</div>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};
