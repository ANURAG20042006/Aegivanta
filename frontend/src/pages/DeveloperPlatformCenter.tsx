import React, { useEffect, useState } from 'react';
import {
  Code,
  Activity,
  ChevronRight,
  Zap,
  Key,
  Radio,
  Sliders,
  Send,
  Copy,
  Check
} from 'lucide-react';
import { saasApi } from '../services/saas';

export const DeveloperPlatformCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'api_keys' | 'webhooks' | 'deliveries' | 'openapi_explorer' | 'developer_studio'>('overview');
  const [summary, setSummary] = useState<any>(null);
  const [apiKeys, setApiKeys] = useState<any[]>([]);
  const [webhooks, setWebhooks] = useState<any[]>([]);
  const [deliveries, setDeliveries] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Key creation state
  const [keyName, setKeyName] = useState<string>('Custom SOAR Pipeline Integration Key');
  const [scopes, setScopes] = useState<string>('telemetry:read,alerts:write,soar:execute');
  const [rateLimitRpm, setRateLimitRpm] = useState<number>(2000);
  const [createdKey, setCreatedKey] = useState<any>(null);
  const [copiedKey, setCopiedKey] = useState<boolean>(false);

  // Webhook subscription state
  const [endpointUrl, setEndpointUrl] = useState<string>('https://webhook.site/test-endpoint');
  const [subscribedEvents, setSubscribedEvents] = useState<string>('alert.created,threat.blocked');
  const [createdSub, setCreatedSub] = useState<any>(null);

  // Test dispatch state
  const [testUrl, setTestUrl] = useState<string>('https://webhook.site/test-endpoint');
  const [testEvent, setTestEvent] = useState<string>('alert.created');
  const [testResult, setTestResult] = useState<any>(null);

  useEffect(() => {
    fetchDeveloperData();
  }, []);

  const fetchDeveloperData = async () => {
    try {
      setLoading(true);
      const [sum, keys, subs, dels] = await Promise.all([
        saasApi.getDeveloperSummary(),
        saasApi.getDeveloperApiKeys(),
        saasApi.getWebhookSubscriptions(),
        saasApi.getDeveloperWebhookDeliveries()
      ]);
      setSummary(sum);
      setApiKeys(keys);
      setWebhooks(subs);
      setDeliveries(dels);
    } catch (err) {
      console.error('Failed to load Developer Platform data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateKey = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await saasApi.createDeveloperApiKey({
        key_name: keyName,
        scopes: scopes,
        rate_limit_rpm: Number(rateLimitRpm)
      });
      setCreatedKey(res);
      fetchDeveloperData();
    } catch (err) {
      console.error('Failed to create API key:', err);
    }
  };

  const handleCreateWebhook = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await saasApi.createWebhookSubscription({
        endpoint_url: endpointUrl,
        subscribed_events: subscribedEvents
      });
      setCreatedSub(res);
      fetchDeveloperData();
    } catch (err) {
      console.error('Failed to create webhook:', err);
    }
  };

  const handleTestDispatch = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await saasApi.testDispatchWebhook({
        endpoint_url: testUrl,
        event_type: testEvent
      });
      setTestResult(res);
      fetchDeveloperData();
    } catch (err) {
      console.error('Failed to test dispatch webhook:', err);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(true);
    setTimeout(() => setCopiedKey(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Code className="h-7 w-7 text-emerald-400" />
            Developer Platform & High-Throughput Webhooks Engine
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Programmatic Scoped REST APIs, HMAC-SHA256 Signed Webhook Dispatches, and OpenAPI 3.1 Integration Studio.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('developer_studio')}
            className="flex items-center gap-2 px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold transition-colors"
          >
            <Key className="h-4 w-4" /> API & Webhooks Studio
          </button>
        </div>
      </div>

      {/* Top Metrics Ribbon */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Developer Score</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.overall_developer_score}<span className="text-xs text-slate-500">/100</span></div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Enterprise Ready</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Active API Keys</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{summary.active_api_keys_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Scoped RBAC</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Webhooks Subscribed</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{summary.active_webhook_subscriptions_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Real-Time Streams</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Dispatched Events</div>
            <div className="text-2xl font-bold text-slate-200 mt-1">{summary.total_dispatched_deliveries_count}</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">{(summary.delivery_success_rate * 100).toFixed(2)}% Success</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Mean Latency</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.mean_webhook_latency_ms} <span className="text-xs text-slate-500">ms</span></div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Sub-50ms Tier</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">OpenAPI Version</div>
            <div className="text-2xl font-bold text-amber-400 mt-1">3.1.0</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Type-Safe Schema</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'Platform Overview', icon: Code },
          { id: 'api_keys', label: 'Scoped API Keys', icon: Key },
          { id: 'webhooks', label: 'Webhook Subscriptions', icon: Radio },
          { id: 'deliveries', label: 'Delivery Logs & DLQ', icon: Activity },
          { id: 'openapi_explorer', label: 'OpenAPI 3.1 & SDKs', icon: Zap },
          { id: 'developer_studio', label: 'Key & Dispatch Studio', icon: Sliders }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'border-emerald-500 text-emerald-300'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Icon className="h-4 w-4" />{tab.label}
            </button>
          );
        })}
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Activity className="h-6 w-6 animate-spin text-emerald-400 mr-3" />
          Synchronizing Developer API Keys, Webhook Subscriptions & Deliveries...
        </div>
      ) : (
        <>
          {/* TAB 1: Overview */}
          {activeTab === 'overview' && summary && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* API Keys Overview */}
              <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Key className="h-4 w-4 text-emerald-400" /> Active Scoped API Keys
                </h3>
                <div className="space-y-3">
                  {apiKeys.map((k) => (
                    <div key={k.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                      <div className="flex justify-between items-center font-bold">
                        <span className="text-slate-100">{k.key_name}</span>
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold border border-emerald-500/30">
                          ACTIVE
                        </span>
                      </div>
                      <div className="text-[11px] text-cyan-300">Prefix: <span className="font-mono">{k.key_prefix}••••••••••••</span></div>
                      <div className="flex justify-between items-center text-[10px] text-slate-400 pt-1 border-t border-slate-800/60">
                        <span>Scopes: <strong className="font-mono text-slate-300">{k.scopes}</strong></span>
                        <span>Rate Limit: <strong className="text-emerald-400">{k.rate_limit_rpm} RPM</strong></span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-3 border-t border-slate-800/60">
                  <div className="text-xs font-bold text-slate-300 mb-2">Priority Developer Directives:</div>
                  <div className="space-y-1.5">
                    {summary.top_developer_priorities.map((pri: string, idx: number) => (
                      <div key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                        <ChevronRight className="h-3.5 w-3.5 text-emerald-400 shrink-0 mt-0.5" />
                        {pri}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Webhooks Overview */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Radio className="h-4 w-4 text-emerald-400" /> Active Webhook Subscriptions
                </h3>
                <div className="space-y-3">
                  {webhooks.map((sub) => (
                    <div key={sub.id} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60 text-xs space-y-1.5">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span className="truncate max-w-[200px] font-mono text-[11px]">{sub.endpoint_url}</span>
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold">STREAMING</span>
                      </div>
                      <div className="text-[10px] text-slate-400">Events: <strong className="text-cyan-300">{sub.subscribed_events}</strong></div>
                      <div className="text-[10px] text-slate-500">Max Retries: {sub.retry_count_max} (Exponential Backoff + DLQ)</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: API Keys */}
          {activeTab === 'api_keys' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Key className="h-4 w-4 text-emerald-400" /> Scoped Developer API Keys
                </h3>
                <button
                  onClick={() => setActiveTab('developer_studio')}
                  className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold"
                >
                  + Generate API Key
                </button>
              </div>

              <div className="space-y-3">
                {apiKeys.map((key) => (
                  <div key={key.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <span className="text-slate-100 text-sm">{key.key_name}</span>
                      <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold text-[10px]">
                        ACTIVE
                      </span>
                    </div>

                    <div className="p-2 bg-slate-900 rounded font-mono text-[11px] text-emerald-300">
                      Prefix: {key.key_prefix}••••••••••••••••••••••••
                    </div>

                    <div className="flex justify-between items-center text-[11px] text-slate-400 pt-1 border-t border-slate-800/60">
                      <span>Scopes: <strong className="font-mono text-cyan-300">{key.scopes}</strong></span>
                      <span>Rate Limit: <strong className="text-slate-200">{key.rate_limit_rpm} RPM</strong></span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: Webhooks */}
          {activeTab === 'webhooks' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Radio className="h-4 w-4 text-emerald-400" /> Webhook Subscriptions & HMAC Signing
              </h3>

              <form onSubmit={handleCreateWebhook} className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3">
                <div className="text-xs font-bold text-slate-200">Register New Webhook Endpoint</div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] text-slate-400 mb-1">Receiver HTTPS Endpoint URL</label>
                    <input
                      type="url"
                      value={endpointUrl}
                      onChange={(e) => setEndpointUrl(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-slate-200 text-xs font-mono"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] text-slate-400 mb-1">Subscribed Events (Comma-Separated)</label>
                    <input
                      type="text"
                      value={subscribedEvents}
                      onChange={(e) => setSubscribedEvents(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-slate-200 text-xs font-mono"
                      required
                    />
                  </div>
                </div>
                <div className="flex justify-end">
                  <button
                    type="submit"
                    className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5"
                  >
                    <Radio className="h-3.5 w-3.5" /> Save Subscription
                  </button>
                </div>
              </form>

              {createdSub && (
                <div className="p-4 bg-slate-950 rounded-xl border border-emerald-500/30 text-xs space-y-2">
                  <div className="flex justify-between items-center text-emerald-400 font-bold">
                    <span>Webhook Registered</span>
                    <span>Active</span>
                  </div>
                  <div className="p-2 bg-slate-900 rounded font-mono text-[10px] text-cyan-300 break-all">
                    Secret Signing Token: {createdSub.secret_token}
                  </div>
                </div>
              )}

              <div className="space-y-3">
                {webhooks.map((sub) => (
                  <div key={sub.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <span className="font-mono text-cyan-300">{sub.endpoint_url}</span>
                      <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold text-[10px]">
                        HMAC_SHA256_ACTIVE
                      </span>
                    </div>

                    <div className="text-[11px] text-slate-400">
                      Subscribed Events: <strong className="text-slate-200">{sub.subscribed_events}</strong>
                    </div>

                    <div className="flex justify-between items-center text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">
                      <span>Max Retry Attempts: {sub.retry_count_max}</span>
                      <span>Created: {new Date(sub.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: Delivery Logs & DLQ */}
          {activeTab === 'deliveries' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Activity className="h-4 w-4 text-emerald-400" /> Real-Time Webhook Delivery Logs & DLQ
              </h3>

              <div className="space-y-3">
                {deliveries.map((del) => (
                  <div key={del.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-cyan-300">{del.event_type}</span>
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[10px]">HTTP {del.response_status}</span>
                      </div>
                      <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold text-[10px]">
                        {del.status}
                      </span>
                    </div>

                    <pre className="p-3 bg-slate-900 rounded font-mono text-[10px] text-slate-300 overflow-x-auto">
                      {JSON.stringify(del.payload_json, null, 2)}
                    </pre>

                    <div className="flex justify-between items-center text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">
                      <span>Latency: <strong className="text-emerald-400">{del.duration_ms} ms</strong></span>
                      <span>Sent: {new Date(del.sent_at).toLocaleString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: OpenAPI Explorer */}
          {activeTab === 'openapi_explorer' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 max-w-2xl mx-auto space-y-4 text-xs">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Zap className="h-5 w-5 text-emerald-400" /> OpenAPI 3.1 Interactive SDK Code Snippets
              </h3>
              <p className="text-slate-400 leading-relaxed">
                Connect programmatically to Aegivanta using standard HTTP clients or generated Python/TypeScript SDKs.
              </p>
              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2 font-mono text-[11px] text-emerald-300 overflow-x-auto">
                <div>curl -X GET "https://api.aegivanta.io/api/v1/alerts" \</div>
                <div>&nbsp;&nbsp;-H "Authorization: Bearer aeg_live_abc123..." \</div>
                <div>&nbsp;&nbsp;-H "Accept: application/json"</div>
              </div>
              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2 font-mono text-[11px] text-cyan-300 overflow-x-auto">
                <div>// Node.js / TypeScript SDK Example</div>
                <div>import &#123; AegivantaClient &#125; from '@aegivanta/sdk';</div>
                <div>const client = new AegivantaClient(&#123; apiKey: process.env.AEGIVANTA_API_KEY &#125;);</div>
                <div>const alerts = await client.alerts.list(&#123; severity: 'CRITICAL' &#125;);</div>
              </div>
            </div>
          )}

          {/* TAB 6: Developer Studio */}
          {activeTab === 'developer_studio' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Generate API Key Form */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 space-y-4">
                <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                  <Key className="h-5 w-5 text-emerald-400" /> Generate Scoped API Key
                </h3>
                <p className="text-xs text-slate-400">
                  Create a new API key with granular permissions and rate limits.
                </p>

                <form onSubmit={handleCreateKey} className="space-y-3 text-xs">
                  <div>
                    <label className="block text-slate-400 mb-1">Key Name / Description</label>
                    <input
                      type="text"
                      value={keyName}
                      onChange={(e) => setKeyName(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1">RBAC Scopes (Comma-Separated)</label>
                    <input
                      type="text"
                      value={scopes}
                      onChange={(e) => setScopes(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200 font-mono text-[11px]"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1">Rate Limit (Requests per Minute)</label>
                    <input
                      type="number"
                      value={rateLimitRpm}
                      onChange={(e) => setRateLimitRpm(Number(e.target.value))}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                      required
                    />
                  </div>
                  <div className="flex justify-end pt-2">
                    <button
                      type="submit"
                      className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-semibold flex items-center gap-2"
                    >
                      <Key className="h-4 w-4" /> Generate Token
                    </button>
                  </div>
                </form>

                {createdKey && (
                  <div className="p-4 bg-slate-950 rounded-xl border border-emerald-500/30 text-xs space-y-2 mt-4">
                    <div className="flex justify-between items-center text-emerald-400 font-bold">
                      <span>API Key Generated (Copy Now)</span>
                      <span>{createdKey.rate_limit_rpm} RPM</span>
                    </div>
                    <div className="p-2 bg-slate-900 rounded font-mono text-[11px] text-cyan-300 break-all flex items-center justify-between">
                      <span>{createdKey.raw_api_key}</span>
                      <button
                        onClick={() => copyToClipboard(createdKey.raw_api_key)}
                        className="ml-2 p-1 text-slate-400 hover:text-white"
                      >
                        {copiedKey ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4 text-slate-400" />}
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Webhook Subscription & Test Dispatch Form */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 space-y-4">
                <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                  <Send className="h-5 w-5 text-emerald-400" /> Webhook Test Dispatcher
                </h3>
                <p className="text-xs text-slate-400">
                  Simulate a signed webhook event to verify your receiver endpoint.
                </p>

                <form onSubmit={handleTestDispatch} className="space-y-3 text-xs">
                  <div>
                    <label className="block text-slate-400 mb-1">Target Endpoint URL</label>
                    <input
                      type="url"
                      value={testUrl}
                      onChange={(e) => setTestUrl(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200 font-mono text-[11px]"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1">Event Type</label>
                    <select
                      value={testEvent}
                      onChange={(e) => setTestEvent(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                    >
                      <option value="alert.created">alert.created (Security Alert Triggered)</option>
                      <option value="threat.blocked">threat.blocked (Edge IP BGP Blocked)</option>
                      <option value="policy.violated">policy.violated (ZTNA Microsegment Violation)</option>
                    </select>
                  </div>
                  <div className="flex justify-end pt-2">
                    <button
                      type="submit"
                      className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-semibold flex items-center gap-2"
                    >
                      <Send className="h-4 w-4" /> Dispatch Test Event
                    </button>
                  </div>
                </form>

                {testResult && (
                  <div className="p-4 bg-slate-950 rounded-xl border border-emerald-500/30 text-xs space-y-2 mt-4">
                    <div className="flex justify-between items-center text-emerald-400 font-bold">
                      <span>Event Dispatched (HTTP {testResult.response_status})</span>
                      <span>{testResult.duration_ms} ms</span>
                    </div>
                    <div className="p-2 bg-slate-900 rounded font-mono text-[10px] text-cyan-300 break-all">
                      X-Aegivanta-Signature: {testResult.hmac_signature_header}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
