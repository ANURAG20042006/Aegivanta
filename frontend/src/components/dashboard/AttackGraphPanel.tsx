import React, { useState, useEffect } from 'react';
import { 
  Network, 
  RefreshCw
} from 'lucide-react';
import api from '../../services/api';

interface GraphNode {
  id: string;
  node_type: string;
  label: string;
  reference_id?: string;
  criticality?: string;
  severity?: string;
  risk_score?: number;
  ip_address?: string;
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relationship_type: string;
  confidence?: number;
  evidence_count?: number;
}

interface ChokePoint {
  node_id: string;
  label: string;
  node_type: string;
  total_degree: number;
  betweenness_score: number;
  isolation_priority: string;
}

export const AttackGraphPanel: React.FC = () => {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [chokePoints, setChokePoints] = useState<ChokePoint[]>([]);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [blastRadius, setBlastRadius] = useState<any | null>(null);
  const [highlightChokePoints, setHighlightChokePoints] = useState<boolean>(false);
  const [highlightCrownJewels, setHighlightCrownJewels] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isCalculatingBlast, setIsCalculatingBlast] = useState<boolean>(false);

  const fetchGraphData = async () => {
    setIsLoading(true);
    try {
      const [topoRes, chokeRes] = await Promise.allSettled([
        api.get('/threat-graph/topology?limit=50'),
        api.get('/threat-graph/chokepoints?top_n=5')
      ]);

      if (topoRes.status === 'fulfilled' && topoRes.value.data) {
        setNodes(topoRes.value.data.nodes || []);
        setEdges(topoRes.value.data.edges || []);
      }
      if (chokeRes.status === 'fulfilled' && Array.isArray(chokeRes.value.data)) {
        setChokePoints(chokeRes.value.data);
      }
    } catch (err) {
      console.error('Failed to load attack graph:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchGraphData();
  }, []);

  const handleNodeClick = async (node: GraphNode) => {
    setSelectedNode(node);
    setIsCalculatingBlast(true);
    try {
      const res = await api.get(`/threat-graph/blast-radius?origin_node_id=${encodeURIComponent(node.id)}&max_depth=3`);
      setBlastRadius(res.data);
    } catch (err) {
      setBlastRadius(null);
    } finally {
      setIsCalculatingBlast(false);
    }
  };

  const getNodeColor = (node: GraphNode) => {
    const isChoke = chokePoints.some((c) => c.node_id === node.id);
    const isCrownJewel = node.criticality === 'CRITICAL' || node.criticality === 'critical';

    if (highlightChokePoints && isChoke) return 'border-amber-400 bg-amber-500/20 text-amber-300 shadow-amber-500/30';
    if (highlightCrownJewels && isCrownJewel) return 'border-rose-400 bg-rose-500/20 text-rose-300 shadow-rose-500/30';

    switch (node.node_type?.toUpperCase()) {
      case 'ASSET':
        return 'border-cyan-500/40 bg-cyan-500/10 text-cyan-300';
      case 'INCIDENT':
        return 'border-red-500/40 bg-red-500/10 text-red-300';
      case 'IOC':
        return 'border-purple-500/40 bg-purple-500/10 text-purple-300';
      case 'TECHNIQUE':
        return 'border-indigo-500/40 bg-indigo-500/10 text-indigo-300';
      default:
        return 'border-slate-700 bg-slate-800 text-slate-300';
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-2xl backdrop-blur-md space-y-4 font-mono">
      {/* Header & Mode Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-indigo-500/10 border border-indigo-500/30 rounded-xl text-indigo-400">
            <Network className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              Attack Graph & Lateral Movement Topology
            </h3>
            <p className="text-xs text-slate-400">
              IP &rarr; USER &rarr; HOST &rarr; IOC &rarr; INCIDENT &rarr; ASSET Provenance Map
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Choke Points Toggle */}
          <button
            onClick={() => setHighlightChokePoints(!highlightChokePoints)}
            className={`px-2.5 py-1 text-xs rounded-xl border transition-all ${
              highlightChokePoints
                ? 'bg-amber-500/20 border-amber-500/50 text-amber-300 shadow-md shadow-amber-500/20'
                : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            Choke Points
          </button>

          {/* Crown Jewels Toggle */}
          <button
            onClick={() => setHighlightCrownJewels(!highlightCrownJewels)}
            className={`px-2.5 py-1 text-xs rounded-xl border transition-all ${
              highlightCrownJewels
                ? 'bg-rose-500/20 border-rose-500/50 text-rose-300 shadow-md shadow-rose-500/20'
                : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            Crown Jewels
          </button>

          <button
            onClick={fetchGraphData}
            className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl"
            title="Refresh Topology"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Main Canvas & Inspection Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Topology Nodes Grid Area */}
        <div className="lg:col-span-2 bg-slate-950/70 border border-slate-800/80 rounded-xl p-4 min-h-[300px] flex flex-col justify-between">
          {isLoading ? (
            <div className="h-full min-h-[250px] flex items-center justify-center text-slate-500 text-xs">
              <RefreshCw className="w-5 h-5 animate-spin mr-2 text-cyan-400" />
              BUILDING GRAPH TOPOLOGY & DEGREE CENTRALITY...
            </div>
          ) : nodes.length === 0 ? (
            <div className="h-full min-h-[250px] flex items-center justify-center text-slate-500 text-xs">
              NO TOPOLOGICAL NODES IN ACTIVE SOC GRAPH
            </div>
          ) : (
            <div className="space-y-3">
              <div className="text-[11px] text-slate-400 flex items-center justify-between">
                <span>Total Entities: {nodes.length} Nodes &bull; {edges.length} Relationships</span>
                <span className="text-cyan-400">Click any node for Blast Radius computation</span>
              </div>

              {/* Node Chips */}
              <div className="flex flex-wrap gap-2 max-h-[220px] overflow-y-auto p-1">
                {nodes.map((n) => {
                  const isSelected = selectedNode?.id === n.id;
                  return (
                    <div
                      key={n.id}
                      onClick={() => handleNodeClick(n)}
                      className={`px-3 py-1.5 rounded-xl border text-xs cursor-pointer transition-all shadow-md flex items-center space-x-1.5 ${getNodeColor(n)} ${
                        isSelected ? 'ring-2 ring-cyan-400 scale-105' : 'hover:scale-[1.03]'
                      }`}
                    >
                      <span className="font-bold">{n.label || n.id}</span>
                      <span className="text-[9px] opacity-70 uppercase tracking-wider">({n.node_type})</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Legend */}
          <div className="flex flex-wrap items-center gap-3 pt-3 border-t border-slate-800/60 text-[10px] text-slate-400">
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 rounded-full bg-cyan-400" />
              <span>Asset</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 rounded-full bg-red-400" />
              <span>Incident</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 rounded-full bg-purple-400" />
              <span>IOC</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 rounded-full bg-amber-400" />
              <span>Choke Point</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 rounded-full bg-rose-500" />
              <span>Crown Jewel</span>
            </span>
          </div>
        </div>

        {/* Selected Node & Blast Radius Drawer */}
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              Entity Blast Radius
            </h4>
            {selectedNode && (
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                {selectedNode.node_type}
              </span>
            )}
          </div>

          {!selectedNode ? (
            <div className="py-12 text-center text-slate-500 text-xs">
              Select an entity node to compute forward reachability and Crown Jewel Exposure Index.
            </div>
          ) : isCalculatingBlast ? (
            <div className="py-12 text-center text-cyan-400 text-xs flex items-center justify-center">
              <RefreshCw className="w-4 h-4 animate-spin mr-2" />
              CALCULATING BLAST RADIUS...
            </div>
          ) : blastRadius ? (
            <div className="space-y-2.5 text-xs">
              <div>
                <span className="text-slate-500 text-[10px]">TARGET NODE</span>
                <p className="text-slate-100 font-bold text-sm">{blastRadius.origin_label}</p>
              </div>

              <div className="grid grid-cols-2 gap-2 bg-slate-900/80 p-2.5 rounded-xl border border-slate-800">
                <div>
                  <span className="text-[10px] text-slate-500">BLAST RADIUS</span>
                  <p className="text-rose-400 font-bold text-base">{blastRadius.blast_radius_score}%</p>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500">CROWN JEWEL EXPOSURE</span>
                  <p className="text-amber-400 font-bold text-base">{blastRadius.crown_jewel_exposure_index}%</p>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500">REACHABLE NODES</span>
                  <p className="text-slate-200 font-bold">{blastRadius.total_reachable_nodes}</p>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500">EXPOSED ASSETS</span>
                  <p className="text-slate-200 font-bold">{blastRadius.reachable_assets_count}</p>
                </div>
              </div>

              {blastRadius.reachable_assets && blastRadius.reachable_assets.length > 0 && (
                <div>
                  <span className="text-[10px] text-slate-500">EXPOSED ASSETS LIST:</span>
                  <div className="max-h-24 overflow-y-auto space-y-1 mt-1">
                    {blastRadius.reachable_assets.map((ast: any, idx: number) => (
                      <div key={idx} className="p-1 bg-slate-900 rounded text-[10px] flex justify-between">
                        <span className="text-slate-300 font-bold">{ast.label}</span>
                        <span className="text-amber-400">{ast.criticality} ({ast.hop_distance} hops)</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-xs text-slate-500 py-6 text-center">
              No blast radius data available for selected entity.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
