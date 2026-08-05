import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export const FeatureImportanceChart: React.FC = () => {
  const chartData = {
    labels: [
      'Flow Packets/s',
      'Packet Length Mean',
      'SYN Flag Count',
      'Destination Port',
      'Flow Duration',
      'Bwd Packet Length Std',
      'Total Fwd Packets',
      'ACK Flag Count',
    ],
    datasets: [
      {
        label: 'SHAP Mean Attribution Weight',
        data: [0.42, 0.35, 0.28, 0.22, 0.18, 0.14, 0.11, 0.08],
        backgroundColor: '#00F0FF',
        borderRadius: 4,
      },
    ],
  };

  const options = {
    indexAxis: 'y' as const,
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#0F172A',
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
        grid: { display: false },
        ticks: { color: '#94A3B8', font: { family: 'Fira Code', size: 10 } },
      },
    },
  };

  return (
    <div className="h-64 w-full">
      <Bar data={chartData} options={options} />
    </div>
  );
};
