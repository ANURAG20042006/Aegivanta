import React from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';
import { AttackDistributionItem } from '../../types';

ChartJS.register(ArcElement, Tooltip, Legend);

interface AttackDistributionChartProps {
  distribution?: AttackDistributionItem[];
  data?: AttackDistributionItem[];
}

export const AttackDistributionChart: React.FC<AttackDistributionChartProps> = ({ distribution, data }) => {
  const dist = distribution || data || [];

  if (dist.length === 0) {
    return <div className="h-64 flex items-center justify-center text-xs font-mono text-slate-500">No incident data yet.</div>;
  }

  const chartData = {
    labels: dist.map((d) => d.attack_type),
    datasets: [
      {
        data: dist.map((d) => d.count),
        backgroundColor: [
          '#00FF9D',
          '#FF0055',
          '#FFB800',
          '#A855F7',
          '#00F0FF',
          '#F43F5E',
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
    <div className="h-64 w-full bg-slate-900/80 border border-slate-800/80 rounded-xl p-4 backdrop-blur-md flex items-center justify-center">
      <Doughnut data={chartData} options={options} />
    </div>
  );
};
