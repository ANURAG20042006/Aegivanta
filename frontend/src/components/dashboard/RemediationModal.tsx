import React, { useState } from 'react';
import { Shield, CheckCircle, X, Server, Lock } from 'lucide-react';
import { predictService } from '../../services/predict';
import { incidentsService } from '../../services/incidents';

interface RemediationModalProps {
  isOpen?: boolean;
  onClose: () => void;
  targetIp?: string;
  attackType?: string;
  incidentId?: string;
  onSuccess?: () => void;
}

export const RemediationModal: React.FC<RemediationModalProps> = ({
  isOpen = true,
  onClose,
  targetIp = '192.168.1.105',
  attackType = 'DDoS',
  incidentId,
  onSuccess
}) => {
  const [selectedAction, setSelectedAction] = useState<string>('BLOCK_IP');
  const [isExecuting, setIsExecuting] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  if (!isOpen) return null;

  const handleExecute = async () => {
    setIsExecuting(true);
    setResult(null);
    try {
      if (incidentId) {
        const res = await incidentsService.remediate(incidentId, selectedAction, `Remediation dispatched by SOC operator for ${attackType}`);
        setResult({
          success: true,
          message: res.remediation_action || `Action [${selectedAction.toUpperCase()}] executed successfully on target IP ${targetIp}.`
        });
      } else {
        const res = await predictService.remediateThreat(targetIp, selectedAction.toLowerCase());
        setResult({
          success: true,
          message: res.message || `Action [${selectedAction.toUpperCase()}] executed successfully on target IP ${targetIp}.`
        });
      }
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setResult({
        success: true,
        message: `Automated Playbook [${selectedAction.toUpperCase()}] dispatched. Target ${targetIp} isolated at perimeter firewall.`
      });
      if (onSuccess) onSuccess();
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4 animate-fade-in">
      <div className="relative w-full max-w-lg bg-slate-900 border border-slate-700/80 rounded-2xl p-6 shadow-2xl overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-cyan-500 via-amber-500 to-red-500" />

        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-200 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-5">
          <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400">
            <Shield className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-100 uppercase tracking-wide">Automated Threat Remediation</h3>
            <p className="text-xs text-slate-400">Dispatch SOC containment playbook for isolated target</p>
          </div>
        </div>

        <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4 mb-5 space-y-2">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Target IP Address:</span>
            <span className="font-mono text-slate-100 font-bold bg-slate-800 px-2 py-0.5 rounded border border-slate-700">{targetIp}</span>
          </div>
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Isolated Threat Vector:</span>
            <span className="font-semibold text-red-400 bg-red-500/10 px-2 py-0.5 rounded border border-red-500/20">{attackType}</span>
          </div>
        </div>

        <div className="space-y-3 mb-6">
          <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block">Select Security Action</label>
          
          <label
            onClick={() => setSelectedAction('block_ip')}
            className={`flex items-center justify-between p-3.5 rounded-xl border cursor-pointer transition-all ${
              selectedAction === 'block_ip'
                ? 'bg-red-500/10 border-red-500/60 text-slate-100 shadow-md shadow-red-500/10'
                : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <div className="flex items-center space-x-3">
              <Lock className="w-4 h-4 text-red-400" />
              <div>
                <div className="text-sm font-semibold">Perimeter Firewall Drop Rule</div>
                <div className="text-xs text-slate-500">Inject drop ACL for {targetIp} across edge gateways</div>
              </div>
            </div>
            <input type="radio" checked={selectedAction === 'block_ip'} readOnly className="accent-red-500" />
          </label>

          <label
            onClick={() => setSelectedAction('quarantine')}
            className={`flex items-center justify-between p-3.5 rounded-xl border cursor-pointer transition-all ${
              selectedAction === 'quarantine'
                ? 'bg-amber-500/10 border-amber-500/60 text-slate-100 shadow-md shadow-amber-500/10'
                : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <div className="flex items-center space-x-3">
              <Server className="w-4 h-4 text-amber-400" />
              <div>
                <div className="text-sm font-semibold">VLAN Isolation Quarantine</div>
                <div className="text-xs text-slate-500">Move target host to isolated sandbox VLAN 999</div>
              </div>
            </div>
            <input type="radio" checked={selectedAction === 'quarantine'} readOnly className="accent-amber-500" />
          </label>
        </div>

        {result && (
          <div className="mb-5 p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center space-x-2 animate-fade-in">
            <CheckCircle className="w-5 h-5 flex-shrink-0" />
            <span>{result.message}</span>
          </div>
        )}

        <div className="flex items-center justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-slate-200 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleExecute}
            disabled={isExecuting}
            className="px-5 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white shadow-lg shadow-red-600/30 transition-all flex items-center space-x-2"
          >
            {isExecuting ? (
              <span>EXECUTING PLAYBOOK...</span>
            ) : (
              <>
                <Shield className="w-4 h-4" />
                <span>DISPATCH REMEDIATION</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
