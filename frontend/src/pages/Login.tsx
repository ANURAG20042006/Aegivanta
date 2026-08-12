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

  const setQuickUsername = (user: string) => {
    setUsername(user);
    setPassword('');
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
          <div className="inline-flex p-3 bg-cyan-500/10 border border-cyan-500/30 rounded-xl mb-2 text-cyan-400">
            <Shield className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white font-mono">SENTINEL AI</h1>
          <p className="text-xs text-slate-400">Enterprise Cyber Intrusion Detection & AI Analysis</p>
        </div>

        {error && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg flex items-center gap-2 text-rose-400 text-xs font-mono">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-mono text-slate-400 mb-1">USERNAME</label>
            <div className="relative">
              <UserIcon className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter analyst or admin username"
                className="w-full bg-slate-900/80 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500/50"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono text-slate-400 mb-1">PASSWORD</label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full bg-slate-900/80 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500/50"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-mono text-xs font-semibold rounded-lg shadow-lg shadow-cyan-500/20 disabled:opacity-50 transition-all"
          >
            {isSubmitting ? 'AUTHENTICATING...' : 'ACCESS SENTINEL AI'}
          </button>
        </form>

        {showDemoAccounts && (
          <div className="pt-4 border-t border-slate-800">
            <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest text-center mb-2">
              Select demo account username
            </div>
            <div className="grid grid-cols-3 gap-2">
              <button
                onClick={() => setQuickUsername('admin')}
                className="py-1.5 px-2 bg-slate-900 border border-slate-800 rounded text-[10px] font-mono text-cyan-400 hover:border-cyan-500/40"
              >
                admin
              </button>
              <button
                onClick={() => setQuickUsername('analyst')}
                className="py-1.5 px-2 bg-slate-900 border border-slate-800 rounded text-[10px] font-mono text-emerald-400 hover:border-emerald-500/40"
              >
                analyst
              </button>
              <button
                onClick={() => setQuickUsername('viewer')}
                className="py-1.5 px-2 bg-slate-900 border border-slate-800 rounded text-[10px] font-mono text-slate-400 hover:border-slate-700"
              >
                viewer
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
