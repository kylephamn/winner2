// ============================================================
// gamification.js — daily goals, wellness score, badges, facts
// ============================================================

// ── Active pet species (set when a patient is loaded) ─────────
let _activePetSpecies = '';
function setActivePetSpecies(species) { _activePetSpecies = (species || '').toLowerCase(); }

// ── Daily goals definition ────────────────────────────────────
const DAILY_GOALS = [
  { id: 'breakfast', icon: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2a5 5 0 0 0-5 5v6h3v7"/></svg>', label: 'Healthy Breakfast', pts: 50,  bg: '#F9D8A0' },
  { id: 'walk',      icon: '<svg viewBox="0 0 24 24" width="22" height="22" fill="white"><circle cx="7" cy="4.5" r="1.5"/><circle cx="12" cy="3" r="1.5"/><circle cx="17" cy="4.5" r="1.5"/><circle cx="20.5" cy="9" r="1.5"/><path d="M12 21.5c-3 0-6-2.5-5.5-6 .5-3 3-3.5 4.5-2 .5.5 1.5.5 2 0 1.5-1.5 4-1 4.5 2 .5 3.5-2.5 6-5.5 6z"/></svg>', label: 'A Long Walk',        pts: 100, bg: '#F4A8A0' },
  { id: 'teeth',     icon: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3h6a4 4 0 0 1 4 4c0 2-1.5 4-1.5 7l-1 6c-.2 1-1 1.2-1.5.5L14 18a2 2 0 0 0-4 0l-1 2.5c-.5.7-1.3.5-1.5-.5l-1-6C6.5 11 5 9 5 7a4 4 0 0 1 4-4z"/></svg>', label: 'Teeth Brushing',     pts: 30,  bg: '#A0D8D4' },
  { id: 'checkin',   icon: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>', label: 'Check-in with Vet', pts: 10,  bg: '#F4A0B8' },
];

const BADGE_META = {
  first_steps:       { emoji: '<svg viewBox="0 0 24 24" width="24" height="24" fill="white"><circle cx="7" cy="4.5" r="1.5"/><circle cx="12" cy="3" r="1.5"/><circle cx="17" cy="4.5" r="1.5"/><circle cx="20.5" cy="9" r="1.5"/><path d="M12 21.5c-3 0-6-2.5-5.5-6 .5-3 3-3.5 4.5-2 .5.5 1.5.5 2 0 1.5-1.5 4-1 4.5 2 .5 3.5-2.5 6-5.5 6z"/></svg>', name: 'First Steps'        },
  health_starter:    { emoji: '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 8C8 10 5.9 16.17 3.82 22c8.41-3.48 10.17-8.17 10.18-11z"/><path d="M3.82 22c2 1 4 2 6 2a13 13 0 0 0 13-13c0-4-2-7-4-9"/></svg>', name: 'Health Starter'     },
  wellness_champion: { emoji: '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 21h8"/><path d="M12 17v4"/><path d="M17 2H7a2 2 0 0 0-2 2v4c0 3.31 2.69 6 6 6s6-2.69 6-6V4a2 2 0 0 0-2-2z"/><path d="M19 5h2a2 2 0 0 1 2 2v1a4 4 0 0 1-4 4h-1"/><path d="M5 5H3a2 2 0 0 0-2 2v1a4 4 0 0 0 4 4h1"/></svg>', name: 'Wellness Champion'  },
  dedicated_owner:   { emoji: '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>', name: 'Dedicated Owner'    },
  pet_health_hero:   { emoji: '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>', name: 'Pet Health Hero'    },
};

// ── localStorage goal state (resets each calendar day, per pet) ──

function _todayKey() {
  const petId = (typeof getActivePatient === 'function' ? getActivePatient() : null) || 'default';
  return 'pawff_goals_' + petId + '_' + new Date().toISOString().slice(0, 10);
}

function getGoalStates() {
  try {
    const raw = localStorage.getItem(_todayKey());
    return raw ? JSON.parse(raw) : {};
  } catch { return {}; }
}

function setGoalState(goalId, checked) {
  const states = getGoalStates();
  states[goalId] = checked;
  try { localStorage.setItem(_todayKey(), JSON.stringify(states)); } catch {}
}

// ── Wellness percentage ───────────────────────────────────────

function calcWellbeingPct() {
  const states = getGoalStates();
  const done   = DAILY_GOALS.filter(g => states[g.id]).length;
  return Math.round(done / DAILY_GOALS.length * 100);
}

function calcTodayPts() {
  const states = getGoalStates();
  return DAILY_GOALS.filter(g => states[g.id]).reduce((sum, g) => sum + g.pts, 0);
}

// ── Update all wellness indicators (bar, face, body img) ──────

function updateWellbeingDisplay() {
  const pct = calcWellbeingPct();
  const pts = calcTodayPts();

  // Today's earned wellness points
  const heroEl = document.getElementById('hero-pts');
  if (heroEl) heroEl.textContent = pts.toLocaleString() + ' Wellness Points';

  // Progress bar: shrink the white mask from right
  const track = document.getElementById('wb-track');
  if (track) track.style.setProperty('--wb-mask', (100 - pct) + '%');

  // Percentage label
  const pctEl = document.getElementById('wb-pct');
  if (pctEl) pctEl.textContent = pct + '%';

  // Choose images based on wellness and species
  let faceImg, bodyImg;
  const isCat = _activePetSpecies === 'cat';
  if (pct >= 75) {
    faceImg = isCat ? '/images/cat_happy.png'   : '/images/face3.png';
    bodyImg = isCat ? '/images/cat_body_happy.png'   : '/images/body3.png';
  } else if (pct >= 40) {
    faceImg = isCat ? '/images/cat_neutral.png' : '/images/face1.png';
    bodyImg = isCat ? '/images/cat_body_neutral.png' : '/images/body3.png';
  } else {
    faceImg = isCat ? '/images/cat_sad.png'     : '/images/sad_dog.png';
    bodyImg = isCat ? '/images/cat_body_sad.png'     : '/images/body1.png';
  }

  const ids = ['wb-face', 'header-pet-face'];
  ids.forEach(id => { const el = document.getElementById(id); if (el) el.src = faceImg; });

  const bodyIds = ['wb-body-img', 'hero-body-img'];
  bodyIds.forEach(id => { const el = document.getElementById(id); if (el) el.src = bodyImg; });

  // Achievement card
  _updateAchievementCard(pct);
}

function _updateAchievementCard(pct) {
  const card   = document.getElementById('achievement-card');
  const rankEl = document.getElementById('achievement-rank');
  if (!card || !rankEl) return;

  if (pct >= 75) {
    card.style.display = 'flex';
    rankEl.textContent  = `You've completed ${pct}% of today's goals — incredible!`;
  } else if (pct >= 50) {
    card.style.display = 'flex';
    rankEl.textContent  = `Halfway there! ${pct}% of daily goals done.`;
  } else {
    card.style.display = 'none';
  }
}

// ── Render a goals list into a container ──────────────────────

function renderGoalsList(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const states = getGoalStates();
  container.innerHTML = '';

  DAILY_GOALS.forEach(goal => {
    const checked = !!states[goal.id];

    const item = document.createElement('div');
    item.className = 'goal-item' + (checked ? ' completed' : '');
    item.dataset.goalId = goal.id;
    item.innerHTML = `
      <input type="checkbox" class="goal-checkbox" ${checked ? 'checked' : ''} />
      <div class="goal-icon-wrap" style="background:${goal.bg}">${goal.icon}</div>
      <span class="goal-name">${goal.label}</span>
      <span class="goal-pts">+${goal.pts} WP</span>
    `;

    const checkbox = item.querySelector('.goal-checkbox');
    checkbox.addEventListener('change', e => {
      e.stopPropagation();
      setGoalState(goal.id, checkbox.checked);
      // Re-render both lists to stay in sync
      renderGoalsList('goals-list-home');
      renderGoalsList('goals-list-wellness');
      updateWellbeingDisplay();
      _syncGoalToServer(goal.id, checkbox.checked);
    });

    // Tapping the row also toggles
    item.addEventListener('click', e => {
      if (e.target === checkbox) return;
      checkbox.checked = !checkbox.checked;
      checkbox.dispatchEvent(new Event('change'));
    });

    container.appendChild(item);
  });
}

// ── Sync a goal check/uncheck to the server for ranking ──────

async function _syncGoalToServer(goalId, checked) {
  const petId = (typeof getActivePatient === 'function' ? getActivePatient() : null);
  if (!petId) return; // no pet selected yet

  const today = new Date().toISOString().slice(0, 10);
  try {
    const res = await fetch('/api/gamification/daily-goal', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pet_id: petId, goal_id: goalId, date: today, checked }),
    });
    if (!res.ok) return;
    const data = await res.json();
    _updateRankCard(data.percentile);
  } catch { /* network error — ranking display stays as-is */ }
}

