import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface LiveTrafficChartProps {
  dataPoints?: number[];
  labels?: string[];
}

export const LiveTrafficChart: React.FC<LiveTrafficChartProps> = ({
  dataPoints = [],
  labels = [],
}) => {
  if (dataPoints.length === 0) {
    return <div className="h-64 flex items-center justify-center text-xs font-mono text-slate-500">Waiting for live telemetry...</div>;
  }
  const chartData = {
    labels,
    datasets: [
      {
        label: 'Network Throughput (Packets/sec)',
        data: dataPoints,
        borderColor: '#00F0FF',
        backgroundColor: 'rgba(0, 240, 255, 0.12)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: '#00F0FF',
        pointHoverRadius: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        labels: {
          color: '#94A3B8',
          font: { family: 'Fira Code', size: 11 },
        },
      },
      tooltip: {
        backgroundColor: '#0F172A',
        titleColor: '#00F0FF',
        bodyColor: '#F8FAFC',
        borderColor: '#334155',
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(51, 65, 85, 0.3)' },
        ticks: { color: '#64748B', font: { family: 'Fira Code', size: 10 } },
      },
      y: {
        grid: { color: 'rgba(51, 65, 85, 0.3)' },
        ticks: { color: '#64748B', font: { family: 'Fira Code', size: 10 } },
      },
    },
  };

  return (
    <div className="h-64 w-full">
      <Line data={chartData} options={options} />
    </div>
  );
};
