import React, { ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  public state: ErrorBoundaryState = { hasError: false };

  public static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('Aegivanta screen error:', error, errorInfo);
  }

  public render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="app-shell min-h-screen flex items-center justify-center p-6">
          <div className="glass-panel-glow max-w-md w-full p-7 rounded-2xl text-center space-y-4">
            <div className="w-11 h-11 mx-auto rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400"><AlertTriangle className="w-5 h-5" /></div>
            <div>
              <h1 className="text-lg font-semibold text-white">Something needs a refresh</h1>
              <p className="mt-2 text-xs text-slate-400">Aegivanta could not display this screen. Your account and saved data are safe.</p>
            </div>
            <button type="button" onClick={() => window.location.reload()} className="mx-auto px-4 py-2 rounded-lg bg-cyan-500 text-slate-950 text-xs font-bold inline-flex items-center gap-2"><RefreshCw className="w-3.5 h-3.5" />Reload app</button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
