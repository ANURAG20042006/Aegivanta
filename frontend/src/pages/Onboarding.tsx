import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { saasApi } from '../services/saas';

export const OnboardingPage: React.FC = () => {
  const navigate = useNavigate();
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Step 1 Org inputs
  const [orgName, setOrgName] = useState('');
  const [orgSlug, setOrgSlug] = useState('');
  const [billingEmail, setBillingEmail] = useState('');

  // Step 3 Sensor inputs
  const [sensorName, setSensorName] = useState('');
  const [hostname, setHostname] = useState('');
  const [ipAddress, setIpAddress] = useState('');
  const [sensorToken, setSensorToken] = useState<string | null>(null);

  const [message, setMessage] = useState<{ text: string; isError: boolean } | null>(null);

  const checkStatus = async () => {
    setLoading(true);
    try {
      const data = await saasApi.getOnboardingStatus();
      setStatus(data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkStatus();
  }, []);

  const handleCreateOrg = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await saasApi.createOrganization({ name: orgName, slug: orgSlug, billing_email: billingEmail });
      setMessage({ text: 'Organization created! Proceeding to next step...', isError: false });
      checkStatus();
    } catch (err: any) {
      setMessage({ text: err.response?.data?.detail || 'Failed to create organization', isError: true });
    }
  };

  const handleEnrollSensor = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await saasApi.enrollSensor({ name: sensorName, hostname, ip_address: ipAddress });
      setSensorToken(res.enrollment_token);
      setMessage({ text: 'Sensor enrolled! Connect your agent to complete onboarding.', isError: false });
      checkStatus();
    } catch (err: any) {
      setMessage({ text: err.response?.data?.detail || 'Sensor enrollment failed', isError: true });
    }
  };

  const STEPS = [
    { num: 1, title: 'Create Organization', desc: 'Define your company security workspace' },
    { num: 2, title: 'Select Subscription', desc: 'Choose tier and feature entitlements' },
    { num: 3, title: 'Deploy Telemetry Sensor', desc: 'Connect endpoints & network taps' },
    { num: 4, title: 'SOC Verification', desc: 'Live alerts and detection validation' }
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6 font-mono py-4">
      <div className="border-b border-gray-800 pb-4 text-center">
        <h1 className="text-2xl font-bold text-cyan-400 tracking-wider">SENTINELAI CUSTOMER ONBOARDING</h1>
        <p className="text-xs text-gray-400 mt-1">Enterprise Cybersecurity SOC Platform Guided Deployment</p>
      </div>

      {/* Stepper Wizard Bar */}
      <div className="grid grid-cols-4 gap-2">
        {STEPS.map((s) => {
          const isDone = status && status.current_step > s.num;
          const isCurrent = status && status.current_step === s.num;
          return (
            <div
              key={s.num}
              className={`p-3 rounded border text-center transition-all ${isCurrent ? 'bg-cyan-950/40 border-cyan-500/80 text-cyan-300' : isDone ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-400' : 'bg-gray-900/40 border-gray-800 text-gray-500'}`}
            >
              <div className="text-xs font-bold">{isDone ? '✓ STEP ' + s.num : 'STEP ' + s.num}</div>
              <div className="text-[11px] font-semibold mt-0.5 truncate">{s.title}</div>
            </div>
          );
        })}
      </div>

      {message && (
        <div className={`p-3 text-xs rounded border ${message.isError ? 'bg-red-950/40 border-red-500/50 text-red-300' : 'bg-emerald-950/40 border-emerald-500/50 text-emerald-300'}`}>
          {message.text}
        </div>
      )}

      {loading ? (
        <div className="text-cyan-400 text-xs animate-pulse text-center py-8">INITIALIZING ONBOARDING PROGRESS...</div>
      ) : (
        <div className="bg-gray-900/60 border border-gray-800 rounded p-6">
          {/* Step 1: Create Organization */}
          {status?.current_step === 1 && (
            <div className="space-y-4">
              <h2 className="text-sm font-bold text-white uppercase">Step 1: Set Up Your Organization</h2>
              <form onSubmit={handleCreateOrg} className="space-y-3 text-xs max-w-md">
                <div>
                  <label className="block text-gray-400 mb-1">Company / Organization Name</label>
                  <input
                    type="text"
                    required
                    value={orgName}
                    onChange={(e) => setOrgName(e.target.value)}
                    className="w-full bg-black/60 border border-gray-700 rounded p-2 text-white"
                    placeholder="Acme Defense Systems"
                  />
                </div>
                <div>
                  <label className="block text-gray-400 mb-1">Unique Workspace Slug</label>
                  <input
                    type="text"
                    required
                    value={orgSlug}
                    onChange={(e) => setOrgSlug(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ''))}
                    className="w-full bg-black/60 border border-gray-700 rounded p-2 text-white"
                    placeholder="acme-defense"
                  />
                </div>
                <div>
                  <label className="block text-gray-400 mb-1">Security & Billing Email</label>
                  <input
                    type="email"
                    required
                    value={billingEmail}
                    onChange={(e) => setBillingEmail(e.target.value)}
                    className="w-full bg-black/60 border border-gray-700 rounded p-2 text-white"
                    placeholder="soc-lead@acme.com"
                  />
                </div>
                <button
                  type="submit"
                  className="px-6 py-2 bg-cyan-600 hover:bg-cyan-500 text-black font-bold rounded"
                >
                  Create & Proceed →
                </button>
              </form>
            </div>
          )}

          {/* Step 2: Subscription & Entitlement */}
          {status?.current_step === 2 && (
            <div className="space-y-4">
              <h2 className="text-sm font-bold text-white uppercase">Step 2: Subscription Tier Configured</h2>
              <p className="text-xs text-gray-300">
                Your workspace is currently initialized with the <strong>FREE Tier</strong> (3 Users, 5GB monthly telemetry, standard rules).
              </p>
              <div className="flex space-x-3 pt-2">
                <button
                  onClick={() => checkStatus()}
                  className="px-5 py-2 bg-cyan-600 hover:bg-cyan-500 text-black font-bold text-xs rounded"
                >
                  Continue with Current Plan →
                </button>
                <button
                  onClick={() => navigate('/billing')}
                  className="px-5 py-2 bg-gray-800 hover:bg-gray-700 text-cyan-400 border border-cyan-500/30 text-xs rounded"
                >
                  Explore Commercial Tiers
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Deploy Telemetry Sensor */}
          {status?.current_step === 3 && (
            <div className="space-y-4">
              <h2 className="text-sm font-bold text-white uppercase">Step 3: Enroll Telemetry Collection Agent</h2>
              <p className="text-xs text-gray-300">Deploy the lightweight SentinelAI daemon to stream host/network metrics.</p>

              {sensorToken ? (
                <div className="space-y-3">
                  <div className="p-3 bg-emerald-950/40 border border-emerald-500/50 rounded text-emerald-300 text-xs">
                    Sensor successfully enrolled! Run the daemon using this authentication token:
                  </div>
                  <div className="p-3 bg-black border border-gray-700 rounded font-mono text-cyan-300 text-xs select-all break-all">
                    sentinelai-agent --tenant={status.organization_slug} --token={sensorToken}
                  </div>
                  <button
                    onClick={() => navigate('/dashboard')}
                    className="px-6 py-2 bg-cyan-600 hover:bg-cyan-500 text-black font-bold text-xs rounded"
                  >
                    Open SOC Command Center →
                  </button>
                </div>
              ) : (
                <form onSubmit={handleEnrollSensor} className="space-y-3 text-xs max-w-md">
                  <div>
                    <label className="block text-gray-400 mb-1">Sensor Display Name</label>
                    <input
                      type="text"
                      required
                      value={sensorName}
                      onChange={(e) => setSensorName(e.target.value)}
                      className="w-full bg-black/60 border border-gray-700 rounded p-2 text-white"
                      placeholder="DMZ Core Firewall Tap"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-400 mb-1">Target Hostname</label>
                    <input
                      type="text"
                      required
                      value={hostname}
                      onChange={(e) => setHostname(e.target.value)}
                      className="w-full bg-black/60 border border-gray-700 rounded p-2 text-white"
                      placeholder="fw-edge-01.internal"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-400 mb-1">IP Address</label>
                    <input
                      type="text"
                      required
                      value={ipAddress}
                      onChange={(e) => setIpAddress(e.target.value)}
                      className="w-full bg-black/60 border border-gray-700 rounded p-2 text-white"
                      placeholder="10.0.1.254"
                    />
                  </div>
                  <button
                    type="submit"
                    className="px-6 py-2 bg-cyan-600 hover:bg-cyan-500 text-black font-bold rounded"
                  >
                    Enroll Sensor & Get Token →
                  </button>
                </form>
              )}
            </div>
          )}

          {/* Step 4: Verification & Completed */}
          {status?.current_step === 4 && (
            <div className="space-y-4 text-center py-4">
              <div className="text-4xl text-emerald-400">✓</div>
              <h2 className="text-lg font-bold text-white uppercase">Workspace Verified & Operational</h2>
              <p className="text-xs text-gray-400 max-w-md mx-auto">
                Your organization ({status.organization_name}) is fully connected with {status.sensor_count} active sensors.
              </p>
              <button
                onClick={() => navigate('/dashboard')}
                className="px-8 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-black font-bold text-xs rounded transition-colors"
              >
                LAUNCH SOC COMMAND CENTER
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
