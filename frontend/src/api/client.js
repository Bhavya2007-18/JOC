import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const systemApi = {
  analyze: () => api.get('/analyze'),
  fix: (action, target) => api.post('/fix', { action, target }),
  executeTweak: (tweakName) => api.post('/tweak/execute', { tweak_name: tweakName }),
  revertAction: (actionId) => api.post('/action/revert', { action_id: actionId }),
};

export const storageApi = {
  scan: (params) => api.get('/scan', { params }),
  cleanup: (type, confirm = true) => api.post('/cleanup', { type, confirm }),
};

export default api;
