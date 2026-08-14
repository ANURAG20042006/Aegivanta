import React, { useState, useEffect } from 'react';
import { TrendingUp, AlertOctagon, Zap, Clock, Info, CheckCircle2 } from 'lucide-react';
import { predictiveService, RiskForecastData, VolumeForecastData } from '../services/predictiveService';
import api from '../services/api';

export const PredictiveAnalytics: React.FC = () => {
  const [assets, setAssets] = useState<any[]>([]);
  const [selectedAssetId, setSelectedAssetId] = useState<string>('');
  const [forecastType, setForecastType] = useState<string>('24H');
  const [assetForecast, setAssetForecast] = useState<RiskForecastData | null>(null);
  const [volumeForecast, setVolumeForecast] = useState<VolumeForecastData | null>(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (selectedAssetId) {
      loadAssetForecast(selectedAssetId, forecastType);
    }
  }, [selectedAssetId, forecastType]);

  const loadInitialData = async () => {
    try {
      const [assetsRes, volRes] = await Promise.all([
        api.get('/assets'),
        predictiveService.getVolumeForecast()
      ]);
      const assetList = Array.isArray(assetsRes.data) ? assetsRes.data : (assetsRes.data?.items || []);
      setAssets(assetList);
      setVolumeForecast(volRes);
      if (assetList.length > 0) {
        setSelectedAssetId(assetList[0].id);
      }
    } catch (err) {
      console.error('Failed to load predictive analytics data', err);
    }
  };

  const loadAssetForecast = async (assetId: string, type: string) => {
    try {
      const fc = await predictiveService.getAssetForecast(assetId, type);
      setAssetForecast(fc);
    } catch (err) {
      console.error('Failed to load asset forecast', err);
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 75) return 'text-red-400 border-red-500/30 bg-red-500/10';
    if (score >= 50) return 'text-orange-400 border-orange-500/30 bg-orange-500/10';
    if (score >= 25) return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
    return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-slate-900/40 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-indigo-500/10 rounded-lg text-indigo-400 border border-indigo-500/20">
            <TrendingUp className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-wide">Predictive Security Analytics</h1>
        </div>
        <p className="text-slate-400 text-sm">
          Deterministic statistical risk trajectory forecasting and enterprise alert volume projections.
        </p>
      </div>

      {/* Enterprise Volume Projection Card */}
      {volumeForecast && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-slate-900/40 p-5 rounded-2xl border border-slate-800 space-y-3">
            <div className="text-xs text-slate-400 font-semibold uppercase flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400" />
              Projected 24H Alert Volume
            </div>
            <div className="text-3xl font-bold text-white">
              {volumeForecast.predicted_alert_count}{' '}
              <span className="text-xs font-normal text-slate-400">alerts projected</span>
            </div>
            <div className="text-xs text-slate-400">
              Reference: <span className="text-slate-200">{volumeForecast.historical_reference_count}</span> actual events in previous window
            </div>
          </div>

          <div className="bg-slate-900/40 p-5 rounded-2xl border border-slate-800 space-y-3">
            <div className="text-xs text-slate-400 font-semibold uppercase flex items-center gap-2">
              <Clock className="w-4 h-4 text-indigo-400" />
              Forecast Horizon
            </div>
            <div className="text-3xl font-bold text-indigo-300">
              {volumeForecast.forecast_window.replace('_', ' ')}
            </div>
            <div className="text-xs text-slate-400">Model Family: {volumeForecast.model_family}</div>
          </div>

          <div className="bg-slate-900/40 p-5 rounded-2xl border border-slate-800 space-y-3">
            <div className="text-xs text-slate-400 font-semibold uppercase flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              Confidence Meter
            </div>
            <div className="text-3xl font-bold text-emerald-400">
              {Math.round(volumeForecast.confidence * 100)}%
            </div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
              <div
                className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.round(volumeForecast.confidence * 100)}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Asset Risk Trajectory Forecasting Section */}
      <div className="bg-slate-900/40 p-6 rounded-2xl border border-slate-800 space-y-6">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <AlertOctagon className="w-5 h-5 text-indigo-400" />
              Asset Risk Trajectory Forecasting
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Empirical risk score projection combining velocity factors, health states, and baseline score.
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Asset Selector */}
            <select
              value={selectedAssetId}
              onChange={(e) => setSelectedAssetId(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              {assets.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name} ({a.criticality})
                </option>
              ))}
            </select>

            {/* 24H vs 7D Toggle */}
            <div className="flex bg-slate-800 rounded-xl p-1 border border-slate-700">
              <button
                onClick={() => setForecastType('24H')}
                className={`px-3 py-1 text-xs font-medium rounded-lg transition ${forecastType === '24H' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}
              >
                24H Horizon
              </button>
              <button
                onClick={() => setForecastType('7D')}
                className={`px-3 py-1 text-xs font-medium rounded-lg transition ${forecastType === '7D' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}
              >
                7D Horizon
              </button>
            </div>
          </div>
        </div>

        {assetForecast ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Predicted Score Gauge */}
            <div className="bg-slate-800/40 p-6 rounded-2xl border border-slate-800 flex flex-col items-center justify-center text-center space-y-4">
              <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
                Predicted Operational Risk Score
              </div>
              <div className={`text-6xl font-black px-6 py-3 rounded-2xl border ${getRiskColor(assetForecast.predicted_score)}`}>
                {assetForecast.predicted_score}
              </div>
              <div className="text-xs text-slate-400">
                Baseline Reference: <span className="text-slate-200 font-medium">{assetForecast.baseline_score} / 100</span>
              </div>
            </div>

            {/* Confidence & Model Metrics */}
            <div className="bg-slate-800/40 p-6 rounded-2xl border border-slate-800 space-y-4">
              <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Forecast Reliability
              </h3>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-xs text-slate-400 mb-1">
                    <span>Forecast Confidence:</span>
                    <span className="font-semibold text-emerald-400">{Math.round(assetForecast.confidence * 100)}%</span>
                  </div>
                  <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-emerald-500 h-full rounded-full"
                      style={{ width: `${Math.round(assetForecast.confidence * 100)}%` }}
                    />
                  </div>
                </div>

                <div className="pt-2 text-xs space-y-1.5 text-slate-400">
                  <div>Model Version: <span className="text-slate-200 font-mono">{assetForecast.model_version}</span></div>
                  <div>Horizon: <span className="text-indigo-300 font-medium">{assetForecast.forecast_horizon}</span></div>
                  <div>Evaluated At: <span className="text-slate-300">{new Date(assetForecast.created_at).toLocaleString()}</span></div>
                </div>
              </div>
            </div>

            {/* Mathematical Rationale / Explanation */}
            <div className="bg-slate-800/40 p-6 rounded-2xl border border-slate-800 space-y-3">
              <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Info className="w-4 h-4 text-indigo-400" />
                Contributing Factors
              </h3>
              <div className="text-xs text-slate-300 space-y-2">
                <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800">
                  <div className="text-slate-500">Status</div>
                  <div className="font-semibold text-indigo-300 mt-0.5">{assetForecast.explanation?.status || 'Active'}</div>
                </div>
                <div className="grid grid-cols-2 gap-2 text-center">
                  <div className="p-2.5 bg-slate-900/60 rounded-xl border border-slate-800">
                    <div className="text-slate-500 text-[11px]">Recent Alerts</div>
                    <div className="font-bold text-white text-sm">{assetForecast.explanation?.recent_alerts || 0}</div>
                  </div>
                  <div className="p-2.5 bg-slate-900/60 rounded-xl border border-slate-800">
                    <div className="text-slate-500 text-[11px]">Recent Anomalies</div>
                    <div className="font-bold text-white text-sm">{assetForecast.explanation?.recent_anomalies || 0}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <p className="text-xs text-slate-500 text-center py-12">Loading asset forecast data...</p>
        )}
      </div>
    </div>
  );
};
