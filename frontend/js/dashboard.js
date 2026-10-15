/**
 * AI RESUME LAB — Dashboard Module
 */

document.addEventListener('DOMContentLoaded', () => {
  initDashboard();
});

let dashboardData = null;
let applications = [];

async function initDashboard() {
  // Set greeting and date
  const user = Auth.getUser() || { name: 'Alex' };
  const nameEl = document.getElementById('user-greeting-name');
  if (nameEl) nameEl.textContent = user.name?.split(' ')[0] || 'Alex';

  const navName = document.getElementById('nav-user-name');
  if (navName) navName.textContent = user.name?.split(' ')[0] || 'User';

  const avatar = document.getElementById('nav-avatar');
  if (avatar) avatar.textContent = (user.name || 'A').charAt(0).toUpperCase();

  const dateEl = document.getElementById('current-date');
  if (dateEl) dateEl.textContent = new Date().toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
  });

  loadDashboard();
}

async function loadDashboard() {
  try {
    dashboardData = await DashboardAPI.getData();
  } catch {
    dashboardData = MockData.dashboardData;
  }

  updateStats(dashboardData);
  renderCharts(dashboardData);
  renderApplications(dashboardData.applications || MockData.dashboardData.applications);
  renderHealthCircle(dashboardData.resume_health || 87);
}

function updateStats(data) {
  setStatValue('stat-ats', data.ats_score || 87);
  setStatValue('stat-match', (data.job_match || 92) + '%');
  setStatValue('stat-skills', data.total_skills || 24);
  setStatValue('stat-apps', data.total_applications || 12);
  setStatValue('stat-interviews', data.total_interviews || 4);
  setStatValue('stat-health', data.resume_health || 87);
}

function setStatValue(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function renderCharts(data) {
  // Score History Line Chart
  const scoreCanvas = document.getElementById('score-history-chart');
  if (scoreCanvas) {
    const dpr = window.devicePixelRatio || 1;
    const rect = scoreCanvas.parentElement.getBoundingClientRect();
    scoreCanvas.width = rect.width * dpr;
    scoreCanvas.height = 220 * dpr;
    scoreCanvas.style.width = rect.width + 'px';
    scoreCanvas.style.height = '220px';
    scoreCanvas.getContext('2d').scale(dpr, dpr);
    Charts.lineChart(scoreCanvas, data.score_history || [72, 75, 78, 80, 82, 85, 87],
      ['Jan 1', 'Jan 5', 'Jan 8', 'Jan 10', 'Jan 12', 'Jan 14', 'Jan 15'], '#06b6d4');
  }

  // Skills Donut Chart
  const donutCanvas = document.getElementById('skills-donut-chart');
  if (donutCanvas) {
    Charts.donutChart(donutCanvas, [12, 7, 5], ['#06b6d4', '#8b5cf6', '#10b981']);
  }
}

function renderHealthCircle(score) {
  const el = document.getElementById('health-score-circle');
  if (el) ScoreCircle.render(el, score, 'cyan', 'Resume Health');

  // Animate progress bars
  setTimeout(() => ProgressBar.animateAll(0), 400);
}

function renderApplications(apps) {
  applications = apps;
  const tbody = document.getElementById('applications-tbody');
  if (!tbody) return;

  if (!apps || apps.length === 0) {
    tbody.innerHTML = `
      <tr><td colspan="5" style="text-align:center;padding:32px;color:var(--text-muted);">
        No applications yet. <a href="#" style="color:var(--accent-cyan);" onclick="Modal.open('add-application-modal')">Add one!</a>
      </td></tr>
    `;
    return;
  }

  tbody.innerHTML = apps.map((app, idx) => `
    <tr>
      <td><span style="font-weight:600;color:var(--text-primary);">${escHtml(app.company)}</span></td>
      <td>${escHtml(app.job_title)}</td>
      <td><span class="status-pill ${app.status}">${capitalize(app.status)}</span></td>
      <td>${formatDate(app.applied_date)}</td>
      <td>
        <div style="display:flex;gap:6px;">
          <button class="btn btn-ghost btn-sm" onclick="updateAppStatus(${idx})">Edit</button>
          <button class="btn btn-ghost btn-sm" style="color:var(--accent-red);" onclick="removeApp(${idx})">✕</button>
        </div>
      </td>
    </tr>
  `).join('');
}

function addApplication() {
  const company = document.getElementById('app-company')?.value.trim();
  const role = document.getElementById('app-role')?.value.trim();
  const status = document.getElementById('app-status')?.value;
  const date = document.getElementById('app-date')?.value;

  if (!company || !role) {
    Toast.warning('Missing Fields', 'Please fill in company and job title.');
    return;
  }

  applications.push({ company, job_title: role, status, applied_date: date || new Date().toISOString().split('T')[0] });
  renderApplications(applications);
  Modal.close('add-application-modal');

  // Clear form
  ['app-company', 'app-role', 'app-date'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });

  Toast.success('Application Added', `${company} — ${role}`);

  // Try to sync with API
  DashboardAPI.addApplication({ company, job_title: role, status, applied_date: date }).catch(() => {});
}

function removeApp(idx) {
  applications.splice(idx, 1);
  renderApplications(applications);
  Toast.info('Removed', 'Application removed.');
}

function updateAppStatus(idx) {
  const app = applications[idx];
  if (!app) return;
  const statuses = ['applied', 'interview', 'offer', 'rejected'];
  const currentIdx = statuses.indexOf(app.status);
  app.status = statuses[(currentIdx + 1) % statuses.length];
  renderApplications(applications);
  Toast.success('Updated', `${app.company} status: ${capitalize(app.status)}`);
}

// ── Helpers ───────────────────────────────────────────────────
function capitalize(str) {
  return str ? str.charAt(0).toUpperCase() + str.slice(1) : '';
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  } catch { return dateStr; }
}

function escHtml(str) {
  const div = document.createElement('div');
  div.textContent = str || '';
  return div.innerHTML;
}

window.addApplication = addApplication;
window.removeApp = removeApp;
window.updateAppStatus = updateAppStatus;
window.loadDashboard = loadDashboard;
