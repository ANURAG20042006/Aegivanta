import React, { useState, useEffect } from 'react';
import { 
  Crosshair, 
  RefreshCw,
  Globe
} from 'lucide-react';
import { dashboardService, ThreatIntelDashboardData } from '../../services/dashboard';

export const ThreatIntelPanel: React.FC = () => {
  const [intelData, setIntelData] = useState<ThreatIntelDashboardData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchIntelData = async () => {
    setIsLoading(true);
    try {
      const data = await dashboardService.getThreatIntel();
      setIntelData(data);
    } catch (err) {
      console.error('Failed to load threat intel dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchIntelData();
  }, []);

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-2xl backdrop-blur-md space-y-4 font-mono">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-purple-500/10 border border-purple-500/30 rounded-xl text-purple-400">
            <Crosshair className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              Threat Intelligence & Fast IOC Cache
            </h3>
            <p className="text-xs text-slate-400">
              Normalized IOC indicators, pluggable feed health, & zero-DB memory lookups
            </p>
          </div>
        </div>

        <button
          onClick={fetchIntelData}
          className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl w-fit"
          title="Refresh Threat Intel"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
          <span className="text-[10px] text-slate-500 block">ACTIVE INDICATORS</span>
          <span className="text-base font-bold text-cyan-400">
            {intelData?.active_indicators_count ?? 0}
          </span>
        </div>
        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
          <span className="text-[10px] text-slate-500 block">CACHE HIT RATIO</span>
          <span className="text-base font-bold text-emerald-400">
            {((intelData?.cache_stats?.hit_ratio ?? 0) * 100).toFixed(1)}%
          </span>
        </div>
        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
          <span className="text-[10px] text-slate-500 block">TOTAL LOOKUPS / HITS</span>
          <span className="text-base font-bold text-purple-400">
            {intelData?.cache_stats?.total_lookups ?? 0} / {intelData?.cache_stats?.total_hits ?? 0}
          </span>
        </div>
        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
          <span className="text-[10px] text-slate-500 block">THREAT FEEDS</span>
          <span className="text-base font-bold text-slate-200">
            {intelData?.active_feeds ?? 0} Active / {intelData?.total_feeds ?? 0} Total
          </span>
        </div>
      </div>

      {/* Feeds Health List */}
      <div>
        <h4 className="text-xs font-bold text-slate-300 mb-2">Threat Intelligence Feeds</h4>
        {isLoading ? (
          <div className="py-6 text-center text-slate-500 text-xs flex items-center justify-center">
            <RefreshCw className="w-4 h-4 animate-spin mr-2" />
            SYNCHRONIZING THREAT FEEDS...
          </div>
        ) : !intelData || intelData.feeds.length === 0 ? (
          <div className="py-6 text-center text-slate-500 text-xs">
            NO EXTERNAL THREAT FEEDS REGISTERED
          </div>
        ) : (
          <div className="space-y-2 max-h-[160px] overflow-y-auto pr-1">
            {intelData.feeds.map((feed) => (
              <div
                key={feed.id}
                className="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-between"
              >
                <div className="flex items-center space-x-2.5">
                  <Globe className="w-4 h-4 text-cyan-400" />
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-slate-200 text-xs">{feed.feed_name}</span>
                      <span className="text-[10px] text-slate-500">({feed.provider_type})</span>
                    </div>
                    <div className="text-[10px] text-slate-400">
                      {feed.last_synced_at ? `Last Synced: ${new Date(feed.last_synced_at).toLocaleTimeString()}` : 'Never Synced'}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                    feed.status === 'HEALTHY'
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      : 'bg-red-500/10 text-red-400 border-red-500/30'
                  }`}>
                    {feed.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
