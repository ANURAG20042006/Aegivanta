import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { WebSocketProvider } from './context/WebSocketContext';
import { useAuth } from './hooks/useAuth';
import { Navbar } from './components/common/Navbar';

import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Analytics } from './pages/Analytics';
import { Prediction } from './pages/Prediction';
import { Reports } from './pages/Reports';
import { HistoryPage } from './pages/History';
import { UsersPage } from './pages/Users';
import { SettingsPage } from './pages/Settings';
import { AboutPage } from './pages/About';

const ProtectedLayout: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="app-shell min-h-screen flex items-center justify-center font-mono text-cyan-400 text-xs">
        <div className="animate-pulse">INITIALIZING SENTINELAI CORE...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <WebSocketProvider>
      <div className="app-shell min-h-screen flex flex-col">
        <Navbar />
        <div className="flex flex-1">
          <main className="flex-1 p-6 overflow-y-auto max-w-7xl mx-auto w-full">
            <Routes>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/prediction" element={<Prediction />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route path="/users" element={<UsersPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </WebSocketProvider>
  );
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/*" element={<ProtectedLayout />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
