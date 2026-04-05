// ============================================================
// visits.js — visit history timeline
// ============================================================

async function loadVisitHistory(patientId) {
  const container = document.getElementById('visit-history');
  if (!container) return;
  container.innerHTML = '<p class="empty-state">Loading visit history…</p>';

  try {
    const res = await fetch(`/api/visits/?patient_id=${encodeURIComponent(patientId)}`);
    if (!res.ok) throw new Error(res.statusText);
    const visits = await res.json();
    renderVisitTimeline(visits);
  } catch {
    container.innerHTML = '<p class="empty-state" style="color:#c0392b">Could not load visit history.</p>';
  }
}

function renderVisitTimeline(visits) {
  const container = document.getElementById('visit-history');
  if (!container) return;

  if (!visits || visits.length === 0) {
    container.innerHTML = '<p class="empty-state">No visit records on file yet.</p>';
    return;
  }

  // Newest visits first
  const sorted = [...visits].sort((a, b) => new Date(b.visit_date) - new Date(a.visit_date));

  const timeline = document.createElement('div');
  timeline.className = 'visit-timeline';

  sorted.forEach(visit => {
    const entry = document.createElement('div');
    entry.className = 'visit-entry';

    const dateLabel = typeof formatDate === 'function'
      ? formatDate(visit.visit_date)
      : visit.visit_date || '—';

    const vetLine = visit.attending_vet
      ? `<div class="visit-vet">Dr. ${visit.attending_vet}</div>`
      : '';

    const notesLine = visit.notes
      ? `<div class="visit-notes">${visit.notes}</div>`
      : '';

    entry.innerHTML = `
      <div class="visit-card">
        <div class="visit-date">${dateLabel}</div>
        <div class="visit-reason">${visit.reason || 'General Visit'}</div>
        ${vetLine}
        ${notesLine}
      </div>
    `;

    timeline.appendChild(entry);
  });

  container.innerHTML = '';
  container.appendChild(timeline);
}
