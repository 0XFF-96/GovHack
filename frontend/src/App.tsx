import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, App as AntdApp } from 'antd';
import enUS from 'antd/locale/en_US';

// Layout and Common Components
import { MainLayout } from './layouts/MainLayout';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { LoadingSpinner } from './components/common/LoadingSpinner';

// Pages (lazy loaded for better performance)
const ChatPage = React.lazy(() => import('./pages/ChatPage').then(module => ({ default: module.ChatPage })));
const DashboardPage = React.lazy(() => import('./pages/DashboardPage').then(module => ({ default: module.DashboardPage })));
const DatasetsPage = React.lazy(() => import('./pages/DatasetsPage').then(module => ({ default: module.DatasetsPage })));
const SettingsPage = React.lazy(() => import('./pages/SettingsPage').then(module => ({ default: module.SettingsPage })));

// Ant Design theme configuration
const theme = {
  token: {
    colorPrimary: '#0066CC', // Government blue
    borderRadius: 8,
    fontFamily: '"Inter", -apple-system, system-ui, sans-serif',
  },
  components: {
    Layout: {
      headerBg: '#ffffff',
      siderBg: '#ffffff',
      bodyBg: '#f8fafc',
    },
    Menu: {
      itemBg: 'transparent',
      itemSelectedBg: '#e6f4ff',
      itemSelectedColor: '#0066CC',
      itemHoverBg: '#f0f9ff',
    },
    Card: {
      paddingLG: 24,
      boxShadowTertiary: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    },
  },
};

function App() {
  return (
    <ErrorBoundary>
      <ConfigProvider theme={theme} locale={enUS}>
        <AntdApp>
          <Router>
            <MainLayout>
              <Suspense fallback={<LoadingSpinner fullscreen tip="Loading page..." />}>
                <Routes>
                  {/* Default route redirects to chat */}
                  <Route path="/" element={<ChatPage />} />
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/datasets" element={<DatasetsPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                  
                  {/* Catch-all route redirects to home */}
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Suspense>
            </MainLayout>
          </Router>
        </AntdApp>
      </ConfigProvider>
    </ErrorBoundary>
  );
}

export default App;