import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

async function wrapRequest(fn) {
  try {
    const res = await fn();
    return {
      status: 'success',
      data: res.data,
      message: '',
    };
  } catch (err) {
    const message =
      err.response?.data?.message ||
      err.response?.data?.detail ||
      err.message ||
      'Request failed';
    return {
      status: 'error',
      data: null,
      message,
    };
  }
}

export const systemApi = {
  getStats: () => api.get('/system/stats'),
  getProcesses: (limit = 10) => api.get(`/system/processes?limit=${limit}`),
  analyze: () => api.get('/analyze'),
fix: (action, target, pid) => {
  const payload = { action };

  if (action === 'kill_process') {
    payload.pid = pid;
  } else {
    payload.target = target;
    if (pid !== undefined) {
      payload.pid = pid;
    }
  }

  return api.post('/fix', payload);
},

safeAnalyze: () => wrapRequest(() => api.get('/analyze')),
getActionHistory: () => api.get('/action/history'),
revertAction: (actionId) =>
  api.post('/action/revert', { action_id: actionId }),
getTimeline: (limit = 50) => api.get(`/system/timeline?limit=${limit}`),
rollbackAction: (rollbackId) => api.post('/action/rollback_intercept', { rollback_id: rollbackId }),
};

export const intelligenceApi = {
  logState: () => api.post('/intelligence/log'),
  getPatterns: (windowMinutes = 60) => api.get(`/intelligence/patterns?window_minutes=${windowMinutes}`),
  getAnomalies: (windowMinutes = 60) => api.get(`/intelligence/anomalies?window_minutes=${windowMinutes}`),
  getDecisions: (windowMinutes = 60) => api.get(`/intelligence/decisions?window_minutes=${windowMinutes}`),
  safePatterns: (windowMinutes = 60) => wrapRequest(() => api.get(`/intelligence/patterns?window_minutes=${windowMinutes}`)),
  safeAnomalies: (windowMinutes = 60) => wrapRequest(() => api.get(`/intelligence/anomalies?window_minutes=${windowMinutes}`)),
  safeDecisions: (windowMinutes = 60) => wrapRequest(() => api.get(`/intelligence/decisions?window_minutes=${windowMinutes}`)),
  getForecast: () => api.get('/intelligence/forecast'),
  getCausalGraph: () => api.get('/intelligence/causal-graph'),
};

export const optimizerApi = {
  boost: (payload) => api.post('/optimize/boost', payload),
  cleanup: (payload) => api.post('/optimize/cleanup', payload),
  getSuggestions: (cpuThreshold = 30, maxProcesses = 10) => 
    api.get(`/optimize/suggestions?cpu_threshold=${cpuThreshold}&max_processes=${maxProcesses}`),
  processAction: {
    kill: (pid) => api.post('/process/kill', { pid }),
    priority: (pid, priority) => api.post('/process/priority', { pid, priority }),
    suspend: (pid) => api.post('/process/suspend', { pid }),
    resume: (pid) => api.post('/process/resume', { pid }),
  },
  executeTweak: (tweakName) => api.post('/tweak/execute', { tweak_name: tweakName }),
  revertAction: (actionId) => api.post('/action/revert', { action_id: actionId }),
  safeBoost: (payload) => wrapRequest(() => api.post('/optimize/boost', payload)),
  safeCleanup: (payload) => wrapRequest(() => api.post('/optimize/cleanup', payload)),
};

export const simulationApi = {
  run: (payload) => api.post('/simulate/run', payload),
  getReport: (id) => api.get(`/simulation/${id}`),
  getHistory: () => api.get('/simulation/history'),
  stop: (reason) => api.post('/simulate/stop', { reason }),
};

export const storageApi = {
  scan: (params) => api.get('/scan', { params }),
  cleanup: (type, { confirm = true, dryRun = false } = {}) =>
    api.post('/cleanup', { type, confirm, dry_run: dryRun }),
  analysis: (params) => api.get('/storage/analysis', { params }),
};

export default api;
