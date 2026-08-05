import React from 'react';
import { Cpu, Database, CheckCircle2 } from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl">
        <h1 className="text-xl font-mono font-bold text-white">About SentinelAI</h1>
        <p className="text-xs text-slate-400 font-mono mt-1">Learn how SentinelAI checks network traffic and turns it into clear, useful alerts.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-xl space-y-4 font-mono text-xs">
          <h2 className="text-sm font-bold text-cyan-400 flex items-center space-x-2">
            <Cpu className="w-4 h-4" />
            <span>How detection works</span>
          </h2>
          <ul className="space-y-2 text-slate-300">
            <li className="flex items-center space-x-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /><span>Multiple models review each traffic pattern</span></li>
            <li className="flex items-center space-x-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /><span>The active model is shown on your dashboard</span></li>
            <li className="flex items-center space-x-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /><span>Results include a confidence score and priority</span></li>
            <li className="flex items-center space-x-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /><span>Important traffic signals are explained after each check</span></li>
            <li className="flex items-center space-x-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /><span>New or unusual behavior can be surfaced as an alert</span></li>
          </ul>
        </div>

        <div className="glass-panel p-6 rounded-xl space-y-4 font-mono text-xs">
          <h2 className="text-sm font-bold text-cyan-400 flex items-center space-x-2">
            <Database className="w-4 h-4" />
            <span>Traffic data we understand</span>
          </h2>
          <ul className="space-y-2 text-slate-300">
            <li className="flex items-center space-x-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /><span>Built around the public CICIDS2017 benchmark</span></li>
            <li className="flex items-center space-x-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /><span>Reads up to 78 traffic measurements per flow</span></li>
            <li className="flex items-center space-x-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /><span>Recognizes common network attack categories</span></li>
            <li className="flex items-center space-x-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /><span>Cleans and prepares incoming data automatically</span></li>
            <li className="flex items-center space-x-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /><span>Shows which signals influenced each decision</span></li>
          </ul>
        </div>
      </div>
    </div>
  );
};
