import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { SnackbarProvider } from 'notistack';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import AlertList from './components/AlertList';
import AlertDetail from './components/AlertDetail';
import CaseList from './components/CaseList';
import CaseDetail from './components/CaseDetail';
import NetworkAnalytics from './components/NetworkAnalytics';
import SanctionsScreening from './components/SanctionsScreening';
import RegulatoryReports from './components/RegulatoryReports';
import AuditLogs from './components/AuditLogs';
import DataSources from './components/DataSources';
import AMLPage from './components/AMLPage';
import FraudPage from './components/FraudPage';
import KYCPage from './components/KYCPage';
import ActOnePage from './components/ActOnePage';
import AIMLPage from './components/AIMLPage';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#1a237e' },
    secondary: { main: '#ff6f00' },
    error: { main: '#d32f2f' },
    warning: { main: '#f57c00' },
    success: { main: '#388e3c' },
    background: { default: '#f5f5f5' },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: { fontWeight: 600 },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: { borderRadius: 12 },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 8, textTransform: 'none', fontWeight: 600 },
      },
    },
  },
});

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider maxSnack={3} anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route
                path="/*"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/alerts" element={<AlertList />} />
                        <Route path="/alerts/:id" element={<AlertDetail />} />
                        <Route path="/cases" element={<CaseList />} />
                        <Route path="/cases/:id" element={<CaseDetail />} />
                        <Route path="/network" element={<NetworkAnalytics />} />
                        <Route path="/sanctions" element={<SanctionsScreening />} />
                        <Route path="/reports" element={<RegulatoryReports />} />
                        <Route path="/audit" element={<AuditLogs />} />
                        <Route path="/aml" element={<AMLPage />} />
                        <Route path="/fraud" element={<FraudPage />} />
                        <Route path="/kyc" element={<KYCPage />} />
                        <Route path="/actone" element={<ActOnePage />} />
                        <Route path="/aiml" element={<AIMLPage />} />
                        <Route path="/admin/data-sources" element={<DataSources />} />
                      </Routes>
                    </Layout>
                  </ProtectedRoute>
                }
              />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </SnackbarProvider>
    </ThemeProvider>
  );
}

export default App;
