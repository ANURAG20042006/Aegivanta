import React, { useState, useEffect } from 'react';
import { 
  Server, 
  Globe, 
  Database, 
  Plus, 
  Search, 
  Edit3, 
  Trash2, 
  Activity, 
  RefreshCw, 
  X 
} from 'lucide-react';
import { ProtectedAsset } from '../types';
import { assetService } from '../services/assetService';
import { useAuth } from '../hooks/useAuth';

export const AssetsPage: React.FC = () => {
  const { user } = useAuth();
  const [assets, setAssets] = useState<ProtectedAsset[]>([]);
  const [stats, setStats] = useState<{
    total_assets: number;
    active_healthy: number;
    degraded: number;
    compromised: number;
    high_or_critical_risk_assets: number;
  }>({
    total_assets: 0,
    active_healthy: 0,
    degraded: 0,
    compromised: 0,
    high_or_critical_risk_assets: 0
  });

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('');
  const [selectedEnv, setSelectedEnv] = useState<string>('');
  const [selectedCrit, setSelectedCrit] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [editingAsset, setEditingAsset] = useState<ProtectedAsset | null>(null);
  const [formData, setFormData] = useState<{
    name: string;
    hostname: string;
    url: string;
    ip_address: string;
    asset_type: 'website' | 'api' | 'server' | 'database' | 'endpoint' | 'network' | 'other';
    environment: 'production' | 'staging' | 'development';
    criticality: 'low' | 'medium' | 'high' | 'critical';
    status: 'active' | 'degraded' | 'compromised' | 'maintenance' | 'inactive';
    description: string;
  }>({
    name: '',
    hostname: '',
    url: '',
    ip_address: '',
    asset_type: 'website',
    environment: 'production',
    criticality: 'medium',
    status: 'active',
    description: ''
  });
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const canManage = user?.role === 'admin' || user?.role === 'analyst';
  const isAdmin = user?.role === 'admin';

  const fetchAssets = async () => {
    setIsLoading(true);
    try {
      const [listRes, statsRes] = await Promise.allSettled([
        assetService.listAssets({
          search: searchTerm || undefined,
          asset_type: selectedType || undefined,
          environment: selectedEnv || undefined,
          criticality: selectedCrit || undefined,
          status: selectedStatus || undefined
        }),
        assetService.getSummaryStats()
      ]);

      if (listRes.status === 'fulfilled') {
        setAssets(listRes.value.items || []);
      }
      if (statsRes.status === 'fulfilled') {
        setStats(statsRes.value);
      }
    } catch (err) {
      console.error('Failed to load protected assets:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAssets();
  }, [searchTerm, selectedType, selectedEnv, selectedCrit, selectedStatus]);

  const handleOpenCreateModal = () => {
    setEditingAsset(null);
    setFormData({
      name: '',
      hostname: '',
      url: '',
      ip_address: '',
      asset_type: 'website',
      environment: 'production',
      criticality: 'medium',
      status: 'active',
      description: ''
    });
    setFormError(null);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (asset: ProtectedAsset) => {
    setEditingAsset(asset);
    setFormData({
      name: asset.name,
      hostname: asset.hostname,
      url: asset.url || '',
      ip_address: asset.ip_address || '',
      asset_type: asset.asset_type,
      environment: asset.environment,
      criticality: asset.criticality,
      status: asset.status,
      description: asset.description || ''
    });
    setFormError(null);
    setIsModalOpen(true);
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setIsSubmitting(true);

    try {
      if (editingAsset) {
        await assetService.updateAsset(editingAsset.id, formData);
      } else {
        await assetService.createAsset(formData);
      }
      setIsModalOpen(false);
      fetchAssets();
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Failed to save asset';
      setFormError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteAsset = async (id: string, name: string) => {
    if (!window.confirm(`Are you sure you want to delete asset "${name}"?`)) return;
    try {
      await assetService.deleteAsset(id);
      fetchAssets();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete asset');
    }
  };

  const getAssetIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'website':
        return <Globe className="w-4 h-4 text-cyan-400" />;
      case 'api':
        return <Activity className="w-4 h-4 text-purple-400" />;
      case 'database':
        return <Database className="w-4 h-4 text-amber-400" />;
      default:
        return <Server className="w-4 h-4 text-blue-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">ACTIVE</span>;
      case 'degraded':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-amber-500/10 border border-amber-500/30 text-amber-400">DEGRADED</span>;
      case 'compromised':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-red-500/10 border border-red-500/30 text-red-400">COMPROMISED</span>;
      case 'maintenance':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-blue-500/10 border border-blue-500/30 text-blue-400">MAINTENANCE</span>;
      default:
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-slate-500/10 border border-slate-500/30 text-slate-400">INACTIVE</span>;
    }
  };

  const getRiskMeter = (score: number) => {
    let color = 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    if (score >= 75) color = 'text-red-400 bg-red-500/10 border-red-500/30';
    else if (score >= 50) color = 'text-amber-400 bg-amber-500/10 border-amber-500/30';
    else if (score >= 25) color = 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30';

    return (
      <div className="flex items-center space-x-2">
        <span className={`px-2 py-0.5 rounded-md text-xs font-mono font-bold border ${color}`}>
          {score.toFixed(1)}
        </span>
        <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
          <div 
            className={`h-full rounded-full ${
              score >= 75 ? 'bg-red-500' : score >= 50 ? 'bg-amber-500' : score >= 25 ? 'bg-yellow-500' : 'bg-emerald-500'
            }`}
            style={{ width: `${Math.min(100, Math.max(5, score))}%` }}
          />
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6 pb-12 animate-fade-in">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-cyan-500/10 border border-cyan-500/30 rounded-2xl text-cyan-400">
              <Server className="w-7 h-7" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-slate-100 font-mono uppercase tracking-wider">
                Protected Asset Inventory
              </h1>
              <p className="text-xs text-slate-400 mt-0.5">
                Centralized registry for protected domains, APIs, internal services, and mission-critical telemetry endpoints.
              </p>
            </div>
          </div>
        </div>

        {canManage && (
          <button
            onClick={handleOpenCreateModal}
            className="px-4 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold font-mono rounded-xl shadow-lg shadow-cyan-600/20 transition-all flex items-center space-x-2 cursor-pointer shrink-0"
          >
            <Plus className="w-4 h-4" />
            <span>Register Protected Asset</span>
          </button>
        )}
      </div>

      {/* Stats Summary Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
          <span className="text-xs font-mono text-slate-400 uppercase">Monitored Assets</span>
          <div className="text-2xl font-black font-mono text-slate-100 mt-1">{stats.total_assets}</div>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
          <span className="text-xs font-mono text-emerald-400 uppercase">Healthy / Active</span>
          <div className="text-2xl font-black font-mono text-emerald-400 mt-1">{stats.active_healthy}</div>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
          <span className="text-xs font-mono text-amber-400 uppercase">Degraded State</span>
          <div className="text-2xl font-black font-mono text-amber-400 mt-1">{stats.degraded}</div>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
          <span className="text-xs font-mono text-red-400 uppercase">Compromised / High Risk</span>
          <div className="text-2xl font-black font-mono text-red-400 mt-1">
            {stats.compromised + stats.high_or_critical_risk_assets}
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 flex flex-wrap items-center gap-3">
        <div className="flex-1 min-w-[240px] relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by asset name, domain, hostname, or IP..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-sans"
          />
        </div>

        <select
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
          className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-cyan-500 font-mono"
        >
          <option value="">All Types</option>
          <option value="website">Website</option>
          <option value="api">API Service</option>
          <option value="server">Server</option>
          <option value="database">Database</option>
          <option value="endpoint">Endpoint</option>
          <option value="network">Network</option>
        </select>

        <select
          value={selectedEnv}
          onChange={(e) => setSelectedEnv(e.target.value)}
          className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-cyan-500 font-mono"
        >
          <option value="">All Environments</option>
          <option value="production">Production</option>
          <option value="staging">Staging</option>
          <option value="development">Development</option>
        </select>

        <select
          value={selectedCrit}
          onChange={(e) => setSelectedCrit(e.target.value)}
          className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-cyan-500 font-mono"
        >
          <option value="">All Criticalities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>

        <select
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-cyan-500 font-mono"
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="degraded">Degraded</option>
          <option value="compromised">Compromised</option>
          <option value="maintenance">Maintenance</option>
          <option value="inactive">Inactive</option>
        </select>

        <button
          onClick={fetchAssets}
          className="p-2 bg-slate-950 hover:bg-slate-800 text-slate-300 rounded-xl border border-slate-800 transition-colors cursor-pointer"
          title="Refresh Inventory"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Asset Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 font-mono uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-3.5">Asset Identity</th>
                <th className="px-4 py-3.5">Environment</th>
                <th className="px-4 py-3.5">Criticality</th>
                <th className="px-4 py-3.5">Risk Score</th>
                <th className="px-4 py-3.5">Status</th>
                <th className="px-4 py-3.5">Last Seen</th>
                {canManage && <th className="px-6 py-3.5 text-right">Actions</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-500">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-cyan-500" />
                    Loading monitored assets...
                  </td>
                </tr>
              ) : assets.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-500">
                    No protected assets matched the filter criteria.
                  </td>
                </tr>
              ) : (
                assets.map((asset) => (
                  <tr key={asset.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-3">
                        <div className="p-2 bg-slate-950 rounded-xl border border-slate-800 shrink-0">
                          {getAssetIcon(asset.asset_type)}
                        </div>
                        <div>
                          <div className="font-bold text-slate-100 font-sans text-sm">{asset.name}</div>
                          <div className="text-[11px] text-slate-400 font-mono flex items-center space-x-2">
                            <span>{asset.hostname}</span>
                            {asset.ip_address && (
                              <>
                                <span className="text-slate-600">•</span>
                                <span className="text-cyan-400">{asset.ip_address}</span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <span className="px-2 py-0.5 rounded-md text-[11px] font-bold bg-slate-950 border border-slate-800 text-slate-300 uppercase">
                        {asset.environment}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <span className={`px-2 py-0.5 rounded-md text-[11px] font-bold uppercase ${
                        asset.criticality === 'critical' ? 'text-red-400 bg-red-500/10 border border-red-500/30' :
                        asset.criticality === 'high' ? 'text-amber-400 bg-amber-500/10 border border-amber-500/30' :
                        'text-slate-300 bg-slate-950 border border-slate-800'
                      }`}>
                        {asset.criticality}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      {getRiskMeter(asset.risk_score)}
                    </td>
                    <td className="px-4 py-4">
                      {getStatusBadge(asset.status)}
                    </td>
                    <td className="px-4 py-4 text-slate-400 text-[11px]">
                      {new Date(asset.last_seen).toLocaleString()}
                    </td>
                    {canManage && (
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => handleOpenEditModal(asset)}
                            className="p-1.5 bg-slate-950 hover:bg-cyan-950 text-slate-400 hover:text-cyan-400 rounded-lg border border-slate-800 transition-colors cursor-pointer"
                            title="Edit Asset"
                          >
                            <Edit3 className="w-3.5 h-3.5" />
                          </button>
                          {isAdmin && (
                            <button
                              onClick={() => handleDeleteAsset(asset.id, asset.name)}
                              className="p-1.5 bg-slate-950 hover:bg-red-950 text-slate-400 hover:text-red-400 rounded-lg border border-slate-800 transition-colors cursor-pointer"
                              title="Delete Asset"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          )}
                        </div>
                      </td>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Asset Modal (Create/Edit) */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl animate-scale-in">
            <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
              <h3 className="text-lg font-bold font-mono text-slate-100">
                {editingAsset ? 'Edit Protected Asset' : 'Register New Monitored Asset'}
              </h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-200 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {formError && (
              <div className="mb-4 p-3 bg-red-950/40 border border-red-800 rounded-xl text-red-300 text-xs font-mono">
                {formError}
              </div>
            )}

            <form onSubmit={handleFormSubmit} className="space-y-4 text-xs font-mono">
              <div>
                <label className="block text-slate-400 mb-1">Asset Name *</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. Primary Banking API Gateway"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500 font-sans"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Hostname / Domain *</label>
                  <input
                    type="text"
                    required
                    value={formData.hostname}
                    onChange={(e) => setFormData({ ...formData, hostname: e.target.value })}
                    placeholder="api.aegivanta.internal"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Target IP Address</label>
                  <input
                    type="text"
                    value={formData.ip_address}
                    onChange={(e) => setFormData({ ...formData, ip_address: e.target.value })}
                    placeholder="10.0.0.1"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Type</label>
                  <select
                    value={formData.asset_type}
                    onChange={(e) => setFormData({ ...formData, asset_type: e.target.value as any })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                  >
                    <option value="website">Website</option>
                    <option value="api">API</option>
                    <option value="server">Server</option>
                    <option value="database">Database</option>
                    <option value="endpoint">Endpoint</option>
                    <option value="network">Network</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Environment</label>
                  <select
                    value={formData.environment}
                    onChange={(e) => setFormData({ ...formData, environment: e.target.value as any })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                  >
                    <option value="production">Production</option>
                    <option value="staging">Staging</option>
                    <option value="development">Dev</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Criticality</label>
                  <select
                    value={formData.criticality}
                    onChange={(e) => setFormData({ ...formData, criticality: e.target.value as any })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Description</label>
                <textarea
                  rows={2}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Operational notes, owning team, SLA constraints..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500 font-sans"
                />
              </div>

              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-5 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-bold rounded-xl shadow-lg shadow-cyan-600/20 transition-all cursor-pointer"
                >
                  {isSubmitting ? 'Saving...' : (editingAsset ? 'Update Asset' : 'Register Asset')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
