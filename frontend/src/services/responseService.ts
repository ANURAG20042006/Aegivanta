/**
 * frontend/src/services/responseService.ts
 * API Service for Controlled SOAR Approvals & Dry-Run Executions.
 */

import api from './api';

export interface ResponseApprovalItem {
  id: string;
  incident_id: string;
  requested_action: string;
  target_entity: string;
  parameters?: any;
  requested_by: string;
  requested_at: string;
  approved_by?: string;
  approved_at?: string;
  rejected_by?: string;
  rejected_at?: string;
  status: string;
  reason?: string;
  is_dry_run: boolean;
  execution_id?: string;
  audit_id?: string;
}

export const responseService = {
  listRequests: async (statusFilter?: string): Promise<ResponseApprovalItem[]> => {
    const url = statusFilter ? `/response/requests?status_filter=${statusFilter}` : '/response/requests';
    const res = await api.get(url);
    return Array.isArray(res.data) ? res.data : (res.data?.items || []);
  },

  submitRequest: async (incidentId: string, requestedAction: string, targetEntity: string, parameters?: any): Promise<any> => {
    const res = await api.post('/response/request', {
      incident_id: incidentId,
      requested_action: requestedAction,
      target_entity: targetEntity,
      parameters
    });
    return res.data;
  },

  approveRequest: async (requestId: string, forceLive: boolean = false): Promise<any> => {
    const res = await api.post(`/response/approve/${requestId}?force_live=${forceLive}`);
    return res.data;
  },

  rejectRequest: async (requestId: string, reason: string): Promise<any> => {
    const res = await api.post(`/response/reject/${requestId}`, { reason });
    return res.data;
  },

  executeDryRun: async (incidentId: string, actionType: string, targetEntity: string, parameters?: any): Promise<any> => {
    const res = await api.post('/response/execute-dryrun', {
      incident_id: incidentId,
      action_type: actionType,
      target_entity: targetEntity,
      parameters
    });
    return res.data;
  }
};
