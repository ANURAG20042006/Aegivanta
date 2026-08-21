import React, { useEffect, useState } from 'react';
import { Activity, BarChart3, DollarSign, Server, CheckCircle2, AlertTriangle } from 'lucide-react';
import { saasApi } from '../services/saas';

export const GlobalOpsCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'finops' | 'capacity' | 'sre'>('finops');
  const [finops, setFinops] = useState<any>(null);
  const [capacity, setCapacity] = useState<any>(null);
  const [slo, setSlo] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchAll(); }, []);

  const fetchAll = async () => {
    try {
      setLoading(true);
      const [f, c, s] = await Promise.all([
        saasApi.getFinOpsDashboard(),
        saasApi.getCapacityDashboard(),
        saasApi.getSLODashboard()
      ]);
      setFinops(f); setCapacity(c); setSlo(s);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const tabs = [
    { id: 'finops', label: 'FinOps', icon: DollarSign },
    { id: 'capacity', label: 'Capacity', icon: BarChart3 },
    { id: 'sre', label: 'SRE/SLO', icon: Activity }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <Server className="h-7 w-7 text-indigo-400" />
          Global Operations Center
        </h1>
        <p className="text-slate-400 text-sm mt-1">FinOps cost intelligence, capacity planning, and SRE SLO dashboards.</p>
      </div>

      <div className="flex border-b border-slate-800 gap-2">
        {tabs.map(tab => {
          const Icon = tab.icon;
          return (
            <button key={tab.id} onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 transition-colors ${
                activeTab === tab.id ? 'border-indigo-500 text-indigo-300' : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}>
              <Icon className="h-4 w-4" />{tab.label}
            </button>
          );
        })}
      </div>

      {loading ? (
        <div className="h-48 flex items-center justify-center text-slate-400">
          <Activity className="h-6 w-6 animate-spin text-indigo-400 mr-3" />Loading operations data...
        </div>
      ) : (
        <>
          {activeTab === 'finops' && finops && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5">
                  <div className="text-xs text-slate-400">Total Monthly Cost ({finops.period})</div>
                  <div className="text-3xl font-bold text-emerald-400 mt-1">${finops.current_month.total_monthly_usd.toLocaleString()}</div>
                  <div className={`text-xs mt-1 ${finops.month_over_month_change_pct > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                    {finops.month_over_month_change_pct > 0 ? '▲' : '▼'} {Math.abs(finops.month_over_month_change_pct)}% MoM
                  </div>
                </div>
                {Object.entries(finops.current_month.breakdown).map(([key, val]: [string, any]) => (
                  <div key={key} className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
                    <div className="text-[11px] text-slate-400 capitalize">{key.replace(/_usd$/, '').replace(/_/g, ' ')}</div>
                    <div className="text-xl font-bold text-slate-100 mt-1">${val.toLocaleString()}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'capacity' && capacity && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {[
                { label: 'Events/sec (EPS)', value: capacity.telemetry_eps, color: 'text-cyan-400' },
                { label: 'Worker Utilization', value: `${capacity.worker_utilization_pct}%`, color: 'text-indigo-400' },
                { label: 'CPU Utilization', value: `${capacity.cpu_utilization_pct}%`, color: capacity.cpu_utilization_pct > 80 ? 'text-rose-400' : 'text-emerald-400' },
                { label: 'Memory', value: `${capacity.memory_utilization_pct}%`, color: capacity.memory_utilization_pct > 80 ? 'text-rose-400' : 'text-emerald-400' },
                { label: 'Alert Queue', value: capacity.queue_depth_alerts, color: 'text-slate-100' },
                { label: 'Telemetry Queue', value: capacity.queue_depth_telemetry, color: 'text-slate-100' },
                { label: 'Storage Used (GB)', value: `${capacity.storage_used_gb}/${capacity.storage_capacity_gb}`, color: 'text-slate-100' },
                { label: 'Active Sensors', value: `${capacity.active_sensors}/${capacity.sensor_count}`, color: 'text-emerald-400' },
              ].map(m => (
                <div key={m.label} className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
                  <div className="text-[11px] text-slate-400">{m.label}</div>
                  <div className={`text-xl font-bold mt-1 ${m.color}`}>{m.value}</div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'sre' && slo && (
            <div className="space-y-3">
              <div className={`p-3 rounded-xl border text-xs font-bold flex items-center gap-2 ${slo.overall_compliance ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300' : 'bg-rose-950/40 border-rose-500/30 text-rose-300'}`}>
                {slo.overall_compliance ? <CheckCircle2 className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
                SLO Status: {slo.overall_compliance ? 'ALL COMPLIANT' : 'VIOLATION DETECTED'}
              </div>
              {slo.slos.map((s: any) => (
                <div key={s.slo_name} className="p-4 bg-slate-900/60 border border-slate-800/80 rounded-xl flex items-center justify-between gap-3">
                  <div>
                    <div className="text-sm font-bold text-slate-200 capitalize">{s.slo_name.replace(/_/g, ' ')}</div>
                    <div className="text-xs text-slate-400 mt-0.5">Target: {s.target} · Measured: {s.measured}</div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div className="text-[10px] text-slate-400">Error Budget Left</div>
                      <div className={`text-sm font-bold ${s.error_budget_remaining_pct > 30 ? 'text-emerald-400' : 'text-amber-400'}`}>{s.error_budget_remaining_pct.toFixed(1)}%</div>
                    </div>
                    <span className={`px-2 py-1 rounded text-[10px] font-bold border ${s.compliant ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'}`}>
                      {s.compliant ? '✓ PASS' : '✗ FAIL'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
};
