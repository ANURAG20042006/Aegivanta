import React, { useState, useEffect } from 'react';
import { ShieldCheck, CheckCircle2, XCircle } from 'lucide-react';
import { responseService, ResponseApprovalItem } from '../services/responseService';

export const ResponseCenter: React.FC = () => {
  const [requests, setRequests] = useState<ResponseApprovalItem[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [rejectModalId, setRejectModalId] = useState<string | null>(null);
  const [rejectReason, setRejectReason] = useState<string>('');

  useEffect(() => {
    loadRequests();
  }, [statusFilter]);

  const loadRequests = async () => {
    try {
      const data = await responseService.listRequests(statusFilter || undefined);
      setRequests(data);
    } catch (err) {
      console.error('Failed to load response requests', err);
    }
  };

  const handleApprove = async (id: string) => {
    setActionLoading(id);
    try {
      await responseService.approveRequest(id, false); // Simulation dry-run default
      loadRequests();
    } catch (err) {
      console.error('Failed to approve request', err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async () => {
    if (!rejectModalId || !rejectReason.trim()) return;
    setActionLoading(rejectModalId);
    try {
      await responseService.rejectRequest(rejectModalId, rejectReason);
      setRejectModalId(null);
      setRejectReason('');
      loadRequests();
    } catch (err) {
      console.error('Failed to reject request', err);
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900/40 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-indigo-500/10 rounded-lg text-indigo-400 border border-indigo-500/20">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-wide">Controlled SOAR Response Center</h1>
        </div>
        <p className="text-slate-400 text-sm">
          Multi-tier authorization workflow for remediation actions. Default enforcement: <strong className="text-indigo-300">is_dry_run = True</strong>.
        </p>
      </div>

      {/* Filter Tabs */}
      <div className="flex justify-between items-center bg-slate-900/40 p-3 rounded-2xl border border-slate-800">
        <div className="flex gap-2">
          {['', 'REQUESTED', 'COMPLETED', 'REJECTED'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold uppercase tracking-wider transition ${
                statusFilter === st ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white bg-slate-800/40'
              }`}
            >
              {st || 'All Requests'}
            </button>
          ))}
        </div>
        <div className="text-xs text-slate-400 font-mono px-3">
          {requests.length} approval entries
        </div>
      </div>

      {/* Approval Requests Table */}
      <div className="bg-slate-900/40 rounded-2xl border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/80 text-slate-400 text-xs uppercase sticky top-0 backdrop-blur-md">
              <tr>
                <th className="p-4">Action / Target</th>
                <th className="p-4">Incident ID</th>
                <th className="p-4">Requested By</th>
                <th className="p-4">Mode & Status</th>
                <th className="p-4">Timestamp</th>
                <th className="p-4 text-right">Authorization</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {requests.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-10 text-center text-slate-500">
                    No response requests matching filter.
                  </td>
                </tr>
              ) : (
                requests.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/40 transition">
                    <td className="p-4">
                      <div className="font-semibold text-slate-200">{r.requested_action}</div>
                      <div className="text-xs text-indigo-400 font-mono mt-0.5">{r.target_entity}</div>
                    </td>
                    <td className="p-4 text-xs font-mono text-slate-300">
                      {r.incident_id.slice(0, 8)}...
                    </td>
                    <td className="p-4 text-xs text-slate-300">
                      {r.requested_by}
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <span className={`px-2.5 py-0.5 rounded text-xs font-semibold uppercase ${
                          r.status === 'REQUESTED' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                          r.status === 'COMPLETED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                          'bg-red-500/10 text-red-400 border border-red-500/20'
                        }`}>
                          {r.status}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                          DRY RUN
                        </span>
                      </div>
                    </td>
                    <td className="p-4 text-xs text-slate-400">
                      {new Date(r.requested_at).toLocaleString()}
                    </td>
                    <td className="p-4 text-right">
                      {r.status === 'REQUESTED' ? (
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleApprove(r.id)}
                            disabled={actionLoading === r.id}
                            className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold transition disabled:opacity-50"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            Approve
                          </button>
                          <button
                            onClick={() => setRejectModalId(r.id)}
                            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-red-400 rounded-lg text-xs font-semibold border border-red-500/20 transition"
                          >
                            <XCircle className="w-3.5 h-3.5" />
                            Reject
                          </button>
                        </div>
                      ) : (
                        <span className="text-xs text-slate-500">
                          {r.approved_by ? `Approved by ${r.approved_by}` : (r.rejected_by ? `Rejected by ${r.rejected_by}` : 'Processed')}
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Reject Modal */}
      {rejectModalId && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4">
            <h3 className="text-lg font-semibold text-white">Reject Response Action</h3>
            <p className="text-xs text-slate-400">Provide an operational justification for rejecting this action request.</p>
            <textarea
              rows={3}
              placeholder="e.g. Host is a critical business API gateway, cannot block without failover."
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
            />
            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={() => setRejectModalId(null)}
                className="px-4 py-2 text-slate-400 hover:text-white text-sm"
              >
                Cancel
              </button>
              <button
                onClick={handleReject}
                className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-xl text-sm font-medium"
              >
                Confirm Rejection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
