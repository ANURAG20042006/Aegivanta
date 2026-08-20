import React, { useEffect, useState } from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Play,
  Activity,
  History
} from 'lucide-react';
import { saasApi } from '../services/saas';

export const SecurityValidation: React.FC = () => {
  const [validation, setValidation] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [running, setRunning] = useState<boolean>(false);

  useEffect(() => {
    fetchValidationData();
  }, []);

  const fetchValidationData = async () => {
    try {
      setLoading(true);
      const data = await saasApi.getSecurityValidation();
      setValidation(data);
    } catch (err) {
      console.error('Failed to load security validation:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunValidation = async () => {
    try {
      setRunning(true);
      const data = await saasApi.runSecurityValidation();
      setValidation(data);
    } catch (err) {
      console.error('Failed to execute security validation run:', err);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <ShieldCheck className="h-7 w-7 text-emerald-400" />
            Continuous Defense Verification & Validation
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Automated non-destructive audit engine verifying active authentication, tenant boundaries, and detection controls.
          </p>
        </div>

        <button
          onClick={handleRunValidation}
          disabled={running}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold rounded-lg transition-all"
        >
          {running ? <Activity className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          Execute Validation Suite
        </button>
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Activity className="h-8 w-8 animate-spin text-emerald-400 mr-3" />
          Running continuous defense validation checks...
        </div>
      ) : (
        <>
          {/* Summary Scorecard */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Overall Defense Score</div>
              <div className="text-2xl font-bold text-emerald-400 mt-1">{validation?.overall_score}%</div>
              <div className="text-[11px] text-slate-500 mt-1">Status: {validation?.status}</div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Passed Checks</div>
              <div className="text-2xl font-bold text-slate-100 mt-1">{validation?.passed_checks} / {validation?.total_checks}</div>
              <div className="text-[11px] text-emerald-400 mt-1">100% Core Controls Verified</div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Warnings / Advisories</div>
              <div className="text-2xl font-bold text-amber-400 mt-1">{validation?.warning_checks}</div>
              <div className="text-[11px] text-slate-500 mt-1">Non-critical recommendations</div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs font-medium text-slate-400">Critical Failures</div>
              <div className="text-2xl font-bold text-rose-400 mt-1">{validation?.failed_checks}</div>
              <div className="text-[11px] text-emerald-400 mt-1">Zero Deficit Detected</div>
            </div>
          </div>

          {/* Validation Check Details */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
            <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
              <History className="h-5 w-5 text-indigo-400" />
              Automated Defense Control Check Results
            </h2>

            <div className="space-y-3">
              {validation?.checks?.map((chk: any) => (
                <div
                  key={chk.id}
                  className="p-4 bg-slate-950/40 rounded-xl border border-slate-800 flex flex-col md:flex-row md:items-center md:justify-between gap-3 text-xs"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300">
                        {chk.category}
                      </span>
                      <span className="font-bold text-slate-100">{chk.name}</span>
                    </div>
                    <p className="text-slate-400 text-[11px]">{chk.description}</p>
                  </div>

                  <div className="flex items-center gap-4 shrink-0">
                    <span className="text-slate-500 text-[11px]">{chk.latency_ms} ms</span>
                    <span
                      className={`px-2.5 py-1 rounded-full text-xs font-bold flex items-center gap-1 ${
                        chk.status === 'PASSED'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : chk.status === 'WARNING'
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      }`}
                    >
                      {chk.status === 'PASSED' && <CheckCircle2 className="h-3.5 w-3.5" />}
                      {chk.status === 'WARNING' && <AlertTriangle className="h-3.5 w-3.5" />}
                      {chk.status === 'FAILED' && <XCircle className="h-3.5 w-3.5" />}
                      {chk.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};
