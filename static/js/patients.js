// ============================================================
// patients.js — patient list, hero card, and detail panel
// ============================================================

// ── Load all patients ─────────────────────────────────────────

async function loadPatients() {
  const listEl = document.getElementById('patient-list');
  try {
    const res = await fetch('/api/patients/');
    if (!res.ok) throw new Error(res.statusText);
    const patients = await res.json();
    renderPatientList(patients);

    // Auto-load the first patient on startup
    if (patients.length > 0 && !getActivePatient()) {
      await loadPatientDetail(patients[0].id);
    }
  } catch {
    if (listEl) listEl.innerHTML = '<p class="empty-state" style="color:#c0392b">Failed to load pets.</p>';
  } finally {
    if (typeof hideLoading === 'function') hideLoading();
  }
}

// ── Render patient list (profile tab) + pet selector chips ────

function renderPatientList(patients) {
  const listEl     = document.getElementById('patient-list');
  const selectorEl = document.getElementById('pet-selector');

  if (listEl) listEl.innerHTML = '';

  if (!patients || patients.length === 0) {
    if (listEl)     listEl.innerHTML    = '<p class="empty-state">No pets registered yet.</p>';
    if (selectorEl) selectorEl.style.display = 'none';
    return;
  }

  // Pet selector chips (only when >1 pet)
  if (selectorEl) {
    if (patients.length > 1) {
      selectorEl.style.display = 'flex';
      selectorEl.innerHTML = '';
      patients.forEach(p => {
        const chip  = document.createElement('button');
        chip.className = 'pet-chip';
        chip.id        = 'chip-' + p.id;
        chip.textContent = p.name || 'Pet';
        chip.onclick = () => loadPatientDetail(p.id);
        selectorEl.appendChild(chip);
      });
    } else {
      selectorEl.style.display = 'none';
    }
  }

  // Profile tab — full list cards
  if (listEl) {
    patients.forEach(patient => {
      const species = (patient.species || '').toLowerCase();
      const icon    = species.includes('cat') ? '🐱' : '🐶';

      const item    = document.createElement('div');
      item.className = 'patient-item';
      item.id        = 'patient-item-' + patient.id;
      item.innerHTML = `
        <div class="patient-item-avatar">${icon}</div>
        <div>
          <div class="patient-name">${patient.name || 'Unknown'}</div>
          <div class="patient-meta">${[patient.species, patient.breed].filter(Boolean).join(' · ')}</div>
        </div>
      `;
      item.onmouseenter = () => { if (typeof prefetchOnHover === 'function') prefetchOnHover(patient.id); };
      item.onclick      = () => { loadPatientDetail(patient.id); switchTab('home'); };
      listEl.appendChild(item);
    });
  }
}

// ── Load and display a single patient ────────────────────────

async function loadPatientDetail(patientId) {
  if (typeof setActivePatient === 'function') setActivePatient(patientId);

  // Highlight active chip + list item
  document.querySelectorAll('.pet-chip').forEach(c => c.classList.remove('active'));
  document.querySelectorAll('.patient-item').forEach(i => i.classList.remove('active'));
  const chip     = document.getElementById('chip-' + patientId);
  const listItem = document.getElementById('patient-item-' + patientId);
  if (chip)     chip.classList.add('active');
  if (listItem) listItem.classList.add('active');

  try {
    // POST to calculate_patients_mood — returns patient data + mood_image
    const res = await fetch(`/api/patients/${patientId}`, { method: 'POST' });
    if (!res.ok) throw new Error(res.statusText);
    const patient = await res.json();

    renderPatientHero(patient);
    renderPatientInfo(patient);

    // Re-render goals so state is scoped to the newly active pet
    if (typeof renderGoalsList === 'function') {
      renderGoalsList('goals-list-home');
      renderGoalsList('goals-list-wellness');
    }

    if (typeof loadVaccineCard    === 'function') loadVaccineCard(patientId);
    if (typeof loadVisitHistory   === 'function') loadVisitHistory(patientId);
    if (typeof loadGamification   === 'function') loadGamification(patientId);
  } catch (err) {
    console.error('Failed to load patient:', err);
  }
}

// ── Populate hero card (home tab) ─────────────────────────────

