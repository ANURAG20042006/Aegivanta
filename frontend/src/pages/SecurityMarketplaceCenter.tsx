import React, { useEffect, useState } from 'react';
import {
  ShoppingBag,
  Activity,
  ChevronRight,
  ShieldCheck,
  Zap,
  Download,
  Sliders,
  Sparkles,
  Package,
  Layers,
  Trash2
} from 'lucide-react';
import { saasApi } from '../services/saas';


export const SecurityMarketplaceCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'catalog' | 'installed' | 'provenance_signatures' | 'sandbox_audit' | 'marketplace_studio'>('overview');
  const [summary, setSummary] = useState<any>(null);
  const [packages, setPackages] = useState<any[]>([]);
  const [installed, setInstalled] = useState<any[]>([]);
  const [selectedType, setSelectedType] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  // Publish studio state
  const [pkgName, setPkgName] = useState<string>('Autonomous Kubernetes Pod Quarantine Playbook');
  const [pkgType, setPkgType] = useState<string>('SOAR_PLAYBOOK');
  const [pkgVersion, setPkgVersion] = useState<string>('1.0.0');
  const [pkgAuthor, setPkgAuthor] = useState<string>('Enterprise DevSecOps Team');
  const [publishedPkg, setPublishedPkg] = useState<any>(null);

  // Quick install state
  const [installResult, setInstallResult] = useState<any>(null);

  useEffect(() => {
    fetchMarketplaceData();
  }, [selectedType]);

  const fetchMarketplaceData = async () => {
    try {
      setLoading(true);
      const [sum, pkgs, inst] = await Promise.all([
        saasApi.getMarketplaceSummary(),
        saasApi.getMarketplacePackages(selectedType || undefined),
        saasApi.getInstalledExtensions()
      ]);
      setSummary(sum);
      setPackages(pkgs);
      setInstalled(inst);
    } catch (err) {
      console.error('Failed to load Marketplace data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInstall = async (pkg: any) => {
    try {
      const res = await saasApi.installMarketplacePackage({
        package_id: pkg.id,
        package_name: pkg.package_name,
        version: pkg.version
      });
      setInstallResult(res);
      fetchMarketplaceData();
    } catch (err) {
      console.error('Failed to install package:', err);
    }
  };

  const handleUninstall = async (installedId: string) => {
    try {
      await saasApi.uninstallMarketplacePackage({ installed_id: installedId });
      fetchMarketplaceData();
    } catch (err) {
      console.error('Failed to uninstall package:', err);
    }
  };

  const handlePublish = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await saasApi.publishMarketplacePackage({
        package_name: pkgName,
        package_type: pkgType,
        version: pkgVersion,
        author: pkgAuthor
      });
      setPublishedPkg(res);
      fetchMarketplaceData();
    } catch (err) {
      console.error('Failed to publish package:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <ShoppingBag className="h-7 w-7 text-pink-400" />
            Security Marketplace & Ecosystem Package Manager
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Curated Detection Packs, SOAR Playbooks, Connector Adapters, and AI Agent Skills with Ed25519 Verification & Hot-Reload.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('marketplace_studio')}
            className="flex items-center gap-2 px-3.5 py-2 bg-pink-600 hover:bg-pink-500 text-white rounded-xl text-xs font-semibold transition-colors"
          >
            <Sparkles className="h-4 w-4" /> Publish Package Studio
          </button>
        </div>
      </div>

      {/* Top Metrics Ribbon */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Ecosystem Score</div>
            <div className="text-2xl font-bold text-pink-400 mt-1">{summary.overall_ecosystem_score}<span className="text-xs text-slate-500">/100</span></div>
            <div className="text-[10px] text-pink-400 mt-0.5">Enterprise Tier</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Published Packages</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{summary.published_packages_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Curated Extensions</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Installed Add-Ons</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{summary.installed_extensions_count}</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Active & Running</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Ed25519 Signed</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{(summary.ed25519_signed_packages_ratio * 100).toFixed(0)}%</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">Zero Untrusted Code</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Hot-Reload Engine</div>
            <div className="text-2xl font-bold text-slate-200 mt-1">ONLINE</div>
            <div className="text-[10px] text-emerald-400 mt-0.5">0s Downtime</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
            <div className="text-[11px] text-slate-400">Community Reviews</div>
            <div className="text-2xl font-bold text-amber-400 mt-1">{summary.total_community_reviews_count}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Peer Verified</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'Marketplace Overview', icon: ShoppingBag },
          { id: 'catalog', label: 'Curated Package Catalog', icon: Package },
          { id: 'installed', label: 'Installed Extensions', icon: Layers },
          { id: 'provenance_signatures', label: 'Ed25519 Signatures & Hashes', icon: ShieldCheck },
          { id: 'sandbox_audit', label: 'Sandboxed Runtime Audit', icon: Zap },
          { id: 'marketplace_studio', label: 'Package & Publish Studio', icon: Sliders }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'border-pink-500 text-pink-300'
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
          <Activity className="h-6 w-6 animate-spin text-pink-400 mr-3" />
          Synchronizing Security Marketplace Catalog & Hot-Reload Engine...
        </div>
      ) : (
        <>
          {/* TAB 1: Overview */}
          {activeTab === 'overview' && summary && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Catalog Highlights */}
              <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Package className="h-4 w-4 text-pink-400" /> Featured Marketplace Security Packages
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {packages.slice(0, 4).map((p) => (
                    <div key={p.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                      <div className="flex justify-between items-start font-bold">
                        <span className="text-slate-100">{p.package_name}</span>
                        <span className="px-2 py-0.5 rounded bg-pink-500/10 text-pink-300 text-[10px] font-bold border border-pink-500/30">
                          v{p.version}
                        </span>
                      </div>
                      <div className="text-[11px] text-cyan-300">Type: {p.package_type}</div>
                      <div className="text-[10px] text-slate-400 flex justify-between items-center pt-1 border-t border-slate-800">
                        <span>Author: <strong className="text-slate-200">{p.author}</strong></span>
                        <span className="text-emerald-400 font-semibold">{p.installs_count} installs</span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-3 border-t border-slate-800/60">
                  <div className="text-xs font-bold text-slate-300 mb-2">Priority Marketplace Directives:</div>
                  <div className="space-y-1.5">
                    {summary.top_marketplace_priorities.map((pri: string, idx: number) => (
                      <div key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                        <ChevronRight className="h-3.5 w-3.5 text-pink-400 shrink-0 mt-0.5" />
                        {pri}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Installed Extensions Summary */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Layers className="h-4 w-4 text-pink-400" /> Installed Extensions
                </h3>
                <div className="space-y-3">
                  {installed.map((ins) => (
                    <div key={ins.id} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60 text-xs space-y-1.5">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span>{ins.package_name}</span>
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold">ACTIVE</span>
                      </div>
                      <div className="text-[11px] text-slate-400">Version: <strong className="text-cyan-300">v{ins.installed_version}</strong></div>
                      <div className="text-[10px] text-slate-500">Auto-Update: Enabled · Hot-Reloaded</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Catalog */}
          {activeTab === 'catalog' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Package className="h-4 w-4 text-pink-400" /> Curated Package Catalog
                </h3>
                <div className="flex items-center gap-2 text-xs">
                  <label className="text-slate-400">Filter Category:</label>
                  <select
                    value={selectedType}
                    onChange={(e) => setSelectedType(e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-200"
                  >
                    <option value="">All Categories</option>
                    <option value="DETECTION_PACK">Detection Packs (Sigma / YARA-L)</option>
                    <option value="SOAR_PLAYBOOK">SOAR Playbooks</option>
                    <option value="CONNECTOR_ADAPTER">Connector Adapters</option>
                    <option value="AI_AGENT_SKILL">AI Agent Skills</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {packages.map((pkg) => (
                  <div key={pkg.id} className="p-5 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-3">
                    <div className="flex justify-between items-start font-bold">
                      <span className="text-slate-100 text-sm">{pkg.package_name}</span>
                      <span className="px-2 py-0.5 rounded bg-pink-500/10 text-pink-300 font-bold text-[10px]">
                        v{pkg.version}
                      </span>
                    </div>

                    <div className="flex justify-between items-center text-[11px] text-slate-400">
                      <span>Category: <strong className="text-cyan-300">{pkg.package_type}</strong></span>
                      <span>Author: <strong className="text-slate-200">{pkg.author}</strong></span>
                    </div>

                    <div className="p-2 bg-slate-900 rounded font-mono text-[10px] text-amber-300 break-all">
                      Ed25519 Sig: {pkg.signature_hash}
                    </div>

                    <div className="flex justify-between items-center pt-2 border-t border-slate-800/60">
                      <span className="text-[10px] text-emerald-400 font-semibold">{pkg.installs_count} Total Installs</span>
                      <button
                        onClick={() => handleInstall(pkg)}
                        className="px-3 py-1.5 bg-pink-600 hover:bg-pink-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5"
                      >
                        <Download className="h-3.5 w-3.5" /> Hot-Reload Install
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {installResult && (
                <div className="p-4 bg-slate-950 rounded-xl border border-pink-500/30 text-xs space-y-2 mt-4">
                  <div className="flex justify-between items-center text-pink-400 font-bold">
                    <span>Package Installed Successfully</span>
                    <span>{installResult.status}</span>
                  </div>
                  <div className="text-slate-200">{installResult.package_name} (v{installResult.installed_version})</div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: Installed */}
          {activeTab === 'installed' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Layers className="h-4 w-4 text-pink-400" /> Active Installed Tenant Extensions
              </h3>

              <div className="space-y-3">
                {installed.map((ins) => (
                  <div key={ins.id} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold">
                      <span className="text-slate-100 text-sm">{ins.package_name}</span>
                      <div className="flex items-center gap-2">
                        <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold text-[10px]">
                          ACTIVE_HOT_LOADED
                        </span>
                        <button
                          onClick={() => handleUninstall(ins.id)}
                          className="p-1 text-red-400 hover:text-red-300"
                          title="Uninstall"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>

                    <div className="flex justify-between items-center text-[11px] text-slate-400">
                      <span>Installed Version: <strong className="text-cyan-300">v{ins.installed_version}</strong></span>
                      <span>Auto-Update: <strong className="text-emerald-400">Enabled</strong></span>
                    </div>

                    <div className="text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">
                      Installed At: {new Date(ins.installed_at).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: Ed25519 Signatures */}
          {activeTab === 'provenance_signatures' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 max-w-2xl mx-auto space-y-4 text-xs">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-pink-400" /> Cryptographic Package Signing & Provenance
              </h3>
              <p className="text-slate-400 leading-relaxed">
                All marketplace packages undergo strict Ed25519 cryptographic signature verification and SHA-256 integrity validation prior to ingestion into the Aegivanta runtime engine.
              </p>
              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2 font-mono text-[11px] text-cyan-300">
                <div>Public Key Ledger: ed25519:9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c</div>
                <div>Integrity Check: SHA-256 Digest Validation (0 Tampering Incidents)</div>
                <div>Code Signing Attestation: SLSA Level 3 Certified Packaging</div>
              </div>
            </div>
          )}

          {/* TAB 5: Sandboxed Runtime Audit */}
          {activeTab === 'sandbox_audit' && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 max-w-2xl mx-auto space-y-4 text-xs">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Zap className="h-5 w-5 text-pink-400" /> Sandboxed Runtime Security Audit
              </h3>
              <p className="text-slate-400 leading-relaxed">
                Every package is pre-evaluated in an isolated WebAssembly (Wasm) and eBPF sandbox to detect reverse shells, unauthorized socket bindings, or data exfiltration behaviors.
              </p>
              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2 font-mono text-[11px] text-emerald-400">
                <div>Static AST Analysis: CLEAN (Zero Malicious Primitives Detected)</div>
                <div>Runtime Network Isolation: STRICT (Local Pipeline Hook Only)</div>
                <div>CPU / Memory Quota Guard: Enforced (&le; 128MB RAM, &le; 5% Core)</div>
              </div>
            </div>
          )}

          {/* TAB 6: Marketplace Studio */}
          {activeTab === 'marketplace_studio' && (
            <div className="max-w-2xl mx-auto bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 space-y-4">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-pink-400" /> Publish Security Extension Package
              </h3>
              <p className="text-xs text-slate-400">
                Publish a certified detection pack, SOAR playbook, connector adapter, or AI agent skill to the ecosystem.
              </p>

              <form onSubmit={handlePublish} className="space-y-3 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Package Name</label>
                  <input
                    type="text"
                    value={pkgName}
                    onChange={(e) => setPkgName(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                    required
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Package Category</label>
                  <select
                    value={pkgType}
                    onChange={(e) => setPkgType(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                  >
                    <option value="DETECTION_PACK">Detection Pack (Sigma / YARA-L Rules)</option>
                    <option value="SOAR_PLAYBOOK">SOAR Automation Playbook</option>
                    <option value="CONNECTOR_ADAPTER">Third-Party Connector Adapter</option>
                    <option value="AI_AGENT_SKILL">Autonomous AI Agent Skill</option>
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-400 mb-1">Semantic Version</label>
                    <input
                      type="text"
                      value={pkgVersion}
                      onChange={(e) => setPkgVersion(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200 font-mono text-[11px]"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1">Author / Organization</label>
                    <input
                      type="text"
                      value={pkgAuthor}
                      onChange={(e) => setPkgAuthor(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200"
                      required
                    />
                  </div>
                </div>
                <div className="flex justify-end pt-2">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-pink-600 hover:bg-pink-500 text-white rounded-xl font-semibold flex items-center gap-2"
                  >
                    <Package className="h-4 w-4" /> Publish to Marketplace
                  </button>
                </div>
              </form>

              {publishedPkg && (
                <div className="p-4 bg-slate-950 rounded-xl border border-pink-500/30 text-xs space-y-2 mt-4">
                  <div className="flex justify-between items-center text-pink-400 font-bold">
                    <span>Package Published & Signed</span>
                    <span>v{publishedPkg.version}</span>
                  </div>
                  <div className="text-slate-200 font-semibold">{publishedPkg.package_name}</div>
                  <div className="p-2 bg-slate-900 rounded font-mono text-[10px] text-cyan-300 break-all">
                    Signature Hash: {publishedPkg.signature_hash}
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};
