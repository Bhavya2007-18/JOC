import { useState, useEffect, useCallback, useRef } from 'react';
import { systemApi, intelligenceApi } from '../api/client';
import useSystemStore from '../store/useSystemStore';

export function useSystemData(pollingInterval = 15000) {
  const [stats, setStats] = useState(null);
  const [processes, setProcesses] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [decisions, setDecisions] = useState([]);
  const [health, setHealth] = useState(100);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [events, setEvents] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [causalGraph, setCausalGraph] = useState(null);
  const previousCpuByPid = useRef({});
  const setStoreState = useSystemStore((state) => state.setState);

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
      const res = await systemApi.analyze();
      const data = res.data;

      if (data.summary) {
        setStats({
          cpu: { usage_percent: data.summary.cpu_percent || 0 },
          memory: { percent: data.summary.memory_percent || 0 },
          disk: { percent: data.summary.disk_percent || 0 }
        });
      }

      try {
        const procRes = await systemApi.getProcesses(20);
        if (procRes.data && procRes.data.top_processes) {
          setProcesses(procRes.data.top_processes);
        }
      } catch (err) {
        console.error("Failed to fetch processes", err);
      }

      setAnomalies(data.issues);
      setDecisions(data.issues);
      setHealth(Number(data.system_health_score || 0));

      const seen = new Set();
      if (Array.isArray(data.changes)) {
        data.changes.forEach(change => {
          const key = `${change.type}-${change.name}`;
          if (!seen.has(key)) {
            addEvent(`${change.type}: ${change.name || ''}`, 'info');
            seen.add(key);
          }
        });
      }

      try {
        const timelineRes = await systemApi.getTimeline(10);
        if (timelineRes.data && timelineRes.data.events) {
            setEvents(timelineRes.data.events.map(ev => ({
              id: ev.timestamp,
              timestamp: new Date(ev.timestamp * 1000).toLocaleTimeString(),
              message: ev.message,
              type: ev.event_type || 'info'
            })));
        }
      } catch (err) {
        // Timeline fetch failed
      }

      try {
        const forecastRes = await intelligenceApi.getForecast();
        if (forecastRes.data && !forecastRes.data.status) {
           setForecast(forecastRes.data);
        }
      } catch (err) {}

      try {
        const [thermalRes, thermalPredictionRes] = await Promise.all([
          systemApi.getThermalState(),
          systemApi.getThermalPrediction(),
        ]);
        setStoreState({
          thermal: thermalRes?.data || null,
          thermalPrediction: thermalPredictionRes?.data || null,
        });
      } catch (err) {
        // Keep stale thermal state if fallback fetch fails.
      }

      try {
        const cgRes = await intelligenceApi.getCausalGraph();
        if (cgRes.data) {
           setCausalGraph(cgRes.data);
        }
      } catch (err) {}

      setLoading(false);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch system data:', err);
      setError(err.message);
      // Don't set loading to false here to show stale data while retrying
    }
  }, [addEvent, setStoreState]);

  useEffect(() => {
    let isMounted = true;

    const poll = async () => {
      while (isMounted) {
        await fetchData(); // wait for request to finish
        await new Promise(res => setTimeout(res, pollingInterval));
      }
    };

    poll();

    return () => {
      isMounted = false;
    };
  }, [fetchData, pollingInterval]);

  return {
    stats,
    processes,
    anomalies,
    decisions,
    health,
    loading,
    error,
    events,
    forecast,
    causalGraph,
    addEvent,
    refresh: fetchData
  };
}
