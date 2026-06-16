/* API client — all calls to the FastAPI backend */
const API = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') ? 'http://localhost:8000' : '';

async function apiFetch(path, opts = {}) {
  try {
    const res = await fetch(API + path, {
      headers: { 'Content-Type': 'application/json', ...opts.headers },
      ...opts,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Request failed');
    }
    return await res.json();
  } catch (e) {
    console.error('[API]', path, e.message);
    throw e;
  }
}

const api = {
  health: () => apiFetch('/health'),
  analytics: () => apiFetch('/api/analytics/overview'),

  // Content
  generateContent: (body) => apiFetch('/api/content/generate', { method: 'POST', body: JSON.stringify(body) }),
  contentHistory: () => apiFetch('/api/content/history'),

  // Leads
  listLeads: () => apiFetch('/api/leads/'),
  createLead: (body) => apiFetch('/api/leads/', { method: 'POST', body: JSON.stringify(body) }),
  generateOutreach: (body) => apiFetch('/api/leads/outreach', { method: 'POST', body: JSON.stringify(body) }),
  updateLeadStatus: (id, status) => apiFetch(`/api/leads/${id}/status?status=${status}`, { method: 'PATCH' }),

  // Campaigns
  listCampaigns: () => apiFetch('/api/campaigns/'),
  createCampaign: (body) => apiFetch('/api/campaigns/', { method: 'POST', body: JSON.stringify(body) }),
  updateCampaign: (id, body) => apiFetch(`/api/campaigns/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
  deleteCampaign: (id) => apiFetch(`/api/campaigns/${id}`, { method: 'DELETE' }),

  // Ads
  generateAds: (body) => apiFetch('/api/analytics/insights', { method: 'POST', body: JSON.stringify(body) }),
  adCreatives: (body) => apiFetch('/api/content/generate', { method: 'POST', body: JSON.stringify(body) }),

  // Chat
  chat: (body) => apiFetch('/api/chat/', { method: 'POST', body: JSON.stringify(body) }),

  // Stocks & Trading
  stockPrediction: (body) => apiFetch('/api/stocks/predict', { method: 'POST', body: JSON.stringify(body) }),
  portfolio: () => apiFetch('/api/stocks/portfolio'),
  trade: (body) => apiFetch('/api/stocks/trade', { method: 'POST', body: JSON.stringify(body) }),
  trades: () => apiFetch('/api/stocks/trades'),
};
