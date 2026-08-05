import React from 'react';
import { Globe, ShieldAlert } from 'lucide-react';

interface CountryThreat {
  code: string;
  country: string;
  count: number;
  flag: string;
  percentage: number;
  status: 'critical' | 'high' | 'medium';
}

export const GlobalAttackMap: React.FC = () => {
  const topCountries: CountryThreat[] = [
    { code: 'US', country: 'United States', count: 642, flag: '🇺🇸', percentage: 34.8, status: 'critical' },
    { code: 'RU', country: 'Russian Federation', count: 480, flag: '🇷🇺', percentage: 26.0, status: 'critical' },
    { code: 'CN', country: 'China', count: 320, flag: '🇨🇳', percentage: 17.3, status: 'high' },
    { code: 'DE', country: 'Germany', count: 185, flag: '🇩🇪', percentage: 10.0, status: 'medium' },
    { code: 'BR', country: 'Brazil', count: 125, flag: '🇧🇷', percentage: 6.8, status: 'medium' },
  ];

  return (
    <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-md space-y-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/30 rounded-xl text-cyan-400">
            <Globe className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-mono">
              Global Threat Origin Matrix
            </h3>
            <p className="text-xs text-slate-400">Geolocation breakdown of external malicious packet sources</p>
          </div>
        </div>

        <div className="flex items-center space-x-2 text-xs font-mono text-cyan-400">
          <ShieldAlert className="w-4 h-4 text-red-400" />
          <span className="text-slate-300">Active Geoblocks:</span>
          <span className="font-bold text-red-400 bg-red-500/10 px-2 py-0.5 rounded border border-red-500/20">5 Regions</span>
        </div>
      </div>

      <div className="space-y-3">
        {topCountries.map((c) => (
          <div
            key={c.code}
            className="p-3.5 bg-slate-950/60 border border-slate-800/80 rounded-xl flex items-center justify-between hover:border-slate-700 transition-all"
          >
            <div className="flex items-center space-x-3">
              <span className="text-xl">{c.flag}</span>
              <div>
                <div className="text-xs font-bold text-slate-200">{c.country}</div>
                <div className="text-[10px] text-slate-500 font-mono">ISO: {c.code} · Threat Score: {c.status.toUpperCase()}</div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="w-28 bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-800 hidden sm:block">
                <div
                  className={`h-full rounded-full ${
                    c.status === 'critical'
                      ? 'bg-red-500 shadow-sm shadow-red-500'
                      : c.status === 'high'
                      ? 'bg-amber-500'
                      : 'bg-cyan-500'
                  }`}
                  style={{ width: `${c.percentage}%` }}
                />
              </div>
              <div className="text-right font-mono">
                <div className="text-xs font-bold text-slate-100">{c.count} flows</div>
                <div className="text-[10px] text-cyan-400">{c.percentage}% total</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
