import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  BarChart3,
  Search,
  FileText,
  History,
  Users,
  Settings,
  Info,
  ShieldCheck,
  HelpCircle,
  Sparkles,
  Server,
  BellRing,
  Globe,
  Database,
  SearchCode,
  Network,
  TrendingUp,
  Target,
  Activity,
  Zap,
  Key,
  FileCode,
  Share2,
  Scale,
  ShoppingBag,
  Code,
  Workflow,






  Brain,
  Cloud,
  Laptop,
  Plug,





  Layers,
  Flame,
  Shield,
  GitBranch,
  Crosshair,
  Lock
} from 'lucide-react';






export const navItems = [
  { path: '/dashboard', label: 'Dashboard', section: 'Monitor', icon: LayoutDashboard },
  { path: '/alerts', label: 'Live alerts', section: 'Monitor', icon: BellRing },
  { path: '/assets', label: 'Protected assets', section: 'Monitor', icon: Server },
  { path: '/monitoring', label: 'Asset health', section: 'Monitor', icon: Globe },
  
  { path: '/threat-intel', label: 'Threat intel', section: 'Intelligence', icon: Database },
  { path: '/investigations', label: 'Investigations', section: 'Intelligence', icon: SearchCode },
  { path: '/analytics', label: 'Model insights', section: 'Intelligence', icon: BarChart3 },

  { path: '/copilot', label: 'AI Security Copilot', section: 'Advanced SOC', icon: Sparkles },
  { path: '/threat-hunting', label: 'Threat Hunting', section: 'Advanced SOC', icon: Search },
  { path: '/predictive-analytics', label: 'Predictive Risk', section: 'Advanced SOC', icon: TrendingUp },
  { path: '/threat-graph', label: 'Threat Graph', section: 'Advanced SOC', icon: Network },
  { path: '/attack-coverage', label: 'ATT&CK Matrix', section: 'Advanced SOC', icon: Target },
  { path: '/soc-analytics', label: 'SOC Analytics', section: 'Advanced SOC', icon: Activity },

  { path: '/detection-quality', label: 'Detection Quality', section: 'Production Intel', icon: Activity },
  { path: '/alert-queue', label: 'Alert Queue', section: 'Production Intel', icon: Layers },
  { path: '/security-value', label: 'Security ROI & Value', section: 'Production Intel', icon: ShieldCheck },
  { path: '/telemetry-cost', label: 'Telemetry Costs', section: 'Production Intel', icon: BarChart3 },
  { path: '/benchmarking', label: 'ML Benchmarks', section: 'Production Intel', icon: Zap },
  { path: '/ai-intelligence', label: 'AI Security Intel', section: 'Production Intel', icon: Brain },
  { path: '/cloud-security', label: 'Cloud & Containers', section: 'Production Intel', icon: Cloud },
  { path: '/endpoint-xdr', label: 'Endpoint XDR', section: 'Production Intel', icon: Laptop },
  { path: '/integrations', label: 'Integrations', section: 'Production Intel', icon: Plug },
  { path: '/global-ops', label: 'Global Operations', section: 'Production Intel', icon: Server },
  { path: '/soc-v2', label: 'SOC Center V2', section: 'Production Intel', icon: Shield },
  { path: '/enterprise-iam', label: 'Enterprise IAM & PAM', section: 'Production Intel', icon: Key },
  { path: '/supply-chain', label: 'Supply Chain & SBOM', section: 'Production Intel', icon: GitBranch },
  { path: '/llm-security', label: 'AI/LLM Security & OWASP', section: 'Production Intel', icon: Brain },
  { path: '/attack-surface', label: 'Attack Surface & CTEM', section: 'Production Intel', icon: Globe },
  { path: '/threat-intel-v2', label: 'Threat Intel 2.0 & STIX', section: 'Production Intel', icon: Crosshair },
  { path: '/deception', label: 'Deception & Honeypots', section: 'Production Intel', icon: Sparkles },
  { path: '/vulnerability-mgmt', label: 'Vulnerability & EPSS 2.0', section: 'Production Intel', icon: Flame },
  { path: '/dlp-security', label: 'DLP & Tokenization', section: 'Production Intel', icon: Lock },
  { path: '/microsegmentation', label: 'ZTNA & Microsegmentation', section: 'Production Intel', icon: Network },
  { path: '/ai-soc-ueba', label: 'AI SOC Autonomy & UEBA', section: 'Production Intel', icon: Brain },
  { path: '/compliance-detection', label: 'Compliance & Detection-as-Code', section: 'Production Intel', icon: FileCode },
  { path: '/predictive-intel', label: 'Predictive Intel & Forecasting', section: 'Production Intel', icon: TrendingUp },
  { path: '/federated-threat', label: 'Federated Threat & Privacy', section: 'Production Intel', icon: Share2 },
  { path: '/edge-fabric', label: 'Edge Security & Ingestion', section: 'Production Intel', icon: Globe },
  { path: '/multi-region', label: 'Multi-Region & Residency', section: 'Production Intel', icon: Database },
  { path: '/governance-dsar', label: 'Data Governance & DSAR', section: 'Production Intel', icon: Scale },
  { path: '/marketplace', label: 'Security Marketplace', section: 'Production Intel', icon: ShoppingBag },
  { path: '/developer', label: 'Developer & Webhooks', section: 'Production Intel', icon: Code },
  { path: '/automation-studio', label: 'Automation Studio', section: 'Production Intel', icon: Workflow },
  { path: '/executive-intelligence', label: 'Executive Intelligence', section: 'Production Intel', icon: TrendingUp },
  { path: '/ml-platform', label: 'AI/ML Model Platform', section: 'Production Intel', icon: Brain },
  { path: '/control-plane', label: 'Autonomous Control Plane', section: 'Production Intel', icon: Target },
  { path: '/global-certification', label: 'Global Certification (Phase 50)', section: 'Production Intel', icon: ShieldCheck },






















  { path: '/security-automation', label: 'Autonomous Response', section: 'Autonomous Ops', icon: Zap },



  { path: '/response-approvals', label: 'Response Approvals', section: 'Autonomous Ops', icon: ShieldCheck },
  { path: '/security-validation', label: 'Continuous Validation', section: 'Autonomous Ops', icon: ShieldCheck },
  { path: '/soar-command-center', label: 'SOAR 2.0 Center', section: 'Autonomous Ops', icon: Zap },
  { path: '/threat-intelligence-center', label: 'Threat Intel Platform', section: 'Threat Intel', icon: Flame },

  { path: '/response-center', label: 'Response Center', section: 'Actions', icon: Zap },




  { path: '/guide', label: 'How to use', section: 'Actions', icon: Sparkles },
  { path: '/prediction', label: 'Inspect traffic', section: 'Actions', icon: Search },
  { path: '/reports', label: 'Create reports', section: 'Actions', icon: FileText },
  { path: '/history', label: 'Incident history', section: 'Actions', icon: History },
  
  { path: '/security-center', label: 'Security Center', section: 'Enterprise SaaS', icon: ShieldCheck },
  { path: '/organizations', label: 'Organizations', section: 'Enterprise SaaS', icon: Users },
  { path: '/billing', label: 'Billing & Plans', section: 'Enterprise SaaS', icon: BarChart3 },
  { path: '/api-keys', label: 'API Keys', section: 'Enterprise SaaS', icon: Key },
  { path: '/sensors', label: 'Sensors & Agents', section: 'Enterprise SaaS', icon: Server },
  { path: '/integrations', label: 'Integrations', section: 'Enterprise SaaS', icon: Network },
  { path: '/onboarding', label: 'Setup Guide', section: 'Enterprise SaaS', icon: HelpCircle },


  { path: '/users', label: 'Team members', section: 'Manage', icon: Users },
  { path: '/settings', label: 'Settings', section: 'Manage', icon: Settings },
  { path: '/about', label: 'About Aegivanta', section: 'Manage', icon: Info },
];


