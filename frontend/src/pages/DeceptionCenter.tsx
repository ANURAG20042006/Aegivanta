import React, { useEffect, useState } from 'react';
import {
  Sparkles,
  Shield,
  Activity,
  ChevronRight,
  Database,
  Zap,
  Server,
  Key,
  Plus
} from 'lucide-react';
import { saasApi } from '../services/saas';


export const DeceptionCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'honeypots' | 'canaries' | 'interactions' | 'endpoint_lures' | 'mitre_engage'>('overview');
  const [summary, setSummary] = useState<any>(null);
  const [honeypots, setHoneypots] = useState<any[]>([]);
  const [canaries, setCanaries] = useState<any[]>([]);
  const [interactions, setInteractions] = useState<any[]>([]);
  const [lures, setLures] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Deploy honeypot modal state
  const [showDeployModal, setShowDeployModal] = useState<boolean>(false);
  const [newDecoyName, setNewDecoyName] = useState<string>('decoy-k8s-api-server');
  const [newDecoyType, setNewDecoyType] = useState<string>('WEB_PORTAL');
  const [newDecoyIp, setNewDecoyIp] = useState<string>('10.0.12.55');

  // Generate canary modal state
  const [showCanaryModal, setShowCanaryModal] = useState<boolean>(false);
  const [newCanaryType, setNewCanaryType] = useState<string>('AWS_API_KEY');
  const [newCanaryName, setNewCanaryName] = useState<string>('ci-cd-prod-aws-key');
  const [newCanaryPlacement, setNewCanaryPlacement] = useState<string>('Placed in Jenkins workspace /var/lib/jenkins/.aws');

  useEffect(() => {
    fetchDeceptionData();
  }, []);

  const fetchDeceptionData = async () => {
    try {
      setLoading(true);
      const [sum, pots, cn, intx, lr] = await Promise.all([
        saasApi.getDeceptionSummary(),
        saasApi.getHoneypots(),
        saasApi.getCanaries(),
        saasApi.getDeceptionInteractions(),
        saasApi.getEndpointLures()
      ]);
      setSummary(sum);
      setHoneypots(pots);
      setCanaries(cn);
      setInteractions(intx);
      setLures(lr);
    } catch (err) {
      console.error('Failed to load deception data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeployHoneypot = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await saasApi.deployHoneypot({
        node_name: newDecoyName,
        decoy_type: newDecoyType,
        internal_ip: newDecoyIp,
        vlan_segment: 'DECEPTION-VLAN-100'
      });
      setShowDeployModal(false);
      fetchDeceptionData();
    } catch (err) {
      console.error('Failed to deploy honeypot:', err);
    }
  };

  const handleGenerateCanary = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await saasApi.generateCanary({
        token_type: newCanaryType,
        token_name: newCanaryName,
        placement_description: newCanaryPlacement
      });
      setShowCanaryModal(false);
      fetchDeceptionData();
    } catch (err) {
      console.error('Failed to generate canary token:', err);
    }
  };

  const handleTriggerCanary = async (tokenId: string) => {
    try {
      await saasApi.triggerCanary(tokenId, { source_ip: '198.51.100.99' });
      fetchDeceptionData();
    } catch (err) {
      console.error('Failed to simulate canary trip:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Sparkles className="h-7 w-7 text-indigo-400" />
            Deception Technology & Active Adversary Engagement
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            MITRE Engage Fleet: SSH Cowrie Decoys, Canary Token Beacons, Zero-False-Positive Adversary Ledgers & Endpoint Lures.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowCanaryModal(true)}
            className="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold transition-colors"
          >
            <Key className="h-4 w-4 text-amber-400" /> Create Canary Token
          </button>
          <button
            onClick={() => setShowDeployModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-colors"
          >
            <Plus className="h-4 w-4" /> Deploy Honeypot Decoy
          </button>
        </div>
      </div>

      {/* Top Metrics Ribbon */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Deception Score</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.overall_deception_readiness_score}<span className="text-xs text-slate-500">/100</span></div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Active Engagement</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Honeypot Decoys</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{summary.total_deployed_honeypots_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Listening on VLANs</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Canary Tokens</div>
            <div className="text-2xl font-bold text-amber-400 mt-1">{summary.active_canary_tokens_count}</div>
            <div className="text-[10px] text-amber-400 mt-0.5">AWS, Docs, DNS</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Attacker Interactions</div>
            <div className="text-2xl font-bold text-rose-400 mt-1">{summary.total_adversary_interactions_count}</div>
            <div className="text-[10px] text-rose-400 mt-0.5">Zero False Positives</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Endpoint Lures</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{summary.endpoint_lures_deployed_count}</div>
            <div className="text-[10px] text-cyan-400 mt-0.5">LSASS & Browser</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Fidelity Rate</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">100%</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Guaranteed True+</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'Deception Overview', icon: Sparkles },
          { id: 'honeypots', label: 'Honeypot Decoy Fleet', icon: Server },
          { id: 'canaries', label: 'Canary Token Generator', icon: Key },
          { id: 'interactions', label: 'Adversary Interaction Ledger', icon: Zap },
          { id: 'endpoint_lures', label: 'Endpoint Lure Distribution', icon: Database },
          { id: 'mitre_engage', label: 'MITRE Engage Matrix', icon: Shield }
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
          Loading Active Deception & Honeypot Fleet...
        </div>
      ) : (
        <>
          {/* TAB 1: Overview */}
          {activeTab === 'overview' && summary && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Deception Health & Recent Hits */}
              <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Zap className="h-4 w-4 text-rose-400" /> Recent True-Positive Adversary Engagements
                </h3>
                <div className="space-y-3">
                  {interactions.map((evt) => (
                    <div key={evt.id} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60 text-xs space-y-1.5">
                      <div className="flex justify-between items-center font-bold">
                        <span className="text-rose-400">{evt.source_ip} ({evt.attacker_asn})</span>
                        <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 text-[10px]">
                          {evt.containment_action_taken}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-300 font-mono bg-slate-900/80 p-2 rounded">
                        {evt.captured_payload_or_command}
                      </div>
                      <div className="text-[10px] text-slate-400 flex justify-between">
                        <span>Target: <strong className="text-indigo-300">{evt.target_decoy_name}</strong> · Activity: {evt.mitre_engage_activity}</span>
                        <span>Fidelity: 100% True-Positive</span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-3 border-t border-slate-800/60">
                  <div className="text-xs font-bold text-slate-300 mb-2">Priority Deception Deployments:</div>
                  <div className="space-y-1.5">
                    {summary.top_deception_priorities.map((pri: string, idx: number) => (
                      <div key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                        <ChevronRight className="h-3.5 w-3.5 text-indigo-400 shrink-0 mt-0.5" />
                        {pri}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Honeypot Decoys Summary */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Server className="h-4 w-4 text-indigo-400" /> Active Honeypot Nodes
                </h3>
                <div className="space-y-2.5">
                  {honeypots.map((pot) => (
                    <div key={pot.id} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60 text-xs space-y-1">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span>{pot.node_name}</span>
                        <span className="text-emerald-400 text-[10px]">{pot.status}</span>
                      </div>
                      <div className="text-[10px] text-slate-400 font-mono">{pot.internal_ip} ({pot.vlan_segment})</div>
                      <div className="text-[10px] text-slate-500">Profile: {pot.emulation_profile} · Hits: {pot.total_hits_count}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Honeypot Fleet */}
          {activeTab === 'honeypots' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Server className="h-4 w-4 text-indigo-400" /> Enterprise Honeypot Decoy Fleet
                </h3>
                <button
                  onClick={() => setShowDeployModal(true)}
                  className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold"
                >
                  + Deploy Decoy
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {honeypots.map((pot) => (
                  <div key={pot.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold text-slate-200">
                      <span className="text-sm text-indigo-300">{pot.node_name}</span>
                      <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px]">
                        {pot.status}
                      </span>
                    </div>
                    <div className="text-slate-400 font-mono text-[11px]">{pot.internal_ip} · {pot.vlan_segment}</div>
                    <div className="text-[11px] text-slate-300">Decoy Type: <strong>{pot.decoy_type}</strong> ({pot.interaction_level} Interaction)</div>
                    <div className="text-[10px] text-slate-500">Emulation Profile: {pot.emulation_profile}</div>
                    <div className="flex justify-between items-center text-[10px] text-slate-400 pt-2 border-t border-slate-800/60">
                      <span>Total Infiltrator Hits: <strong className="text-rose-400">{pot.total_hits_count}</strong></span>
                      <span>Deployed: {new Date(pot.deployed_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: Canary Tokens */}
          {activeTab === 'canaries' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Key className="h-4 w-4 text-amber-400" /> Traceable Canary Tokens & Beacons
                </h3>
                <button
                  onClick={() => setShowCanaryModal(true)}
                  className="px-3 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-semibold"
                >
                  + Generate Canary
                </button>
              </div>

              <div className="space-y-3">
                {canaries.map((can) => (
                  <div key={can.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs flex justify-between items-center">
                    <div className="space-y-1">
                      <div className="font-bold text-slate-200 text-sm flex items-center gap-2">
                        {can.token_name}
                        <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 text-[10px]">{can.token_type}</span>
                      </div>
                      <div className="text-slate-400 font-mono text-[10px]">{can.token_value_preview}</div>
                      <div className="text-[10px] text-slate-500">Placement: {can.placement_description}</div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-[11px] text-rose-400 font-bold bg-rose-500/10 px-2.5 py-1 rounded">
                        Tripped: {can.times_triggered}x
                      </span>
                      <button
                        onClick={() => handleTriggerCanary(can.id)}
                        className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold"
                      >
                        Simulate Trip
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: Adversary Interactions */}
          {activeTab === 'interactions' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Zap className="h-4 w-4 text-rose-400" /> Real-Time Attacker Keystroke & Interaction Ledger
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                    <tr>
                      <th className="p-3">Source IP & ASN</th>
                      <th className="p-3">Target Decoy</th>
                      <th className="p-3">Interaction Type</th>
                      <th className="p-3">Captured Keystrokes / Command</th>
                      <th className="p-3">MITRE Engage</th>
                      <th className="p-3">Containment Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50 text-slate-200">
                    {interactions.map((evt) => (
                      <tr key={evt.id} className="hover:bg-slate-950/40">
                        <td className="p-3">
                          <div className="font-mono text-rose-400 font-bold">{evt.source_ip}</div>
                          <div className="text-[10px] text-slate-500">{evt.attacker_asn}</div>
                        </td>
                        <td className="p-3 text-indigo-300 font-semibold">{evt.target_decoy_name}</td>
                        <td className="p-3">
                          <span className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px]">{evt.interaction_type}</span>
                        </td>
                        <td className="p-3 font-mono text-emerald-300 text-[11px] max-w-xs truncate">{evt.captured_payload_or_command}</td>
                        <td className="p-3 text-cyan-300 text-[10px]">{evt.mitre_engage_activity}</td>
                        <td className="p-3 font-bold text-rose-400 text-[10px]">{evt.containment_action_taken}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 5: Endpoint Lures */}
          {activeTab === 'endpoint_lures' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Database className="h-4 w-4 text-cyan-400" /> Endpoint Deception Lure Distribution Map
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {lures.map((lure) => (
                  <div key={lure.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold text-slate-200">
                      <span className="text-cyan-300">{lure.endpoint_hostname}</span>
                      <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px]">
                        {lure.deployment_status}
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-300">Lure Type: <strong>{lure.lure_type}</strong></div>
                    <div className="text-[10px] text-slate-400 font-mono">Injected User: {lure.target_honey_user}</div>
                    <div className="text-[10px] text-slate-500 pt-2 border-t border-slate-800/60">
                      Verified: {new Date(lure.last_verified_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 6: MITRE Engage Matrix */}
          {activeTab === 'mitre_engage' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Shield className="h-4 w-4 text-indigo-400" /> MITRE Engage Deception Goals & Activities
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {[
                  { goal: '1. EXPOSE', desc: 'Force adversary to reveal their presence and TTPs via honeytokens.', color: 'text-amber-400' },
                  { goal: '2. LURE', desc: 'Entice attacker into controlled decoy environments using breadcrumbs.', color: 'text-indigo-400' },
                  { goal: '3. REDIRECT', desc: 'Steer adversary traffic away from legitimate enterprise assets to decoys.', color: 'text-cyan-400' },
                  { goal: '4. ELICIT', desc: 'Provoke adversary into executing their custom malware payloads for analysis.', color: 'text-rose-400' },
                  { goal: '5. DEGRADE', desc: 'Slow down and frustrate adversary progress with high-latency decoys.', color: 'text-emerald-400' },
                  { goal: '6. DISRUPT', desc: 'Trigger automated SOAR containment to instantly sever attacker sessions.', color: 'text-purple-400' }
                ].map((act, idx) => (
                  <div key={idx} className="p-4 bg-slate-950/80 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className={`font-bold text-sm ${act.color}`}>{act.goal}</div>
                    <div className="text-slate-400 text-[11px] leading-relaxed">{act.desc}</div>
                    <div className="text-[10px] text-emerald-400 font-semibold pt-1">Active in Aegivanta Fleet</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Deploy Honeypot Modal */}
      {showDeployModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4">
            <h3 className="text-base font-bold text-slate-100">Deploy New Honeypot Decoy</h3>
            <form onSubmit={handleDeployHoneypot} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Decoy Name</label>
                <input
                  type="text"
                  value={newDecoyName}
                  onChange={(e) => setNewDecoyName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                  required
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Decoy Type</label>
                <select
                  value={newDecoyType}
                  onChange={(e) => setNewDecoyType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                >
                  <option value="SSH_COWRIE">SSH Cowrie (OpenSSH 8.9p1)</option>
                  <option value="WEB_PORTAL">Web Admin Portal (Jenkins/GitLab/WP)</option>
                  <option value="SMB_FILE_SHARE">Windows SMB File Share</option>
                  <option value="DATABASE">PostgreSQL / MySQL Decoy</option>
                  <option value="AD_KERBEROAST">Active Directory Honey SPN</option>
                </select>
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Internal Decoy IP</label>
                <input
                  type="text"
                  value={newDecoyIp}
                  onChange={(e) => setNewDecoyIp(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                  required
                />
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowDeployModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold"
                >
                  Deploy Decoy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Generate Canary Modal */}
      {showCanaryModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4">
            <h3 className="text-base font-bold text-slate-100">Generate Traceable Canary Token</h3>
            <form onSubmit={handleGenerateCanary} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Token Name</label>
                <input
                  type="text"
                  value={newCanaryName}
                  onChange={(e) => setNewCanaryName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                  required
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Token Type</label>
                <select
                  value={newCanaryType}
                  onChange={(e) => setNewCanaryType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                >
                  <option value="AWS_API_KEY">AWS IAM Access Key (AKIA...)</option>
                  <option value="WEBHOOK_DOC">Word / PDF Webhook Beacon</option>
                  <option value="DNS_BEACON">DNS Canary Subdomain</option>
                  <option value="KUBECONFIG">Kubeconfig Decoy Token</option>
                </select>
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Placement Description</label>
                <input
                  type="text"
                  value={newCanaryPlacement}
                  onChange={(e) => setNewCanaryPlacement(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                  required
                />
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowCanaryModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-xl font-semibold"
                >
                  Generate Token
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
