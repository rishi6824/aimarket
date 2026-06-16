/* agents.js — AI agent interactions: content, leads, ads, outreach */

// ── Utility Security ─────────────────────────────────────────────────────────
function escapeHTML(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, tag => ({'&': '&amp;','<': '&lt;','>': '&gt;',"'": '&#39;','"': '&quot;'}[tag]));
}

// ── Content Studio ─────────────────────────────────────────────────────────

async function generateContent() {
  const topic = document.getElementById('content-topic').value.trim();
  if (!topic) { showToast('⚠️ Please enter a topic first'); return; }

  const btn = document.getElementById('generate-btn');
  const btnText = document.getElementById('generate-btn-text');
  btn.disabled = true;
  btnText.innerHTML = '<span class="spinner"></span>Generating...';

  const payload = {
    content_type: document.getElementById('content-type').value,
    topic,
    tone: document.getElementById('content-tone').value,
    platform: document.getElementById('content-platform').value || null,
    keywords: document.getElementById('content-keywords').value
      .split(',').map(k => k.trim()).filter(Boolean),
  };

  try {
    const data = await api.generateContent(payload);
    document.getElementById('content-placeholder').style.display = 'none';
    document.getElementById('content-output-card').style.display = 'flex';
    document.getElementById('content-output').textContent = data.content;
    document.getElementById('content-meta').textContent =
      `${data.word_count} words · ${data.content_type.replace('_', ' ')} ${data.platform ? '· ' + data.platform : ''}`;

    const sugg = document.getElementById('content-suggestions');
    sugg.innerHTML = data.suggestions?.map(s =>
      `<div class="suggestion-tip">💡 ${escapeHTML(s)}</div>`).join('') || '';

    showToast('✨ Content generated!');
  } catch (e) {
    showToast('❌ ' + e.message);
  } finally {
    btn.disabled = false;
    btnText.textContent = '✨ Generate Content';
  }
}

function copyContent() {
  const text = document.getElementById('content-output').textContent;
  navigator.clipboard.writeText(text).then(() => showToast('📋 Copied!'));
}

function saveContent() { showToast('💾 Saved to history!'); }

// ── Leads ──────────────────────────────────────────────────────────────────

let allLeads = [];

async function loadLeads() {
  try {
    const data = await api.listLeads();
    allLeads = data.leads || [];
    renderLeads(allLeads);
  } catch (e) {
    document.getElementById('leads-tbody').innerHTML =
      `<tr><td colspan="6" class="loading-row">Could not load leads: ${e.message}</td></tr>`;
  }
}

function renderLeads(leads) {
  const tbody = document.getElementById('leads-tbody');
  if (!leads.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="loading-row">No leads yet. Add your first lead!</td></tr>';
    return;
  }
  tbody.innerHTML = leads.map(l => {
    const grade = l.grade || 'C';
    const score = l.score || 0;
    const status = l.status || 'new';
    return `<tr>
      <td><strong>${l.name}</strong></td>
      <td>${l.company || '—'}</td>
      <td>
        <div class="score-bar">
          <span class="score-num">${score}</span>
          <div class="score-track"><div class="score-fill" style="width:${score}%"></div></div>
        </div>
      </td>
      <td><span class="grade-badge grade-${grade}">${grade}</span></td>
      <td><span class="status-pill status-${status}">${status.replace('_',' ')}</span></td>
      <td>
        <button class="btn-ghost" style="font-size:.75rem;padding:.3rem .6rem"
          onclick="openOutreach('${l.name}','${l.company||''}')">📨 Outreach</button>
      </td>
    </tr>`;
  }).join('');
}

function filterLeads() {
  const q = document.getElementById('leads-search').value.toLowerCase();
  renderLeads(allLeads.filter(l =>
    (l.name||'').toLowerCase().includes(q) ||
    (l.company||'').toLowerCase().includes(q) ||
    (l.industry||'').toLowerCase().includes(q)
  ));
}

function openLeadModal() { document.getElementById('lead-modal').style.display = 'grid'; }
function closeLeadModal() { document.getElementById('lead-modal').style.display = 'none'; }

async function createLead() {
  const name = document.getElementById('lead-name').value.trim();
  if (!name) { showToast('⚠️ Name is required'); return; }
  try {
    const payload = {
      name,
      email: document.getElementById('lead-email').value || null,
      phone: document.getElementById('lead-phone').value || null,
      company: document.getElementById('lead-company').value || null,
      industry: document.getElementById('lead-industry').value || null,
      notes: document.getElementById('lead-notes').value || null,
    };
    showToast('🤖 Scoring with AI...');
    await api.createLead(payload);
    closeLeadModal();
    await loadLeads();
    showToast('✅ Lead added and scored!');
  } catch (e) { showToast('❌ ' + e.message); }
}

function openOutreach(name, company) {
  document.getElementById('outreach-lead-name').value = name;
  document.getElementById('outreach-result').style.display = 'none';
  document.getElementById('outreach-result').textContent = '';
  document.getElementById('outreach-modal').style.display = 'grid';
}

async function generateOutreach() {
  const product = document.getElementById('outreach-product').value.trim();
  const value = document.getElementById('outreach-value').value.trim();
  if (!product || !value) { showToast('⚠️ Fill in product and value prop'); return; }
  try {
    showToast('✨ Generating outreach...');
    const data = await api.generateOutreach({
      lead_name: document.getElementById('outreach-lead-name').value,
      product_name: product,
      value_proposition: value,
      channel: document.getElementById('outreach-channel').value,
    });
    const el = document.getElementById('outreach-result');
    el.textContent = data.message;
    el.style.display = 'block';
    showToast('✅ Outreach generated!');
  } catch (e) { showToast('❌ ' + e.message); }
}

