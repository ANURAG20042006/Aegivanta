import React, { useMemo, useState } from 'react';
import { Activity, ShieldCheck } from 'lucide-react';
import { useTheme } from '../../hooks/useTheme';

interface SentinelOrbProps {
  threatCount?: number;
  status?: string;
}

export const SentinelOrb: React.FC<SentinelOrbProps> = ({ threatCount = 0, status = 'MONITORING' }) => {
  const { theme } = useTheme();
  const [rotation, setRotation] = useState({ x: -8, y: 18 });
  const isCritical = status === 'CRITICAL' || threatCount > 0;
  const orbitStyle = useMemo(() => ({ transform: `rotateX(${rotation.x}deg) rotateY(${rotation.y}deg)` }), [rotation]);

  const handlePointerMove = (event: React.PointerEvent<HTMLDivElement>) => {
    const bounds = event.currentTarget.getBoundingClientRect();
    const x = ((event.clientX - bounds.left) / bounds.width - 0.5) * 26;
    const y = ((event.clientY - bounds.top) / bounds.height - 0.5) * -26;
    setRotation({ x: y - 8, y: x + 18 });
  };

  return (
    <div
      className={`sentinel-orb-stage theme-${theme}`}
      onPointerMove={handlePointerMove}
      onPointerLeave={() => setRotation({ x: -8, y: 18 })}
      aria-label="Interactive 3D Aegivanta status orb"
    >
      <div className="sentinel-orb-grid" />
      <div className={`sentinel-orb ${isCritical ? 'is-critical' : ''}`} style={orbitStyle}>
        <div className="orb-ring orb-ring-outer" />
        <div className="orb-ring orb-ring-middle" />
        <div className="orb-ring orb-ring-inner" />
        <div className="orb-core">
          <ShieldCheck className="w-7 h-7" />
          <span className="text-[8px] font-mono tracking-[0.16em]">AEGIVANTA</span>
          <span className="text-[10px] font-mono font-bold">{isCritical ? 'THREAT' : 'SECURE'}</span>
        </div>
        <div className="orb-scanline" />
      </div>
      <div className="orb-readout">
        <span><Activity className="w-3 h-3" /> {status}</span>
        <span>{threatCount} ACTIVE SIGNAL{threatCount === 1 ? '' : 'S'}</span>
      </div>
    </div>
  );
};
