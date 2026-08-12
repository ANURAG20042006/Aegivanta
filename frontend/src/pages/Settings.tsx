import React, { useState } from 'react';
import { Save, Palette, Check, CheckCircle2 } from 'lucide-react';
import { useTheme } from '../hooks/useTheme';

const SETTINGS_STORAGE_KEY = 'sentinel_user_preferences';

interface StoredPreferences {
  anomalyThreshold: number;
  activeModel: string;
  autoExportPDF: boolean;
}

const defaultPreferences: StoredPreferences = {
  anomalyThreshold: 0.85,
  activeModel: 'Random Forest',
  autoExportPDF: true,
};

const loadPreferences = (): StoredPreferences => {
  try {
    const stored = localStorage.getItem(SETTINGS_STORAGE_KEY);
    if (!stored) return defaultPreferences;
    const parsed = JSON.parse(stored) as Partial<StoredPreferences>;
    return {
      anomalyThreshold: typeof parsed.anomalyThreshold === 'number' ? parsed.anomalyThreshold : defaultPreferences.anomalyThreshold,
      activeModel: typeof parsed.activeModel === 'string' ? parsed.activeModel : defaultPreferences.activeModel,
      autoExportPDF: typeof parsed.autoExportPDF === 'boolean' ? parsed.autoExportPDF : defaultPreferences.autoExportPDF,
    };
  } catch {
    return defaultPreferences;
  }
};

export const SettingsPage: React.FC = () => {
  const [preferences] = useState<StoredPreferences>(loadPreferences);
  const [anomalyThreshold, setAnomalyThreshold] = useState<number>(preferences.anomalyThreshold);
  const [activeModel, setActiveModel] = useState<string>(preferences.activeModel);
  const [autoExportPDF, setAutoExportPDF] = useState<boolean>(preferences.autoExportPDF);
  const [saveStatus, setSaveStatus] = useState('');
  const { theme, setTheme, options } = useTheme();

  const handleSave = () => {
    const nextPreferences = { anomalyThreshold, activeModel, autoExportPDF };
    localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(nextPreferences));
    localStorage.setItem('sentinel_default_model', activeModel);
    setSaveStatus('Your preferences were saved for this browser.');
  };

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl">
        <h1 className="text-xl font-mono font-bold text-white">Settings</h1>
        <p className="text-xs text-slate-400 font-mono mt-1">Adjust how SentinelAI looks, detects risk, and prepares reports.</p>
      </div>

      <div className="glass-panel p-6 rounded-xl space-y-6 max-w-2xl font-mono text-xs">
        <div className="theme-settings-card space-y-3 pb-5 border-b border-slate-800">
          <div className="flex items-center gap-2 text-slate-300 font-bold">
            <Palette className="w-4 h-4 text-cyan-400" />
            <span>Choose your look</span>
          </div>
          <p className="text-[10px] text-slate-500">Changes apply instantly across every panel and are synced to this browser.</p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            {options.map((option) => (
              <button
                key={option.id}
                type="button"
                onClick={() => setTheme(option.id)}
                className={`theme-tile ${theme === option.id ? 'is-active' : ''}`}
              >
                <span className="flex items-center justify-between">
                  <span className="flex items-center gap-2"><span className="theme-swatch" style={{ backgroundColor: option.accent }} />{option.label}</span>
                  {theme === option.id && <Check className="w-3.5 h-3.5" />}
                </span>
                <span className="block mt-1 text-[9px] opacity-60 text-left">{option.description}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-slate-300 font-bold block">Alert sensitivity ({anomalyThreshold * 100}%)</label>
          <input
            type="range"
            min="0.50"
            max="0.99"
            step="0.01"
            value={anomalyThreshold}
            onChange={(e) => setAnomalyThreshold(parseFloat(e.target.value))}
            className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
          />
          <p className="text-[10px] text-slate-500">Saved as your preferred alert threshold for this browser.</p>
        </div>

        <div className="space-y-2 pt-4 border-t border-slate-800">
          <label className="text-slate-300 font-bold block">Default detection model</label>
          <select
            value={activeModel}
            onChange={(e) => setActiveModel(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 text-cyan-400 px-3 py-2 rounded-lg"
          >
            <option value="XGBoost">XGBoost (Boosting Champion)</option>
            <option value="Random Forest">Random Forest (Ensemble)</option>
            <option value="LightGBM">LightGBM (Boosting)</option>
            <option value="CatBoost">CatBoost (Boosting)</option>
            <option value="1D-CNN">1D-CNN (Deep Spatial Net)</option>
            <option value="LSTM">LSTM (Sequence Net)</option>
          </select>
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-slate-800">
          <div>
            <div className="text-slate-300 font-bold">Daily report</div>
            <div className="text-[10px] text-slate-500">Save your preference for daily summary reports</div>
          </div>
          <input
            type="checkbox"
            checked={autoExportPDF}
            onChange={(e) => setAutoExportPDF(e.target.checked)}
            className="w-4 h-4 accent-cyan-400 cursor-pointer"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleSave}
            className="px-6 py-2.5 bg-cyan-500 text-slate-950 font-bold rounded-lg flex items-center space-x-2 shadow-[0_0_15px_rgba(0,240,255,0.2)]"
          >
            <Save className="w-4 h-4" />
            <span>Save settings</span>
          </button>
          {saveStatus && <span className="flex items-center gap-1.5 text-[10px] text-emerald-400"><CheckCircle2 className="w-3.5 h-3.5" />{saveStatus}</span>}
        </div>
      </div>
    </div>
  );
};
