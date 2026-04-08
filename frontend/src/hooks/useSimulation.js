import { useState, useCallback, useRef, useEffect } from 'react';
import { simulationApi } from '../api/client';

export function useSimulation() {
  const [isRunning, setIsRunning] = useState(false);
  const [report, setReport] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);
  const pollingRef = useRef(null);

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  }, []);

  const fetchReport = useCallback(async (simulationId) => {
    try {
      const res = await simulationApi.getReport(simulationId);
      setReport(res.data);
      if (res.data.status === 'completed' || res.data.status === 'failed') {
        setIsRunning(false);
        stopPolling();
      }
    } catch (err) {
      console.error('Failed to fetch simulation report:', err);
      setError(err.message);
      setIsRunning(false);
      stopPolling();
    }
  }, [stopPolling]);

  const runSimulation = useCallback(async (payload) => {
    setIsRunning(true);
    setReport(null);
    setError(null);
    try {
      const res = await simulationApi.run(payload);
      const simulationId = res.data.simulation_id;
      
      // Start polling for report
      pollingRef.current = setInterval(() => fetchReport(simulationId), 1000);
      return res.data;
    } catch (err) {
      console.error('Failed to run simulation:', err);
      setError(err.message);
      setIsRunning(false);
      return null;
    }
  }, [fetchReport]);

  const stopSimulation = useCallback(async (reason = 'User stopped') => {
    try {
      await simulationApi.stop(reason);
      setIsRunning(false);
      stopPolling();
    } catch (err) {
      console.error('Failed to stop simulation:', err);
      setError(err.message);
    }
  }, [stopPolling]);

  const fetchHistory = useCallback(async () => {
    try {
      const res = await simulationApi.getHistory();
      setHistory(res.data.reports);
    } catch (err) {
      console.error('Failed to fetch simulation history:', err);
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    return () => stopPolling();
  }, [stopPolling]);

  return {
    isRunning,
    report,
    history,
    error,
    runSimulation,
    stopSimulation,
    fetchHistory
  };
}
