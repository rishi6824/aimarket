/* Charts — Chart.js initializations */
let perfChart, channelChart;

function initCharts(kpis = {}) {
  const gridColor = 'rgba(255,255,255,0.05)';
  const textColor = '#64748b';

  // ── Performance Chart ──────────────────────────────────────────
  const perfCtx = document.getElementById('performanceChart');
  if (perfCtx) {
    if (perfChart) perfChart.destroy();
    perfChart = new Chart(perfCtx, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
        datasets: [
          {
            label: 'Impressions (K)',
            data: [28, 42, 38, 65, 71, 84, Math.round((kpis.total_impressions || 284500) / 1000)],
            borderColor: '#8b5cf6',
            backgroundColor: 'rgba(139,92,246,0.08)',
            fill: true,
            tension: 0.4,
            pointRadius: 4,
            pointBackgroundColor: '#8b5cf6',
          },
          {
            label: 'Conversions',
            data: [45, 78, 62, 110, 134, 198, kpis.total_conversions || 312],
            borderColor: '#06b6d4',
            backgroundColor: 'rgba(6,182,212,0.06)',
            fill: true,
            tension: 0.4,
            pointRadius: 4,
            pointBackgroundColor: '#06b6d4',
          },
        ],
      },
      options: {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        plugins: { legend: { labels: { color: textColor, font: { size: 11 } } } },
        scales: {
          x: { grid: { color: gridColor }, ticks: { color: textColor } },
          y: { grid: { color: gridColor }, ticks: { color: textColor } },
        },
      },
    });
  }

  // ── Channel Donut ──────────────────────────────────────────────
  const chCtx = document.getElementById('channelChart');
  if (chCtx) {
    if (channelChart) channelChart.destroy();
    channelChart = new Chart(chCtx, {
      type: 'doughnut',
      data: {
        labels: ['Social', 'Email', 'Paid Ads', 'SMS', 'WhatsApp'],
        datasets: [{
          data: [35, 25, 28, 7, 5],
          backgroundColor: ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'],
          borderWidth: 0,
          hoverOffset: 6,
        }],
      },
      options: {
        responsive: true,
        cutout: '68%',
        plugins: {
          legend: { position: 'bottom', labels: { color: textColor, font: { size: 11 }, padding: 12 } },
        },
      },
    });
  }
}