export const Sidebar: React.FC = () => {
  return (
    <aside className="app-sidebar w-64 border-r border-slate-800 flex flex-col justify-between hidden md:flex min-h-[calc(100vh-4rem)] sticky top-16">
      <div className="p-4 space-y-1 overflow-y-auto max-h-[calc(100vh-12rem)]">
        <div className="sidebar-workspace-heading">
          <span className="flex items-center gap-2"><span className="sidebar-heading-icon"><ShieldCheck className="w-3.5 h-3.5" /></span>Workspace</span>
          <span>17 tools</span>
        </div>
        {navItems.map((item, index) => {
          const Icon = item.icon;
          const previousSection = navItems[index - 1]?.section;
          return (
            <React.Fragment key={item.path}>
              {item.section !== previousSection && <div className="sidebar-section-label">{item.section}</div>}
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `sidebar-nav-link ${isActive ? 'is-active' : ''}`
                }
              >
                <span className="sidebar-nav-icon"><Icon className="w-4 h-4" /></span>
                <span className="truncate">{item.label}</span>
                {item.path === '/global-certification' && (
                  <span className="ml-auto px-1.5 py-0.5 rounded text-[8px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                    SELF-ATTESTED
                  </span>
                )}
                {item.section === 'Advanced SOC' && (
                  <span className="ml-auto px-1.5 py-0.5 rounded text-[8px] font-bold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                    PROD
                  </span>
                )}
                {item.section === 'Enterprise SaaS' && item.path !== '/integrations' && (
                  <span className="ml-auto px-1.5 py-0.5 rounded text-[8px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    SaaS
                  </span>
                )}
              </NavLink>
            </React.Fragment>
          );
        })}
      </div>


      {/* Simple system status */}
      <div className="sidebar-status-card p-4 m-4 rounded-xl text-xs font-mono space-y-3">
        <div className="flex items-center gap-2">
          <span className="status-dot is-online" />
          <span className="text-slate-300 font-semibold">Phase 3 SOC Active</span>
          <span className="ml-auto text-[10px] text-emerald-400 font-bold">READY</span>
        </div>
        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
          <div className="bg-cyan-400 h-full w-[100%] animate-pulse"></div>
        </div>
        <div className="flex items-center justify-between text-[10px] text-slate-500">
          <span>Unified SOC Engine</span>
          <HelpCircle className="w-3.5 h-3.5" aria-label="Protection status help" />
        </div>
      </div>
    </aside>
  );
};