// ── Campaigns ──────────────────────────────────────────────────────────────

async function loadCampaigns() {
  try {
    const data = await api.listCampaigns();
    renderCampaigns(data.campaigns || []);
  } catch (e) {
    document.getElementById('campaign-grid').innerHTML =
      `<div class="loading-row" style="color:#94a3b8">Could not load campaigns: ${e.message}</div>`;
  }
}

function renderCampaigns(campaigns) {
  const grid = document.getElementById('campaign-grid');
  if (!campaigns.length) {
    grid.innerHTML = '<div class="loading-row" style="color:#94a3b8">No campaigns yet. Create your first!</div>';
    return;
  }
  const channelEmoji = { social: '📱', email: '📧', ads: '🎯', sms: '💬', whatsapp: '📲' };
  grid.innerHTML = campaigns.map(c => `
    <div class="campaign-card">
      <div class="camp-header">
        <span class="camp-name">${c.name}</span>
        <span class="camp-channel-badge">${channelEmoji[c.channel] || '📊'} ${c.channel}</span>
      </div>
      <span class="status-pill status-${c.status || 'draft'}">${(c.status||'draft').replace('_',' ')}</span>
      <div class="camp-stats">
        <div class="camp-stat"><div class="camp-stat-val">${fmtNum(c.impressions||0)}</div><div class="camp-stat-lbl">Impressions</div></div>
        <div class="camp-stat"><div class="camp-stat-val">${fmtNum(c.clicks||0)}</div><div class="camp-stat-lbl">Clicks</div></div>
        <div class="camp-stat"><div class="camp-stat-val">${c.conversions||0}</div><div class="camp-stat-lbl">Conversions</div></div>
        <div class="camp-stat"><div class="camp-stat-val">$${(c.spend||0).toLocaleString()}</div><div class="camp-stat-lbl">Spend</div></div>
      </div>
      <div style="display:flex;gap:.5rem;margin-top:.75rem">
        <button class="btn-ghost" style="flex:1;font-size:.75rem" onclick="toggleCampaign('${c.id}','${c.status}')">
          ${c.status==='active'?'⏸ Pause':'▶ Activate'}
        </button>
        <button class="btn-ghost" style="font-size:.75rem;color:#ef4444;border-color:#ef4444" onclick="deleteCampaign('${c.id}')">🗑</button>
      </div>
    </div>`).join('');
}

function openCampaignModal() { document.getElementById('campaign-modal').style.display = 'grid'; }

async function createCampaign() {
  const name = document.getElementById('camp-name').value.trim();
  if (!name) { showToast('⚠️ Campaign name required'); return; }
  try {
    await api.createCampaign({
      name,
      channel: document.getElementById('camp-channel').value,
      budget: parseFloat(document.getElementById('camp-budget').value) || null,
      goal: document.getElementById('camp-goal').value || null,
      target_audience: document.getElementById('camp-audience').value || null,
    });
    document.getElementById('campaign-modal').style.display = 'none';
    await loadCampaigns();
    showToast('🚀 Campaign created!');
  } catch (e) { showToast('❌ ' + e.message); }
}

async function toggleCampaign(id, currentStatus) {
  const newStatus = currentStatus === 'active' ? 'paused' : 'active';
  try {
    await api.updateCampaign(id, { status: newStatus });
    await loadCampaigns();
    showToast(`✅ Campaign ${newStatus}`);
  } catch (e) { showToast('❌ ' + e.message); }
}

async function deleteCampaign(id) {
  if (!confirm('Delete this campaign?')) return;
  try {
    await api.deleteCampaign(id);
    await loadCampaigns();
    showToast('🗑 Campaign deleted');
  } catch (e) { showToast('❌ ' + e.message); }
}

// ── Ad Creatives ───────────────────────────────────────────────────────────

async function generateAds() {
  const product = document.getElementById('ad-product').value.trim();
  const audience = document.getElementById('ad-audience').value.trim();
  if (!product || !audience) { showToast('⚠️ Fill in product and audience'); return; }

  const btn = document.getElementById('ad-gen-btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>Generating...';

  try {
    // Use content agent with ad_copy type for each variant
    const platform = document.getElementById('ad-platform').value;
    const variants = parseInt(document.getElementById('ad-variants').value);
    const results = await Promise.all(
      Array.from({ length: variants }, (_, i) => api.generateContent({
        content_type: 'ad_copy',
        topic: `${product} — for ${audience}`,
        tone: ['professional', 'urgent', 'inspirational'][i % 3],
        platform,
        keywords: [product, audience],
      }))
    );

    const container = document.getElementById('ads-output');
    container.innerHTML = `<div class="ad-variants-grid">` +
      results.map((r, i) => `
        <div class="ad-card">
          <div class="ad-card-header">
            <span class="ad-variant-num">Variant ${i + 1}</span>
            <span class="ad-angle">Tone: ${['Professional','Urgent','Inspirational'][i%3]}</span>
          </div>
          <div class="ad-body" style="white-space:pre-wrap">${escapeHTML(r.content)}</div>
          <div class="ad-footer">
            <button class="btn-ghost" style="font-size:.75rem" onclick="navigator.clipboard.writeText(this.closest('.ad-card').querySelector('.ad-body').textContent);showToast('📋 Copied!')">📋 Copy</button>
            <span class="ad-why" style="font-size:.75rem;color:#10b981">${escapeHTML(r.suggestions?.[0]||'')}</span>
          </div>
        </div>`).join('') + `</div>`;
    showToast('🎨 Ad creatives ready!');
  } catch (e) {
    showToast('❌ ' + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = '🎯 Generate Ad Creatives';
  }
}

// ── Utility ────────────────────────────────────────────────────────────────
function fmtNum(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
  return n.toString();
}
