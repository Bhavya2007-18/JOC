import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import { systemApi } from '../api/client';
import { useSystemData } from '../hooks/useSystemData';
import useSystemStore from '../store/useSystemStore';

const SystemModeContext = createContext();

export function SystemModeProvider({ children }) {
  const [systemMode, setSystemModeState] = useState('smart');
  const [visualIntensity, setVisualIntensity] = useState(0.5);
  const [targetIntensity, setTargetIntensity] = useState(0.5);
  const { stats } = useSystemData(3000);
  const thermal = useSystemStore((state) => state.thermal);
  const thermalPrediction = useSystemStore((state) => state.thermalPrediction);

  // Sync with backend on mount
  useEffect(() => {
    systemApi.getMode().then(res => {
      if (res.data?.mode) {
        setSystemModeState(res.data.mode);
      }
    }).catch(() => {});
  }, []);

  const setSystemMode = useCallback(async (mode) => {
    const previousMode = systemMode;
    // Optimistic update for immediate UI responsiveness.
    setSystemModeState(mode);
    try {
      const res = await systemApi.setMode(mode);
      const effectiveMode = res?.data?.mode || mode;
      if (effectiveMode !== mode) {
        setSystemModeState(effectiveMode);
      }
      return res?.data || { mode: effectiveMode };
    } catch (err) {
      // Roll back UI if backend rejects the switch.
      setSystemModeState(previousMode);
      console.error('Failed to update system mode:', err);
      throw err;
    }
  }, [systemMode]);

  // Soft interpolation for Visual Intensity
  useEffect(() => {
    const modeBase = {
      chill: 0.15,
      smart: 0.45,
      beast: 0.85
    }[systemMode];

    const cpuLoad = (stats?.cpu?.usage_percent || 0) / 100;
    const nextTarget = Math.min(1, Math.max(0, modeBase + (cpuLoad * 0.25)));
    setTargetIntensity(nextTarget);
  }, [systemMode, stats]);

  // Smooth lerp for intensity to prevent jumps
  useEffect(() => {
    let frame;
    const lerp = () => {
      setVisualIntensity(prev => {
        const diff = targetIntensity - prev;
        if (Math.abs(diff) < 0.001) return targetIntensity;
        return prev + diff * 0.05; // Smoothing factor
      });
      frame = requestAnimationFrame(lerp);
    };
    frame = requestAnimationFrame(lerp);
    return () => cancelAnimationFrame(frame);
  }, [targetIntensity]);

  const value = useMemo(() => ({
    systemMode,
    setSystemMode,
    visualIntensity,
    telemetry: {
      cpu: stats?.cpu?.usage_percent || 0,
      memory: stats?.memory?.percent || 0,
      thermalState: thermal?.state || 'COOL',
      thermalRisk: thermalPrediction?.risk || 'SAFE',
    }
  }), [systemMode, setSystemMode, visualIntensity, stats, thermal, thermalPrediction]);

  return (
    <SystemModeContext.Provider value={value}>
      {children}
    </SystemModeContext.Provider>
  );
}

export function useSystemMode() {
  const context = useContext(SystemModeContext);
  if (!context) {
    throw new Error('useSystemMode must be used within a SystemModeProvider');
  }
  return context;
}
