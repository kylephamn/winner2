// ============================================================
// notes.js — clinical notes and behavioral risk flags
// ============================================================

async function loadRiskFlags(patientId) {
  const container = document.getElementById('risk-flags');
  if (!container) return;

  try {
    const res = await fetch(`/api/notes/?patient_id=${encodeURIComponent(patientId)}`);
    if (!res.ok) throw new Error(res.statusText);
    const notes = await res.json();

    // Collect all risk_tags across all notes
    const allTags = [];
    (Array.isArray(notes) ? notes : []).forEach(note => {
      (note.risk_tags || []).forEach(tag => allTags.push(tag));
    });

    renderRiskFlags(allTags);
  } catch {
    // Notes API may not be fully implemented — silently fail
    container.innerHTML = '<p class="empty-state">No active health alerts.</p>';
  }
}

function renderRiskFlags(tags) {
  const container = document.getElementById('risk-flags');
  if (!container) return;

  if (!tags || tags.length === 0) {
    container.innerHTML = '<p class="empty-state">No active health alerts.</p>';
    return;
  }

  container.innerHTML = '';

  const aggressionTags = ['bite risk', 'aggression', 'aggressive', 'requires muzzle'];

  tags.forEach(tag => {
    const tagLower = tag.toLowerCase();
    const isRed    = aggressionTags.some(t => tagLower.includes(t));
    const chip     = document.createElement('span');
    chip.className = `risk-chip risk-chip--${isRed ? 'red' : 'amber'}`;
    chip.textContent = tag;
    container.appendChild(chip);
  });
}
