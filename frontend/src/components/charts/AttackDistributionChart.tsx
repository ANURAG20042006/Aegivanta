import React from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';
import { AttackDistributionItem } from '../../types';

ChartJS.register(ArcElement, Tooltip, Legend);

interface AttackDistributionChartProps {
  distribution?: AttackDistributionItem[];
}

export const AttackDistributionChart: React.FC<AttackDistributionChartProps> = ({ distribution }) => {
  const dist = distribution || [];

  if (dist.length === 0) {
    return <div className="h-64 flex items-center justify-center text-xs font-mono text-slate-500">No incident data yet.</div>;
  }

  const chartData = {
    labels: dist.map((d) => d.attack_type),
    datasets: [
      {
        data: dist.map((d) => d.count),
        backgroundColor: [
          '#00FF9D', // BENIGN Green
          '#FF0055', // DDoS Red
          '#FFB800', // DoS Amber
          '#A855F7', // Port Scan Purple
          '#00F0FF', // SQL Cyan
          '#F43F5E', // Anomaly Crimson
        ],
        borderColor: '#0F172A',
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
        labels: {
          color: '#94A3B8',
          font: { family: 'Fira Code', size: 11 },
          padding: 12,
        },
      },
      tooltip: {
        backgroundColor: '#0F172A',
        borderColor: '#334155',
        borderWidth: 1,
      },
    },
  };

  return (
    <div className="h-64 w-full flex items-center justify-center">
      <Doughnut data={chartData} options={options} />
    </div>
  );
};
