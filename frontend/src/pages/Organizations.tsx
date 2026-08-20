import React, { useState, useEffect } from 'react';
import { saasApi, Organization, Member } from '../services/saas';

export const OrganizationsPage: React.FC = () => {
  const [orgs, setOrgs] = useState<Organization[]>([]);
  const [selectedOrg, setSelectedOrg] = useState<Organization | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [showInviteModal, setShowInviteModal] = useState<boolean>(false);
  
  // Form states
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [billingEmail, setBillingEmail] = useState('');
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('SECURITY_ANALYST');
  const [message, setMessage] = useState<{ text: string; isError: boolean } | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const orgList = await saasApi.listMyOrganizations();
      setOrgs(orgList);
      if (orgList.length > 0) {
        const active = orgList[0];
        setSelectedOrg(active);
        const memList = await saasApi.listMembers(active.id);
        setMembers(memList);
      }
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateOrg = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await saasApi.createOrganization({ name, slug, billing_email: billingEmail });
      setMessage({ text: `Organization '${created.name}' created successfully!`, isError: false });
      setShowCreateModal(false);
      setName('');
      setSlug('');
      setBillingEmail('');
      loadData();
    } catch (err: any) {
      setMessage({ text: err.response?.data?.detail || 'Failed to create organization', isError: true });
    }
  };

  const handleInviteMember = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedOrg) return;
    try {
      await saasApi.inviteMember(selectedOrg.id, { email: inviteEmail, role: inviteRole });
      setMessage({ text: `Invited '${inviteEmail}' successfully!`, isError: false });
      setShowInviteModal(false);
      setInviteEmail('');
      const updatedMembers = await saasApi.listMembers(selectedOrg.id);
      setMembers(updatedMembers);
    } catch (err: any) {
      setMessage({ text: err.response?.data?.detail || 'Failed to invite member', isError: true });
    }
  };

  return (
    <div className="space-y-6 font-mono">
      <div className="flex justify-between items-center border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-cyan-400 tracking-wider">ORGANIZATION MANAGEMENT</h1>
          <p className="text-xs text-gray-400">Enterprise Tenant Security Boundaries & RBAC Governance</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-black text-xs font-bold rounded transition-colors"
        >
          + CREATE ORGANIZATION
        </button>
      </div>

      {message && (
        <div className={`p-3 text-xs rounded border ${message.isError ? 'bg-red-950/40 border-red-500/50 text-red-300' : 'bg-emerald-950/40 border-emerald-500/50 text-emerald-300'}`}>
          {message.text}
        </div>
      )}

      {loading ? (
        <div className="text-cyan-400 text-xs animate-pulse">LOADING TENANT STRUCTURE...</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Organizations List */}
          <div className="bg-gray-900/60 border border-gray-800 rounded p-4 space-y-3">
            <h2 className="text-xs font-semibold text-gray-300 uppercase tracking-wider">Organizations</h2>
            {orgs.length === 0 ? (
              <p className="text-xs text-gray-500">No organizations found.</p>
            ) : (
              <div className="space-y-2">
                {orgs.map((org) => (
                  <div
                    key={org.id}
                    onClick={() => {
                      setSelectedOrg(org);
                      saasApi.listMembers(org.id).then(setMembers);
                    }}
                    className={`p-3 rounded border cursor-pointer transition-all ${selectedOrg?.id === org.id ? 'bg-cyan-950/30 border-cyan-500/50 text-cyan-300' : 'bg-gray-800/30 border-gray-800 hover:border-gray-700 text-gray-300'}`}
                  >
                    <div className="font-bold text-sm">{org.name}</div>
                    <div className="text-xs text-gray-400 flex justify-between mt-1">
                      <span>Slug: {org.slug}</span>
                      <span className="text-cyan-400 font-semibold">{org.plan_tier}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Selected Org Members & Governance */}
          <div className="lg:col-span-2 bg-gray-900/60 border border-gray-800 rounded p-4 space-y-4">
            {selectedOrg ? (
              <>
                <div className="flex justify-between items-center border-b border-gray-800 pb-3">
                  <div>
                    <h3 className="text-sm font-bold text-white">{selectedOrg.name} — Members</h3>
                    <p className="text-xs text-gray-400">Plan: {selectedOrg.plan_tier} | Billing: {selectedOrg.billing_email}</p>
                  </div>
                  <button
                    onClick={() => setShowInviteModal(true)}
                    className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-cyan-400 border border-cyan-500/30 text-xs rounded"
                  >
                    + Invite Member
                  </button>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-gray-800 text-gray-400">
                        <th className="py-2">USER</th>
                        <th className="py-2">EMAIL</th>
                        <th className="py-2">ROLE</th>
                        <th className="py-2">STATUS</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800/50">
                      {members.map((m) => (
                        <tr key={m.id} className="hover:bg-gray-800/20">
                          <td className="py-2 text-cyan-300">{m.username || m.user_id.slice(0, 8)}</td>
                          <td className="py-2 text-gray-300">{m.email || 'N/A'}</td>
                          <td className="py-2">
                            <span className="px-2 py-0.5 bg-gray-800 text-cyan-400 rounded text-[10px] border border-cyan-500/20">
                              {m.role}
                            </span>
                          </td>
                          <td className="py-2">
                            <span className={`px-2 py-0.5 rounded text-[10px] ${m.status === 'ACTIVE' ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/30' : 'bg-amber-950 text-amber-400 border border-amber-500/30'}`}>
                              {m.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            ) : (
              <p className="text-xs text-gray-500">Select an organization to view details.</p>
            )}
          </div>
        </div>
      )}

      {/* Create Org Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 border border-cyan-500/40 rounded p-6 max-w-md w-full space-y-4">
            <h3 className="text-sm font-bold text-cyan-400 uppercase">Create New Organization</h3>
            <form onSubmit={handleCreateOrg} className="space-y-3 text-xs">
              <div>
                <label className="block text-gray-400 mb-1">Organization Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-black/60 border border-gray-700 rounded p-2 text-white"
                  placeholder="Acme Security Corp"
                />
              </div>
              <div>
                <label className="block text-gray-400 mb-1">Unique Slug (URL Identifier)</label>
                <input
                  type="text"
                  required
                  value={slug}
                  onChange={(e) => setSlug(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ''))}
                  className="w-full bg-black/60 border border-gray-700 rounded p-2 text-white"
                  placeholder="acme-sec"
                />
              </div>
              <div>
                <label className="block text-gray-400 mb-1">Billing Email</label>
                <input
                  type="email"
                  required
                  value={billingEmail}
                  onChange={(e) => setBillingEmail(e.target.value)}
                  className="w-full bg-black/60 border border-gray-700 rounded p-2 text-white"
                  placeholder="billing@acme.com"
                />
              </div>
              <div className="flex justify-end space-x-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-black font-bold rounded"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Invite Member Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 border border-cyan-500/40 rounded p-6 max-w-md w-full space-y-4">
            <h3 className="text-sm font-bold text-cyan-400 uppercase">Invite Team Member</h3>
            <form onSubmit={handleInviteMember} className="space-y-3 text-xs">
              <div>
                <label className="block text-gray-400 mb-1">User Email Address</label>
                <input
                  type="email"
                  required
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  className="w-full bg-black/60 border border-gray-700 rounded p-2 text-white"
                  placeholder="analyst@acme.com"
                />
              </div>
              <div>
                <label className="block text-gray-400 mb-1">Tenant Role</label>
                <select
                  value={inviteRole}
                  onChange={(e) => setInviteRole(e.target.value)}
                  className="w-full bg-black/60 border border-gray-700 rounded p-2 text-white"
                >
                  <option value="SECURITY_ANALYST">SECURITY_ANALYST (Detection & Investigation)</option>
                  <option value="RESPONDER">RESPONDER (SOAR & Incident Remediation)</option>
                  <option value="ADMIN">ADMIN (Workspace & User Management)</option>
                  <option value="BILLING_ADMIN">BILLING_ADMIN (Subscription & Invoices)</option>
                  <option value="API_ADMIN">API_ADMIN (API Keys & Integrations)</option>
                  <option value="VIEWER">VIEWER (Read-Only Dashboards)</option>
                </select>
              </div>
              <div className="flex justify-end space-x-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowInviteModal(false)}
                  className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-black font-bold rounded"
                >
                  Send Invite
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
