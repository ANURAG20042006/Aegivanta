import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, User as UserIcon, AlertCircle } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { ThemeSwitcher } from '../components/common/ThemeSwitcher';

export const Login: React.FC = () => {
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const showDemoAccounts = import.meta.env.DEV;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);
    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please check credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const setQuickRole = (user: string, pass: string) => {
    setUsername(user);
    setPassword(pass);
  };

  return (
    <div className="app-shell min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute top-4 right-4 z-20">
        <ThemeSwitcher />
      </div>
      {/* Background Cyber Grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f293710_1px,transparent_1px),linear-gradient(to_bottom,#1f293710_1px,transparent_1px)] bg-[size:4rem_4rem]" />
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
      <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />

      <div className="w-full max-w-md glass-panel-glow p-8 rounded-2xl relative z-10 space-y-6">
        <div className="text-center space-y-2">
          <div className="w-14 h-14 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center mx-auto shadow-[0_0_25px_rgba(0,240,255,0.2)]">
            <Shield className="w-8 h-8 text-cyan-400" />
          </div>
          <h1 className="text-2xl font-mono font-extrabold bg-gradient-to-r from-cyan-400 via-teal-300 to-emerald-400 bg-clip-text text-transparent">
            SENTINEL<span className="text-white">AI</span>
          </h1>
          <p className="text-xs text-slate-400 font-mono">Simple, intelligent network protection</p>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-mono flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-mono text-slate-400 mb-1">Username</label>
            <div className="relative">
              <UserIcon className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full pl-9 pr-3 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-400 transition-colors"
                placeholder="Enter handle"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono text-slate-400 mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full pl-9 pr-3 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-400 transition-colors"
                placeholder="••••••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3 bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-400 hover:to-teal-400 text-slate-950 font-mono font-bold text-xs rounded-lg shadow-[0_0_20px_rgba(0,240,255,0.3)] transition-all duration-200"
          >
            {isSubmitting ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        {showDemoAccounts && (
          <div className="pt-4 border-t border-slate-800">
            <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest text-center mb-2">
              Quick demo accounts
            </div>
            <div className="grid grid-cols-3 gap-2">
              <button
                onClick={() => setQuickRole('admin', atob('QWRtaW5TZWN1cmUyMDI2IQ=='))}
                className="py-1.5 px-2 bg-slate-900 border border-slate-800 rounded text-[10px] font-mono text-cyan-400 hover:border-cyan-500/40"
              >
                Admin
              </button>
              <button
                onClick={() => setQuickRole('analyst', atob('QW5hbHlzdFNlY3VyZTIwMjYh'))}
                className="py-1.5 px-2 bg-slate-900 border border-slate-800 rounded text-[10px] font-mono text-emerald-400 hover:border-emerald-500/40"
              >
                Analyst
              </button>
              <button
                onClick={() => setQuickRole('viewer', atob('Vmlld2VyU2VjdXJlMjAyNiE='))}
                className="py-1.5 px-2 bg-slate-900 border border-slate-800 rounded text-[10px] font-mono text-slate-400 hover:border-slate-700"
              >
                Viewer
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
