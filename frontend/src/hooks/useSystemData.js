import { useState, useEffect, useCallback, useRef } from 'react';
import { systemApi, intelligenceApi } from '../api/client';

export function useSystemData(pollingInterval = 2000) {
  const [stats, setStats] = useState(null);
  const [processes, setProcesses] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [events, setEvents] = useState([]);
  const previousCpuByPid = useRef({});

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
    let attempts = 0;
    while (attempts < 3) {
      try {
        const [statsRes, procRes, anomalyRes, decisionRes] = await Promise.all([
          systemApi.safeStats(),
          systemApi.safeProcesses(10),
          intelligenceApi.safeAnomalies(5),
          intelligenceApi.safeDecisions(5)
        ]);

        if (statsRes.status === 'success') {
          setStats(statsRes.data);
        }
        if (procRes.status === 'success') {
          const incoming = procRes.data.top_processes || [];
          const prevMap = previousCpuByPid.current || {};
          const nextMap = {};
          const withTrend = incoming.map((p) => {
            const prevCpu = prevMap[p.pid];
            let trend = 'flat';
            if (typeof prevCpu === 'number') {
              if (p.cpu_percent > prevCpu) trend = 'up';
              else if (p.cpu_percent < prevCpu) trend = 'down';
            }
            nextMap[p.pid] = p.cpu_percent;
            return { ...p, trend };
          });
          previousCpuByPid.current = nextMap;
          setProcesses(withTrend);
        }

        if (anomalyRes.status === 'success') {
          const anomaliesData = anomalyRes.data.anomalies;
          if (anomaliesData.length > anomalies.length) {
            const newAnomalies = anomaliesData.slice(0, anomaliesData.length - anomalies.length);
            newAnomalies.forEach(a => addEvent(`Anomaly Detected: ${a.description}`, 'warning'));
          }
          setAnomalies(anomaliesData);
        }

        if (decisionRes.status === 'success') {
          setDecisions(decisionRes.data.decisions);
        }

        setLoading(false);
        setError(null);
        return;
      } catch (err) {
        attempts += 1;
        if (attempts >= 3) {
          setError(err.message || 'Failed to refresh system data.');
          return;
        }
        await new Promise((resolve) => setTimeout(resolve, 500));
      }
    }
  }, [anomalies.length, addEvent]);

  useEffect(() => {
    const immediate = setTimeout(() => {
      fetchData();
    }, 0);
    const interval = setInterval(fetchData, pollingInterval);
    return () => {
      clearTimeout(immediate);
      clearInterval(interval);
    };
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
