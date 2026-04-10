import { useState, useEffect, useCallback, useRef } from 'react';
import { systemApi } from '../api/client';

export function useSystemData(pollingInterval = 2000) {
  const [stats, setStats] = useState(null);
  const [processes, setProcesses] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [decisions, setDecisions] = useState([]);
  const [health, setHealth] = useState(100);
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

      setProcesses(
        data.issues.flatMap(issue =>
          (issue.affected_processes || []).map(p => ({
            name: p.name,
            pid: p.pid
          }))
        )
      );

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

      setLoading(false);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch system data:', err);
      setError(err.message);
      // Don't set loading to false here to show stale data while retrying
    }
  }, [addEvent]);

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
    addEvent,
    refresh: fetchData
  };
}
