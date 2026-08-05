import React from 'react';
import { User } from '../../types';
import { Shield, CheckCircle, XCircle } from 'lucide-react';

interface UserTableProps {
  users: User[];
  onEdit?: (user: User) => void;
  onDelete?: (userId: string) => void;
}

export const UserTable: React.FC<UserTableProps> = ({ users }) => {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left border-collapse text-xs font-mono">
        <thead>
          <tr className="border-b border-slate-800 bg-slate-900/80 text-slate-400 uppercase tracking-wider">
            <th className="p-3">User</th>
            <th className="p-3">Email</th>
            <th className="p-3">Role</th>
            <th className="p-3">Status</th>
            <th className="p-3">Registered At</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60">
          {users.map((u) => (
            <tr key={u.id} className="hover:bg-slate-800/40 transition-colors">
              <td className="p-3 flex items-center space-x-2">
                <div className="w-7 h-7 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                  <Shield className="w-3.5 h-3.5" />
                </div>
                <div>
                  <div className="font-bold text-slate-200">{u.username}</div>
                  <div className="text-[10px] text-slate-500">{u.full_name}</div>
                </div>
              </td>
              <td className="p-3 text-slate-400">{u.email}</td>
              <td className="p-3">
                <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-slate-800 text-cyan-400 border border-slate-700">
                  {u.username === 'anshika' && u.role === 'admin' ? 'Co-admin' : u.role}
                </span>
              </td>
              <td className="p-3">
                {u.is_active ? (
                  <span className="inline-flex items-center text-emerald-400 text-[10px] font-bold">
                    <CheckCircle className="w-3 h-3 mr-1" /> ACTIVE
                  </span>
                ) : (
                  <span className="inline-flex items-center text-rose-400 text-[10px] font-bold">
                    <XCircle className="w-3 h-3 mr-1" /> DISABLED
                  </span>
                )}
              </td>
              <td className="p-3 text-slate-500">{u.created_at.substring(0, 10)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
