/**
 * frontend/src/services/threatGraphService.ts
 * API Service for Threat Intelligence Graph Topology and Evidence Inspection.
 */

import api from './api';

export interface ThreatGraphNodeItem {
  id: string;
  node_type: string;
  label: string;
  reference_id?: string;
  criticality?: string;
  ip_address?: string;
  attack_type?: string;
  severity?: string;
  risk_score?: number;
  threat_type?: string;
  stage?: string;
}

export interface ThreatGraphEdgeItem {
  id: string;
  source: string;
  target: string;
  relationship_type: string;
  confidence: number;
  evidence_count: number;
}

export interface ThreatGraphData {
  total_nodes: number;
  total_edges: number;
  nodes: ThreatGraphNodeItem[];
  edges: ThreatGraphEdgeItem[];
  generated_at: string;
}

export const threatGraphService = {
  getGraphTopology: async (limit: number = 150): Promise<ThreatGraphData> => {
    const res = await api.get(`/threat-graph?limit=${limit}`);
    return res.data;
  },

  getNodeEvidence: async (nodeId: string): Promise<any> => {
    const res = await api.get(`/threat-graph/nodes/${nodeId}/evidence`);
    return res.data;
  }
};
