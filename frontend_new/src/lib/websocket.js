import useSystemStore from '../store/useSystemStore';

let ws = null;
let reconnectWait = 1000;
const MAX_RECONNECT_WAIT = 10000;
let isIntentionalDisconnect = false;

export function connectWebSocket() {
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    return;
  }
  
  isIntentionalDisconnect = false;
  
  // Connect to the WebSocket
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  // Allow overriding host for prod
  const host = window.location.hostname === 'localhost' ? 'localhost:8000' : window.location.host;
  ws = new WebSocket(`${protocol}://${host}/ws/live`);

  ws.onopen = () => {
    useSystemStore.getState().setState({ connected: true });
    reconnectWait = 1000; // reset
  };

  ws.onmessage = (event) => {
    try {
      const parsed = JSON.parse(event.data);
      if (parsed.type === 'state_update') {
        const stateData = parsed.data;
        useSystemStore.getState().setState({
          systemMode: stateData.mode,
          cpuUsage: stateData.cpu_usage,
          ramUsage: stateData.ram_usage,
          threatLevel: stateData.threat_level,
          simulationStatus: stateData.simulation_status,
        });
      } else if (parsed.type === 'event') {
        useSystemStore.getState().addEvent(parsed.data);
      }
    } catch (err) {
      console.error('Error parsing WS message:', err);
    }
  };

  ws.onclose = () => {
    useSystemStore.getState().setState({ connected: false });
    ws = null;
    if (!isIntentionalDisconnect) {
      setTimeout(connectWebSocket, reconnectWait);
      reconnectWait = Math.min(reconnectWait * 2, MAX_RECONNECT_WAIT);
    }
  };

  ws.onerror = (err) => {
    console.error('WS error:', err);
    if(ws) ws.close();
  };
}

export function disconnectWebSocket() {
  isIntentionalDisconnect = true;
  if (ws) {
    ws.close();
    ws = null;
  }
}
