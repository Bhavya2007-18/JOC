import useSystemStore from '../store/useSystemStore';

let ws = null;
let reconnectWait = 1000;
const MAX_RECONNECT_WAIT = 10000;
let isIntentionalDisconnect = false;
let intelligenceDebounceTimer = null;

function normalizeEvent(eventData) {
  const idSeed = eventData?.timestamp || Date.now();
  const typeRaw = String(
    eventData?.event_type || eventData?.type || eventData?.severity || 'info'
  ).toLowerCase();
  const mappedType =
    typeRaw.includes('warn') || typeRaw.includes('critical')
      ? 'warning'
      : typeRaw.includes('success')
        ? 'success'
        : typeRaw.includes('config')
          ? 'config'
          : 'activity';

  const message =
    eventData?.message ||
    eventData?.event ||
    eventData?.title ||
    'Telemetry update';
  return {
    id: `${idSeed}-${Math.floor(Math.random() * 1000)}`,
    timestamp: eventData?.timestamp
      ? new Date(Number(eventData.timestamp) * 1000).toLocaleTimeString()
      : new Date().toLocaleTimeString(),
    message,
    type: mappedType,
    payload: eventData || {},
  };
}

export function connectWebSocket() {
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    return;
  }
  
  isIntentionalDisconnect = false;
  
  // Connect to the WebSocket
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  // Allow overriding host for prod
  const host = window.location.hostname === 'localhost' ? 'localhost:8000' : window.location.host;
  ws = new WebSocket(`${protocol}://${host}/api/ws/live`);

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
      } else if (parsed.type === 'intelligence_update') {
        // Debounce rapid server pushes to avoid excessive re-renders.
        if (intelligenceDebounceTimer) {
          clearTimeout(intelligenceDebounceTimer);
        }
        intelligenceDebounceTimer = setTimeout(() => {
          useSystemStore.getState().setIntelligenceUpdate(parsed.data || {});
        }, 160);
      } else if (parsed.type === 'thermal_update') {
        useSystemStore.getState().setState({
          thermal: parsed.data || null,
        });
      } else if (parsed.type === 'thermal_prediction') {
        useSystemStore.getState().setState({
          thermalPrediction: parsed.data || null,
        });
      } else if (parsed.type === 'event') {
        useSystemStore.getState().addEvent(normalizeEvent(parsed.data));
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
  if (intelligenceDebounceTimer) {
    clearTimeout(intelligenceDebounceTimer);
    intelligenceDebounceTimer = null;
  }
}
