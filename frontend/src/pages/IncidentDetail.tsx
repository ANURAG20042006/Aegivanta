import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  ShieldAlert, 
  Server, 
  ArrowLeft, 
  Activity, 
  Wrench, 
  RefreshCw
} from 'lucide-react';
import { IncidentDetail } from '../types';
import { incidentsService } from '../services/incidents';
import { AttackTimeline } from '../components/dashboard/AttackTimeline';
import { RemediationModal } from '../components/dashboard/RemediationModal';
import { useAuth } from '../hooks/useAuth';

export const IncidentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [incident, setIncident] = useState<IncidentDetail | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState<boolean>(false);
  const [statusNotes, setStatusNotes] = useState<string>('');
  const [isRemediationOpen, setIsRemediationOpen] = useState<boolean>(false);

  const canTriage = user?.role === 'admin' || user?.role === 'analyst';

  const fetchIncident = async () => {
    if (!id) return;
    setIsLoading(true);
    try {
      const data = await incidentsService.get(id);
      setIncident(data);
    } catch (err) {
      console.error('Failed to load incident detail:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchIncident();
  }, [id]);

  const handleStatusTransition = async (newStatus: string) => {
    if (!incident) return;
    setIsUpdatingStatus(true);
    try {
      await incidentsService.updateStatus(incident.id, newStatus, statusNotes);
      setStatusNotes('');
      fetchIncident();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to transition incident status');
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[500px] text-cyan-400 font-mono text-xs">
        <RefreshCw className="w-6 h-6 animate-spin mr-2" />
        LOADING INCIDENT & ATTACK TIMELINE...
      </div>
    );
  }

  if (!incident) {
    return (
      <div className="text-center py-20 font-mono">
        <h2 className="text-xl font-bold text-slate-200 mb-2">Incident Not Found</h2>
        <p className="text-xs text-slate-500 mb-6">The requested security incident identifier does not exist.</p>
        <Link to="/history" className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs">
          Return to Incident History
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-12 animate-fade-in">
      {/* Top Breadcrumb & Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center space-x-2 text-xs font-mono text-slate-400 hover:text-cyan-400 transition-colors cursor-pointer w-fit"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>BACK TO PREVIOUS VIEW</span>
        </button>

        <div className="flex items-center space-x-3">
          {canTriage && (
            <button
              onClick={() => setIsRemediationOpen(true)}
              className="px-4 py-2 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white rounded-xl text-xs font-mono font-bold shadow-lg shadow-red-600/30 transition-all flex items-center space-x-2 cursor-pointer"
            >
              <Wrench className="w-4 h-4" />
              <span>Execute Containment / Remediation</span>
            </button>
          )}
          <button
            onClick={fetchIncident}
            className="p-2 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded-xl border border-slate-800 transition-colors cursor-pointer"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Primary Incident Info Card */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="flex items-start space-x-4">
            <div className="p-3.5 bg-red-500/10 border border-red-500/30 rounded-2xl text-red-400 shrink-0 mt-1">
              <ShieldAlert className="w-8 h-8 animate-pulse" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-black uppercase bg-red-500/10 border border-red-500/30 text-red-400">
                  {incident.severity}
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-blue-500/10 border border-blue-500/30 text-blue-400">
                  STATUS: {incident.status}
                </span>
                <span className="text-xs font-mono text-cyan-400 font-bold">
                  {incident.incident_code || incident.id}
                </span>
              </div>

              <h1 className="text-xl sm:text-2xl font-black text-slate-100 font-mono tracking-wide">
                {incident.title || `${incident.attack_type} Detected`}
              </h1>
              <p className="text-xs text-slate-400 mt-1 max-w-2xl font-sans leading-relaxed">
                {incident.description || 'Continuous threat telemetry correlation record.'}
              </p>
            </div>
          </div>

          {/* Dynamic Risk Gauge */}
          <div className="flex items-center space-x-6 bg-slate-950/80 p-4 rounded-2xl border border-slate-800 shrink-0">
            <div>
              <span className="text-[11px] font-mono text-slate-400 uppercase block">Dynamic Risk Score</span>
              <div className="flex items-baseline space-x-1.5 mt-0.5">
                <span className={`text-3xl font-black font-mono ${(incident.risk_score || 0) >= 75 ? 'text-red-400' : 'text-amber-400'}`}>
                  {(incident.risk_score || 0).toFixed(1)}
                </span>
                <span className="text-xs text-slate-500 font-mono">/ 100</span>
              </div>
            </div>
            <div className="h-10 w-[1px] bg-slate-800" />
            <div>
              <span className="text-[11px] font-mono text-slate-400 uppercase block">Correlated Alerts</span>
              <span className="text-2xl font-black font-mono text-cyan-400 mt-0.5 block">
                {incident.alert_count || incident.alerts?.length || 1}
              </span>
            </div>
          </div>
        </div>

        {/* Telemetry metadata row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 pt-6 border-t border-slate-800/80 text-xs font-mono">
          <div>
            <span className="text-slate-500 uppercase block text-[10px]">Source Actor IP</span>
            <span className="text-slate-200 font-bold mt-0.5 block">{incident.source_ip}:{incident.source_port}</span>
          </div>
          <div>
            <span className="text-slate-500 uppercase block text-[10px]">Target Destination IP</span>
            <span className="text-slate-200 font-bold mt-0.5 block">{incident.destination_ip}:{incident.destination_port}</span>
          </div>
          <div>
            <span className="text-slate-500 uppercase block text-[10px]">First Detected</span>
            <span className="text-slate-300 mt-0.5 block">{new Date(incident.first_seen || incident.timestamp).toLocaleString()}</span>
          </div>
          <div>
            <span className="text-slate-500 uppercase block text-[10px]">Last Seen Activity</span>
            <span className="text-slate-300 mt-0.5 block">{new Date(incident.last_seen || incident.timestamp).toLocaleString()}</span>
          </div>
        </div>
      </div>

      {/* Middle Grid: Affected Asset + Status State Machine Workflow */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Affected Asset Card */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl">
          <div className="flex items-center space-x-3 mb-4 pb-3 border-b border-slate-800">
            <div className="p-2 bg-cyan-500/10 border border-cyan-500/30 rounded-xl text-cyan-400">
              <Server className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-100 font-mono">
                AFFECTED PROTECTED ASSET
              </h3>
              <p className="text-[11px] text-slate-400 font-sans">
                Monitored infrastructure target in inventory.
              </p>
            </div>
          </div>

          {incident.asset ? (
            <div className="space-y-3 text-xs font-mono">
              <div className="flex justify-between">
                <span className="text-slate-400">Asset Name:</span>
                <span className="text-slate-200 font-bold font-sans">{incident.asset.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Hostname / FQDN:</span>
                <span className="text-cyan-400 font-bold">{incident.asset.hostname}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Asset Type:</span>
                <span className="text-slate-300 uppercase">{incident.asset.asset_type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Criticality:</span>
                <span className="text-red-400 font-bold uppercase">{incident.asset.criticality}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Current Health:</span>
                <span className="text-amber-400 font-bold uppercase">{incident.asset.status}</span>
              </div>
            </div>
          ) : (
            <div className="text-center py-6 text-slate-500 text-xs font-mono">
              Target IP ({incident.destination_ip}) is not yet registered as a named protected asset.
              <Link to="/assets" className="block text-cyan-400 hover:underline mt-2">
                + Register to Inventory
              </Link>
            </div>
          )}
        </div>

        {/* State Machine Transition Workflow */}
        <div className="lg:col-span-2 bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl">
          <div className="flex items-center space-x-3 mb-4 pb-3 border-b border-slate-800">
            <div className="p-2 bg-blue-500/10 border border-blue-500/30 rounded-xl text-blue-400">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-100 font-mono">
                LIFECYCLE STATE WORKFLOW
              </h3>
              <p className="text-[11px] text-slate-400 font-sans">
                Progress incident along the verified SOC lifecycle machine.
              </p>
            </div>
          </div>

          <div className="space-y-4 text-xs font-mono">
            {/* Progression Steps */}
            <div className="flex items-center justify-between overflow-x-auto py-2">
              {['DETECTED', 'TRIAGED', 'INVESTIGATING', 'CONTAINED', 'RESOLVED', 'CLOSED'].map((st, idx) => {
                const isActive = (incident?.status || '').toUpperCase() === st;
                return (
                  <div key={st} className="flex items-center shrink-0">
                    <div className={`px-3 py-1 rounded-lg text-xs font-bold font-mono border ${
                      isActive 
                        ? 'bg-cyan-500/20 border-cyan-500 text-cyan-300 shadow-md shadow-cyan-500/20' 
                        : 'bg-slate-950 border-slate-800 text-slate-500'
                    }`}>
                      {st}
                    </div>
                    {idx < 5 && <div className="w-4 h-[1px] bg-slate-800 mx-1" />}
                  </div>
                );
              })}
            </div>

            {canTriage && (
              <div className="pt-2 border-t border-slate-800/80 flex flex-wrap items-center gap-2">
                <span className="text-slate-400 uppercase text-[10px] mr-2">Transition State:</span>
                {incident.status === 'DETECTED' && (
                  <button
                    disabled={isUpdatingStatus}
                    onClick={() => handleStatusTransition('TRIAGED')}
                    className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-bold transition-all cursor-pointer"
                  >
                    Triage Incident
                  </button>
                )}
                {incident.status === 'TRIAGED' && (
                  <>
                    <button
                      disabled={isUpdatingStatus}
                      onClick={() => handleStatusTransition('INVESTIGATING')}
                      className="px-3 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg font-bold transition-all cursor-pointer"
                    >
                      Begin Investigation
                    </button>
                    <button
                      disabled={isUpdatingStatus}
                      onClick={() => handleStatusTransition('CLOSED')}
                      className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg font-bold transition-all cursor-pointer"
                    >
                      Close (False Positive)
                    </button>
                  </>
                )}
                {incident.status === 'INVESTIGATING' && (
                  <>
                    <button
                      disabled={isUpdatingStatus}
                      onClick={() => handleStatusTransition('CONTAINED')}
                      className="px-3 py-1.5 bg-red-600 hover:bg-red-500 text-white rounded-lg font-bold transition-all cursor-pointer"
                    >
                      Contain Threat
                    </button>
                    <button
                      disabled={isUpdatingStatus}
                      onClick={() => handleStatusTransition('RESOLVED')}
                      className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold transition-all cursor-pointer"
                    >
                      Resolve Incident
                    </button>
                  </>
                )}
                {incident.status === 'CONTAINED' && (
                  <button
                    disabled={isUpdatingStatus}
                    onClick={() => handleStatusTransition('RESOLVED')}
                    className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold transition-all cursor-pointer"
                  >
                    Resolve Incident
                  </button>
                )}
                {incident.status === 'RESOLVED' && (
                  <button
                    disabled={isUpdatingStatus}
                    onClick={() => handleStatusTransition('CLOSED')}
                    className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg font-bold transition-all cursor-pointer"
                  >
                    Close Incident
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Correlated Alerts List */}
      {incident.alerts && incident.alerts.length > 0 && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl">
          <h3 className="text-base font-bold text-slate-100 font-mono mb-4 pb-2 border-b border-slate-800">
            CORRELATED THREAT ALERTS ({incident.alerts.length})
          </h3>
          <div className="space-y-2">
            {incident.alerts.map((a) => (
              <div key={a.id} className="p-3 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-between text-xs font-mono">
                <div className="flex items-center space-x-3">
                  <span className="text-cyan-400 font-bold">{a.alert_id}</span>
                  <span className="text-slate-200">{a.title}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-red-500/10 border border-red-500/30 text-red-400">
                    {a.severity}
                  </span>
                </div>
                <div className="text-slate-400 text-[11px]">
                  {new Date(a.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Chronological Attack Timeline Component */}
      <AttackTimeline
        incidentId={incident.id}
        timeline={incident.timeline || []}
        onEventAdded={fetchIncident}
        canEdit={canTriage}
      />

      {/* Remediation Modal */}
      {isRemediationOpen && (
        <RemediationModal
          incidentId={incident.id}
          targetIp={incident.source_ip}
          attackType={incident.attack_type}
          onClose={() => setIsRemediationOpen(false)}
          onSuccess={() => {
            setIsRemediationOpen(false);
            fetchIncident();
          }}
        />
      )}
    </div>
  );
};
