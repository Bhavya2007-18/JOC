import { useState, useEffect, useCallback } from 'react';
import { systemApi, intelligenceApi, optimizerApi } from '../api/client';

export function useSystemData(pollingInterval = 2000) {
  const [stats, setStats] = useState(null);
  const [processes, setProcesses] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [events, setEvents] = useState([]);

  const addEvent = useCallback((message, type = 'info') => {
    const newEvent = {
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString(),
      message,
      type
    };
    setEvents(prev => [newEvent, ...prev].slice(0, 50));
  }, []);

  const fetchData = useCallback(async () => {
    try {
      const [statsRes, procRes, anomalyRes, decisionRes] = await Promise.all([
        systemApi.getStats(),
        systemApi.getProcesses(10),
        intelligenceApi.getAnomalies(5),
        intelligenceApi.getDecisions(5)
      ]);

      setStats(statsRes.data);
      setProcesses(procRes.data.top_processes);
      
      // Check for new anomalies to add to event stream
      if (anomalyRes.data.anomalies.length > anomalies.length) {
        const newAnomalies = anomalyRes.data.anomalies.slice(0, anomalyRes.data.anomalies.length - anomalies.length);
        newAnomalies.forEach(a => addEvent(`Anomaly Detected: ${a.description}`, 'warning'));
      }
      
      setAnomalies(anomalyRes.data.anomalies);
      setDecisions(decisionRes.data.decisions);
      setLoading(false);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch system data:', err);
      setError(err.message);
      // Don't set loading to false here to show stale data while retrying
    }
  }, [anomalies.length, addEvent]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, pollingInterval);
    return () => clearInterval(interval);
  }, [fetchData, pollingInterval]);

  return {
    stats,
    processes,
    anomalies,
    decisions,
    loading,
    error,
    events,
    addEvent,
    refresh: fetchData
  };
}
