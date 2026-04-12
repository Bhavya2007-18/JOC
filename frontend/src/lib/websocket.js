import useSystemStore from '../store/useSystemStore';

let ws = null;
let reconnectWait = 1000;
const MAX_RECONNECT_WAIT = 10000;
let isIntentionalDisconnect = false;
let pingInterval = null;
let lastPongTime = Date.now();

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
    lastPongTime = Date.now();
    
    // Heartbeat mechanism
    if (pingInterval) clearInterval(pingInterval);
    pingInterval = setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        // If we haven't received any message (pong or data) in 30s, assume dead
        if (Date.now() - lastPongTime > 30000) {
          console.warn("WebSocket dead - missing heartbeats. Closing...");
          ws.close();
        } else {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      }
    }, 10000);
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
        useSystemStore.getState().setIntelligenceFeed(parsed.data);
      } else if (parsed.type === 'autonomy_update') {
        useSystemStore.getState().setAutonomyFeed(parsed.data);
      } else if (parsed.type === 'event') {
        useSystemStore.getState().addEvent(parsed.data);
      } else if (parsed.type === 'pong') {
        // Just record pong time, handled below
      }
      
      // Update pong time on ANY valid message from backend
      lastPongTime = Date.now();
    } catch (err) {
      console.error('Error parsing WS message:', err);
    }
  };

  ws.onclose = () => {
    useSystemStore.getState().setState({ connected: false });
    if (pingInterval) clearInterval(pingInterval);
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
  if (pingInterval) clearInterval(pingInterval);
  if (ws) {
    ws.close();
    ws = null;
  }
}
