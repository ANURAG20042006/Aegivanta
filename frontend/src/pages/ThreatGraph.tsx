import React, { useState, useEffect } from 'react';
import { Network, Database, RefreshCw } from 'lucide-react';
import { threatGraphService, ThreatGraphData, ThreatGraphNodeItem } from '../services/threatGraphService';

export const ThreatGraph: React.FC = () => {
  const [graphData, setGraphData] = useState<ThreatGraphData | null>(null);
  const [selectedNode, setSelectedNode] = useState<ThreatGraphNodeItem | null>(null);
  const [nodeEvidence, setNodeEvidence] = useState<any | null>(null);
  const [loadingEvidence, setLoadingEvidence] = useState<boolean>(false);

  useEffect(() => {
    loadGraph();
  }, []);

  const loadGraph = async () => {
    try {
      const data = await threatGraphService.getGraphTopology();
      setGraphData(data);
      if (data.nodes && data.nodes.length > 0) {
        handleSelectNode(data.nodes[0]);
      }
    } catch (err) {
      console.error('Failed to load threat graph topology', err);
    }
  };

  const handleSelectNode = async (node: ThreatGraphNodeItem) => {
    setSelectedNode(node);
    setLoadingEvidence(true);
    try {
      const ev = await threatGraphService.getNodeEvidence(node.id);
      setNodeEvidence(ev);
    } catch (err) {
      console.error('Failed to load node evidence', err);
    } finally {
      setLoadingEvidence(false);
    }
  };

  const getNodeColor = (type: string) => {
    switch (type) {
      case 'ASSET':
        return 'border-blue-500/40 bg-blue-500/10 text-blue-400';
      case 'INCIDENT':
        return 'border-red-500/40 bg-red-500/10 text-red-400';
      case 'IOC':
        return 'border-purple-500/40 bg-purple-500/10 text-purple-400';
      case 'TECHNIQUE':
        return 'border-amber-500/40 bg-amber-500/10 text-amber-400';
      default:
        return 'border-slate-500/40 bg-slate-500/10 text-slate-400';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center bg-slate-900/40 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-indigo-500/10 rounded-lg text-indigo-400 border border-indigo-500/20">
              <Network className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-wide">Threat Intelligence Graph</h1>
          </div>
          <p className="text-slate-400 text-sm">
            Evidence-backed multi-entity relationships linking Protected Assets, Incidents, Threat IOCs, and MITRE Techniques.
          </p>
        </div>

        <button
          onClick={loadGraph}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-sm font-medium border border-slate-700 transition"
        >
          <RefreshCw className="w-4 h-4 text-indigo-400" />
          Refresh Topology
        </button>
      </div>

      {/* Graph Visualizer & Evidence Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Interactive Node & Edge Mesh */}
        <div className="lg:col-span-2 bg-slate-900/40 p-6 rounded-2xl border border-slate-800 space-y-6 min-h-[500px]">
          <div className="flex justify-between items-center text-xs text-slate-400">
            <div className="flex items-center gap-4">
              <span>Nodes: <strong className="text-slate-200">{graphData?.total_nodes || 0}</strong></span>
              <span>•</span>
              <span>Evidence Edges: <strong className="text-slate-200">{graphData?.total_edges || 0}</strong></span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-400 inline-block" /> Asset
              <span className="w-2.5 h-2.5 rounded-full bg-red-400 inline-block ml-2" /> Incident
              <span className="w-2.5 h-2.5 rounded-full bg-purple-400 inline-block ml-2" /> IOC
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block ml-2" /> Technique
            </div>
          </div>

          {/* Node Cards Matrix */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3.5 max-h-[420px] overflow-y-auto pr-1">
            {graphData?.nodes.map((node) => (
              <div
                key={node.id}
                onClick={() => handleSelectNode(node)}
                className={`p-4 rounded-xl border cursor-pointer transition flex flex-col justify-between ${
                  selectedNode?.id === node.id ? 'ring-2 ring-indigo-500 scale-[1.02]' : 'hover:border-slate-700'
                } ${getNodeColor(node.node_type)}`}
              >
                <div>
                  <div className="text-[10px] font-bold uppercase tracking-wider opacity-75">{node.node_type}</div>
                  <div className="font-semibold text-slate-100 text-sm mt-1 line-clamp-1">{node.label}</div>
                </div>

                <div className="text-[11px] opacity-80 mt-3 pt-2 border-t border-slate-800/40 flex justify-between">
                  <span>{node.severity || node.criticality || node.threat_type || 'Active'}</span>
                  {node.risk_score && <span className="font-bold">{node.risk_score} / 100</span>}
                </div>
              </div>
            ))}
          </div>

          {/* Active Relationship Edges List */}
          <div className="pt-4 border-t border-slate-800 space-y-2">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Verified Evidence-Backed Relationship Links
            </h3>
            <div className="space-y-1.5 max-h-[140px] overflow-y-auto pr-1 text-xs">
              {graphData?.edges.map((edge) => (
                <div key={edge.id} className="p-2 bg-slate-800/40 rounded-lg border border-slate-800/60 flex items-center justify-between text-slate-300 font-mono">
                  <div>
                    <span className="text-indigo-400">{edge.source}</span>
                    <span className="text-slate-500 px-2">──({edge.relationship_type})──&gt;</span>
                    <span className="text-emerald-400">{edge.target}</span>
                  </div>
                  <span className="text-[11px] text-slate-400 font-sans">{edge.evidence_count} evidence items</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Col: Node Evidence Drilldown */}
        <div className="bg-slate-900/40 p-5 rounded-2xl border border-slate-800 space-y-4">
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <Database className="w-4 h-4 text-indigo-400" />
            Underlying Node Evidence
          </h2>

          {selectedNode ? (
            <div className="space-y-4 text-xs">
              <div className="p-4 bg-slate-800/60 rounded-xl border border-slate-700/60 space-y-2">
                <div className="text-xs text-indigo-400 font-semibold uppercase">{selectedNode.node_type} Entity</div>
                <div className="text-base font-bold text-white">{selectedNode.label}</div>
                <div className="font-mono text-[11px] text-slate-400 break-all">{selectedNode.id}</div>
              </div>

              {loadingEvidence ? (
                <p className="text-xs text-slate-500 text-center py-6">Loading evidence records...</p>
              ) : (
                <div className="space-y-3">
                  <div className="p-3.5 bg-slate-800/40 rounded-xl border border-slate-800 space-y-1.5">
                    <div className="text-slate-400 font-medium">Record Attributes:</div>
                    <pre className="text-[11px] text-slate-300 whitespace-pre-wrap font-mono max-h-[220px] overflow-y-auto">
                      {JSON.stringify(nodeEvidence?.data || {}, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-slate-500 py-12 text-center">Select any graph node to inspect underlying evidence.</p>
          )}
        </div>
      </div>
    </div>
  );
};
