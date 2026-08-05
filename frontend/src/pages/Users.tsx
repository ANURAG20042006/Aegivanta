import React, { useCallback, useEffect, useState } from 'react';
import { CheckCircle2, Loader2, RefreshCw, UserPlus, X } from 'lucide-react';
import { UserTable } from '../components/tables/UserTable';
import { User } from '../types';
import api from '../services/api';

type UserRole = User['role'];

interface NewUserForm {
  username: string;
  full_name: string;
  email: string;
  password: string;
  role: UserRole;
}

const emptyForm: NewUserForm = {
  username: '',
  full_name: '',
  email: '',
  password: '',
  role: 'viewer',
};

export const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');
  const [notice, setNotice] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [form, setForm] = useState<NewUserForm>(emptyForm);

  const loadUsers = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage('');
    try {
      const response = await api.get<User[]>('/users');
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to load users:', error);
      setUsers([]);
      setErrorMessage('We could not load team members. Make sure you are signed in as an administrator, then try again.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadUsers();
  }, [loadUsers]);

  const updateField = <Key extends keyof NewUserForm>(field: Key, value: NewUserForm[Key]) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const handleCreate = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsSaving(true);
    setErrorMessage('');
    try {
      await api.post<User>('/users', { ...form, is_active: true });
      setNotice(`${form.full_name} was added to the team.`);
      setForm(emptyForm);
      setIsModalOpen(false);
      await loadUsers();
    } catch (error: unknown) {
      const detail = typeof error === 'object' && error !== null && 'response' in error
        ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : undefined;
      setErrorMessage(detail || 'We could not add that team member. Please check the details and try again.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-mono font-bold text-white">Team members</h1>
          <p className="text-xs text-slate-400 font-mono mt-1">Manage who can view alerts, inspect traffic, and change settings.</p>
        </div>
        <div className="flex items-center gap-2">
          <button type="button" onClick={() => void loadUsers()} title="Refresh team list" className="p-2 rounded-xl border border-slate-700 text-slate-400 hover:text-cyan-400 hover:border-cyan-400 transition-colors">
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
          <button onClick={() => { setNotice(''); setErrorMessage(''); setIsModalOpen(true); }} className="px-4 py-2 bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/20 font-mono text-xs font-bold rounded-xl flex items-center space-x-2 transition-colors">
            <UserPlus className="w-4 h-4" />
            <span>Add team member</span>
          </button>
        </div>
      </div>

      {notice && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 text-xs font-mono">
          <CheckCircle2 className="w-4 h-4" /> {notice}
        </div>
      )}

      {errorMessage && (
        <div className="friendly-note flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-slate-400 font-mono">
          <span>{errorMessage}</span>
          <button type="button" onClick={() => void loadUsers()} className="text-cyan-400 hover:text-cyan-300 whitespace-nowrap">Try again</button>
        </div>
      )}

      <div className="glass-panel p-5 rounded-xl">
        {isLoading ? (
          <div className="p-8 flex items-center justify-center gap-2 text-xs font-mono text-slate-500"><Loader2 className="w-4 h-4 animate-spin" /> Loading team members...</div>
        ) : (
          <UserTable users={users} />
        )}
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <button type="button" className="absolute inset-0 bg-slate-950/75 backdrop-blur-sm" aria-label="Close add team member dialog" onClick={() => !isSaving && setIsModalOpen(false)} />
          <form onSubmit={handleCreate} className="relative z-10 w-full max-w-lg glass-panel-glow p-6 rounded-2xl space-y-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-base font-semibold text-white">Add a team member</h2>
                <p className="text-xs text-slate-400 mt-1">Choose what this person is allowed to do in SentinelAI.</p>
              </div>
              <button type="button" onClick={() => setIsModalOpen(false)} disabled={isSaving} className="p-1 rounded text-slate-400 hover:text-white disabled:opacity-50" aria-label="Close dialog"><X className="w-5 h-5" /></button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <label className="space-y-1.5"><span className="text-slate-300">Full name</span><input required value={form.full_name} onChange={(event) => updateField('full_name', event.target.value)} className="form-input" placeholder="e.g. Priya Sharma" /></label>
              <label className="space-y-1.5"><span className="text-slate-300">Username</span><input required minLength={3} value={form.username} onChange={(event) => updateField('username', event.target.value)} className="form-input" placeholder="e.g. priya" /></label>
              <label className="space-y-1.5 sm:col-span-2"><span className="text-slate-300">Email address</span><input required type="email" value={form.email} onChange={(event) => updateField('email', event.target.value)} className="form-input" placeholder="name@example.com" /></label>
              <label className="space-y-1.5"><span className="text-slate-300">Temporary password</span><input required minLength={8} type="password" value={form.password} onChange={(event) => updateField('password', event.target.value)} className="form-input" placeholder="At least 8 characters" /></label>
              <label className="space-y-1.5"><span className="text-slate-300">Access level</span><select value={form.role} onChange={(event) => updateField('role', event.target.value as UserRole)} className="form-input"><option value="viewer">Viewer — read-only access</option><option value="analyst">Analyst — inspect traffic and reports</option><option value="admin">Admin — manage all settings and users</option></select></label>
            </div>

            <div className="flex justify-end gap-3 pt-1">
              <button type="button" onClick={() => setIsModalOpen(false)} disabled={isSaving} className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-slate-200 disabled:opacity-50">Cancel</button>
              <button type="submit" disabled={isSaving} className="px-4 py-2 rounded-lg bg-cyan-500 text-slate-950 text-xs font-bold flex items-center gap-2 disabled:opacity-50">{isSaving && <Loader2 className="w-3.5 h-3.5 animate-spin" />}{isSaving ? 'Adding...' : 'Add member'}</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
