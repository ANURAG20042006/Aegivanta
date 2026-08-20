import React, { useEffect, useState } from 'react';
import {
  CheckCircle,
  XCircle,
  Activity,
  UserCheck
} from 'lucide-react';


export const ResponseApprovals: React.FC = () => {
  const [approvals, setApprovals] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  useEffect(() => {
    fetchApprovals();
  }, []);

  const fetchApprovals = async () => {
    try {
      setLoading(true);
      // Simulated active response approval tickets
      setApprovals([
        {
          id: 'APP-9901',
          incident_id: 'INC-8831',
          requested_action: 'ISOLATE_ENDPOINT',
          target_entity: 'Sensor-Worker-Node-04 (10.0.0.45)',
          requested_by: 'AUTONOMOUS_POLICY_LEVEL_2',
          risk_score: 88,
          business_impact: 'MEDIUM',
          blast_radius_assets: 1,
          reason: 'Correlated C2 Beaconing and active lateral movement probing detected on endpoint.'
        },
        {
          id: 'APP-9902',
          incident_id: 'INC-8840',
          requested_action: 'DISABLE_API_KEY',
          target_entity: 'key_prod_ingest_9a7b (CI/CD Pipeline)',
          requested_by: 'BEHAVIORAL_ANOMALY_ENGINE',
          risk_score: 79,
          business_impact: 'HIGH',
          blast_radius_assets: 3,
          reason: 'Excessive 403 authorization bursts originating from untrusted geolocations.'
        }
      ]);
    } catch (err) {
      console.error('Failed to load response approvals:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: string) => {
    setActionSuccess(`Response action ${id} successfully APPROVED and dispatched for execution.`);
    setApprovals((prev) => prev.filter((a) => a.id !== id));
    setTimeout(() => setActionSuccess(null), 4000);
  };

  const handleReject = async (id: string) => {
    setActionSuccess(`Response action ${id} REJECTED. Threat marked for manual investigation.`);
    setApprovals((prev) => prev.filter((a) => a.id !== id));
    setTimeout(() => setActionSuccess(null), 4000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <UserCheck className="h-7 w-7 text-indigo-400" />
            Response Approval Center & Gated Remediation
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Two-tier authorization workflow for high-impact autonomous containment and rollback management.
          </p>
        </div>

        <button
          onClick={fetchApprovals}
          className="flex items-center gap-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-colors"
        >
          <Activity className="h-4 w-4 text-cyan-400" /> Refresh Queue
        </button>
      </div>

      {actionSuccess && (
        <div className="p-3.5 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 text-xs font-semibold flex items-center gap-2">
          <CheckCircle className="h-4 w-4 shrink-0" />
          {actionSuccess}
        </div>
      )}

      {loading ? (
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Activity className="h-8 w-8 animate-spin text-indigo-400 mr-3" />
          Loading pending response approvals...
        </div>
      ) : (
        <div className="space-y-4">
          {approvals.length === 0 ? (
            <div className="p-12 text-center bg-slate-900/40 border border-slate-800/80 rounded-xl">
              <CheckCircle className="h-10 w-10 text-emerald-400 mx-auto mb-3" />
              <h3 className="text-sm font-semibold text-slate-200">No Pending Approvals</h3>
              <p className="text-xs text-slate-500 mt-1">All autonomous remediation queues are clear.</p>
            </div>
          ) : (
            approvals.map((app) => (
              <div
                key={app.id}
                className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 backdrop-blur-sm space-y-4"
              >
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2 border-b border-slate-800 pb-3">
                  <div className="flex items-center gap-3">
                    <span className="px-2.5 py-1 rounded-md text-xs font-mono font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                      {app.id}
                    </span>
                    <span className="text-sm font-bold text-slate-100">{app.requested_action}</span>
                    <span className="text-xs text-slate-400">Target: {app.target_entity}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                      Risk {app.risk_score}/100
                    </span>
                    <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      Impact: {app.business_impact}
                    </span>
                  </div>
                </div>

                <div className="text-xs text-slate-300">
                  <strong>Trigger Reason:</strong> {app.reason}
                </div>

                <div className="flex items-center justify-end gap-3 pt-2">
                  <button
                    onClick={() => handleReject(app.id)}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 text-xs font-bold rounded-lg border border-rose-500/30 transition-all"
                  >
                    <XCircle className="h-4 w-4" /> Reject Action
                  </button>
                  <button
                    onClick={() => handleApprove(app.id)}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold rounded-lg transition-all"
                  >
                    <CheckCircle className="h-4 w-4" /> Approve & Execute
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};
