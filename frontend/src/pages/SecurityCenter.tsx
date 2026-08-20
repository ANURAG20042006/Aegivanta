import React, { useState, useEffect } from 'react';
import { saasApi } from '../services/saas';

export const SecurityCenterPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'posture' | 'identity' | 'sessions' | 'policies' | 'events'>('posture');
  const [posture, setPosture] = useState<any>(null);
  const [sessions, setSessions] = useState<any[]>([]);
  const [policies, setPolicies] = useState<any>(null);
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [message, setMessage] = useState<{ text: string; isError: boolean } | null>(null);

  // MFA Setup State
  const [mfaData, setMfaData] = useState<{ secret: string; recovery_codes: string[]; otpauth_uri: string } | null>(null);
  const [mfaCode, setMfaCode] = useState('');

  // SSO Form State
  const [ssoProvider, setSsoProvider] = useState('OIDC');
  const [ssoName, setSsoName] = useState('');
  const [ssoClientId, setSsoClientId] = useState('');
  const [ssoDiscoveryUrl, setSsoDiscoveryUrl] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [postureRes, sessionsRes, policiesRes, eventsRes] = await Promise.all([
        saasApi.getSecurityPosture().catch(() => null),
        saasApi.listSessions().catch(() => []),
        saasApi.getSecurityPolicies().catch(() => null),
        saasApi.listSecurityEvents().catch(() => [])
      ]);
      setPosture(postureRes);
      setSessions(sessionsRes);
      setPolicies(policiesRes);
      setEvents(eventsRes);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleStartMfa = async () => {
    try {
      const res = await saasApi.setupMFA();
      setMfaData(res);
    } catch (err: any) {
      setMessage({ text: err.response?.data?.detail || 'MFA setup failed', isError: true });
    }
  };

  const handleVerifyMfa = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await saasApi.verifyMFA(mfaCode);
      setMessage({ text: 'MFA activated successfully!', isError: false });
      setMfaData(null);
      setMfaCode('');
      loadData();
    } catch (err: any) {
      setMessage({ text: err.response?.data?.detail || 'Invalid verification code', isError: true });
    }
  };

  const handleRevokeSession = async (id: string) => {
    try {
      await saasApi.revokeSession(id);
      setMessage({ text: 'Session terminated.', isError: false });
      const updated = await saasApi.listSessions();
      setSessions(updated);
    } catch (err: any) {
      setMessage({ text: err.response?.data?.detail || 'Failed to revoke session', isError: true });
    }
  };

  const handleSaveSSO = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await saasApi.configureSSO({
        provider_type: ssoProvider,
        name: ssoName,
        client_id: ssoClientId,
        discovery_url: ssoDiscoveryUrl
      });
      setMessage({ text: 'Enterprise SSO configured successfully!', isError: false });
      loadData();
    } catch (err: any) {
      setMessage({ text: err.response?.data?.detail || 'Failed to configure SSO', isError: true });
    }
  };

  const handleTogglePolicy = async (key: string, value: boolean) => {
    try {
      const updated = await saasApi.updateSecurityPolicies({ [key]: value });
      setPolicies(updated);
      setMessage({ text: 'Security policy updated.', isError: false });
      loadData();
    } catch (err: any) {
      setMessage({ text: err.response?.data?.detail || 'Failed to update policy', isError: true });
    }
  };

  return (
    <div className="space-y-6 font-mono">
      <div className="flex justify-between items-center border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-cyan-400 tracking-wider">ENTERPRISE SECURITY CENTER</h1>
          <p className="text-xs text-gray-400">Identity Governance, Security Policies & Posture Analytics</p>
        </div>
        {posture && (
          <div className="flex items-center space-x-3 bg-gray-900 border border-cyan-500/30 px-3 py-1.5 rounded">
            <span className="text-xs text-gray-400">POSTURE SCORE:</span>
            <span className={`text-base font-bold ${posture.overall_posture_score >= 85 ? 'text-emerald-400' : 'text-amber-400'}`}>
              {posture.overall_posture_score}/100
            </span>
          </div>
        )}
      </div>

      {message && (
        <div className={`p-3 text-xs rounded border ${message.isError ? 'bg-red-950/40 border-red-500/50 text-red-300' : 'bg-emerald-950/40 border-emerald-500/50 text-emerald-300'}`}>
          {message.text}
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex space-x-2 border-b border-gray-800">
        {[
          { id: 'posture', label: 'Security Posture' },
          { id: 'identity', label: 'Identity & SSO' },
          { id: 'sessions', label: `Active Sessions (${sessions.length})` },
          { id: 'policies', label: 'Security Policies' },
          { id: 'events', label: 'Security Events' }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-4 py-2 text-xs font-bold border-b-2 transition-all ${activeTab === tab.id ? 'border-cyan-400 text-cyan-400 bg-cyan-950/20' : 'border-transparent text-gray-400 hover:text-gray-200'}`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-cyan-400 text-xs animate-pulse">ANALYZING ENTERPRISE SECURITY POSTURE...</div>
      ) : (
        <>
          {/* TAB 1: Security Posture */}
          {activeTab === 'posture' && posture && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                {Object.entries(posture.dimension_scores || {}).map(([dim, score]: [string, any]) => (
                  <div key={dim} className="bg-gray-900/60 border border-gray-800 rounded p-4">
                    <div className="text-[10px] text-gray-400 uppercase tracking-wider">{dim.replace('_', ' ')}</div>
                    <div className="text-xl font-bold text-cyan-300 mt-1">{score}/100</div>
                    <div className="w-full bg-gray-800 h-1 mt-2 rounded overflow-hidden">
                      <div className="bg-cyan-400 h-full" style={{ width: `${score}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>

              {posture.recommendations?.length > 0 && (
                <div className="bg-gray-900/60 border border-gray-800 rounded p-4 space-y-2">
                  <h3 className="text-xs font-bold text-amber-400 uppercase tracking-wider">Actionable Security Recommendations</h3>
                  <ul className="space-y-1.5 text-xs text-gray-300">
                    {posture.recommendations.map((rec: string, i: number) => (
                      <li key={i} className="flex items-start space-x-2">
                        <span className="text-amber-400 font-bold">!</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: Identity, MFA & SSO */}
          {activeTab === 'identity' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* TOTP MFA Enrollment */}
              <div className="bg-gray-900/60 border border-gray-800 rounded p-5 space-y-4">
                <h3 className="text-sm font-bold text-white uppercase">Multi-Factor Authentication (TOTP)</h3>
                <p className="text-xs text-gray-400">Protect account access with Google Authenticator or hardware tokens.</p>

                {mfaData ? (
                  <div className="space-y-3">
                    <div className="p-3 bg-black border border-gray-800 rounded text-xs space-y-1">
                      <div className="text-gray-400">Base32 Secret:</div>
                      <div className="font-mono text-cyan-400 font-bold select-all">{mfaData.secret}</div>
                    </div>
                    <form onSubmit={handleVerifyMfa} className="space-y-2 text-xs">
                      <label className="block text-gray-400">Enter 6-Digit Code to Activate:</label>
                      <div className="flex space-x-2">
                        <input
                          type="text"
                          required
                          maxLength={6}
                          value={mfaCode}
                          onChange={(e) => setMfaCode(e.target.value)}
                          className="w-32 bg-black border border-gray-700 rounded p-2 text-center text-white tracking-widest font-bold"
                          placeholder="123456"
                        />
                        <button type="submit" className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-black font-bold rounded">
                          Verify & Enable
                        </button>
                      </div>
                    </form>
                  </div>
                ) : (
                  <button
                    onClick={handleStartMfa}
                    className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-cyan-400 border border-cyan-500/30 text-xs rounded font-bold"
                  >
                    Enroll TOTP Authenticator
                  </button>
                )}
              </div>

              {/* Enterprise SSO */}
              <div className="bg-gray-900/60 border border-gray-800 rounded p-5 space-y-4">
                <h3 className="text-sm font-bold text-white uppercase">Enterprise Single Sign-On (SSO)</h3>
                <form onSubmit={handleSaveSSO} className="space-y-3 text-xs">
                  <div>
                    <label className="block text-gray-400 mb-1">SSO Protocol</label>
                    <select
                      value={ssoProvider}
                      onChange={(e) => setSsoProvider(e.target.value)}
                      className="w-full bg-black border border-gray-700 rounded p-2 text-white"
                    >
                      <option value="OIDC">OpenID Connect (OIDC / OAuth 2.0)</option>
                      <option value="SAML">SAML 2.0 (Okta, Azure AD, OneLogin)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-gray-400 mb-1">IdP Display Name</label>
                    <input
                      type="text"
                      required
                      value={ssoName}
                      onChange={(e) => setSsoName(e.target.value)}
                      className="w-full bg-black border border-gray-700 rounded p-2 text-white"
                      placeholder="e.g. Okta Corporate Directory"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-400 mb-1">Client ID / Entity ID</label>
                    <input
                      type="text"
                      required
                      value={ssoClientId}
                      onChange={(e) => setSsoClientId(e.target.value)}
                      className="w-full bg-black border border-gray-700 rounded p-2 text-white"
                      placeholder="0oa1b2c3d4..."
                    />
                  </div>
                  <div>
                    <label className="block text-gray-400 mb-1">OIDC Discovery / SAML SSO URL</label>
                    <input
                      type="url"
                      required
                      value={ssoDiscoveryUrl}
                      onChange={(e) => setSsoDiscoveryUrl(e.target.value)}
                      className="w-full bg-black border border-gray-700 rounded p-2 text-white"
                      placeholder="https://company.okta.com/.well-known/openid-configuration"
                    />
                  </div>
                  <button type="submit" className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-black font-bold rounded">
                    Save SSO Config
                  </button>
                </form>
              </div>
            </div>
          )}

          {/* TAB 3: Active Sessions */}
          {activeTab === 'sessions' && (
            <div className="bg-gray-900/60 border border-gray-800 rounded p-4">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-gray-800 text-gray-400">
                      <th className="py-2.5">IP ADDRESS</th>
                      <th className="py-2.5">USER AGENT</th>
                      <th className="py-2.5">LAST ACTIVE</th>
                      <th className="py-2.5">SECURITY STATUS</th>
                      <th className="py-2.5 text-right">ACTION</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800/50">
                    {sessions.map((s) => (
                      <tr key={s.id} className="hover:bg-gray-800/20">
                        <td className="py-3 font-mono text-cyan-300">{s.ip_address}</td>
                        <td className="py-3 text-gray-300 truncate max-w-xs">{s.user_agent}</td>
                        <td className="py-3 text-gray-400">{new Date(s.last_activity_at).toLocaleTimeString()}</td>
                        <td className="py-3">
                          {s.is_suspicious ? (
                            <span className="px-2 py-0.5 bg-amber-950 text-amber-400 rounded text-[10px] border border-amber-500/30">
                              NEW IP
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 bg-emerald-950 text-emerald-400 rounded text-[10px] border border-emerald-500/30">
                              VERIFIED
                            </span>
                          )}
                        </td>
                        <td className="py-3 text-right">
                          <button
                            onClick={() => handleRevokeSession(s.id)}
                            className="px-2.5 py-1 bg-red-950 hover:bg-red-900 text-red-300 text-[10px] rounded border border-red-500/30"
                          >
                            Terminate
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 4: Security Policies */}
          {activeTab === 'policies' && policies && (
            <div className="bg-gray-900/60 border border-gray-800 rounded p-5 space-y-4 max-w-2xl">
              <h3 className="text-sm font-bold text-white uppercase">Enterprise Security Policies</h3>
              <div className="space-y-3 text-xs">
                <label className="flex items-center justify-between p-3 bg-gray-800/30 border border-gray-800 rounded cursor-pointer">
                  <div>
                    <div className="font-bold text-white">Require Multi-Factor Authentication (MFA)</div>
                    <div className="text-gray-400">Block logins without verified TOTP authenticator</div>
                  </div>
                  <input
                    type="checkbox"
                    checked={policies.require_mfa}
                    onChange={(e) => handleTogglePolicy('require_mfa', e.target.checked)}
                    className="w-4 h-4 text-cyan-600 rounded"
                  />
                </label>

                <label className="flex items-center justify-between p-3 bg-gray-800/30 border border-gray-800 rounded cursor-pointer">
                  <div>
                    <div className="font-bold text-white">Enforce Enterprise SSO</div>
                    <div className="text-gray-400">Disable password logins and require IdP authentication</div>
                  </div>
                  <input
                    type="checkbox"
                    checked={policies.require_sso}
                    onChange={(e) => handleTogglePolicy('require_sso', e.target.checked)}
                    className="w-4 h-4 text-cyan-600 rounded"
                  />
                </label>
              </div>
            </div>
          )}

          {/* TAB 5: Security Events */}
          {activeTab === 'events' && (
            <div className="bg-gray-900/60 border border-gray-800 rounded p-4">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-gray-800 text-gray-400">
                      <th className="py-2.5">TIMESTAMP</th>
                      <th className="py-2.5">EVENT</th>
                      <th className="py-2.5">ACTOR</th>
                      <th className="py-2.5">SEVERITY</th>
                      <th className="py-2.5">ACTION DETAILS</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800/50">
                    {events.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="py-6 text-center text-gray-500">No security events recorded.</td>
                      </tr>
                    ) : (
                      events.map((e) => (
                        <tr key={e.id} className="hover:bg-gray-800/20">
                          <td className="py-3 text-gray-400">{new Date(e.timestamp).toLocaleTimeString()}</td>
                          <td className="py-3 font-bold text-cyan-300">{e.event_type}</td>
                          <td className="py-3 text-gray-300">{e.actor_email || e.actor_id}</td>
                          <td className="py-3">
                            <span className={`px-2 py-0.5 rounded text-[10px] ${e.severity === 'CRITICAL' ? 'bg-red-950 text-red-400' : e.severity === 'WARNING' ? 'bg-amber-950 text-amber-400' : 'bg-gray-800 text-gray-300'}`}>
                              {e.severity}
                            </span>
                          </td>
                          <td className="py-3 text-white">{e.action}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
