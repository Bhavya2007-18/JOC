import { create } from 'zustand';

const useSystemStore = create((set) => ({
  systemMode: 'SMART',
  cpuUsage: 0,
  ramUsage: 0,
  threatLevel: 0,
  simulationStatus: 'stopped',
  events: [],           // live event log (last 100)
  connected: false,     // WebSocket connection health
  
  // Phase 1: Sentient Telemetry Data
  intelligenceFeed: null,
  autonomyFeed: null,

  setState: (data) => set(data),
  addEvent: (event) => set((state) => ({
    events: [event, ...state.events].slice(0, 100)
  })),
  setIntelligenceFeed: (data) => set({ intelligenceFeed: data }),
  setAutonomyFeed: (data) => set({ autonomyFeed: data }),
}));

export default useSystemStore;
