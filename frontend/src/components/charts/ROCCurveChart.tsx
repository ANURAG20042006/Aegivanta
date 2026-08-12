import React, { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { analyticsService } from '../../services/analytics';

ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend);

export const ROCCurveChart: React.FC = () => {
  const [curves, setCurves] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    analyticsService.getROCCurves()
      .then(data => {
        setCurves(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching ROC curves data', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="h-64 w-full flex items-center justify-center text-slate-400 font-mono text-sm">
        Loading ROC data...
      </div>
    );
  }

  const datasets = [];

  if (curves && curves.active_model) {
    const active = curves.active_model;
    datasets.push({
      label: `${active.model_name} (Active Model AUC = ${active.auc ?? 'N/A'})`,
      data: active.tpr,
      borderColor: '#FF7A00',
      borderWidth: 3,
      tension: 0.2,
    });
  }

  if (curves && curves.historical_baselines && curves.historical_baselines.length > 0) {
    const colors = ['#00F0FF', '#00FF9D', '#A855F7'];
    curves.historical_baselines.forEach((model: any, index: number) => {
      datasets.push({
        label: `${model.model_name} (Historical Baseline AUC = ${model.auc})`,
        data: model.tpr,
        borderColor: colors[index % colors.length],
        borderWidth: 2,
        tension: 0.2,
      });
    });
  }

  if (datasets.length === 0) {
    return (
      <div className="h-64 w-full flex items-center justify-center text-slate-500 font-mono text-sm">
        No ROC data available
      </div>
    );
  }

  // Mathematically legitimate reference baseline
  datasets.push({
    label: 'Random Baseline (AUC = 0.500)',
    data: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    borderColor: '#64748B',
    borderWidth: 1,
    borderDash: [5, 5],
  });

  const chartData = {
    labels: ['0.0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0'],
    datasets,
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
