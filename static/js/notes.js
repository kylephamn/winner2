// ============================================================
// notes.js — clinical notes and behavioral risk flags
// ============================================================

// ------------------------------------------------------------
// TODO: Fetch risk flags (lightweight, for sidebar)
//   - GET /api/notes/?patient_id=<id>&fields=risk_tags
//   - Return only risk_tags array, not full note text
//   - Used to render the risk icon on sidebar patient cards
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Render risk flag chips on detail panel
//   - Each tag renders as a colored chip inside #risk-flags section
//   - "Bite risk" and aggression tags → red chip
//   - "Anxious / easily stressed" and anxiety tags → amber chip
//   - All chips are removable (× button triggers DELETE/PUT on note)
//   - Chips should be visually prominent — display above other sections
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Render risk flag tooltip on sidebar hover
//   - On hover of a patient card's risk icon, show a small tooltip
//   - Tooltip lists all active risk tag strings for that patient
//   - Hide tooltip on mouseleave
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Render full notes section with tag management UI
//   - Display full note text per note record
//   - Show existing risk_tags as chips within each note
//   - Include an "Add tag" control (dropdown of predefined tags + free-text input)
//   - Include a "New note" button that opens an inline compose area
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Add risk flag handler
//   - On tag add: PUT /api/notes/<id> with updated risk_tags array
//   - After success, re-render chips and invalidate patient cache
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Remove risk flag handler
//   - On chip × click: PUT /api/notes/<id> with tag removed from array
//   - After success, re-render chips and invalidate patient cache
// ------------------------------------------------------------
