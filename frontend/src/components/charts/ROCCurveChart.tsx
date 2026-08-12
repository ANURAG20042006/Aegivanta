import React from 'react';
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend);

export const ROCCurveChart: React.FC = () => {
  const chartData = {
    labels: ['0.0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0'],
    datasets: [
      {
        label: 'XGBoost (Historical Baseline AUC = 0.997)',
        data: [0.0, 0.92, 0.96, 0.98, 0.99, 0.995, 0.998, 1.0, 1.0, 1.0, 1.0],
        borderColor: '#00F0FF',
        borderWidth: 2,
        tension: 0.2,
      },
      {
        label: 'Random Forest (Historical Baseline AUC = 0.994)',
        data: [0.0, 0.88, 0.94, 0.97, 0.985, 0.99, 0.995, 0.998, 1.0, 1.0, 1.0],
        borderColor: '#00FF9D',
        borderWidth: 2,
        tension: 0.2,
      },
      {
        label: 'LSTM DeepNet (Historical Baseline AUC = 0.993)',
        data: [0.0, 0.85, 0.92, 0.95, 0.97, 0.985, 0.99, 0.995, 1.0, 1.0, 1.0],
        borderColor: '#A855F7',
        borderWidth: 2,
        tension: 0.2,
      },
      {
        label: 'Random Baseline (AUC = 0.500)',
        data: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        borderColor: '#64748B',
        borderWidth: 1,
        borderDash: [5, 5],
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          color: '#94A3B8',
          font: { family: 'Fira Code', size: 10 },
        },
      },
    },
    scales: {
      x: {
        title: { display: true, text: 'False Positive Rate (FPR)', color: '#64748B' },
        ticks: { color: '#64748B', font: { family: 'Fira Code', size: 10 } },
        grid: { color: 'rgba(51, 65, 85, 0.3)' },
      },
      y: {
        title: { display: true, text: 'True Positive Rate (TPR)', color: '#64748B' },
        ticks: { color: '#64748B', font: { family: 'Fira Code', size: 10 } },
        grid: { color: 'rgba(51, 65, 85, 0.3)' },
      },
    },
  };

  return (
    <div className="h-64 w-full">
      <Line data={chartData} options={options} />
    </div>
  );
};
