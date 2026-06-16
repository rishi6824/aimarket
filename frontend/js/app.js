/* app.js — main app logic: routing, clock, chat, health */

// ── Page Navigation ─────────────────────────────────────────────────────────
const PAGE_META = {
  dashboard: { title: 'Dashboard', sub: 'Marketing intelligence overview' },
  content: { title: 'Content Studio', sub: 'AI-powered content generation' },
  leads: { title: 'Leads', sub: 'Manage and score your pipeline' },
  campaigns: { title: 'Campaigns', sub: 'Active marketing campaigns' },
  ads: { title: 'Ad Creatives', sub: 'AI ad variants for A/B testing' },
  chat: { title: 'ARIA Chat', sub: 'Your AI marketing strategist' },
  stocks: { title: 'Stocks & Trading', sub: 'Real-time intraday data and AI predictions' },
};

function showPage(id, el) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('page-' + id).classList.add('active');
  if (el) el.classList.add('active');

  const meta = PAGE_META[id] || {};
  document.getElementById('page-title').textContent = meta.title || id;
  document.getElementById('page-sub').textContent = meta.sub || '';

  if (id === 'dashboard') loadDashboard();
  if (id === 'leads') loadLeads();
  if (id === 'campaigns') loadCampaigns();
  if (id === 'stocks') loadPortfolio();
}

// ── Dashboard ───────────────────────────────────────────────────────────────
async function loadDashboard() {
  try {
    const data = await api.analytics();
    const kpis = data.kpis || {};
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    set('kpi-leads', fmtNum(kpis.total_leads || 0));
    set('kpi-campaigns', kpis.active_campaigns || 0);
    set('kpi-impressions', fmtNum(kpis.total_impressions || 0));
    set('kpi-conversions', fmtNum(kpis.total_conversions || 0));
    set('kpi-ctr', (kpis.ctr || 0) + '%');
    set('kpi-spend', '$' + (kpis.total_spend || 0).toLocaleString());
    initCharts(kpis);
  } catch (e) {
    // Show demo values
    const demos = { 'kpi-leads':'47','kpi-campaigns':'5','kpi-impressions':'284K','kpi-conversions':'312','kpi-ctr':'3.45%','kpi-spend':'$4,250' };
    Object.entries(demos).forEach(([id, v]) => { const el = document.getElementById(id); if (el) el.textContent = v; });
    initCharts({});
  }
}

// ── Health Check ─────────────────────────────────────────────────────────────
async function checkHealth() {
  const badge = document.getElementById('health-badge');
  badge.textContent = '⏳ Checking...';
  try {
    const data = await api.health();
    const ok = data.status === 'healthy';
    badge.textContent = ok ? '✅ All Systems OK' : '⚠️ Degraded';
    badge.style.borderColor = ok ? 'rgba(16,185,129,.4)' : 'rgba(245,158,11,.4)';
    badge.style.color = ok ? '#10b981' : '#f59e0b';
    showToast(ok ? '✅ Backend healthy!' : '⚠️ Check API keys');
  } catch (e) {
    badge.textContent = '❌ Backend Offline';
    badge.style.borderColor = 'rgba(239,68,68,.4)';
    badge.style.color = '#ef4444';
    showToast('❌ Backend not reachable — run: uvicorn main:app');
  }
}

// ── Clock ─────────────────────────────────────────────────────────────────────
function updateClock() {
  const el = document.getElementById('topbar-time');
  if (el) el.textContent = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
setInterval(updateClock, 1000);
updateClock();

// ── Toast ─────────────────────────────────────────────────────────────────────
let toastTimer;
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 3000);
}

// ── Chat ──────────────────────────────────────────────────────────────────────
let chatSessionId = null;
let chatHistory = [];
let isChatLoading = false;

function handleChatKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChat(); }
}

function sendSuggestion(btn) {
  document.getElementById('chat-input').value = btn.textContent;
  sendChat();
}

async function sendChat() {
  if (isChatLoading) return;
  const input = document.getElementById('chat-input');
  const msg = input.value.trim();
  if (!msg) return;

  input.value = '';
  isChatLoading = true;
  document.getElementById('chat-send-btn').disabled = true;

  appendMsg('user', msg);
  const typingEl = appendTyping();

  try {
    const data = await api.chat({
      message: msg,
      session_id: chatSessionId,
      history: chatHistory.slice(-10),
    });
    chatSessionId = data.session_id;
    chatHistory.push({ role: 'user', content: msg });
    chatHistory.push({ role: 'assistant', content: data.reply });

    typingEl.remove();
    appendMsg('assistant', data.reply);

    // Update suggestion chips
    if (data.suggestions?.length) {
      const chips = document.getElementById('chat-suggestions');
      chips.innerHTML = data.suggestions.map(s =>
        `<button class="suggestion-chip" onclick="sendSuggestion(this)">${s}</button>`
      ).join('');
    }
  } catch (e) {
    typingEl.remove();
    appendMsg('assistant', `❌ ${e.message}. Make sure the backend is running.`);
  } finally {
    isChatLoading = false;
    document.getElementById('chat-send-btn').disabled = false;
  }
}

// ── Utility & Chat Security ───────────────────────────────────────────────────
function escapeHTML(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, 
    tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[tag])
  );
}

function appendMsg(role, content) {
  const msgs = document.getElementById('chat-messages');
  const isUser = role === 'user';
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  div.innerHTML = `
    <div class="msg-avatar">${isUser ? '👤' : '⚡'}</div>
    <div class="msg-bubble">${escapeHTML(content).replace(/\n/g, '<br/>')}</div>`;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
  return div;
}

function appendTyping() {
  const msgs = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'msg assistant msg-typing';
  div.innerHTML = `<div class="msg-avatar">⚡</div><div class="msg-bubble"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>`;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
  return div;
}

