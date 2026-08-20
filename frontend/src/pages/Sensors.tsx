import React, { useState, useEffect } from 'react';
import { saasApi, SensorItem } from '../services/saas';

export const SensorsPage: React.FC = () => {
  const [sensors, setSensors] = useState<SensorItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [name, setName] = useState('');
  const [hostname, setHostname] = useState('');
  const [ipAddress, setIpAddress] = useState('');
  const [osType, setOsType] = useState('linux');
  const [enrolledToken, setEnrolledToken] = useState<string | null>(null);
  const [message, setMessage] = useState<{ text: string; isError: boolean } | null>(null);

  const loadSensors = async () => {
    setLoading(true);
    try {
      const list = await saasApi.listSensors();
      setSensors(list);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSensors();
  }, []);

  const handleEnroll = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await saasApi.enrollSensor({ name, hostname, ip_address: ipAddress, os_type: osType });
      setEnrolledToken(res.enrollment_token);
      setMessage({ text: 'Sensor enrolled! Copy token to start the agent daemon.', isError: false });
      setName('');
      setHostname('');
      setIpAddress('');
      loadSensors();
    } catch (err: any) {
      setMessage({ text: err.response?.data?.detail || 'Failed to enroll sensor', isError: true });
    }
  };

  const handleRevoke = async (id: string) => {
    if (!window.confirm('Revoke this sensor daemon? Ingestion will immediately cease.')) return;
    try {
      await saasApi.revokeSensor(id);
      setMessage({ text: 'Sensor revoked.', isError: false });
      loadSensors();
    } catch (err: any) {
      setMessage({ text: err.response?.data?.detail || 'Failed to revoke sensor', isError: true });
    }
  };

  return (
    <div className="space-y-6 font-mono">
      <div className="flex justify-between items-center border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-cyan-400 tracking-wider">ENDPOINT & NETWORK SENSORS</h1>
          <p className="text-xs text-gray-400">Lightweight SentinelAI Telemetry Agent Fleet Status</p>
        </div>
        <button
          onClick={() => { setShowModal(true); setEnrolledToken(null); }}
          className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-black text-xs font-bold rounded transition-colors"
        >
          + ENROLL SENSOR
        </button>
      </div>

      {message && (
        <div className={`p-3 text-xs rounded border ${message.isError ? 'bg-red-950/40 border-red-500/50 text-red-300' : 'bg-emerald-950/40 border-emerald-500/50 text-emerald-300'}`}>
          {message.text}
        </div>
      )}

      {loading ? (
        <div className="text-cyan-400 text-xs animate-pulse">LOADING SENSOR FLEET...</div>
      ) : (
        <div className="bg-gray-900/60 border border-gray-800 rounded p-4">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-gray-800 text-gray-400">
                  <th className="py-2.5">NAME</th>
                  <th className="py-2.5">HOSTNAME</th>
                  <th className="py-2.5">IP ADDRESS</th>
                  <th className="py-2.5">OS</th>
                  <th className="py-2.5">VERSION</th>
                  <th className="py-2.5">STATUS</th>
                  <th className="py-2.5">LAST HEARTBEAT</th>
                  <th className="py-2.5 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/50">
                {sensors.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-6 text-center text-gray-500">No sensors registered. Click "+ Enroll Sensor" to deploy an agent.</td>
                  </tr>
                ) : (
                  sensors.map((s) => (
                    <tr key={s.id} className="hover:bg-gray-800/20">
                      <td className="py-3 font-semibold text-white">{s.name}</td>
                      <td className="py-3 text-cyan-300">{s.hostname}</td>
                      <td className="py-3 text-gray-300">{s.ip_address}</td>
                      <td className="py-3 uppercase text-gray-400">{s.os_type}</td>
                      <td className="py-3 text-gray-400">v{s.sensor_version}</td>
                      <td className="py-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] ${s.status === 'ONLINE' ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/30' : 'bg-red-950 text-red-400 border border-red-500/30'}`}>
                          {s.status}
                        </span>
                      </td>
                      <td className="py-3 text-gray-400">{new Date(s.last_heartbeat).toLocaleTimeString()}</td>
                      <td className="py-3 text-right">
                        {s.status !== 'REVOKED' && (
                          <button
                            onClick={() => handleRevoke(s.id)}
                            className="px-2.5 py-1 bg-red-950 hover:bg-red-900 text-red-300 border border-red-500/30 rounded text-[10px]"
                          >
                            Revoke
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Enroll Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 border border-cyan-500/40 rounded p-6 max-w-md w-full space-y-4">
            <h3 className="text-sm font-bold text-cyan-400 uppercase">Enroll Telemetry Sensor</h3>

            {enrolledToken ? (
              <div className="space-y-3">
                <div className="p-3 bg-amber-950/40 border border-amber-500/50 rounded text-amber-200 text-xs">
                  <p className="font-bold">⚠️ Copy agent enrollment token:</p>
                  <p className="mt-1">Pass this token to the daemon config file or CLI flag:</p>
                </div>
                <div className="p-3 bg-black border border-gray-700 rounded font-mono text-cyan-300 text-xs select-all break-all">
                  {enrolledToken}
                </div>
                <button
                  onClick={() => setShowModal(false)}
                  className="w-full py-2 bg-cyan-600 hover:bg-cyan-500 text-black font-bold text-xs rounded"
                >
                  Done
                </button>
              </div>
            ) : (
              <form onSubmit={handleEnroll} className="space-y-3 text-xs">
                <div>
                  <label className="block text-gray-400 mb-1">Sensor Name</label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full bg-black/60 border border-gray-700 rounded p-2 text-white"
                    placeholder="e.g. Core App Cluster Tap"
                  />
                </div>
                <div>
                  <label className="block text-gray-400 mb-1">Hostname</label>
                  <input
                    type="text"
                    required
                    value={hostname}
                    onChange={(e) => setHostname(e.target.value)}
                    className="w-full bg-black/60 border border-gray-700 rounded p-2 text-white"
                    placeholder="node-01.k8s.internal"
                  />
                </div>
                <div>
                  <label className="block text-gray-400 mb-1">IP Address</label>
                  <input
                    type="text"
                    required
                    value={ipAddress}
                    onChange={(e) => setIpAddress(e.target.value)}
                    className="w-full bg-black/60 border border-gray-700 rounded p-2 text-white"
                    placeholder="10.244.0.15"
                  />
                </div>
                <div>
                  <label className="block text-gray-400 mb-1">OS / Platform</label>
                  <select
                    value={osType}
                    onChange={(e) => setOsType(e.target.value)}
                    className="w-full bg-black/60 border border-gray-700 rounded p-2 text-white"
                  >
                    <option value="linux">Linux (eBPF / Netfilter)</option>
                    <option value="windows">Windows (ETW / WinPcap)</option>
                    <option value="macos">macOS (EndpointSecurity)</option>
                    <option value="k8s">Kubernetes DaemonSet</option>
                  </select>
                </div>
                <div className="flex justify-end space-x-2 pt-3">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-black font-bold rounded"
                  >
                    Enroll Sensor
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
