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
  SearchCode
} from 'lucide-react';

export const navItems = [
  { path: '/dashboard', label: 'Dashboard', section: 'Monitor', icon: LayoutDashboard },
  { path: '/alerts', label: 'Live alerts', section: 'Monitor', icon: BellRing },
  { path: '/assets', label: 'Protected assets', section: 'Monitor', icon: Server },
  { path: '/monitoring', label: 'Asset health', section: 'Monitor', icon: Globe },
  { path: '/threat-intel', label: 'Threat intel', section: 'Intelligence', icon: Database },
  { path: '/investigations', label: 'Investigations', section: 'Intelligence', icon: SearchCode },
  { path: '/analytics', label: 'Model insights', section: 'Intelligence', icon: BarChart3 },
  { path: '/guide', label: 'How to use', section: 'Actions', icon: Sparkles },
  { path: '/prediction', label: 'Inspect traffic', section: 'Actions', icon: Search },
  { path: '/reports', label: 'Create reports', section: 'Actions', icon: FileText },
  { path: '/history', label: 'Incident history', section: 'Actions', icon: History },
  { path: '/users', label: 'Team members', section: 'Manage', icon: Users },
  { path: '/settings', label: 'Settings', section: 'Manage', icon: Settings },
  { path: '/about', label: 'About SentinelAI', section: 'Manage', icon: Info },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="app-sidebar w-64 border-r border-slate-800 flex flex-col justify-between hidden md:flex min-h-[calc(100vh-4rem)] sticky top-16">
      <div className="p-4 space-y-1">
        <div className="sidebar-workspace-heading">
          <span className="flex items-center gap-2"><span className="sidebar-heading-icon"><ShieldCheck className="w-3.5 h-3.5" /></span>Workspace</span>
          <span>11 tools</span>
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
                <span>{item.label}</span>
                {item.path === '/guide' && (
                  <span className="ml-auto px-1.5 py-0.5 rounded text-[9px] font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                    NEW
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
          <span className="text-slate-300 font-semibold">Protection is on</span>
          <span className="ml-auto text-[10px] text-emerald-400 font-bold">READY</span>
        </div>
        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
          <div className="bg-cyan-400 h-full w-[94%] animate-pulse"></div>
        </div>
        <div className="flex items-center justify-between text-[10px] text-slate-500">
          <span>Traffic detection is ready</span>
          <HelpCircle className="w-3.5 h-3.5" aria-label="Protection status help" />
        </div>
      </div>
    </aside>
  );
};
