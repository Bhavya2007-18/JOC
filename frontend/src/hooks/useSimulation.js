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

  /**
   * Map backend SimulationReport fields to the shape the frontend expects.
   * Backend uses `state` (SimulationState enum), frontend expects `status`.
   * Backend uses `evaluation.total_score`, frontend expects `score`.
   */
  const mapReport = useCallback((raw) => {
    if (!raw) return null;

    // Map state enum to simple status string
    const stateToStatus = {
      IDLE: 'idle',
      INITIALIZING: 'initializing',
      RUNNING_SIMULATION: 'running',
      OBSERVING: 'observing',
      ANALYZING: 'analyzing',
      COMPLETED: 'completed',
      FAILED: 'failed',
    };

    const status = stateToStatus[raw.state] || raw.state || 'unknown';
    const evaluation = raw.evaluation || {};
    const timeline = raw.timeline || {};
    const metrics = raw.metrics || {};
    const feedback = raw.feedback || {};

    // Collect anomalies from observations
    const anomalies_detected = (raw.observations || [])
      .filter(obs => obs.anomalies_detected || obs.type === 'anomaly')
      .map(obs => obs.message || obs.description || JSON.stringify(obs));

    // If no anomalies from observations, check for any in feedback
    if (anomalies_detected.length === 0 && feedback.anomalies) {
      anomalies_detected.push(...feedback.anomalies);
    }

    // Collect response actions from observations
    const response_actions = (raw.observations || [])
      .filter(obs => obs.action || obs.type === 'action' || obs.type === 'response')
      .map(obs => ({
        action: obs.action || obs.message || obs.description || 'Action taken',
        time: obs.timestamp
          ? new Date(obs.timestamp * 1000).toLocaleTimeString()
          : obs.time || '—',
      }));

    return {
      ...raw,
      status,
      score: evaluation.total_score ?? 0,
      verdict: evaluation.verdict ?? 'unknown',
      detection_score: evaluation.detection_score ?? 0,
      decision_score: evaluation.decision_score ?? 0,
      time_score: evaluation.time_score ?? 0,
      false_negatives: evaluation.false_negatives ?? 0,
      false_positives: evaluation.false_positives ?? 0,
      anomalies_detected: anomalies_detected.length > 0
        ? anomalies_detected
        : (status === 'completed' ? [] : []),
      response_actions: response_actions.length > 0
        ? response_actions
        : (status === 'completed' ? [] : []),
      response_time: metrics.response_time ?? 0,
      detection_delay: metrics.detection_delay ?? 0,
      timeline: {
        ...timeline,
        transitions: timeline.transitions || [],
      },
      feedback,
      attack_plan: raw.attack_plan || null,
    };
  }, []);

  const fetchReport = useCallback(async (simulationId) => {
    try {
      const res = await simulationApi.getReport(simulationId);
      const mapped = mapReport(res.data);
      setReport(mapped);

      if (mapped.status === 'completed' || mapped.status === 'failed') {
        setIsRunning(false);
        stopPolling();
      }
    } catch (err) {
      console.error('Failed to fetch simulation report:', err);
      setError(err.message);
      setIsRunning(false);
      stopPolling();
    }
  }, [stopPolling, mapReport]);

  const runSimulation = useCallback(async (payload) => {
    setIsRunning(true);
    setReport(null);
    setError(null);
    try {
      const res = await simulationApi.run(payload);
      const data = res.data;
      const simulationId = data.simulation_id;

      // If the report came back immediately (synchronous run), map it
      if (data.report) {
        const mapped = mapReport(data.report);
        setReport(mapped);
        if (mapped.status === 'completed' || mapped.status === 'failed') {
          setIsRunning(false);
          return data;
        }
      }

      // Start polling for report
      pollingRef.current = setInterval(() => fetchReport(simulationId), 1000);
      return data;
    } catch (err) {
      console.error('Failed to run simulation:', err);
      setError(err.message);
      setIsRunning(false);
      return null;
    }
  }, [fetchReport, mapReport]);

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
      setHistory((res.data.reports || []).map(mapReport));
    } catch (err) {
      console.error('Failed to fetch simulation history:', err);
      setError(err.message);
    }
  }, [mapReport]);

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