// ── Stocks & Trading ──────────────────────────────────────────────────────────
let tvChart = null;
let lineSeries = null;
let currentSymbol = null;
let currentPrice = null;

async function loadPortfolio() {
  try {
    const data = await api.portfolio();
    document.getElementById('port-usd').textContent = '$' + data.balance.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2});
    
    const holdingsDiv = document.getElementById('port-holdings');
    if (data.holdings.length === 0) {
      holdingsDiv.innerHTML = '<p style="color:var(--text3); font-size:0.85rem">No active positions.</p>';
    } else {
      holdingsDiv.innerHTML = data.holdings.map(h => `
        <div class="holding-item">
          <div>
            <strong style="color:var(--text)">${h.symbol}</strong><br/>
            <span style="font-size:0.8rem; color:var(--text3)">${h.quantity} shares</span>
          </div>
          <div style="text-align:right">
            <strong style="color:var(--text)">$${(h.quantity * h.avg_price).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</strong><br/>
            <span style="font-size:0.8rem; color:var(--text3)">Avg: $${h.avg_price.toFixed(2)}</span>
          </div>
        </div>
      `).join('');
    }
  } catch (e) {
    console.error("Failed to load portfolio", e);
  }
}

async function executeTrade(action) {
  if (!currentSymbol || !currentPrice) {
    showToast('⚠️ Analyze a stock first before trading.');
    return;
  }
  
  const qty = parseFloat(document.getElementById('trade-qty').value);
  if (!qty || qty <= 0) {
    showToast('⚠️ Enter a valid quantity.');
    return;
  }
  
  try {
    const res = await api.trade({
      symbol: currentSymbol,
      action: action,
      quantity: qty,
      price: currentPrice
    });
    showToast(`✅ ${res.message}`);
    loadPortfolio();
  } catch (e) {
    showToast(`❌ ${e.message}`);
  }
}

async function predictStock() {
  const symbol = document.getElementById('stock-symbol').value.trim();
  if (!symbol) { showToast('⚠️ Enter a stock symbol'); return; }

  const btnText = document.getElementById('stock-btn-text');
  const btn = document.getElementById('stock-predict-btn');
  btn.disabled = true;
  btnText.innerHTML = '<span class="spinner"></span>Analyzing...';
  
  const outBox = document.getElementById('stock-prediction-output');
  outBox.style.display = 'none';

  try {
    const data = await api.stockPrediction({ symbol });
    
    currentSymbol = data.symbol;
    currentPrice = data.current_price;
    document.getElementById('trade-price').value = currentPrice;
    
    // Show AI prediction
    outBox.innerHTML = `<strong>${data.symbol} @ $${data.current_price}</strong><br/><br/>${escapeHTML(data.prediction).replace(/\n/g, '<br/>')}`;
    outBox.style.display = 'block';
    
    // Render Chart
    document.getElementById('stock-chart-sub').textContent = `${data.symbol} Intraday (1min)`;
    
    const times = Object.keys(data.time_series_data);
    const prices = Object.values(data.time_series_data);
    
    // Format for Lightweight Charts
    const chartData = times.map((t, i) => {
      const date = new Date(t + ' UTC'); 
      return { time: date.getTime() / 1000, value: prices[i] };
    }).sort((a,b) => a.time - b.time);
    
    const tvContainer = document.getElementById('tvchart');
    if (!tvChart) {
      tvChart = LightweightCharts.createChart(tvContainer, {
        width: tvContainer.clientWidth,
        height: 400,
        layout: { background: { type: 'solid', color: 'transparent' }, textColor: '#94a3b8' },
        grid: { vertLines: { color: 'rgba(255,255,255,0.05)' }, horzLines: { color: 'rgba(255,255,255,0.05)' } },
        crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
        rightPriceScale: { borderColor: 'rgba(255,255,255,0.1)' },
        timeScale: { borderColor: 'rgba(255,255,255,0.1)', timeVisible: true },
      });
      lineSeries = tvChart.addAreaSeries({
        lineColor: '#06b6d4',
        topColor: 'rgba(6,182,212, 0.4)',
        bottomColor: 'rgba(6,182,212, 0)',
        lineWidth: 2,
      });
      
      new ResizeObserver(entries => {
        if (entries.length === 0 || entries[0].target !== tvContainer) return;
        const newRect = entries[0].contentRect;
        tvChart.applyOptions({ height: newRect.height, width: newRect.width });
      }).observe(tvContainer);
    }
    
    lineSeries.setData(chartData);
    tvChart.timeScale().fitContent();
    
    showToast('📈 Analysis complete!');
  } catch (e) {
    showToast('❌ ' + e.message);
  } finally {
    btn.disabled = false;
    btnText.textContent = '⚡ AI Analysis';
  }
}

// ── Dashboard Mock Real-Time Users ──────────────────────────────────────────
setInterval(() => {
  const el = document.getElementById('kpi-realtime');
  if (el && document.getElementById('page-dashboard').classList.contains('active')) {
    let current = parseInt(el.textContent.replace(/,/g, '')) || 1204;
    const change = Math.floor(Math.random() * 11) - 5; // -5 to +5
    current = Math.max(100, current + change);
    el.textContent = current.toLocaleString();
    
    const trend = document.getElementById('kpi-realtime-trend');
    if (change > 0) {
      trend.className = 'kpi-trend up';
      trend.textContent = `+${change} joining`;
    } else if (change < 0) {
      trend.className = 'kpi-trend down';
      trend.textContent = `${Math.abs(change)} leaving`;
    } else {
      trend.className = 'kpi-trend neutral';
      trend.textContent = 'Stable';
    }
  }
}, 3000);

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadDashboard();
  checkHealth();
});
