import React, { useEffect, useRef } from 'react';

interface Node {
  id: string;
  label: string;
  x: number;
  y: number;
  type: 'firewall' | 'server' | 'database' | 'attacker' | 'endpoint';
  status: 'normal' | 'warning' | 'critical';
}

interface Connection {
  from: string;
  to: string;
  active: boolean;
  isMalicious: boolean;
}

export const NetworkTopologyCanvas: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;

    const width = (canvas.width = canvas.parentElement?.clientWidth || 800);
    const height = (canvas.height = 280);

    const nodes: Node[] = [
      { id: 'fw1', label: 'EDGE-FW-01', x: width * 0.15, y: height * 0.5, type: 'firewall', status: 'normal' },
      { id: 'srv1', label: 'APP-SRV-01', x: width * 0.4, y: height * 0.25, type: 'server', status: 'normal' },
      { id: 'srv2', label: 'APP-SRV-02', x: width * 0.4, y: height * 0.75, type: 'server', status: 'normal' },
      { id: 'db1', label: 'CORE-DB-01', x: width * 0.65, y: height * 0.5, type: 'database', status: 'normal' },
      { id: 'atk1', label: 'EXT-192.168.1.105', x: width * 0.88, y: height * 0.2, type: 'attacker', status: 'critical' },
      { id: 'ep1', label: 'ANALYST-WS', x: width * 0.88, y: height * 0.8, type: 'endpoint', status: 'normal' },
    ];

    const connections: Connection[] = [
      { from: 'fw1', to: 'srv1', active: true, isMalicious: false },
      { from: 'fw1', to: 'srv2', active: true, isMalicious: false },
      { from: 'srv1', to: 'db1', active: true, isMalicious: false },
      { from: 'srv2', to: 'db1', active: true, isMalicious: false },
      { from: 'atk1', to: 'fw1', active: true, isMalicious: true },
      { from: 'ep1', to: 'db1', active: true, isMalicious: false },
    ];

    let step = 0;

    const render = () => {
      try {
        ctx.clearRect(0, 0, width, height);

        // Draw Grid Background
        ctx.strokeStyle = 'rgba(30, 41, 59, 0.4)';
        ctx.lineWidth = 1;
        const gridSize = 30;
        for (let x = 0; x < width; x += gridSize) {
          ctx.beginPath();
          ctx.moveTo(x, 0);
          ctx.lineTo(x, height);
          ctx.stroke();
        }
        for (let y = 0; y < height; y += gridSize) {
          ctx.beginPath();
          ctx.moveTo(0, y);
          ctx.lineTo(width, y);
          ctx.stroke();
        }

        // Draw Connections
        connections.forEach((conn) => {
          const fromNode = nodes.find((n) => n.id === conn.from);
          const toNode = nodes.find((n) => n.id === conn.to);
          if (!fromNode || !toNode) return;

          ctx.beginPath();
          ctx.moveTo(fromNode.x, fromNode.y);
          ctx.lineTo(toNode.x, toNode.y);
          ctx.strokeStyle = conn.isMalicious ? 'rgba(239, 68, 68, 0.6)' : 'rgba(59, 130, 246, 0.4)';
          ctx.lineWidth = conn.isMalicious ? 2 : 1.5;
          ctx.setLineDash(conn.isMalicious ? [6, 4] : []);
          ctx.stroke();
          ctx.setLineDash([]);

          const progress = ((step * (conn.isMalicious ? 0.02 : 0.012)) % 1);
          const px = fromNode.x + (toNode.x - fromNode.x) * progress;
          const py = fromNode.y + (toNode.y - fromNode.y) * progress;

          ctx.beginPath();
          ctx.arc(px, py, conn.isMalicious ? 5 : 3.5, 0, Math.PI * 2);
          ctx.fillStyle = conn.isMalicious ? '#EF4444' : '#60A5FA';
          ctx.fill();
        });

        // Draw Nodes
        nodes.forEach((node) => {
          ctx.beginPath();
          ctx.arc(node.x, node.y, 16, 0, Math.PI * 2);

          let color = '#3B82F6';
          if (node.status === 'critical') color = '#EF4444';
          if (node.status === 'warning') color = '#F59E0B';

          ctx.fillStyle = '#0F172A';
          ctx.strokeStyle = color;
          ctx.lineWidth = 2.5;
          ctx.fill();
          ctx.stroke();

          ctx.beginPath();
          ctx.arc(node.x, node.y, 6, 0, Math.PI * 2);
          ctx.fillStyle = color;
          ctx.fill();

          ctx.font = '11px Inter, sans-serif';
          ctx.fillStyle = '#94A3B8';
          ctx.textAlign = 'center';
          ctx.fillText(node.label, node.x, node.y + 32);
        });

        step++;
        animationFrameId = requestAnimationFrame(render);
      } catch (err) {
        // Suppress canvas render exceptions gracefully
      }
    };

    render();

    return () => {
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div className="relative w-full bg-slate-950/80 rounded-xl border border-slate-800/80 p-4 backdrop-blur-md overflow-hidden">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <div className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">Live Network Node Topology & Attack Vectors</h3>
        </div>
        <div className="flex items-center space-x-4 text-xs">
          <span className="flex items-center space-x-1 text-slate-400">
            <span className="w-2 h-2 rounded-full bg-blue-500 inline-block"></span>
            <span>Normal Flow</span>
          </span>
          <span className="flex items-center space-x-1 text-slate-400">
            <span className="w-2 h-2 rounded-full bg-red-500 inline-block animate-ping"></span>
            <span className="text-red-400 font-medium">Malicious Intrusion Stream</span>
          </span>
        </div>
      </div>
      <canvas ref={canvasRef} className="w-full h-[280px] rounded-lg" />
    </div>
  );
};
