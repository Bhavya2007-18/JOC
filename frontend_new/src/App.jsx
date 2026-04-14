import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { connectWebSocket, disconnectWebSocket } from './lib/websocket';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { System } from './pages/System';
import { Storage } from './pages/Storage';
import { Tweaks } from './pages/Tweaks';
import { History } from './pages/History';
import { ErrorBoundary } from './components/ErrorBoundary';

function App() {
  useEffect(() => {
    connectWebSocket();
    return () => {
      disconnectWebSocket();
    };
  }, []);

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
          </Route>
        </Routes>
      </ErrorBoundary>
    </Router>
  );
}

export default App;

