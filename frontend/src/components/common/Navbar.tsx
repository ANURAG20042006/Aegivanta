import React, { useState } from 'react';
import { Shield, Bell, LogOut, Radio, ChevronRight, Menu, X } from 'lucide-react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useWebSocket } from '../../hooks/useWebSocket';
import { ThemeSwitcher } from './ThemeSwitcher';
import { navItems } from './Sidebar';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const { isConnected, threatAlerts } = useWebSocket();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const currentPage = navItems.find((item) => location.pathname.startsWith(item.path)) || navItems[0];
  const roleLabel = user?.role;
  const initials = user?.full_name?.split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase() || 'SA';

  return (
    <>
      <header className="app-navbar h-16 border-b border-slate-800 px-4 md:px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Brand & Status */}
      <div className="flex items-center gap-3 min-w-0">
        <button type="button" className="navbar-mobile-menu-button md:hidden" onClick={() => setIsMobileMenuOpen((open) => !open)} aria-label={isMobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}>
          {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
        <div className="navbar-brand">
          <div className="navbar-brand-mark">
            <Shield className="w-5 h-5 text-cyan-400" />
          </div>
          <span className="font-mono text-lg font-bold bg-gradient-to-r from-cyan-400 via-teal-300 to-emerald-400 bg-clip-text text-transparent hidden sm:inline">
            AEGIVANTA
          </span>
        </div>

        <div className="navbar-breadcrumb hidden lg:flex">
          <span>Workspace</span><ChevronRight className="w-3.5 h-3.5" /><strong>{currentPage.label}</strong>
        </div>

        {/* Live status */}
        <div className="navbar-connection hidden sm:flex">
          <Radio className={`w-3.5 h-3.5 ${isConnected ? 'text-emerald-400 animate-pulse' : 'text-red-500'}`} />
          <span className={isConnected ? 'text-emerald-400' : 'text-slate-500'}>
            {isConnected ? 'Live monitoring' : 'Reconnecting'}
          </span>
        </div>
      </div>

      {/* User Controls */}
      <div className="flex items-center gap-2 md:gap-3">
        <ThemeSwitcher />
        {/* Notification Bell */}
        <div className="relative">
          <button
            type="button"
            className={`navbar-icon-button ${isNotificationsOpen ? 'is-active' : ''}`}
            title={`${threatAlerts.length} active alerts`}
            aria-label={`${threatAlerts.length} active alerts`}
            aria-expanded={isNotificationsOpen}
            onClick={() => setIsNotificationsOpen((open) => !open)}
          >
            <Bell className="w-4 h-4" />
            {threatAlerts.length > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-rose-500 text-[10px] font-bold text-white flex items-center justify-center animate-bounce">
                {threatAlerts.length}
              </span>
            )}
          </button>
          {isNotificationsOpen && (
            <>
              <button type="button" aria-label="Close alerts" className="fixed inset-0 z-40 cursor-default" onClick={() => setIsNotificationsOpen(false)} />
              <div className="notification-panel" role="dialog" aria-label="Live alerts">
                <div className="notification-panel-header">
                  <div>
                    <div className="text-sm font-semibold text-slate-100">Live alerts</div>
                    <div className="text-[10px] text-slate-500">New threats appear here automatically</div>
                  </div>
                  <span className="notification-live-dot"><span /> LIVE</span>
                </div>
                <div className="notification-list">
                  {threatAlerts.length === 0 ? (
                    <div className="notification-empty">
                      <Bell className="w-5 h-5" />
                      <span>No active alerts. Your network looks quiet.</span>
                    </div>
                  ) : (
                    threatAlerts.slice(0, 6).map((item, index) => (
                      <div className="notification-item" key={`${item.timestamp}-${index}`}>
                        <span className={`notification-severity ${item.severity === 'Critical' ? 'is-critical' : ''}`} />
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-xs font-semibold text-slate-200 truncate">{item.attack_type}</span>
                            <span className="text-[9px] text-slate-500">{item.severity}</span>
                          </div>
                          <div className="text-[10px] text-slate-500 truncate">{item.source_ip} → {item.destination_ip}</div>
                          <div className="text-[9px] text-cyan-400 mt-1">
                            {typeof item.confidence_score === 'number' ? `${(item.confidence_score * 100).toFixed(1)}% confidence` : 'Confidence N/A'}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
                <NavLink to="/history" onClick={() => setIsNotificationsOpen(false)} className="notification-view-all">View alert history <ChevronRight className="w-3.5 h-3.5" /></NavLink>
              </div>
            </>
          )}
        </div>

        {/* Profile Card */}
        {user && (
          <div className="navbar-profile">
            <div className="navbar-avatar">{initials}</div>
            <div className="text-left hidden md:block min-w-0">
              <div className="text-xs font-semibold text-slate-200 truncate max-w-32">{user.full_name}</div>
              <div className="text-[10px] font-mono text-cyan-400 uppercase tracking-wider">{roleLabel}</div>
            </div>
            <button
              onClick={logout}
              title="Sign out"
              className="navbar-logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
      </header>

      {isMobileMenuOpen && (
        <nav className="mobile-nav md:hidden" aria-label="Mobile navigation">
          <div className="mobile-nav-heading">Workspace</div>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink key={item.path} to={item.path} onClick={() => setIsMobileMenuOpen(false)} className={({ isActive }) => `mobile-nav-link ${isActive ? 'is-active' : ''}`}>
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
                <ChevronRight className="w-3.5 h-3.5 ml-auto opacity-50" />
              </NavLink>
            );
          })}
        </nav>
      )}

      <nav className="horizontal-nav-shell hidden md:block" aria-label="Primary navigation">
        <div className="horizontal-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink key={item.path} to={item.path} className={({ isActive }) => `horizontal-nav-link ${isActive ? 'is-active' : ''}`}>
                <span className="horizontal-nav-icon"><Icon className="w-3.5 h-3.5" /></span>
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </div>
      </nav>
    </>
  );
};
