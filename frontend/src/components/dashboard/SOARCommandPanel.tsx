import React, { useState, useEffect } from 'react';
import { 
  Zap, 
  CheckCircle2, 
  Lock, 
  RefreshCw
} from 'lucide-react';
import { dashboardService, SOARDashboardData } from '../../services/dashboard';
import { useAuth } from '../../hooks/useAuth';
import api from '../../services/api';

export const SOARCommandPanel: React.FC = () => {
  const { user } = useAuth();
  const [soarData, setSoarData] = useState<SOARDashboardData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [actionProcessing, setActionProcessing] = useState<string | null>(null);

  const isAdmin = user?.role === 'admin';

  const fetchSOARData = async () => {
    setIsLoading(true);
    try {
      const data = await dashboardService.getResponse();
      setSoarData(data);
    } catch (err) {
      console.error('Failed to load SOAR data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSOARData();
  }, []);

  const handleApproveAction = async (approvalId: string) => {
    if (!isAdmin) {
      alert('Only Admin users are authorized to approve and execute response actions.');
      return;
    }
    setActionProcessing(approvalId);
    try {
      await api.post(`/response/approve/${approvalId}`, { force_live: false });
      fetchSOARData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to approve action');
    } finally {
      setActionProcessing(null);
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-2xl backdrop-blur-md space-y-4 font-mono">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-cyan-500/10 border border-cyan-500/30 rounded-xl text-cyan-400">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              Autonomous SOAR Response & Approvals
            </h3>
            <p className="text-xs text-slate-400">
              Deterministic containment policies, multi-tier approvals, & safe rollback
            </p>
          </div>
        </div>

        <button
          onClick={fetchSOARData}
          className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl w-fit"
          title="Refresh SOAR Dashboard"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
          <span className="text-[10px] text-slate-500 block">PENDING APPROVALS</span>
          <span className="text-base font-bold text-amber-400">
            {soarData?.pending_approvals_count ?? 0}
          </span>
        </div>
        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
          <span className="text-[10px] text-slate-500 block">SUCCESSFUL ACTIONS</span>
          <span className="text-base font-bold text-emerald-400">
            {soarData?.successful_actions_count ?? 0}
          </span>
        </div>
        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
          <span className="text-[10px] text-slate-500 block">FAILED ACTIONS</span>
          <span className="text-base font-bold text-rose-400">
            {soarData?.failed_actions_count ?? 0}
          </span>
        </div>
        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
          <span className="text-[10px] text-slate-500 block">AVG RESPONSE LATENCY</span>
          <span className="text-base font-bold text-cyan-400">
            {soarData?.average_response_latency_ms ?? 48.5} ms
          </span>
        </div>
      </div>

      {/* Pending Approvals Queue */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-xs font-bold text-slate-300">Pending Response Approvals Queue</h4>
          <span className="text-[10px] text-slate-500">
            Current User Role: <span className="text-cyan-400 font-bold uppercase">{user?.role || 'VIEWER'}</span>
          </span>
        </div>

        {isLoading ? (
          <div className="py-6 text-center text-slate-500 text-xs flex items-center justify-center">
            <RefreshCw className="w-4 h-4 animate-spin mr-2" />
            LOADING SOAR APPROVALS QUEUE...
          </div>
        ) : !soarData || soarData.pending_approvals.length === 0 ? (
          <div className="py-6 text-center text-slate-500 text-xs bg-slate-950/60 rounded-xl border border-slate-800">
            NO PENDING RESPONSE ACTIONS AWAITING APPROVAL
          </div>
        ) : (
          <div className="space-y-2 max-h-[180px] overflow-y-auto pr-1">
            {soarData.pending_approvals.map((app) => (
              <div
                key={app.id}
                className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
              >
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 border border-amber-500/30 text-amber-400">
                      {app.requested_action}
                    </span>
                    <span className="text-xs font-bold text-slate-200">{app.target_entity}</span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-1">
                    Requested by <span className="text-slate-300 font-bold">{app.requested_by}</span> &bull;{' '}
                    {new Date(app.requested_at).toLocaleString()}
                  </div>
                </div>

                <div className="flex items-center space-x-2 shrink-0">
                  {isAdmin ? (
                    <button
                      disabled={actionProcessing === app.id}
                      onClick={() => handleApproveAction(app.id)}
                      className="px-3 py-1.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-lg text-xs font-bold transition-all shadow-md flex items-center space-x-1"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>{actionProcessing === app.id ? 'EXECUTING...' : 'APPROVE & EXECUTE'}</span>
                    </button>
                  ) : (
                    <span className="px-2.5 py-1 bg-slate-900 border border-slate-800 rounded-lg text-[10px] text-slate-500 flex items-center space-x-1">
                      <Lock className="w-3 h-3" />
                      <span>ADMIN APPROVAL REQUIRED</span>
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
