import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { WebSocketProvider } from './context/WebSocketContext';
import { useAuth } from './hooks/useAuth';
import { Navbar } from './components/common/Navbar';
import { Sidebar } from './components/common/Sidebar';

import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { GuidePage } from './pages/Guide';
import { Prediction } from './pages/Prediction';
import { Reports } from './pages/Reports';
import { HistoryPage } from './pages/History';
import { UsersPage } from './pages/Users';
import { SettingsPage } from './pages/Settings';
import { AboutPage } from './pages/About';
import { AssetsPage } from './pages/Assets';
import { AlertsPage } from './pages/Alerts';
import { IncidentDetailPage } from './pages/IncidentDetail';
import { MonitoringView } from './pages/MonitoringView';
import { ThreatIntelView } from './pages/ThreatIntelView';
import { InvestigationsView } from './pages/InvestigationsView';
import { AnalyticsView } from './pages/AnalyticsView';

// Phase 3 Advanced SOC Pages
import { ThreatHunting } from './pages/ThreatHunting';
import { PredictiveAnalytics } from './pages/PredictiveAnalytics';
import { ThreatGraph } from './pages/ThreatGraph';
import { AttackCoverage } from './pages/AttackCoverage';
import { SOCAnalytics } from './pages/SOCAnalytics';
import { ResponseCenter } from './pages/ResponseCenter';

// Phase 4 Enterprise SaaS Pages
import { OrganizationsPage } from './pages/Organizations';
import { BillingPage } from './pages/Billing';
import { ApiKeysPage } from './pages/ApiKeys';
import { IntegrationsPage } from './pages/Integrations';
import { SensorsPage } from './pages/Sensors';
import { OnboardingPage } from './pages/Onboarding';

// Phase 5 Enterprise Security Center
import { SecurityCenterPage } from './pages/SecurityCenter';

// Phase 9 AI Security Copilot
import { AICopilotPage } from './pages/AICopilot';

// Phase 16 Production Intelligence & Value Pages
import { DetectionQuality } from './pages/DetectionQuality';
import { AlertQueue } from './pages/AlertQueue';
import { SecurityValue } from './pages/SecurityValue';
import { TelemetryCost } from './pages/TelemetryCost';
import { Benchmarking } from './pages/Benchmarking';

// Phase 17 Autonomous Response & Continuous Security Validation Pages
import { SecurityAutomation } from './pages/SecurityAutomation';
import { ResponseApprovals } from './pages/ResponseApprovals';
import { SecurityValidation } from './pages/SecurityValidation';

// Phase 18 Threat Intelligence Platform
import { ThreatIntelligenceCenter } from './pages/ThreatIntelligenceCenter';

// Phase 19 Autonomous SOC & SOAR 2.0 Command Center
import { SOARCommandCenter } from './pages/SOARCommandCenter';








const ProtectedLayout: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="app-shell min-h-screen flex items-center justify-center font-mono text-cyan-400 text-xs">
        <div className="animate-pulse">INITIALIZING AEGIVANTA CORE...</div>
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
          <Sidebar />
          <main className="flex-1 p-6 overflow-y-auto w-full">
            <Routes>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/alerts" element={<AlertsPage />} />
              <Route path="/assets" element={<AssetsPage />} />
              <Route path="/monitoring" element={<MonitoringView />} />
              <Route path="/threat-intel" element={<ThreatIntelView />} />
              <Route path="/investigations" element={<InvestigationsView />} />
              <Route path="/incidents/:id" element={<IncidentDetailPage />} />
              <Route path="/analytics" element={<AnalyticsView />} />
              <Route path="/threat-hunting" element={<ThreatHunting />} />
              <Route path="/predictive-analytics" element={<PredictiveAnalytics />} />
              <Route path="/threat-graph" element={<ThreatGraph />} />
              <Route path="/attack-coverage" element={<AttackCoverage />} />
              <Route path="/soc-analytics" element={<SOCAnalytics />} />
              <Route path="/response-center" element={<ResponseCenter />} />
              <Route path="/copilot" element={<AICopilotPage />} />
              <Route path="/security-center" element={<SecurityCenterPage />} />
              <Route path="/detection-quality" element={<DetectionQuality />} />
              <Route path="/alert-queue" element={<AlertQueue />} />
              <Route path="/security-value" element={<SecurityValue />} />
              <Route path="/telemetry-cost" element={<TelemetryCost />} />
              <Route path="/benchmarking" element={<Benchmarking />} />

              <Route path="/security-automation" element={<SecurityAutomation />} />
              <Route path="/response-approvals" element={<ResponseApprovals />} />
              <Route path="/security-validation" element={<SecurityValidation />} />
              <Route path="/threat-intelligence-center" element={<ThreatIntelligenceCenter />} />
              <Route path="/soar-command-center" element={<SOARCommandCenter />} />




              <Route path="/organizations" element={<OrganizationsPage />} />
              <Route path="/billing" element={<BillingPage />} />
              <Route path="/api-keys" element={<ApiKeysPage />} />
              <Route path="/integrations" element={<IntegrationsPage />} />
              <Route path="/sensors" element={<SensorsPage />} />
              <Route path="/onboarding" element={<OnboardingPage />} />

              <Route path="/guide" element={<GuidePage />} />

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
