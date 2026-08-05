import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Upload, 
  Activity, 
  BarChart2, 
  FileText, 
  Users, 
  Settings as SettingsIcon, 
  ArrowRight, 
  CheckCircle2, 
  Sparkles,
  Lock
} from 'lucide-react';

export const GuidePage: React.FC = () => {
  const [activeStep, setActiveStep] = useState<number>(1);

  const steps = [
    {
      step: 1,
      title: 'Log In & Choose Your Role',
      icon: ShieldCheck,
      color: 'from-blue-500 to-cyan-500',
      badge: 'Step 1: Access',
      description: 'SentinelAI uses Role-Based Access Control (RBAC). Choose a role to experience the platform:',
      details: [
        '👑 Admin: Full control over system settings, user management, and AI model retraining.',
        '🔬 Analyst: Inspect traffic, analyze threat trends, execute remediation playbooks, and export PDF reports.',
        '👁️ Viewer: Read-only access to live dashboards and threat metrics.'
      ]
    },
    {
      step: 2,
      title: 'Inspect Live Dashboard & Topology',
      icon: Activity,
      color: 'from-cyan-500 to-teal-500',
      badge: 'Step 2: Situational Awareness',
      description: 'Navigate to the Master Dashboard to view real-time network health:',
      details: [
        '🌐 Network Topology Canvas: Watch live packet pulses between servers, firewalls, and external attacker nodes.',
        '📡 Live WebSocket Feed: Real-time ticker flashing incoming threat alerts in sub-millisecond latency.',
        '📊 Metric Cards: Monitor total packets inspected, threats isolated, active AI models, and bandwidth.'
      ]
    },
    {
      step: 3,
      title: 'Upload Traffic Capture CSV or Inspect Single Flow',
      icon: Upload,
      color: 'from-purple-500 to-indigo-500',
      badge: 'Step 3: Packet Inference',
      description: 'Navigate to "Inspect Network Traffic" to evaluate network captures:',
      details: [
        '📁 Batch CSV Upload: Drag and drop any network capture CSV file (such as sample_traffic.csv).',
        '⚡ Single Flow Testing: Enter individual packet features (IPs, Ports, Flow Packets/s) to test specific connections.',
        '🔍 SHAP Feature Attribution: Inspect exact feature importance scores explaining why a flow was flagged.'
      ]
    },
    {
      step: 4,
      title: 'Contain Threats with 1-Click Playbooks',
      icon: Lock,
      color: 'from-rose-500 to-red-500',
      badge: 'Step 4: Automated Remediation',
      description: 'When a malicious packet flow or DDoS attack is identified, take immediate action:',
      details: [
        '🛡️ Perimeter Firewall Drop Rule: Injects instant drop ACLs for the target attacker IP across edge gateways.',
        '🏷️ VLAN Quarantine Isolation: Moves infected host devices onto isolated sandbox VLAN 999.',
        '📝 Audit History: Automatically logs every remediation action for compliance.'
      ]
    },
    {
      step: 5,
      title: 'Generate & Export Executive PDF Reports',
      icon: FileText,
      color: 'from-emerald-500 to-teal-500',
      badge: 'Step 5: Compliance & Export',
      description: 'Navigate to "Threat Reports" to share results with executives and audit teams:',
      details: [
        '📄 Executive PDF Reports: Download formatted ReportLab PDF documents with threat tables and charts.',
        '📊 Excel Spreadsheets: Export raw incident logs into OpenPyXL spreadsheets.',
        '📋 Raw CSV Dumps: Download raw data dumps for custom SIEM integration.'
      ]
    }
  ];

  return (
    <div className="space-y-8 pb-16 animate-fade-in max-w-6xl mx-auto">
      {/* Hero Welcome Banner */}
      <div className="relative bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 border border-slate-800 rounded-3xl p-8 shadow-2xl overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 space-y-4">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-bold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" />
            <span>User Friendly Quick Start Guide</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-white uppercase tracking-wide font-mono">
            How To Use SentinelAI
          </h1>
          <p className="text-sm text-slate-300 max-w-3xl leading-relaxed font-sans">
            Welcome to SentinelAI – the intelligent Network Intrusion Detection & Threat Analytics Platform. 
            This friendly guide walks you through navigating the platform, inspecting network traffic, understanding AI predictions, and executing 1-click threat containment.
          </p>

          <div className="pt-2 flex flex-wrap gap-4">
            <a
              href="/prediction"
              className="px-6 py-3 rounded-xl font-mono text-xs font-bold bg-gradient-to-r from-cyan-500 to-teal-500 text-slate-950 shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 transition-all flex items-center space-x-2"
            >
              <span>INSPECT TRAFFIC NOW</span>
              <ArrowRight className="w-4 h-4" />
            </a>
            <a
              href="/"
              className="px-6 py-3 rounded-xl font-mono text-xs font-bold bg-slate-900 text-slate-200 border border-slate-800 hover:border-slate-700 transition-all flex items-center space-x-2"
            >
              <Activity className="w-4 h-4 text-cyan-400" />
              <span>OPEN LIVE DASHBOARD</span>
            </a>
          </div>
        </div>
      </div>

      {/* Step Selector Tabs */}
      <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
        {steps.map((s) => {
          const Icon = s.icon;
          const isActive = activeStep === s.step;
          return (
            <button
              key={s.step}
              onClick={() => setActiveStep(s.step)}
              className={`p-4 rounded-2xl border text-left transition-all duration-300 cursor-pointer ${
                isActive
                  ? 'bg-slate-900 border-cyan-500/60 shadow-lg shadow-cyan-500/10 scale-[1.02]'
                  : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700 text-slate-400'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className={`text-xs font-mono font-bold ${isActive ? 'text-cyan-400' : 'text-slate-500'}`}>
                  STEP 0{s.step}
                </span>
                <Icon className={`w-5 h-5 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
              </div>
              <div className={`text-xs font-bold line-clamp-1 ${isActive ? 'text-white' : 'text-slate-300'}`}>
                {s.title}
              </div>
            </button>
          );
        })}
      </div>

      {/* Active Step Feature Detail Card */}
      {(() => {
        const current = steps.find((s) => s.step === activeStep) || steps[0];
        const CurrentIcon = current.icon;
        return (
          <div className="bg-slate-900/90 border border-slate-800/80 rounded-3xl p-8 backdrop-blur-md shadow-2xl relative overflow-hidden">
            <div className={`absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r ${current.color}`} />

            <div className="flex items-center space-x-4 mb-6">
              <div className={`p-4 rounded-2xl bg-slate-950 border border-slate-800 text-cyan-400 shadow-inner`}>
                <CurrentIcon className="w-8 h-8" />
              </div>
              <div>
                <span className="text-xs font-mono text-cyan-400 font-bold uppercase tracking-wider">
                  {current.badge}
                </span>
                <h2 className="text-2xl font-bold text-white tracking-tight">{current.title}</h2>
              </div>
            </div>

            <p className="text-sm text-slate-300 mb-6 font-sans leading-relaxed">{current.description}</p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              {current.details.map((detail, idx) => (
                <div
                  key={idx}
                  className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-5 space-y-2 hover:border-slate-700 transition-colors"
                >
                  <div className="flex items-center space-x-2 text-cyan-400">
                    <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                    <span className="text-xs font-bold uppercase font-mono">Feature Highlight #{idx + 1}</span>
                  </div>
                  <p className="text-xs text-slate-300 font-sans leading-relaxed">{detail}</p>
                </div>
              ))}
            </div>

            <div className="flex justify-between items-center border-t border-slate-800/80 pt-6">
              <button
                disabled={activeStep === 1}
                onClick={() => setActiveStep((prev) => Math.max(1, prev - 1))}
                className="px-4 py-2 text-xs font-mono font-semibold text-slate-400 hover:text-white disabled:opacity-40"
              >
                ← Previous Step
              </button>

              <button
                disabled={activeStep === 5}
                onClick={() => setActiveStep((prev) => Math.min(5, prev + 1))}
                className="px-5 py-2.5 rounded-xl font-mono text-xs font-bold bg-cyan-500/20 border border-cyan-500/40 text-cyan-400 hover:bg-cyan-500/30 transition-all flex items-center space-x-2 disabled:opacity-40"
              >
                <span>Next Step</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        );
      })()}

      {/* Feature Map Matrix */}
      <div className="glass-panel p-8 rounded-3xl space-y-6">
        <div className="flex items-center space-x-3">
          <Sparkles className="w-6 h-6 text-cyan-400" />
          <h2 className="text-xl font-bold text-white uppercase tracking-wider font-mono">Platform Navigation Sitemap</h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          <a href="/" className="p-5 bg-slate-950/60 border border-slate-800 rounded-2xl hover:border-cyan-500/50 transition-all group">
            <div className="flex items-center space-x-3 mb-2">
              <Activity className="w-5 h-5 text-cyan-400 group-hover:scale-110 transition-transform" />
              <span className="text-sm font-bold text-slate-100 font-mono">Master Dashboard</span>
            </div>
            <p className="text-xs text-slate-400 font-sans">View real-time topology, throughput charts, and live WebSocket threat tickers.</p>
          </a>

          <a href="/prediction" className="p-5 bg-slate-950/60 border border-slate-800 rounded-2xl hover:border-cyan-500/50 transition-all group">
            <div className="flex items-center space-x-3 mb-2">
              <Upload className="w-5 h-5 text-teal-400 group-hover:scale-110 transition-transform" />
              <span className="text-sm font-bold text-slate-100 font-mono">Inspect Network Traffic</span>
            </div>
            <p className="text-xs text-slate-400 font-sans">Upload network capture CSV files or test single packet connection vectors.</p>
          </a>

          <a href="/analytics" className="p-5 bg-slate-950/60 border border-slate-800 rounded-2xl hover:border-cyan-500/50 transition-all group">
            <div className="flex items-center space-x-3 mb-2">
              <BarChart2 className="w-5 h-5 text-purple-400 group-hover:scale-110 transition-transform" />
              <span className="text-sm font-bold text-slate-100 font-mono">12-Model AI Benchmarks</span>
            </div>
            <p className="text-xs text-slate-400 font-sans">Compare accuracy, F1-scores, confusion matrices, and ROC curves across 12 AI models.</p>
          </a>

          <a href="/reports" className="p-5 bg-slate-950/60 border border-slate-800 rounded-2xl hover:border-cyan-500/50 transition-all group">
            <div className="flex items-center space-x-3 mb-2">
              <FileText className="w-5 h-5 text-emerald-400 group-hover:scale-110 transition-transform" />
              <span className="text-sm font-bold text-slate-100 font-mono">Threat Reports</span>
            </div>
            <p className="text-xs text-slate-400 font-sans">Generate and download formatted ReportLab PDF executive reports and Excel workbooks.</p>
          </a>

          <a href="/users" className="p-5 bg-slate-950/60 border border-slate-800 rounded-2xl hover:border-cyan-500/50 transition-all group">
            <div className="flex items-center space-x-3 mb-2">
              <Users className="w-5 h-5 text-amber-400 group-hover:scale-110 transition-transform" />
              <span className="text-sm font-bold text-slate-100 font-mono">User Management</span>
            </div>
            <p className="text-xs text-slate-400 font-sans">Manage user accounts, assign roles (Admin, Analyst, Viewer), and review active profiles.</p>
          </a>

          <a href="/settings" className="p-5 bg-slate-950/60 border border-slate-800 rounded-2xl hover:border-cyan-500/50 transition-all group">
            <div className="flex items-center space-x-3 mb-2">
              <SettingsIcon className="w-5 h-5 text-rose-400 group-hover:scale-110 transition-transform" />
              <span className="text-sm font-bold text-slate-100 font-mono">System Settings</span>
            </div>
            <p className="text-xs text-slate-400 font-sans">Configure default AI models, detection sensitivity thresholds, and API keys.</p>
          </a>
        </div>
      </div>
    </div>
  );
};
