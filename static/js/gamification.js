// ============================================================
// gamification.js — pet health progress, badges, and fun facts
// ============================================================

// ------------------------------------------------------------
// TODO: Fetch pet progress
//   - GET /api/gamification/?patient_id=<id>
//   - Returns: points total, earned badges, next milestone, progress %
//   - Called when a patient is loaded into the detail panel
//   - Pass result to renderGamificationWidget()
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Render progress bar + badge shelf on detail panel
//   - Progress bar fills to (points / next_milestone_threshold) %
//   - Use gold fill color for the bar (CSU gold)
//   - Badge shelf: row of badge icons — earned are full color, locked are grayscale
//   - Show badge name on hover (tooltip)
//   - Display next milestone label below the bar: "Next: Senior Wellness Champion"
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Fetch and display fun fact on loading screen
//   - GET /api/facts/
//   - Call this whenever showLoading() is triggered (see ui.js)
//   - Render the fact text inside #loading-overlay .fact-card
//   - Display should feel warm and friendly — not a loader spinner replacement,
//     but a delightful moment while data loads
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Trigger loading fact fetch whenever showLoading() is called
//   - Hook into ui.js showLoading() so that every time the overlay appears,
//     a fresh fun fact is fetched and displayed
//   - If the fact fetch is slower than the 800ms minimum, show a placeholder
//     ("Did you know...") until the fact arrives
// ------------------------------------------------------------
