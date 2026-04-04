// ============================================================
// visits.js — visit history timeline
// ============================================================

// ------------------------------------------------------------
// TODO: Fetch visit history
//   - GET /api/visits/?patient_id=<id>
//   - Called when a patient is loaded into the detail panel
//   - Pass result to renderVisitTimeline()
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Render chronological visit timeline cards
//   - Newest visit at the top
//   - Each card shows: date, attending vet, reason for visit, brief notes
//   - Use a vertical timeline layout with connectors between cards
//   - Expand/collapse long notes inline
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Surface active risk flags when logging a new visit
//   - Before showing the "New visit" compose form, fetch current risk_tags
//     for the patient (lightweight call or read from cache)
//   - Display active risk chips as a reminder banner above the form
//   - Example: "⚠ This patient has active flags: Bite risk, Requires muzzle"
//   - Do not block form submission — this is informational only
// ------------------------------------------------------------
