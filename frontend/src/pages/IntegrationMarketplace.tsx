import React, { useEffect, useState } from 'react';
import {
  Plug,
  Activity,
  CheckCircle2,
  AlertTriangle,
  Package,
  Webhook,
  RefreshCw,
  XCircle,
  BarChart3,
  Shield
} from 'lucide-react';
import { saasApi } from '../services/saas';

export const IntegrationMarketplace: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'marketplace' | 'connectors' | 'health' | 'webhooks'>('marketplace');
  const [catalog, setCatalog] = useState<any[]>([]);
  const [connectors, setConnectors] = useState<any[]>([]);
  const [deliveries, setDeliveries] = useState<any[]>([]);
  const [healthDashboard, setHealthDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchAll(); }, []);

  const fetchAll = async () => {
    try {
      setLoading(true);
      const [cat, conn, del, health] = await Promise.all([
        saasApi.getIntegrationCatalog(),
        saasApi.getConnectors(),
        saasApi.getWebhookDeliveries(),
        saasApi.getIntegrationHealthDashboard()
      ]);
      setCatalog(cat);
      setConnectors(conn);
      setDeliveries(del);
      setHealthDashboard(health);
    } catch (err) {
      console.error('Failed loading integration data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'ENABLED': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      case 'ERROR': case 'RATE_LIMITED': return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
      case 'DISABLED': return 'text-slate-400 bg-slate-500/10 border-slate-500/20';
      default: return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
    }
  };

  const getConnectorTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      SIEM: '📊', SOAR: '⚡', EDR: '🛡️', IAM: '🔑',
      TICKETING: '🎫', MESSAGING: '💬', EMAIL: '📧',
      WEBHOOK: '🔗', THREAT_INTEL: '🕵️', CLOUD: '☁️'
    };
    return icons[type] || '🔌';
  };

  const typeGroups = catalog.reduce((acc, item) => {
    if (!acc[item.connector_type]) acc[item.connector_type] = [];
    acc[item.connector_type].push(item);
    return acc;
  }, {} as Record<string, any[]>);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <Plug className="h-7 w-7 text-indigo-400" />
          Enterprise Integration Marketplace
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Production-grade security ecosystem connectors with HMAC-signed webhooks, exponential backoff, and dead-letter handling.
        </p>
      </div>

      {/* Stats Summary */}
      {healthDashboard && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: 'Total Connectors', value: healthDashboard.total_connectors, color: 'text-slate-100' },
            { label: 'Healthy', value: healthDashboard.healthy_connectors, color: 'text-emerald-400' },
            { label: 'Delivery Success', value: `${healthDashboard.delivery_success_rate}%`, color: 'text-cyan-400' },
            { label: 'Dead Letters', value: healthDashboard.dead_letter_count, color: 'text-rose-400' }
          ].map(s => (
            <div key={s.label} className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
              <div className="text-xs text-slate-400">{s.label}</div>
              <div className={`text-2xl font-bold mt-1 ${s.color}`}>{s.value}</div>
            </div>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-2 overflow-x-auto">
        {[
          { id: 'marketplace', label: 'Integration Catalog', icon: Package },
          { id: 'connectors', label: 'Connector Manager', icon: Plug },
          { id: 'health', label: 'Health Dashboard', icon: BarChart3 },
          { id: 'webhooks', label: 'Webhook Delivery', icon: Webhook }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'border-indigo-500 text-indigo-300'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Icon className="h-4 w-4" />{tab.label}
            </button>
          );
        })}
      </div>

      {loading ? (
        <div className="h-48 flex items-center justify-center text-slate-400">
          <Activity className="h-6 w-6 animate-spin text-indigo-400 mr-3" />
          Loading integration ecosystem data...
        </div>
      ) : (
        <>
          {/* Tab: Integration Catalog */}
          {activeTab === 'marketplace' && (
            <div className="space-y-6">
              {Object.entries(typeGroups).map(([type, items]) => (
                <div key={type}>
                  <h3 className="text-sm font-bold text-slate-300 mb-3 flex items-center gap-2">
                    <span className="text-xl">{getConnectorTypeIcon(type)}</span>
                    {type} Connectors
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {(items as any[]).map((item: any, idx: number) => (
                      <div key={idx} className="p-4 bg-slate-900/60 border border-slate-800/80 rounded-xl hover:border-indigo-700/50 transition-colors">
                        <div className="flex items-center justify-between gap-2">
                          <div className="font-semibold text-sm text-slate-100">{item.vendor}</div>
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">v{item.version}</span>
                        </div>
                        <div className="text-[11px] text-slate-400 mt-1">{item.description}</div>
                        <div className="flex items-center gap-2 mt-2">
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-950/60 text-indigo-400 border border-indigo-800/40">{item.auth_type}</span>
                          <button className="text-[10px] px-2 py-0.5 bg-indigo-600/30 hover:bg-indigo-600/60 text-indigo-300 rounded transition-colors">
                            Install
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Tab: Connector Manager */}
          {activeTab === 'connectors' && (
            <div className="space-y-3">
              {connectors.map((c) => (
                <div key={c.id} className="p-4 bg-slate-900/60 border border-slate-800/80 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{getConnectorTypeIcon(c.connector_type)}</span>
                      <span className="font-bold text-sm text-slate-100">{c.name}</span>
                      <span className="text-[10px] text-slate-400">{c.vendor}</span>
                    </div>
                    <div className="text-xs text-slate-400 mt-1 flex items-center gap-4">
                      <span>Auth: <strong className="text-slate-300">{c.auth_type}</strong></span>
                      <span>Rate Limit: <strong className="text-slate-300">{c.rate_limit_per_minute} req/min</strong></span>
                      <span>Retries: <strong className="text-slate-300">{c.retry_max_attempts}</strong></span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div className="text-xs text-slate-400">Health</div>
                      <div className={`text-sm font-bold ${c.health_score >= 80 ? 'text-emerald-400' : 'text-amber-400'}`}>{c.health_score}%</div>
                    </div>
                    <span className={`px-2 py-1 rounded text-[10px] font-bold border ${getStatusColor(c.status)}`}>
                      {c.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Tab: Health Dashboard */}
          {activeTab === 'health' && healthDashboard && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-3">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Shield className="h-4 w-4 text-indigo-400" /> Connector Health Matrix
                </h3>
                {connectors.map((c) => (
                  <div key={c.id} className="flex items-center justify-between py-1 border-b border-slate-800/50">
                    <div className="text-xs text-slate-300">{c.name}</div>
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${c.health_score >= 80 ? 'bg-emerald-500' : c.health_score >= 50 ? 'bg-amber-500' : 'bg-rose-500'}`}
                          style={{ width: `${c.health_score}%` }}
                        />
                      </div>
                      <span className="text-xs text-slate-400 w-8 text-right">{c.health_score}%</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-3">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-amber-400" /> Dead-Letter Queue
                </h3>
                {healthDashboard.recent_dead_letters.length === 0 ? (
                  <div className="text-xs text-emerald-400 flex items-center gap-2 py-4">
                    <CheckCircle2 className="h-4 w-4" /> No dead-letter events — all deliveries successful.
                  </div>
                ) : (
                  healthDashboard.recent_dead_letters.map((dl: any) => (
                    <div key={dl.id} className="p-2.5 bg-rose-950/30 rounded-lg border border-rose-800/30 text-xs">
                      <div className="font-bold text-rose-300">{dl.event_id}</div>
                      <div className="text-slate-400 mt-0.5">Connector: {dl.connector_id} | Attempts: {dl.attempt_count}</div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Tab: Webhook Delivery Status */}
          {activeTab === 'webhooks' && (
            <div className="space-y-2">
              {deliveries.map((d) => (
                <div key={d.id} className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                  <div>
                    <div className="flex items-center gap-2">
                      {d.status === 'DELIVERED'
                        ? <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                        : d.is_dead_letter
                        ? <XCircle className="h-4 w-4 text-rose-400" />
                        : <RefreshCw className="h-4 w-4 text-amber-400" />
                      }
                      <span className="font-bold text-slate-200">{d.event_id}</span>
                      <span className="text-slate-400 font-mono">{d.connector_id}</span>
                    </div>
                    <div className="text-[11px] text-slate-400 mt-0.5">
                      Attempts: {d.attempt_count} | HTTP: {d.http_status_code}
                      {d.next_retry_at && ` | Next retry: ${new Date(d.next_retry_at).toLocaleTimeString()}`}
                    </div>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold border shrink-0 ${
                    d.status === 'DELIVERED' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                    : d.is_dead_letter ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                    : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                  }`}>{d.status}</span>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
};
