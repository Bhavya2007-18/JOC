import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { connectWebSocket, disconnectWebSocket } from './lib/websocket';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { System } from './pages/System';
import { Storage } from './pages/Storage';
import { Tweaks } from './pages/Tweaks';
import { History } from './pages/History';
import { ProtocolReport } from './pages/ProtocolReport';
import { Security } from './pages/Security';
import { Cognition } from './pages/Cognition';
import Report from './pages/Report';
import { ErrorBoundary } from './components/ErrorBoundary';
import { systemApi } from './api/client';
import useSystemStore from './store/useSystemStore';

function App() {
  const setStoreState = useSystemStore((state) => state.setState);

  useEffect(() => {
    connectWebSocket();
    return () => {
      disconnectWebSocket();
    };
  }, []);

  useEffect(() => {
    let mounted = true;
    Promise.allSettled([
      systemApi.getThermalState(),
      systemApi.getThermalPrediction(),
    ]).then((results) => {
      if (!mounted) return;
      const thermal =
        results[0].status === 'fulfilled' ? results[0].value?.data || null : null;
      const thermalPrediction =
        results[1].status === 'fulfilled' ? results[1].value?.data || null : null;
      setStoreState({ thermal, thermalPrediction });
    });
    return () => {
      mounted = false;
    };
  }, [setStoreState]);

  return (
    <Router>
      <ErrorBoundary>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="system" element={<System />} />
            <Route path="storage" element={<Storage />} />
            <Route path="tweaks" element={<Tweaks />} />
            <Route path="history" element={<History />} />
            <Route path="report" element={<ProtocolReport />} />
            <Route path="security" element={<Security />} />
            <Route path="intelligence" element={<Cognition />} />
            <Route path="session-report" element={<Report />} />
          </Route>
        </Routes>
      </ErrorBoundary>
    </Router>
  );
}

export default App;
