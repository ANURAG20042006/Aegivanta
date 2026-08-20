import React, { useState, useEffect } from 'react';
import { saasApi, SubscriptionInfo } from '../services/saas';

export const BillingPage: React.FC = () => {
  const [sub, setSub] = useState<SubscriptionInfo | null>(null);
  const [usage, setUsage] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [message, setMessage] = useState<{ text: string; isError: boolean } | null>(null);

  const loadBillingData = async () => {
    setLoading(true);
    try {
      const subInfo = await saasApi.getCurrentSubscription();
      setSub(subInfo);
      const usageData = await saasApi.getUsage();
      setUsage(usageData);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBillingData();
  }, []);

  const handleUpgrade = async (tier: string) => {
    try {
      const updated = await saasApi.upgradePlan(tier);
      setSub(updated);
      setMessage({ text: `Successfully switched to plan: ${tier}!`, isError: false });
      loadBillingData();
    } catch (err: any) {
      setMessage({ text: err.response?.data?.detail || 'Upgrade failed', isError: true });
    }
  };

  const TIERS = [
    {
      name: 'FREE',
      price: '$0 / mo',
      seats: '3 Seats',
      telemetry: '5 GB / month',
      features: ['Basic Detection Rules', 'Real-time Alerts', 'SOC Command Center']
    },
    {
      name: 'PROFESSIONAL',
      price: '$499 / mo',
      seats: '10 Seats',
      telemetry: '50 GB / month',
      features: ['Basic Detection', 'Threat Intel IOC Feeds', 'Attack Graph Analytics', 'Investigation Workbenches']
    },
    {
      name: 'BUSINESS',
      price: '$1,499 / mo',
      seats: '25 Seats',
      telemetry: '250 GB / month',
      features: ['Everything in Pro', 'Autonomous SOAR Response', 'Threat Hunting Engine', 'Customer API Keys', 'SIEM & Slack Connectors']
    },
    {
      name: 'ENTERPRISE',
      price: '$4,999 / mo',
      seats: 'Unlimited Seats',
      telemetry: '5 TB / month',
      features: ['Everything in Business', 'Adaptive ML Detection Engine', 'Dedicated Ingestion Workers', 'Custom Data Retention (365d)', 'Enterprise SSO (SAML/OIDC)']
    }
  ];

  return (
    <div className="space-y-6 font-mono">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-xl font-bold text-cyan-400 tracking-wider">SUBSCRIPTION & COMMERCIAL BILLING</h1>
        <p className="text-xs text-gray-400">Plan Quotas, Usage Metering, and Enterprise Entitlements</p>
      </div>

      {message && (
        <div className={`p-3 text-xs rounded border ${message.isError ? 'bg-red-950/40 border-red-500/50 text-red-300' : 'bg-emerald-950/40 border-emerald-500/50 text-emerald-300'}`}>
          {message.text}
        </div>
      )}

      {loading ? (
        <div className="text-cyan-400 text-xs animate-pulse">LOADING SUBSCRIPTION DATA...</div>
      ) : (
        <>
          {/* Active Plan & Metering Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-900/60 border border-gray-800 rounded p-4">
              <div className="text-xs text-gray-400">CURRENT PLAN</div>
              <div className="text-xl font-bold text-cyan-400 mt-1">{sub?.plan_tier || 'FREE'}</div>
              <div className="text-xs text-emerald-400 mt-1">Status: {sub?.status || 'ACTIVE'}</div>
            </div>

            <div className="bg-gray-900/60 border border-gray-800 rounded p-4">
              <div className="text-xs text-gray-400">SEAT ALLOCATION</div>
              <div className="text-xl font-bold text-white mt-1">{sub?.seat_limit || 3} Users</div>
              <div className="text-xs text-gray-400 mt-1">RBAC Controlled</div>
            </div>

            <div className="bg-gray-900/60 border border-gray-800 rounded p-4">
              <div className="text-xs text-gray-400">TELEMETRY QUOTA</div>
              <div className="text-xl font-bold text-white mt-1">{sub?.telemetry_limit_gb_monthly || 5} GB / mo</div>
              <div className="text-xs text-cyan-400 mt-1">
                Used: {usage?.current_usage?.telemetry_events || 0} events
              </div>
            </div>
          </div>

          {/* Pricing Tiers */}
          <div className="space-y-3">
            <h2 className="text-xs font-semibold text-gray-300 uppercase tracking-wider">Available Subscription Tiers</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {TIERS.map((tier) => {
                const isCurrent = sub?.plan_tier === tier.name;
                return (
                  <div
                    key={tier.name}
                    className={`bg-gray-900/60 border rounded p-4 flex flex-col justify-between space-y-4 ${isCurrent ? 'border-cyan-500/80 bg-cyan-950/20' : 'border-gray-800'}`}
                  >
                    <div>
                      <div className="flex justify-between items-center">
                        <h3 className="text-sm font-bold text-white">{tier.name}</h3>
                        {isCurrent && (
                          <span className="px-2 py-0.5 bg-cyan-950 text-cyan-400 text-[10px] rounded border border-cyan-500/40">
                            ACTIVE
                          </span>
                        )}
                      </div>
                      <div className="text-lg font-bold text-cyan-400 mt-2">{tier.price}</div>
                      <div className="text-xs text-gray-400 mt-1">{tier.seats} • {tier.telemetry}</div>

                      <ul className="mt-4 space-y-1.5 text-xs text-gray-300">
                        {tier.features.map((f, i) => (
                          <li key={i} className="flex items-center space-x-1.5">
                            <span className="text-cyan-400">✓</span>
                            <span>{f}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <button
                      disabled={isCurrent}
                      onClick={() => handleUpgrade(tier.name)}
                      className={`w-full py-2 text-xs font-bold rounded transition-colors ${isCurrent ? 'bg-gray-800 text-gray-500 cursor-not-allowed' : 'bg-cyan-600 hover:bg-cyan-500 text-black'}`}
                    >
                      {isCurrent ? 'CURRENT PLAN' : `SWITCH TO ${tier.name}`}
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
};