function _updateRankCard(percentile) {
  const card   = document.getElementById('achievement-card');
  const rankEl = document.getElementById('achievement-rank');
  if (!card || !rankEl) return;

  if (percentile >= 50) {
    card.style.display = 'flex';
    const topPct = Math.round(100 - percentile);
    rankEl.textContent = topPct === 0
      ? 'You\'re in the TOP 1% of pet parents! Amazing!'
      : `You are in the TOP ${topPct}% of pet parents!`;
  } else if (percentile >= 25) {
    card.style.display = 'flex';
    rankEl.textContent = `You're ahead of ${Math.round(percentile)}% of pet parents — keep it up!`;
  } else {
    card.style.display = 'none';
  }
}

// ── Badge shelf ───────────────────────────────────────────────

function renderBadgeShelf(earnedBadges = []) {
  const shelf = document.getElementById('badge-shelf');
  if (!shelf) return;

  const earnedIds = new Set(
    earnedBadges.map(b => (typeof b === 'string' ? b : b.id))
  );

  shelf.innerHTML = '';

  Object.entries(BADGE_META).forEach(([id, meta]) => {
    const earned = earnedIds.has(id);
    const item   = document.createElement('div');
    item.className = `badge-item ${earned ? 'badge-item--earned' : 'badge-item--locked'}`;
    item.title     = meta.name;
    item.innerHTML = `
      <div class="badge-icon-circle">${meta.emoji}</div>
      <span class="badge-name">${meta.name}</span>
    `;
    shelf.appendChild(item);
  });
}

// ── Gamification API fetch ────────────────────────────────────

async function loadGamification(petId) {
  if (!petId) { renderBadgeShelf([]); return; }
  try {
    const res = await fetch(`/api/gamification/pet-rank?pet_id=${encodeURIComponent(petId)}`);
    if (!res.ok) { renderBadgeShelf([]); return; }

    const data = await res.json();

    if (data.percentile != null) {
      _updateRankCard(data.percentile);
    }
  } catch {
    renderBadgeShelf([]);
  }
}

// ── Fun fact for loading overlay ──────────────────────────────

async function fetchAndShowFact() {
  const factEl = document.getElementById('fact-text');
  if (!factEl) return;
  try {
    const res = await fetch('/api/facts/');
    if (res.ok) {
      const data = await res.json();
      factEl.textContent = data.fact;
    }
  } catch {
    factEl.textContent = 'Regular vet check-ups keep your pet happy and healthy!';
  }
}

// ── Init on page load ─────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  renderGoalsList('goals-list-home');
  renderGoalsList('goals-list-wellness');
  updateWellbeingDisplay();
  renderBadgeShelf([]);
});
