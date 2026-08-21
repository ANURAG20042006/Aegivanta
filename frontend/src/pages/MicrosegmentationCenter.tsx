import React, { useEffect, useState } from 'react';
import {
  Network,
  Activity,
  ChevronRight,
  AlertTriangle,
  Layers,
  Server,
  Sliders,
  Laptop
} from 'lucide-react';
import { saasApi } from '../services/saas';


export const MicrosegmentationCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'policies' | 'connectors' | 'sessions' | 'lateral_alerts' | 'flow_mesh'>('overview');
  const [summary, setSummary] = useState<any>(null);
  const [policies, setPolicies] = useState<any[]>([]);
  const [connectors, setConnectors] = useState<any[]>([]);
  const [sessions, setSessions] = useState<any[]>([]);
  const [lateralAlerts, setLateralAlerts] = useState<any[]>([]);
  const [flowMesh, setFlowMesh] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // New policy modal state
  const [showPolicyModal, setShowPolicyModal] = useState<boolean>(false);
  const [policyName, setPolicyName] = useState<string>('Isolate FinTech Cluster');
  const [srcSeg, setSrcSeg] = useState<string>('PAYMENT_GATEWAY_VPC');
  const [dstSeg, setDstSeg] = useState<string>('CORE_DATABASE_CLUSTER');
  const [protoPort, setProtoPort] = useState<string>('TCP/5432');
  const [action, setAction] = useState<string>('ALLOW_ENCRYPTED_TUNNEL');
  const [minTrust, setMinTrust] = useState<number>(85);

  useEffect(() => {
    fetchMicrosegData();
  }, []);

  const fetchMicrosegData = async () => {
    try {
      setLoading(true);
      const [sum, pols, conns, sess, alerts, mesh] = await Promise.all([
        saasApi.getZTNAMicrosegSummary(),
        saasApi.getMicrosegPolicies(),
        saasApi.getZTNAConnectors(),
        saasApi.getZTNAClients(),
        saasApi.getLateralAlerts(),
        saasApi.getNetworkFlowGraph()
      ]);
      setSummary(sum);
      setPolicies(pols);
      setConnectors(conns);
      setSessions(sess);
      setLateralAlerts(alerts);
      setFlowMesh(mesh);
    } catch (err) {
      console.error('Failed to load Microsegmentation & ZTNA data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePolicy = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await saasApi.createMicrosegPolicy({
        policy_name: policyName,
        source_segment: srcSeg,
        destination_segment: dstSeg,
        protocol_port: protoPort,
        enforcement_action: action,
        min_device_trust_score: minTrust
      });
      setShowPolicyModal(false);
      fetchMicrosegData();
    } catch (err) {
      console.error('Failed to create microsegmentation policy:', err);
    }
  };

  const handleTerminateSession = async (sessId: string) => {
    try {
      await saasApi.terminateZTNASession({ session_id: sessId });
      fetchMicrosegData();
    } catch (err) {
      console.error('Failed to terminate ZTNA session:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Network className="h-7 w-7 text-cyan-500" />
            Microsegmentation, Software-Defined Perimeter & ZTNA 2.0
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Identity-Bound Encrypted Overlays, L4/L7 Segment Isolation Policies, Continuous Trust Attestation & Lateral Movement Defense.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowPolicyModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-xs font-semibold transition-colors"
          >
            <Sliders className="h-4 w-4" /> Create Isolation Policy
          </button>
        </div>
      </div>

      {/* Top Metrics Ribbon */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">ZTNA Posture</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.overall_ztna_posture_score}<span className="text-xs text-slate-500">/100</span></div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Encrypted Overlay</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Gateway Nodes</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{summary.active_connector_nodes_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Global Connectors</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">L4/L7 Policies</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{summary.active_microsegmentation_policies_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">eBPF Enforcing</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Client Tunnels</div>
            <div className="text-2xl font-bold text-slate-200 mt-1">{summary.connected_client_sessions_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Identity-Bound</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Lateral Pivots Blocked</div>
            <div className="text-2xl font-bold text-rose-400 mt-1">{summary.blocked_lateral_traversals_count}</div>
            <div className="text-[10px] text-rose-400 mt-0.5">Boundary Breaches</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Avg Trust Score</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.average_device_trust_score}</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">{summary.inter_segment_encryption_coverage_pct}% mTLS</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'ZTNA Overview', icon: Network },
          { id: 'policies', label: 'L4/L7 Policies', icon: Sliders },
          { id: 'connectors', label: 'SDP Gateway Fleet', icon: Server },
          { id: 'sessions', label: 'Active ZTNA Sessions', icon: Laptop },
          { id: 'lateral_alerts', label: 'Lateral Movement Interceptions', icon: AlertTriangle },
          { id: 'flow_mesh', label: 'Segment Flow Mesh Graph', icon: Layers }
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
          Loading Software-Defined Perimeter & Microsegmentation Engine...
        </div>
      ) : (
        <>
          {/* TAB 1: Overview */}
          {activeTab === 'overview' && summary && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Intercepted Lateral Movement */}
              <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-rose-400" /> Recent Intercepted Lateral Pivots
                </h3>
                <div className="space-y-3">
                  {lateralAlerts.map((alert) => (
                    <div key={alert.id} className="p-3.5 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                      <div className="flex justify-between items-center font-bold">
                        <span className="text-rose-400 text-sm">{alert.threat_classification}</span>
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 text-[10px]">{alert.interception_action}</span>
                          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">{alert.attempted_port_protocol}</span>
                        </div>
                      </div>
                      <div className="text-slate-200">Source: <strong className="text-cyan-400">{alert.source_workload}</strong> ({alert.source_segment}) → Target: <strong className="text-indigo-400">{alert.target_workload}</strong> ({alert.target_segment})</div>
                      <div className="text-[10px] text-slate-500 flex justify-between pt-1 border-t border-slate-800/60">
                        <span>Boundary: Isolated Zero Trust Enclave</span>
                        <span>{new Date(alert.blocked_at).toLocaleString()}</span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-3 border-t border-slate-800/60">
                  <div className="text-xs font-bold text-slate-300 mb-2">Priority Isolation Directives:</div>
                  <div className="space-y-1.5">
                    {summary.top_microsegmentation_priorities.map((pri: string, idx: number) => (
                      <div key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                        <ChevronRight className="h-3.5 w-3.5 text-cyan-400 shrink-0 mt-0.5" />
                        {pri}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Gateway Fleet Health */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Server className="h-4 w-4 text-cyan-400" /> SDP Gateway Connectors
                </h3>
                <div className="space-y-3">
                  {connectors.map((conn) => (
                    <div key={conn.id} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60 text-xs space-y-2">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span className="font-mono text-cyan-300">{conn.connector_name}</span>
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px]">{conn.status}</span>
                      </div>
                      <div className="text-[11px] text-slate-400">
                        Region: <strong className="text-slate-300">{conn.region}</strong> · IP: <span className="font-mono">{conn.public_ip}</span>
                      </div>
                      <div className="text-[10px] text-slate-500 flex justify-between">
                        <span>Active Clients: {conn.active_client_sessions_count}</span>
                        <span>Tunneled: {conn.total_bytes_tunneled_gb} GB</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: L4/L7 Policies */}
          {activeTab === 'policies' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Sliders className="h-4 w-4 text-cyan-400" /> Active Layer 4 & Layer 7 Isolation Policies
                </h3>
                <button
                  onClick={() => setShowPolicyModal(true)}
                  className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold"
                >
                  + Add Isolation Policy
                </button>
              </div>

              <div className="space-y-3">
                {policies.map((p) => (
                  <div key={p.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2.5">
                    <div className="flex justify-between items-center font-bold">
                      <div className="flex items-center gap-2">
                        <span className="text-slate-100 text-sm">{p.policy_name}</span>
                        <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 text-[10px]">{p.protocol_port}</span>
                      </div>
                      <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px]">
                        {p.enforcement_action}
                      </span>
                    </div>

                    <div className="p-2.5 bg-slate-900 rounded font-mono text-[11px] text-slate-300 flex justify-between">
                      <span>Source: <strong className="text-indigo-400">{p.source_segment}</strong></span>
                      <span>→</span>
                      <span>Destination: <strong className="text-cyan-400">{p.destination_segment}</strong></span>
                    </div>

                    <div className="flex justify-between items-center text-[10px] text-slate-400 pt-1">
                      <span>Min Device Trust Score: <strong className="text-emerald-400 font-bold">{p.min_device_trust_score}/100</strong></span>
                      <span>Evaluated Flows: <strong className="text-slate-200">{p.total_evaluated_flows.toLocaleString()}</strong></span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: SDP Gateway Fleet */}
          {activeTab === 'connectors' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Server className="h-4 w-4 text-cyan-400" /> Software-Defined Perimeter (SDP) Gateway Connectors
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                    <tr>
                      <th className="p-3">Connector Name</th>
                      <th className="p-3">Region</th>
                      <th className="p-3">Public Gateway IP</th>
                      <th className="p-3">Overlay CIDR</th>
                      <th className="p-3">Active Clients</th>
                      <th className="p-3">Tunneled Data</th>
                      <th className="p-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50 text-slate-200">
                    {connectors.map((c) => (
                      <tr key={c.id} className="hover:bg-slate-950/40">
                        <td className="p-3 font-semibold text-cyan-300 font-mono">{c.connector_name}</td>
                        <td className="p-3 text-slate-300">{c.region}</td>
                        <td className="p-3 font-mono text-slate-400">{c.public_ip}</td>
                        <td className="p-3 font-mono text-indigo-400">{c.private_overlay_cidr}</td>
                        <td className="p-3 font-bold text-slate-200">{c.active_client_sessions_count}</td>
                        <td className="p-3 text-emerald-400 font-bold">{c.total_bytes_tunneled_gb} GB</td>
                        <td className="p-3">
                          <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold text-[10px]">{c.status}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 4: Active ZTNA Sessions */}
          {activeTab === 'sessions' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Laptop className="h-4 w-4 text-cyan-400" /> Identity-Bound Zero Trust Access Sessions
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                    <tr>
                      <th className="p-3">User Identity</th>
                      <th className="p-3">Device ID</th>
                      <th className="p-3">Gateway Node</th>
                      <th className="p-3">Client Overlay IP</th>
                      <th className="p-3">Target App</th>
                      <th className="p-3">Trust Score</th>
                      <th className="p-3">Status</th>
                      <th className="p-3">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50 text-slate-200">
                    {sessions.map((s) => (
                      <tr key={s.id} className="hover:bg-slate-950/40">
                        <td className="p-3 font-semibold text-cyan-300">{s.user_email}</td>
                        <td className="p-3 font-mono text-slate-400">{s.device_id}</td>
                        <td className="p-3 font-mono text-[11px] text-slate-300">{s.connector_node_name}</td>
                        <td className="p-3 font-mono text-indigo-400">{s.client_overlay_ip}</td>
                        <td className="p-3 font-mono text-slate-300">{s.target_application}</td>
                        <td className="p-3">
                          <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${s.current_trust_score >= 80 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                            {s.current_trust_score}/100
                          </span>
                        </td>
                        <td className="p-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${s.session_status === 'ACTIVE_TUNNEL' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                            {s.session_status}
                          </span>
                        </td>
                        <td className="p-3">
                          {s.session_status === 'ACTIVE_TUNNEL' && (
                            <button
                              onClick={() => handleTerminateSession(s.id)}
                              className="px-2 py-1 bg-rose-950/80 hover:bg-rose-900 text-rose-300 border border-rose-800/60 rounded text-[10px] font-semibold"
                            >
                              Revoke
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 5: Lateral Movement Alerts */}
          {activeTab === 'lateral_alerts' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-rose-400" /> Lateral Movement Interceptions & Microsegmentation Boundary Alerts
              </h3>
              <div className="space-y-3">
                {lateralAlerts.map((alert) => (
                  <div key={alert.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <div className="flex items-center gap-2">
                        <span className="text-rose-400 font-mono text-sm">{alert.threat_classification}</span>
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">{alert.attempted_port_protocol}</span>
                      </div>
                      <span className="px-2.5 py-0.5 rounded bg-rose-500/10 text-rose-400 font-bold text-[10px]">
                        {alert.interception_action}
                      </span>
                    </div>

                    <div className="text-slate-300">
                      Workload <strong className="text-cyan-300">{alert.source_workload}</strong> in segment <strong className="text-indigo-400">{alert.source_segment}</strong> attempted unauthorized traversal to <strong className="text-cyan-300">{alert.target_workload}</strong> in segment <strong className="text-indigo-400">{alert.target_segment}</strong>.
                    </div>

                    <div className="text-[10px] text-slate-500 pt-1 border-t border-slate-800/60 flex justify-between">
                      <span>Interception: eBPF Microsegmentation Kernel Drop</span>
                      <span>{new Date(alert.blocked_at).toLocaleString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 6: Flow Mesh Graph */}
          {activeTab === 'flow_mesh' && flowMesh && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Layers className="h-4 w-4 text-cyan-400" /> Microsegmentation Mesh Topology & Active Inter-Segment Flows
              </h3>
              <p className="text-xs text-slate-400">
                Visual representation of isolated security enclaves, active mTLS tunnels, and blocked lateral movement trajectories.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                {flowMesh.nodes.map((node: any) => (
                  <div key={node.id} className="p-4 bg-slate-950/80 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <span className="text-slate-200">{node.name}</span>
                      <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 text-[10px]">{node.tier}</span>
                    </div>
                    <div className="text-[11px] text-slate-400">
                      Workloads Enrolled: <strong className="text-slate-200">{node.workloads_count}</strong>
                    </div>
                    <div className="text-[10px] text-emerald-400 font-semibold">
                      State: {node.status}
                    </div>
                  </div>
                ))}
              </div>

              <div className="pt-4 border-t border-slate-800">
                <div className="text-xs font-bold text-slate-300 mb-2">Inter-Segment Traffic Trajectories:</div>
                <div className="space-y-2">
                  {flowMesh.links.map((link: any, idx: number) => (
                    <div key={idx} className="p-2.5 bg-slate-950 rounded-lg border border-slate-800 text-xs flex justify-between items-center">
                      <span className="font-mono text-cyan-300">{link.source} → {link.target}</span>
                      <span className="text-slate-400 text-[11px]">{link.protocol} ({link.bandwidth_mbps} Mbps)</span>
                      <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${link.status === 'ALLOWED' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                        {link.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* New Policy Modal */}
      {showPolicyModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4">
            <h3 className="text-base font-bold text-slate-100">Create Microsegmentation Policy</h3>
            <form onSubmit={handleCreatePolicy} className="space-y-3 text-xs">
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
                  <label className="block text-slate-400 mb-1">Source Segment</label>
                  <input
                    type="text"
                    value={srcSeg}
                    onChange={(e) => setSrcSeg(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                    required
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Destination Segment</label>
                  <input
                    type="text"
                    value={dstSeg}
                    onChange={(e) => setDstSeg(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                    required
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-slate-400 mb-1">Protocol / Port</label>
                  <input
                    type="text"
                    value={protoPort}
                    onChange={(e) => setProtoPort(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                    required
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Min Trust Score</label>
                  <input
                    type="number"
                    min={0}
                    max={100}
                    value={minTrust}
                    onChange={(e) => setMinTrust(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Enforcement Action</label>
                <select
                  value={action}
                  onChange={(e) => setAction(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                >
                  <option value="ALLOW_ENCRYPTED_TUNNEL">Allow Encrypted mTLS Tunnel</option>
                  <option value="DENY_ISOLATE">Deny & Isolate Segment Boundary</option>
                  <option value="REQUIRE_MFA_STEPUP">Require Step-Up Hardware MFA</option>
                </select>
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowPolicyModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl font-semibold"
                >
                  Compile & Deploy Policy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
