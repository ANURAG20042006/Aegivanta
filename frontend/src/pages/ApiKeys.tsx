import React, { useState, useEffect } from 'react';
import { saasApi, ApiKeyItem } from '../services/saas';

export const ApiKeysPage: React.FC = () => {
  const [keys, setKeys] = useState<ApiKeyItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [selectedScopes, setSelectedScopes] = useState<string[]>(['READ_TELEMETRY', 'WRITE_TELEMETRY']);
  const [createdSecret, setCreatedSecret] = useState<string | null>(null);
  const [message, setMessage] = useState<{ text: string; isError: boolean } | null>(null);

  const AVAILABLE_SCOPES = [
    { key: 'READ_TELEMETRY', desc: 'Read ingested network and host telemetry flows' },
    { key: 'WRITE_TELEMETRY', desc: 'Ingest raw flow events and PCAP telemetry' },
    { key: 'READ_INCIDENTS', desc: 'Query active and historical security incidents' },
    { key: 'WRITE_INCIDENTS', desc: 'Update incident status, assignees, and notes' },
    { key: 'READ_THREAT_INTEL', desc: 'Query IOC database, fast cache, and threat feeds' },
    { key: 'RUN_HUNTS', desc: 'Execute scheduled or ad-hoc threat hunting queries' },
    { key: 'EXECUTE_RESPONSE', desc: 'Execute SOAR playbooks and autonomous responses' },
    { key: 'READ_ANALYTICS', desc: 'Access attack graph, predictive, and SOC metrics' },
    { key: 'ADMIN', desc: 'Full tenant administrative access' }
  ];

  const loadKeys = async () => {
    setLoading(true);
    try {
      const list = await saasApi.listApiKeys();
      setKeys(list);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadKeys();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await saasApi.createApiKey({ name: newKeyName, scopes: selectedScopes });
      setCreatedSecret(res.secret_key);
      setMessage({ text: 'API Key generated successfully! Save your secret immediately.', isError: false });
      setNewKeyName('');
      loadKeys();
    } catch (err: any) {
      setMessage({ text: err.response?.data?.detail || 'Failed to create API key', isError: true });
    }
  };

  const handleRevoke = async (keyId: string) => {
    if (!window.confirm('Are you sure you want to revoke this API key? This action is immediate and irreversible.')) return;
    try {
      await saasApi.revokeApiKey(keyId);
      setMessage({ text: 'API Key revoked.', isError: false });
      loadKeys();
    } catch (err: any) {
      setMessage({ text: err.response?.data?.detail || 'Failed to revoke API key', isError: true });
    }
  };

  const toggleScope = (scope: string) => {
    if (selectedScopes.includes(scope)) {
      setSelectedScopes(selectedScopes.filter(s => s !== scope));
    } else {
      setSelectedScopes([...selectedScopes, scope]);
    }
  };

  return (
    <div className="space-y-6 font-mono">
      <div className="flex justify-between items-center border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-cyan-400 tracking-wider">API KEY MANAGEMENT</h1>
          <p className="text-xs text-gray-400">Scoped Machine-to-Machine Authentication & Rate Limiting</p>
        </div>
        <button
          onClick={() => { setShowModal(true); setCreatedSecret(null); }}
          className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-black text-xs font-bold rounded transition-colors"
        >
          + GENERATE API KEY
        </button>
      </div>

      {message && (
        <div className={`p-3 text-xs rounded border ${message.isError ? 'bg-red-950/40 border-red-500/50 text-red-300' : 'bg-emerald-950/40 border-emerald-500/50 text-emerald-300'}`}>
          {message.text}
        </div>
      )}

      {loading ? (
        <div className="text-cyan-400 text-xs animate-pulse">LOADING API KEYS...</div>
      ) : (
        <div className="bg-gray-900/60 border border-gray-800 rounded p-4">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-gray-800 text-gray-400">
                  <th className="py-2.5">NAME</th>
                  <th className="py-2.5">PREFIX</th>
                  <th className="py-2.5">SCOPES</th>
                  <th className="py-2.5">RATE LIMIT</th>
                  <th className="py-2.5">STATUS</th>
                  <th className="py-2.5">LAST USED</th>
                  <th className="py-2.5 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/50">
                {keys.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-6 text-center text-gray-500">No API keys found for active tenant.</td>
                  </tr>
                ) : (
                  keys.map((k) => (
                    <tr key={k.id} className="hover:bg-gray-800/20">
                      <td className="py-3 font-semibold text-white">{k.name}</td>
                      <td className="py-3 text-cyan-400 font-bold">{k.key_prefix}...</td>
                      <td className="py-3">
                        <div className="flex flex-wrap gap-1">
                          {k.scopes.map((s, i) => (
                            <span key={i} className="px-1.5 py-0.5 bg-gray-800 text-[10px] text-gray-300 rounded border border-gray-700">
                              {s}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="py-3 text-gray-300">{k.rate_limit_rpm} rpm</td>
                      <td className="py-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] ${k.is_active ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/30' : 'bg-red-950 text-red-400 border border-red-500/30'}`}>
                          {k.is_active ? 'ACTIVE' : 'REVOKED'}
                        </span>
                      </td>
                      <td className="py-3 text-gray-400">{k.last_used_at ? new Date(k.last_used_at).toLocaleDateString() : 'Never'}</td>
                      <td className="py-3 text-right">
                        {k.is_active && (
                          <button
                            onClick={() => handleRevoke(k.id)}
                            className="px-2.5 py-1 bg-red-950 hover:bg-red-900 text-red-300 border border-red-500/30 rounded text-[10px]"
                          >
                            Revoke
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Generate API Key Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 border border-cyan-500/40 rounded p-6 max-w-lg w-full space-y-4">
            <h3 className="text-sm font-bold text-cyan-400 uppercase">Generate New API Key</h3>

            {createdSecret ? (
              <div className="space-y-4">
                <div className="p-3 bg-amber-950/40 border border-amber-500/50 rounded text-amber-200 text-xs">
                  <p className="font-bold">⚠️ Copy your secret key now!</p>
                  <p className="mt-1">For security reasons, this token will NEVER be displayed again.</p>
                </div>
                <div className="p-3 bg-black border border-gray-700 rounded font-mono text-cyan-300 text-xs break-all select-all">
                  {createdSecret}
                </div>
                <button
                  onClick={() => setShowModal(false)}
                  className="w-full py-2 bg-cyan-600 hover:bg-cyan-500 text-black font-bold text-xs rounded"
                >
                  I have saved my secret key
                </button>
              </div>
            ) : (
              <form onSubmit={handleCreate} className="space-y-3 text-xs">
                <div>
                  <label className="block text-gray-400 mb-1">Key Name / Description</label>
                  <input
                    type="text"
                    required
                    value={newKeyName}
                    onChange={(e) => setNewKeyName(e.target.value)}
                    className="w-full bg-black/60 border border-gray-700 rounded p-2 text-white"
                    placeholder="e.g. Splunk Forwarder Ingestion Key"
                  />
                </div>

                <div>
                  <label className="block text-gray-400 mb-2">Entitled Scopes</label>
                  <div className="space-y-1.5 max-h-48 overflow-y-auto border border-gray-800 p-2 rounded bg-black/40">
                    {AVAILABLE_SCOPES.map((s) => (
                      <label key={s.key} className="flex items-start space-x-2 cursor-pointer hover:bg-gray-800/30 p-1 rounded">
                        <input
                          type="checkbox"
                          checked={selectedScopes.includes(s.key)}
                          onChange={() => toggleScope(s.key)}
                          className="mt-0.5 rounded border-gray-700 text-cyan-600 focus:ring-cyan-500"
                        />
                        <div>
                          <div className="font-bold text-white text-[11px]">{s.key}</div>
                          <div className="text-gray-400 text-[10px]">{s.desc}</div>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="flex justify-end space-x-2 pt-3">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-black font-bold rounded"
                  >
                    Generate Key
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
