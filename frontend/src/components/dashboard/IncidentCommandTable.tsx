import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  Search, 
  ArrowUpDown, 
  ChevronLeft, 
  ChevronRight, 
  Flame, 
  ExternalLink, 
  RefreshCw
} from 'lucide-react';
import { dashboardService, DashboardIncidentsResponse } from '../../services/dashboard';

export const IncidentCommandTable: React.FC = () => {
  const navigate = useNavigate();

  const [incidentsData, setIncidentsData] = useState<DashboardIncidentsResponse>({
    total: 0,
    page: 1,
    limit: 10,
    total_pages: 1,
    items: []
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [page, setPage] = useState<number>(1);
  const pageSize = 10;
  const [search, setSearch] = useState<string>('');
  const [severity, setSeverity] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [sortBy, setSortBy] = useState<string>('risk_score');
  const [sortOrder, setSortOrder] = useState<string>('desc');
  const [lookbackHours, setLookbackHours] = useState<number | undefined>(undefined);

  const fetchIncidents = async () => {
    setIsLoading(true);
    try {
      const data = await dashboardService.getIncidents({
        page,
        limit: pageSize,
        search: search.trim() || undefined,
        severity: severity || undefined,
        status: statusFilter || undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
        lookback_hours: lookbackHours
      });
      setIncidentsData(data);
    } catch (err) {
      console.error('Failed to load incident table:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, [page, pageSize, severity, statusFilter, sortBy, sortOrder, lookbackHours]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchIncidents();
  };

  const getSeverityBadge = (sev: string) => {
    switch (sev?.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-red-500/20 text-red-400 border-red-500/40';
      case 'HIGH':
        return 'bg-rose-500/20 text-rose-400 border-rose-500/40';
      case 'MEDIUM':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
      case 'LOW':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/40';
      default:
        return 'bg-slate-700/50 text-slate-300 border-slate-600';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'DETECTED':
      case 'OPEN':
        return 'bg-red-500/10 text-red-400 border-red-500/30';
      case 'TRIAGED':
      case 'INVESTIGATING':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'ESCALATED':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/30';
      case 'CONTAINED':
        return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30';
      case 'RESOLVED':
      case 'CLOSED':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      default:
        return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  const getRiskScoreColor = (score: number) => {
    if (score >= 80) return 'text-red-400 bg-red-500/10 border-red-500/30';
    if (score >= 50) return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
    return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-2xl backdrop-blur-md space-y-4 font-mono">
      {/* Header & Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400">
            <Flame className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h2 className="text-base font-black text-slate-100 uppercase tracking-wider">
              Incident Command Center
            </h2>
            <p className="text-xs text-slate-400">
              Real-time operational triage & forensic incident routing across network entities.
            </p>
          </div>
        </div>

        {/* Filter Controls Bar */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Search Form */}
          <form onSubmit={handleSearchSubmit} className="relative">
            <input
              type="text"
              placeholder="Search IPs, codes, titles..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 w-48 sm:w-60"
            />
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
          </form>

          {/* Severity Dropdown */}
          <select
            value={severity}
            onChange={(e) => { setSeverity(e.target.value); setPage(1); }}
            className="bg-slate-950 border border-slate-800 rounded-xl px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>

          {/* Status Dropdown */}
          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            className="bg-slate-950 border border-slate-800 rounded-xl px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Statuses</option>
            <option value="OPEN">Open</option>
            <option value="TRIAGED">Triaged</option>
            <option value="INVESTIGATING">Investigating</option>
            <option value="ESCALATED">Escalated</option>
            <option value="CONTAINED">Contained</option>
            <option value="RESOLVED">Resolved</option>
            <option value="CLOSED">Closed</option>
          </select>

          {/* Time Filter */}
          <select
            value={lookbackHours ?? ''}
            onChange={(e) => { 
              const val = e.target.value ? Number(e.target.value) : undefined;
              setLookbackHours(val); 
              setPage(1); 
            }}
            className="bg-slate-950 border border-slate-800 rounded-xl px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Time</option>
            <option value="1">Last 1 Hour</option>
            <option value="6">Last 6 Hours</option>
            <option value="24">Last 24 Hours</option>
            <option value="168">Last 7 Days</option>
            <option value="720">Last 30 Days</option>
          </select>

          <button
            onClick={fetchIncidents}
            className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition-colors"
            title="Refresh Incident Table"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Incidents Table */}
      <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/60">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-slate-900/90 text-slate-400 border-b border-slate-800 font-bold">
              <th className="py-3 px-3.5">INCIDENT ID</th>
              <th className="py-3 px-3">
                <button
                  onClick={() => {
                    if (sortBy === 'severity') {
                      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
                    } else {
                      setSortBy('severity');
                      setSortOrder('desc');
                    }
                  }}
                  className="flex items-center space-x-1 hover:text-white"
                >
                  <span>SEVERITY</span>
                  <ArrowUpDown className="w-3 h-3" />
                </button>
              </th>
              <th className="py-3 px-3">
                <button
                  onClick={() => {
                    if (sortBy === 'risk_score') {
                      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
                    } else {
                      setSortBy('risk_score');
                      setSortOrder('desc');
                    }
                  }}
                  className="flex items-center space-x-1 hover:text-white"
                >
                  <span>RISK SCORE</span>
                  <ArrowUpDown className="w-3 h-3" />
                </button>
              </th>
              <th className="py-3 px-3">STATUS</th>
              <th className="py-3 px-3.5">ATTACK / CLASSIFICATION</th>
              <th className="py-3 px-3.5">SOURCE &rarr; DESTINATION</th>
              <th className="py-3 px-3">AFFECTED ASSET</th>
              <th className="py-3 px-3">MITRE & IOCs</th>
              <th className="py-3 px-3">
                <button
                  onClick={() => {
                    if (sortBy === 'timestamp') {
                      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
                    } else {
                      setSortBy('timestamp');
                      setSortOrder('desc');
                    }
                  }}
                  className="flex items-center space-x-1 hover:text-white"
                >
                  <span>DETECTED TIME</span>
                  <ArrowUpDown className="w-3 h-3" />
                </button>
              </th>
              <th className="py-3 px-3 text-right">ACTION</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {isLoading ? (
              <tr>
                <td colSpan={10} className="py-12 text-center text-slate-500">
                  <div className="flex items-center justify-center space-x-2">
                    <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
                    <span>QUERYING INCIDENT OPERATIONS DATABASE...</span>
                  </div>
                </td>
              </tr>
            ) : incidentsData.items.length === 0 ? (
              <tr>
                <td colSpan={10} className="py-12 text-center text-slate-500">
                  NO SECURITY INCIDENTS MATCHING THE SELECTED CRITERIA
                </td>
              </tr>
            ) : (
              incidentsData.items.map((inc) => (
                <tr
                  key={inc.id}
                  className="hover:bg-slate-900/60 transition-colors group cursor-pointer"
                  onClick={() => navigate(`/incidents/${inc.id}`)}
                >
                  {/* Code */}
                  <td className="py-3 px-3.5 font-bold text-cyan-400">
                    {inc.incident_code}
                  </td>

                  {/* Severity */}
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getSeverityBadge(inc.severity)}`}>
                      {inc.severity}
                    </span>
                  </td>

                  {/* Risk Score */}
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 rounded text-[11px] font-bold border ${getRiskScoreColor(inc.risk_score)}`}>
                      {inc.risk_score} / 100
                    </span>
                  </td>

                  {/* Status */}
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getStatusBadge(inc.status)}`}>
                      {inc.status}
                    </span>
                  </td>

                  {/* Attack Type */}
                  <td className="py-3 px-3.5">
                    <div className="font-bold text-slate-200">{inc.attack_type}</div>
                    <div className="text-[10px] text-slate-400">{inc.protocol} &bull; {inc.alert_count} Alerts</div>
                  </td>

                  {/* Source -> Dest */}
                  <td className="py-3 px-3.5">
                    <div className="text-slate-300">{inc.source_ip}</div>
                    <div className="text-slate-500 text-[10px]">&rarr; {inc.destination_ip}:{inc.destination_port || 80}</div>
                  </td>

                  {/* Affected Asset */}
                  <td className="py-3 px-3">
                    {inc.asset_name ? (
                      <div>
                        <div className="text-slate-200 font-bold truncate max-w-[130px]">{inc.asset_name}</div>
                        <span className="text-[9px] px-1 py-0.2 bg-slate-800 rounded text-slate-400 uppercase">
                          {inc.asset_criticality || 'MEDIUM'}
                        </span>
                      </div>
                    ) : (
                      <span className="text-slate-500 italic">Unlinked</span>
                    )}
                  </td>

                  {/* MITRE & IOCs */}
                  <td className="py-3 px-3">
                    <div className="flex flex-wrap gap-1 max-w-[150px]">
                      {inc.mitre_techniques && inc.mitre_techniques.length > 0 ? (
                        inc.mitre_techniques.slice(0, 2).map((tech, idx) => (
                          <span key={idx} className="px-1.5 py-0.2 bg-purple-500/10 border border-purple-500/30 text-purple-300 rounded text-[9px]">
                            {tech}
                          </span>
                        ))
                      ) : (
                        <span className="text-[10px] text-slate-500">T1498 / ML</span>
                      )}
                      {inc.ioc_matches && inc.ioc_matches.length > 0 && (
                        <span className="px-1 py-0.2 bg-red-500/10 border border-red-500/30 text-red-300 rounded text-[9px]">
                          IOC Hit
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Timestamp */}
                  <td className="py-3 px-3 text-slate-400 text-[11px]">
                    {inc.timestamp ? new Date(inc.timestamp).toLocaleString() : 'N/A'}
                  </td>

                  {/* Action Link */}
                  <td className="py-3 px-3 text-right" onClick={(e) => e.stopPropagation()}>
                    <Link
                      to={`/incidents/${inc.id}`}
                      className="inline-flex items-center space-x-1 px-2.5 py-1 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 rounded-lg text-xs transition-colors"
                    >
                      <span>TRIAGE</span>
                      <ExternalLink className="w-3 h-3" />
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 text-xs text-slate-400">
        <div>
          Showing {incidentsData.items.length > 0 ? (page - 1) * pageSize + 1 : 0} to{' '}
          {Math.min(page * pageSize, incidentsData.total)} of {incidentsData.total.toLocaleString()} incidents
        </div>

        <div className="flex items-center space-x-2">
          <button
            disabled={page <= 1}
            onClick={() => setPage(page - 1)}
            className="p-1.5 rounded-lg border border-slate-800 bg-slate-950 text-slate-300 hover:bg-slate-800 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span>
            Page {page} of {incidentsData.total_pages}
          </span>
          <button
            disabled={page >= incidentsData.total_pages}
            onClick={() => setPage(page + 1)}
            className="p-1.5 rounded-lg border border-slate-800 bg-slate-950 text-slate-300 hover:bg-slate-800 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
