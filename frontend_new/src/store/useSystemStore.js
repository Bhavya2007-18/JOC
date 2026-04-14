import { create } from 'zustand';

const useSystemStore = create((set) => ({
  systemMode: 'SMART',
  cpuUsage: 0,
  ramUsage: 0,
  threatLevel: 0,
  simulationStatus: 'stopped',
  thermal: null,
  thermalPrediction: null,
  intelligence: null,
  events: [],           // live event log (last 100)
  connected: false,     // WebSocket connection health

  setState: (data) => set(data),
  setIntelligenceUpdate: (payload) =>
    set(() => ({
      intelligence: payload,
      thermal: payload?.thermal || null,
      thermalPrediction: payload?.thermal_prediction || null,
    })),
  addEvent: (event) => set((state) => ({
    events: [event, ...state.events].slice(0, 100)
  })),
}));

export default useSystemStore;
