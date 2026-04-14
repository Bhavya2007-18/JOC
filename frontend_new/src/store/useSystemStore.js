import { create } from 'zustand';

const useSystemStore = create((set) => ({
  systemMode: 'SMART',
  cpuUsage: 0,
  ramUsage: 0,
  threatLevel: 0,
  simulationStatus: 'stopped',
  events: [],           // live event log (last 100)
  connected: false,     // WebSocket connection health

  setState: (data) => set(data),
  addEvent: (event) => set((state) => ({
    events: [event, ...state.events].slice(0, 100)
  })),
}));

export default useSystemStore;