function renderPatientHero(patient) {
  const nameEl = document.getElementById('hero-name');
  const metaEl = document.getElementById('hero-meta');
  const ptsEl  = document.getElementById('hero-pts');

  if (nameEl) nameEl.textContent = patient.name || 'Your Pet';

  const headerTitle = document.getElementById('app-header-title');
  if (headerTitle) headerTitle.textContent = patient.name ? `${patient.name}'s Well-being` : 'My Pet Well-being';

  // Age from DOB
  let ageStr = '';
  if (patient.dob) {
    const age = Math.floor((Date.now() - new Date(patient.dob)) / (365.25 * 24 * 3600 * 1000));
    ageStr = `${age} year${age !== 1 ? 's' : ''} old`;
  }
  const breedLine = [patient.species, patient.breed].filter(Boolean).join(' · ');
  if (metaEl) metaEl.textContent = ageStr || breedLine;

  // Wellness points — show a placeholder; gamification.js overwrites when API data arrives
  if (ptsEl && !ptsEl.textContent.includes('Wellness Points')) {
    ptsEl.textContent = '— Wellness Points';
  }

  // Track species so gamification.js can pick the right images
  if (typeof setActivePetSpecies === 'function') setActivePetSpecies(patient.species);

  // Update header avatar and body image based on wellness score
  if (typeof updateWellbeingDisplay === 'function') updateWellbeingDisplay();
}

// ── Render patient info card (profile tab) ────────────────────

function renderPatientInfo(patient) {
  const infoEl = document.getElementById('patient-info');
  if (!infoEl) return;

  const moodLabels = {
    '/images/face1.png':       'Feeling great',
    '/images/face2.png':       'Doing well',
    '/images/face3.png':       'Happy & healthy',
    '/images/face4.png':       'Content',
    '/images/face5.png':       'Playful',
    '/images/cat_happy.png':   'Purrfectly happy',
    '/images/cat_neutral.png': 'Cool & content',
    '/images/cat_sad.png':     'Feeling grumpy',
  };

  const moodHTML = patient.mood_image
    ? `<div class="mood-widget">
         <img src="${patient.mood_image}" alt="Mood" class="mood-face" />
         <span class="mood-label">${moodLabels[patient.mood_image] || ''}</span>
       </div>`
    : '';

  let ageStr = '—';
  if (patient.dob) {
    const age = Math.floor((Date.now() - new Date(patient.dob)) / (365.25 * 24 * 3600 * 1000));
    ageStr = `${age} year${age !== 1 ? 's' : ''}`;
  }

  const fields = [
    ['Species',  patient.species],
    ['Breed',    patient.breed],
    ['Sex',      patient.sex],
    ['Age',      ageStr],
    ['Weight',   patient.weight ? `${patient.weight} lbs` : null],
    ['Neutered', patient.neutered != null ? (patient.neutered ? 'Yes' : 'No') : null],
  ].filter(([, v]) => v != null);

  infoEl.innerHTML = `
    <div class="card">
      <div class="card-header">
        <h2>${patient.name || 'Patient'}</h2>
        ${moodHTML}
      </div>
      <div class="card-body">
        <dl class="patient-fields">
          ${fields.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join('')}
        </dl>
      </div>
    </div>`;
}

// ── Create patient (used on /register page) ───────────────────

async function createPatient() {
  const data = {
    name:         (document.getElementById('name')?.value         || '').trim(),
    species:      (document.getElementById('species')?.value      || '').trim(),
    breed:        (document.getElementById('breed')?.value        || '').trim(),
    sex:          (document.getElementById('sex')?.value          || '').trim(),
    dob:          (document.getElementById('dob')?.value          || ''),
    neutered:     document.getElementById('neutered')?.checked    ?? false,
    insurance_id: (document.getElementById('insurance_id')?.value || '').trim(),
    weight:       parseFloat(document.getElementById('weight')?.value) || null,
  };

  const res = await fetch('/api/patients/', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(data),
  });

  const resultEl = document.getElementById('result');

  if (!res.ok) {
    const err = await res.text();
    console.error('Error:', res.status, err);
    if (resultEl) resultEl.textContent = 'Error: ' + err;
    return;
  }

  const created = await res.json();
  if (resultEl) resultEl.textContent = '✓ Registered ' + (created.name || 'pet') + '!';

  // Brief pause, then redirect home
  setTimeout(() => { window.location.href = '/'; }, 1200);
  return created;
}

// ── Delete patient ────────────────────────────────────────────

async function delete_patient() {
  const id = typeof getActivePatient === 'function' ? getActivePatient() : null;
  if (!id) { alert('No patient selected.'); return; }
  if (!confirm('Remove this patient permanently?')) return;

  const res = await fetch(`/api/patients/${id}`, { method: 'DELETE' });
  if (res.ok) {
    if (typeof invalidateCache === 'function') invalidateCache(id);
    loadPatients();
  }
}

// ── Boot ──────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  // Only auto-load if we're on the main dashboard (has patient-list)
  if (document.getElementById('patient-list') || document.getElementById('hero-card')) {
    loadPatients();
  }
});
