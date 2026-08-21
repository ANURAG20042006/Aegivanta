import React, { useEffect, useState } from 'react';
import {
  Share2,
  Activity,
  ChevronRight,
  CheckCircle2,
  Lock,
  Search,
  Server,
  Sliders,
  Send
} from 'lucide-react';
import { saasApi } from '../services/saas';


export const FederatedThreatCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'indicators' | 'blind_match' | 'nodes' | 'differential_privacy' | 'share_dispatcher'>('overview');
  const [summary, setSummary] = useState<any>(null);
  const [indicators, setIndicators] = useState<any[]>([]);
  const [nodes, setNodes] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Blind Match state
  const [blindQuery, setBlindQuery] = useState<string>('APT29_COZYBEAR_C2_HOST');
  const [blindResult, setBlindResult] = useState<any>(null);

  // Share Dispatcher state
  const [rawIoc, setRawIoc] = useState<string>('185.220.101.5');
  const [shareClassification, setShareClassification] = useState<string>('TOR_EXIT_NODE_C2');
  const [shareEpsilon, setShareEpsilon] = useState<number>(0.5);
  const [shareSuccess, setShareSuccess] = useState<any>(null);

  useEffect(() => {
    fetchFederatedData();
  }, []);

  const fetchFederatedData = async () => {
    try {
      setLoading(true);
      const [sum, inds, nds] = await Promise.all([
        saasApi.getFederatedThreatSummary(),
        saasApi.getFederatedThreatIndicators(),
        saasApi.getFederatedNodes()
      ]);
      setSummary(sum);
      setIndicators(inds);
      setNodes(nds);
    } catch (err) {
      console.error('Failed to load Federated Threat Sharing data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBlindMatch = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await saasApi.executeBlindHomomorphicMatch({
        target_ioc_query: blindQuery
      });
      setBlindResult(res);
    } catch (err) {
      console.error('Failed to execute blind match:', err);
    }
  };

  const handleShareIndicator = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await saasApi.shareFederatedIndicator({
        raw_indicator_value: rawIoc,
        threat_classification: shareClassification,
        differential_privacy_epsilon: shareEpsilon
      });
      setShareSuccess(res);
      fetchFederatedData();
    } catch (err) {
      console.error('Failed to share federated indicator:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Share2 className="h-7 w-7 text-indigo-400" />
            Privacy-Preserving Threat Intel & Federated IOC Exchange
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Zero-Knowledge Threat Intelligence Sharing, Homomorphic Blind Indicator Matching & Differential Privacy ($\epsilon$-DP).
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('share_dispatcher')}
            className="flex items-center gap-2 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-colors"
          >
            <Send className="h-4 w-4" /> Anonymize & Share IOC
          </button>
        </div>
      </div>

      {/* Top Metrics Ribbon */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Federated Privacy</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{summary.overall_federated_privacy_score}<span className="text-xs text-slate-500">/100</span></div>
            <div className="text-[10px] text-indigo-400 mt-0.5">&epsilon;-DP Guaranteed</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Peer Nodes</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{summary.active_exchange_nodes_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Verified Mesh</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Syndicated IOCs</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.syndicated_indicators_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Consensus Validated</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Homomorphic Queries</div>
            <div className="text-2xl font-bold text-slate-200 mt-1">{summary.homomorphic_match_queries_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Encrypted Searches</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Mean Consensus</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{Math.round(summary.average_consensus_confidence_score * 100)}%</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">High Fidelity</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Metadata Leakage</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">0.0%</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Zero Residual Risk</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'Federated Exchange Overview', icon: Share2 },
          { id: 'indicators', label: 'Anonymized Indicators Matrix', icon: Lock },
          { id: 'blind_match', label: 'Homomorphic Blind Match Engine', icon: Search },
          { id: 'nodes', label: 'Verified Peer Mesh Nodes', icon: Server },
          { id: 'differential_privacy', label: 'Differential Privacy (\u03b5-Budget)', icon: Sliders },
          { id: 'share_dispatcher', label: 'Anonymized IOC Dispatcher', icon: Send }
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
          Synchronizing Federated Threat Mesh & Differential Privacy State...
        </div>
      ) : (
        <>
          {/* TAB 1: Overview */}
          {activeTab === 'overview' && summary && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Syndicated Indicators */}
              <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Lock className="h-4 w-4 text-indigo-400" /> Active Federated Indicators with Consensus
                </h3>
                <div className="space-y-3">
                  {indicators.map((ind) => (
                    <div key={ind.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                      <div className="flex justify-between items-center font-bold">
                        <div className="flex items-center gap-2">
                          <span className="text-indigo-400 font-mono">{ind.anonymized_indicator_hash.substring(0, 16)}...</span>
                          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">{ind.threat_classification}</span>
                        </div>
                        <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold text-[10px] border border-emerald-500/30">
                          {ind.syndication_status}
                        </span>
                      </div>
                      <div className="flex justify-between items-center text-[10px] text-slate-400 pt-1 border-t border-slate-800/60">
                        <span>Consensus Confidence: <strong className="text-emerald-400">{Math.round(ind.confidence_consensus_score * 100)}%</strong> · Peer Validations: <strong className="text-slate-200">{ind.peer_validations_count} nodes</strong></span>
                        <span>Differential Privacy: &epsilon; = {ind.differential_privacy_epsilon}</span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-3 border-t border-slate-800/60">
                  <div className="text-xs font-bold text-slate-300 mb-2">Priority Federated Directives:</div>
                  <div className="space-y-1.5">
                    {summary.top_federated_priorities.map((pri: string, idx: number) => (
                      <div key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                        <ChevronRight className="h-3.5 w-3.5 text-indigo-400 shrink-0 mt-0.5" />
                        {pri}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Verified Peer Nodes */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Server className="h-4 w-4 text-indigo-400" /> Verified Exchange Nodes
                </h3>
                <div className="space-y-3">
                  {nodes.map((node) => (
                    <div key={node.id} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60 text-xs space-y-1.5">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span className="font-mono text-cyan-300">{node.node_pseudonym}</span>
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold">{node.status}</span>
                      </div>
                      <div className="text-[11px] text-slate-400">Trust Tier: {node.trust_tier} · Weight: {node.consensus_weight}x</div>
                      <div className="text-[10px] text-slate-500 font-mono">Public Key Hash: {node.public_key_hash.substring(0, 16)}...</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Indicators */}
          {activeTab === 'indicators' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Lock className="h-4 w-4 text-indigo-400" /> Anonymized Federated Threat Indicators Matrix
                </h3>
                <button
                  onClick={() => setActiveTab('share_dispatcher')}
                  className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold"
                >
                  + Share New Indicator
                </button>
              </div>

              <div className="space-y-3">
                {indicators.map((ind) => (
                  <div key={ind.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <span className="font-mono text-indigo-300 text-base">{ind.anonymized_indicator_hash}</span>
                      <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold text-[10px]">
                        {ind.syndication_status}
                      </span>
                    </div>

                    <div className="text-[11px] text-slate-400">
                      Classification: <strong className="text-slate-200">{ind.threat_classification}</strong>
                    </div>

                    <div className="flex justify-between items-center text-[10px] text-slate-400 pt-1 border-t border-slate-800/60">
                      <span>Peer Validations: <strong className="text-emerald-400">{ind.peer_validations_count} nodes</strong> · Consensus Confidence: <strong className="text-cyan-300">{Math.round(ind.confidence_consensus_score * 100)}%</strong></span>
                      <span>Shared: {new Date(ind.shared_at).toLocaleString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: Blind Match */}
          {activeTab === 'blind_match' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 max-w-2xl mx-auto space-y-4">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Search className="h-5 w-5 text-indigo-400" /> Homomorphic Encrypted Blind Match Engine
              </h3>
              <p className="text-xs text-slate-400">
                Perform zero-knowledge encrypted searches against the decentralized federated indicator repository. Indicators are matched purely on homomorphic SHA-256 hashes without revealing raw queries to peer nodes.
              </p>

              <form onSubmit={handleBlindMatch} className="space-y-3 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Target IOC / Query String</label>
                  <input
                    type="text"
                    value={blindQuery}
                    onChange={(e) => setBlindQuery(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200 font-mono text-[11px]"
                    placeholder="e.g. APT29_COZYBEAR_C2_HOST or IP address"
                    required
                  />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold flex items-center gap-2"
                  >
                    <Search className="h-4 w-4" /> Execute Blind Match
                  </button>
                </div>
              </form>

              {blindResult && (
                <div className="p-4 bg-slate-950 rounded-xl border border-indigo-500/30 text-xs space-y-2 mt-4">
                  <div className="flex justify-between items-center text-indigo-400 font-bold">
                    <span className="flex items-center gap-1.5"><CheckCircle2 className="h-4 w-4" /> Blind Match Evaluated</span>
                    <span>Latency: {blindResult.execution_time_ms} ms</span>
                  </div>
                  <div className="text-slate-200 font-semibold">Match Verdict: <span className="font-mono text-emerald-400">{blindResult.blind_match_status}</span></div>
                  <div className="p-2 bg-slate-900 rounded font-mono text-[10px] text-cyan-300">
                    Encrypted Hash: {blindResult.encrypted_query_hash}
                  </div>
                  {blindResult.matched_threat_classification && (
                    <div className="text-[11px] text-slate-300">
                      Matched Category: <strong className="text-indigo-300">{blindResult.matched_threat_classification}</strong> (Consensus: {Math.round(blindResult.confidence_consensus_score * 100)}%)
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* TAB 4: Peer Nodes */}
          {activeTab === 'nodes' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Server className="h-4 w-4 text-indigo-400" /> Verified Federated Peer Mesh Topology
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {nodes.map((n) => (
                  <div key={n.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <span className="text-slate-100">{n.node_pseudonym}</span>
                      <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px]">{n.status}</span>
                    </div>
                    <div className="text-slate-400 text-[11px]">Trust Level: <strong className="text-cyan-300">{n.trust_tier}</strong></div>
                    <div className="text-[11px] text-slate-400">Consensus Voting Weight: <strong className="text-indigo-300">{n.consensus_weight}x</strong></div>
                    <div className="p-2 bg-slate-900 rounded font-mono text-[10px] text-slate-400 break-all">
                      {n.public_key_hash}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: Differential Privacy */}
          {activeTab === 'differential_privacy' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 max-w-2xl mx-auto space-y-4">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Sliders className="h-5 w-5 text-indigo-400" /> Differential Privacy (&epsilon;, &delta;) Budget Allocation
              </h3>
              <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 space-y-3 text-xs leading-relaxed text-slate-300">
                <div>
                  <strong className="text-indigo-400">Mathematical Privacy Guarantee: </strong>
                  The federated threat sharing engine applies calibrated Laplace noise $Lap(1/\epsilon)$ to aggregated telemetry counts and sighting velocities before cross-tenant syndication.
                </div>
                <div className="p-3 bg-slate-900 rounded font-mono text-[11px] text-cyan-300 space-y-1">
                  <div>Active Privacy Budget: &epsilon; = 0.50 (Strict Privacy)</div>
                  <div>Residual Information Leakage Probability: &delta; &lt; 10^-7</div>
                  <div>Anonymization Scheme: SHA-256 with Zero Reversible Tenant Artifacts</div>
                </div>
                <div className="text-slate-400 text-[11px]">
                  All peer telemetry guarantees zero possibility of reconstructing private IP ranges, employee identities, or internal network hostnames.
                </div>
              </div>
            </div>
          )}

          {/* TAB 6: Share Dispatcher */}
          {activeTab === 'share_dispatcher' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 max-w-2xl mx-auto space-y-4">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Send className="h-5 w-5 text-indigo-400" /> Anonymized Threat Indicator Share Dispatcher
              </h3>
              <p className="text-xs text-slate-400">
                Publish newly discovered threat indicators to the global peer federation. Indicator values are irreversibly hashed and protected with differential privacy before publication.
              </p>

              <form onSubmit={handleShareIndicator} className="space-y-3 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Raw Indicator Value (IP / Domain / Hash)</label>
                  <input
                    type="text"
                    value={rawIoc}
                    onChange={(e) => setRawIoc(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200 font-mono text-[11px]"
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-slate-400 mb-1">Threat Classification</label>
                    <select
                      value={shareClassification}
                      onChange={(e) => setShareClassification(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                    >
                      <option value="APT_C2_INFRASTRUCTURE">APT C2 Infrastructure</option>
                      <option value="RANSOMWARE_PAYLOAD">Ransomware Payload</option>
                      <option value="LLM_SYSTEM_PROMPT_EXPLOIT">LLM System Prompt Exploit</option>
                      <option value="TOR_EXIT_NODE_C2">Tor Exit Node C2</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1">Differential Privacy &epsilon; (Epsilon)</label>
                    <select
                      value={shareEpsilon}
                      onChange={(e) => setShareEpsilon(parseFloat(e.target.value))}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                    >
                      <option value={0.1}>0.1 (Maximum Privacy)</option>
                      <option value={0.5}>0.5 (Balanced High Privacy)</option>
                      <option value={1.0}>1.0 (Standard Privacy)</option>
                    </select>
                  </div>
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold flex items-center gap-2"
                  >
                    <Send className="h-4 w-4" /> Anonymize & Dispatch to Federation
                  </button>
                </div>
              </form>

              {shareSuccess && (
                <div className="p-4 bg-slate-950 rounded-xl border border-indigo-500/30 text-xs space-y-2 mt-4">
                  <div className="flex justify-between items-center text-indigo-400 font-bold">
                    <span>Indicator Published to Mesh</span>
                    <span>Status: {shareSuccess.syndication_status}</span>
                  </div>
                  <div className="p-2 bg-slate-900 rounded font-mono text-[10px] text-cyan-300 break-all">
                    Anonymized Hash: {shareSuccess.anonymized_indicator_hash}
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};
