import React from 'react';

export const ConfusionMatrixChart: React.FC = () => {
  const classes = ['BENIGN', 'DDoS', 'DoS Hulk', 'Port Scan', 'SQLi'];
  const matrix = [
    [985, 5, 2, 8, 0],
    [3, 272, 4, 1, 0],
    [1, 2, 115, 2, 0],
    [4, 1, 0, 85, 0],
    [0, 0, 0, 1, 49],
  ];

  return (
    <div className="overflow-x-auto">
      <div className="text-xs font-mono text-slate-400 mb-3 flex justify-between items-center">
        <span>PREDICTED CLASS (COLUMNS) vs ACTUAL CLASS (ROWS)</span>
        <span className="text-cyan-400">BENCHMARK: CICIDS2017</span>
      </div>
      <table className="w-full border-collapse font-mono text-xs text-center">
        <thead>
          <tr>
            <th className="p-2 border border-slate-800 bg-slate-900 text-slate-500">Actual \ Pred</th>
            {classes.map((cls) => (
              <th key={cls} className="p-2 border border-slate-800 bg-slate-900 text-cyan-400">
                {cls}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, rIdx) => (
            <tr key={classes[rIdx]}>
              <td className="p-2 border border-slate-800 bg-slate-900 text-slate-300 font-bold">
                {classes[rIdx]}
              </td>
              {row.map((val, cIdx) => {
                const isDiagonal = rIdx === cIdx;
                const bgStyle = isDiagonal
                  ? 'bg-cyan-500/20 text-cyan-300 font-bold border-cyan-500/40'
                  : val > 0
                  ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                  : 'bg-slate-950 text-slate-600 border-slate-900';
                return (
                  <td key={cIdx} className={`p-3 border ${bgStyle}`}>
                    {val}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
