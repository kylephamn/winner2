// ============================================================
// gamification.js — daily goals, wellness score, badges, facts
// ============================================================

// ── Daily goals definition ────────────────────────────────────
const DAILY_GOALS = [
  { id: 'breakfast', icon: '🍽️', label: 'Healthy Breakfast', pts: 50,  bg: '#F9D8A0' },
  { id: 'walk',      icon: '🐕', label: 'A Long Walk',        pts: 100, bg: '#F4A8A0' },
  { id: 'teeth',     icon: '🦷', label: 'Teeth Brushing',     pts: 30,  bg: '#A0D8D4' },
  { id: 'checkin',   icon: '❤️', label: 'Check-in with Vet', pts: 10,  bg: '#F4A0B8' },
];

const BADGE_META = {
  first_steps:       { emoji: '👟', name: 'First Steps'        },
  health_starter:    { emoji: '🌱', name: 'Health Starter'     },
  wellness_champion: { emoji: '🏆', name: 'Wellness Champion'  },
  dedicated_owner:   { emoji: '⭐', name: 'Dedicated Owner'    },
  pet_health_hero:   { emoji: '🦸', name: 'Pet Health Hero'    },
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

  // Choose images based on wellness
  let faceImg, bodyImg;
  if (pct >= 75) {
    faceImg = '/images/face3.png';   // happy
    bodyImg = '/images/body3.png';  // excited/wagging
  } else if (pct >= 40) {
    faceImg = '/images/face1.png';   // neutral
    bodyImg = '/images/body3.png';
  } else {
    faceImg = '/images/sad_dog.png'; // saddest
    bodyImg = '/images/body1.png';  // sad
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
