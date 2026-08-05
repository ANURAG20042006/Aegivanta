import React, { useState } from 'react';
import { FileText, Download, CheckCircle } from 'lucide-react';
import { reportService } from '../services/reports';

export const Reports: React.FC = () => {
  const [selectedFormat, setSelectedFormat] = useState<'pdf' | 'excel' | 'csv'>('pdf');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [reportResult, setReportResult] = useState<any>(null);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setReportResult(null);
    try {
      const res = await reportService.generateReport(selectedFormat);
      setReportResult(res);
    } catch (err) {
      alert('We could not create the report. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = async () => {
    if (!reportResult) return;
    try {
      await reportService.downloadFile(reportResult.download_url);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown download error';
      alert(`Report download failed: ${message}`);
    }
  };

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl">
        <h1 className="text-xl font-mono font-bold text-white">Create a report</h1>
        <p className="text-xs text-slate-400 font-mono mt-1">
          Choose a format to share a clear summary of your network activity and alerts.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* PDF Option */}
        <div
          onClick={() => setSelectedFormat('pdf')}
          className={`glass-panel p-6 rounded-xl cursor-pointer border-2 transition-all ${
            selectedFormat === 'pdf' ? 'border-cyan-400 bg-cyan-500/10' : 'border-slate-800'
          }`}
        >
          <FileText className="w-8 h-8 text-cyan-400 mb-3" />
          <h2 className="text-sm font-mono font-bold text-white">PDF summary</h2>
          <p className="text-xs text-slate-400 mt-2">A polished report for leaders and incident reviews.</p>
        </div>

        {/* Excel Option */}
        <div
          onClick={() => setSelectedFormat('excel')}
          className={`glass-panel p-6 rounded-xl cursor-pointer border-2 transition-all ${
            selectedFormat === 'excel' ? 'border-emerald-400 bg-emerald-500/10' : 'border-slate-800'
          }`}
        >
          <FileText className="w-8 h-8 text-emerald-400 mb-3" />
          <h2 className="text-sm font-mono font-bold text-white">Excel workbook</h2>
          <p className="text-xs text-slate-400 mt-2">A sortable workbook for deeper analysis.</p>
        </div>

        {/* CSV Option */}
        <div
          onClick={() => setSelectedFormat('csv')}
          className={`glass-panel p-6 rounded-xl cursor-pointer border-2 transition-all ${
            selectedFormat === 'csv' ? 'border-purple-400 bg-purple-500/10' : 'border-slate-800'
          }`}
        >
          <FileText className="w-8 h-8 text-purple-400 mb-3" />
          <h2 className="text-sm font-mono font-bold text-white">CSV data</h2>
          <p className="text-xs text-slate-400 mt-2">Raw rows for spreadsheets or other security tools.</p>
        </div>
      </div>

      <div className="glass-panel p-6 rounded-xl text-center space-y-4">
        <button
          onClick={handleGenerate}
          disabled={isGenerating}
          className="px-8 py-3 bg-gradient-to-r from-cyan-500 to-teal-500 text-slate-950 font-mono font-bold text-xs rounded-xl shadow-[0_0_20px_rgba(0,240,255,0.3)] disabled:opacity-50"
        >
          {isGenerating ? 'Creating report...' : `Create ${selectedFormat.toUpperCase()} report`}
        </button>

        {reportResult && (
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/40 text-emerald-400 font-mono text-xs max-w-md mx-auto space-y-3">
            <div className="flex items-center justify-center space-x-2 font-bold">
              <CheckCircle className="w-4 h-4" />
              <span>Your report is ready</span>
            </div>
            <div className="text-slate-300">File: {reportResult.file_name}</div>
            <button
              onClick={handleDownload}
              className="px-4 py-2 bg-emerald-500 text-slate-950 font-bold rounded-lg flex items-center space-x-2 mx-auto"
            >
              <Download className="w-4 h-4" />
              <span>Download {reportResult.format.toUpperCase()}</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
