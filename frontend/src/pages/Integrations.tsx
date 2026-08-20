import React, { useState, useEffect } from 'react';
import { saasApi, IntegrationItem } from '../services/saas';

export const IntegrationsPage: React.FC = () => {
  const [integrations, setIntegrations] = useState<IntegrationItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [integType, setIntegType] = useState('SLACK');
  const [name, setName] = useState('');
  const [webhookUrl, setWebhookUrl] = useState('');
  const [message, setMessage] = useState<{ text: string; isError: boolean } | null>(null);

  const loadIntegrations = async () => {
    setLoading(true);
    try {
      const list = await saasApi.listIntegrations();
      setIntegrations(list);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadIntegrations();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await saasApi.createIntegration({
        integration_type: integType,
        name,
        config: { webhook_url: webhookUrl }
      });
      setMessage({ text: 'Integration connector configured successfully!', isError: false });
      setShowModal(false);
      setName('');
      setWebhookUrl('');
      loadIntegrations();
    } catch (err: any) {
      setMessage({ text: err.response?.data?.detail || 'Failed to create integration', isError: true });
    }
  };

  const handleTest = async (id: string) => {
    try {
      const res = await saasApi.testIntegration(id);
      setMessage({ text: res.message || 'Test dispatch successful!', isError: false });
      loadIntegrations();
    } catch (err: any) {
      setMessage({ text: err.response?.data?.detail || 'Test dispatch failed', isError: true });
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Delete this integration?')) return;
    try {
      await saasApi.deleteIntegration(id);
      setMessage({ text: 'Integration removed.', isError: false });
      loadIntegrations();
    } catch (err: any) {
      setMessage({ text: err.response?.data?.detail || 'Failed to delete integration', isError: true });
    }
  };

  const AVAILABLE_CONNECTORS = [
    { type: 'SLACK', label: 'Slack Alert Dispatcher', desc: 'Post high/critical security alerts into SOC channels' },
    { type: 'WEBHOOK', label: 'Custom HTTP Webhook', desc: 'Stream JSON detection telemetry to SIEM or SOAR webhook' },
    { type: 'SIEM', label: 'Enterprise SIEM Forwarder', desc: 'Forward normalized CEF/JSON to Splunk, Elastic, or Microsoft Sentinel' },
    { type: 'JIRA', label: 'Jira / ServiceNow Ticketing', desc: 'Auto-create investigation tickets upon confirmed incidents' },
    { type: 'EDR', label: 'CrowdStrike / Defender EDR', desc: 'Push host isolation and containment actions directly to EDR' }
  ];

  return (
    <div className="space-y-6 font-mono">
      <div className="flex justify-between items-center border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-cyan-400 tracking-wider">ENTERPRISE INTEGRATION CONNECTORS</h1>
          <p className="text-xs text-gray-400">Bi-directional SIEM, EDR, Ticketing, and Alerting Connectors</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-black text-xs font-bold rounded transition-colors"
        >
          + ADD CONNECTOR
        </button>
      </div>

      {message && (
        <div className={`p-3 text-xs rounded border ${message.isError ? 'bg-red-950/40 border-red-500/50 text-red-300' : 'bg-emerald-950/40 border-emerald-500/50 text-emerald-300'}`}>
          {message.text}
        </div>
      )}

      {loading ? (
        <div className="text-cyan-400 text-xs animate-pulse">LOADING CONNECTORS...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {integrations.length === 0 ? (
            <div className="col-span-full bg-gray-900/40 border border-gray-800 rounded p-8 text-center text-gray-500 text-xs">
              No active integration connectors configured. Click "+ Add Connector" to integrate with Slack, SIEM, or EDR.
            </div>
          ) : (
            integrations.map((integ) => (
              <div key={integ.id} className="bg-gray-900/60 border border-gray-800 rounded p-4 flex flex-col justify-between space-y-3">
                <div>
                  <div className="flex justify-between items-center">
                    <span className="px-2 py-0.5 bg-gray-800 text-cyan-400 text-[10px] rounded border border-cyan-500/20 font-bold">
                      {integ.integration_type}
                    </span>
                    <span className="text-emerald-400 text-[10px] flex items-center space-x-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block"></span>
                      <span>{integ.status}</span>
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-white mt-2">{integ.name}</h3>
                  <div className="text-xs text-gray-400 mt-1">
                    Last sync: {integ.last_sync_at ? new Date(integ.last_sync_at).toLocaleTimeString() : 'Never'}
                  </div>
                </div>

                <div className="flex space-x-2 pt-2 border-t border-gray-800">
                  <button
                    onClick={() => handleTest(integ.id)}
                    className="flex-1 py-1.5 bg-gray-800 hover:bg-gray-700 text-cyan-300 text-xs rounded border border-gray-700"
                  >
                    Test Dispatch
                  </button>
                  <button
                    onClick={() => handleDelete(integ.id)}
                    className="px-3 py-1.5 bg-red-950 hover:bg-red-900 text-red-300 text-xs rounded border border-red-500/30"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Add Integration Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 border border-cyan-500/40 rounded p-6 max-w-md w-full space-y-4">
            <h3 className="text-sm font-bold text-cyan-400 uppercase">Configure New Connector</h3>
            <form onSubmit={handleCreate} className="space-y-3 text-xs">
              <div>
                <label className="block text-gray-400 mb-1">Connector Type</label>
                <select
                  value={integType}
                  onChange={(e) => setIntegType(e.target.value)}
                  className="w-full bg-black/60 border border-gray-700 rounded p-2 text-white"
                >
                  {AVAILABLE_CONNECTORS.map((c) => (
                    <option key={c.type} value={c.type}>{c.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-gray-400 mb-1">Integration Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-black/60 border border-gray-700 rounded p-2 text-white"
                  placeholder="e.g. SOC Team Alert Hook"
                />
              </div>
              <div>
                <label className="block text-gray-400 mb-1">Target Endpoint / Webhook URL</label>
                <input
                  type="url"
                  required
                  value={webhookUrl}
                  onChange={(e) => setWebhookUrl(e.target.value)}
                  className="w-full bg-black/60 border border-gray-700 rounded p-2 text-white"
                  placeholder="https://hooks.slack.com/services/..."
                />
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
                  Save Connector
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
