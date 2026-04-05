// ============================================================
// ui.js — tab switching, loading overlay, cache, notifications
// ============================================================

const API_BASE = '/api';

// ── Patient cache ─────────────────────────────────────────────
const patientCache = {};
const CACHE_TTL    = 60000; // ms

let _activePatientId = null;
let _loadingStart    = null;
let _factPromise     = null;
const MIN_LOADING_MS = 800;

// ── Tab switching ─────────────────────────────────────────────

function switchTab(tabName) {
  document.querySelectorAll('.app-screen').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));

  const screen = document.getElementById('screen-' + tabName);
  const btn    = document.getElementById('nav-'    + tabName);
  if (screen) screen.classList.add('active');
  if (btn)    btn.classList.add('active');

  // Lazy-load profile patient list on first visit
  if (tabName === 'profile') {
    const list = document.getElementById('patient-list');
    if (list && list.querySelector('.empty-state')?.textContent.includes('Loading')) {
      if (typeof loadPatients === 'function') loadPatients();
    }
  }
}

// ── Loading overlay ───────────────────────────────────────────

function showLoading() {
  _loadingStart = Date.now();
  const overlay = document.getElementById('loading-overlay');
  if (overlay) {
    overlay.classList.remove('hidden');
    overlay.style.display = 'flex';
  }
  // Fetch a fun fact while loading
  if (typeof fetchAndShowFact === 'function') _factPromise = fetchAndShowFact();
}

async function hideLoading() {
  const elapsed   = Date.now() - (_loadingStart || 0);
  const remaining = Math.max(0, MIN_LOADING_MS - elapsed);
  await Promise.all([
    remaining > 0 ? new Promise(r => setTimeout(r, remaining)) : Promise.resolve(),
    _factPromise || Promise.resolve(),
  ]);

  const overlay = document.getElementById('loading-overlay');
  if (overlay) {
    overlay.classList.add('hidden');
    setTimeout(() => { if (overlay) overlay.style.display = 'none'; }, 350);
  }
}

// ── Date formatting ───────────────────────────────────────────

function formatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    // Append time to avoid timezone shift when parsing date-only strings
    const d = new Date(dateStr.includes('T') ? dateStr : dateStr + 'T00:00:00');
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  } catch { return dateStr; }
}

// ── Notifications ─────────────────────────────────────────────

function showNotification(msg, urgency = 'info') {
  const icons = { info: '🐾', warning: '⚠️', urgent: '🚨' };

  const banner = document.createElement('div');
  banner.className = `notif-banner notif-banner--${urgency}`;
  banner.innerHTML = `<span>${icons[urgency] || ''}</span><span>${msg}</span>`;
  banner.style.cursor = 'pointer';
  banner.onclick = () => banner.remove();

  // Insert at top of the active screen
  const screen = document.querySelector('.app-screen.active');
  if (screen) screen.prepend(banner);

  const delay = urgency === 'urgent' ? 6000 : urgency === 'warning' ? 5000 : 3500;
  setTimeout(() => banner.remove(), delay);
}

function renderError(msg) {
  showNotification(msg, 'urgent');
}

// ── Patient cache ─────────────────────────────────────────────

function getCachedPatient(patientId) {
  const entry = patientCache[patientId];
  if (!entry || entry._inflight) return null;
  if (Date.now() - entry.timestamp > CACHE_TTL) {
    delete patientCache[patientId];
    return null;
  }
  return entry.data;
}

async function prefetchOnHover(patientId) {
  if (patientCache[patientId]) return; // already cached or in-flight
  patientCache[patientId] = { _inflight: true, timestamp: Date.now() };
  try {
    const res = await fetch(`${API_BASE}/patients/${patientId}`);
    if (res.ok) {
      patientCache[patientId] = { data: await res.json(), timestamp: Date.now() };
    } else {
      delete patientCache[patientId];
    }
  } catch {
    delete patientCache[patientId];
  }
}

function invalidateCache(patientId) {
  delete patientCache[patientId];
}

// ── Active patient ────────────────────────────────────────────

function setActivePatient(id) { _activePatientId = id; }
function getActivePatient()   { return _activePatientId; }

// ── Quick action logger ───────────────────────────────────────

function logQuickAction(action) {
  // Bounce animation on the button
  const btn = document.querySelector(`.qa-btn[data-action="${action}"]`);
  if (btn) {
    btn.style.transform = 'scale(0.88)';
    setTimeout(() => { btn.style.transform = ''; }, 180);
  }

  // Map quick actions to daily goals
  const map = { meals: 'breakfast', play: 'walk', grooming: 'teeth', hydration: null };
  const goalId = map[action];
  if (goalId && typeof setGoalState === 'function') {
    setGoalState(goalId, true);
    if (typeof renderGoalsList === 'function') {
      renderGoalsList('goals-list-home');
      renderGoalsList('goals-list-wellness');
    }
    if (typeof updateWellbeingDisplay === 'function') updateWellbeingDisplay();
  }

  const labels = { meals: 'Meal logged', play: 'Walk logged', grooming: 'Grooming logged', hydration: 'Hydration tracked' };
  showNotification((labels[action] || 'Logged!') + ' Great job! 🐾', 'info');
}
