// ============================================================
// ui.js — shared UI utilities and client-side patient cache
// ============================================================
//
// Patient prefetch cache strategy:
//   Cache is a plain JS object keyed by patient ID.
//   Each entry stores:  { data: <patient object>, timestamp: <Date.now()> }
//   TTL is 60 seconds. Entries older than 60s are treated as a cache miss.
//   Cache is invalidated (entry deleted) on any write operation to that patient
//   (POST, PUT, DELETE on patients, notes, vaccines, visits, labs, or grooming).
//   Cache is populated by:
//     1. A background prefetch fired on patient card mouseenter
//     2. A foreground fetch fired on patient card click (if cache miss)
// ============================================================

const API_BASE = "/api";

// ------------------------------------------------------------
// TODO: formatDate(dateStr)
//   - Accept an ISO date string or timestamp
//   - Return a human-readable string, e.g. "Apr 3, 2026"
//   - Handle null/undefined gracefully (return "—")
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: showLoading(context)
//   - Show #loading-overlay
//   - Trigger shimmer animation on skeleton placeholders
//   - Call gamification.js fact fetcher to load a fun fact into .fact-card
//   - Enforce a minimum display time of 800ms
//     (do not allow hideLoading to resolve before 800ms have elapsed)
//   - Store start timestamp so hideLoading can calculate remaining wait
//   - context: optional string describing what is loading (for accessibility)
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: hideLoading(context)
//   - Wait for any remaining time in the 800ms minimum
//   - Fade in the real content (CSS transition)
//   - Hide #loading-overlay
//   - Remove shimmer classes from skeleton elements
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: renderError(msg)
//   - Display an error message in the active panel
//   - Use a styled error card (red left border, icon, message text)
//   - Auto-dismiss after 5 seconds, or on user click
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: showNotification(msg, urgency)
//   - Display a transient notification banner (top of detail panel or fixed position)
//   - urgency levels: "info", "warning", "urgent"
//   - "info"    → green/neutral style
//   - "warning" → gold/amber style (e.g. upcoming vaccine reminder)
//   - "urgent"  → red style (e.g. overdue vaccine, critical risk flag)
//   - Auto-dismiss after 4–6 seconds depending on urgency
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: prefetchOnHover(patientId)
//   - Fire GET /api/patients/<id> in the background
//   - On success, write to cache: patientCache[patientId] = { data, timestamp }
//   - Do not update UI — this is a silent background operation
//   - Debounce: don't fire if a prefetch for this patient is already in-flight
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: getCachedPatient(patientId)
//   - Read patientCache[patientId]
//   - If entry exists and (Date.now() - timestamp) < 60000, return data
//   - Otherwise return null (cache miss or expired)
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: invalidateCache(patientId)
//   - Delete patientCache[patientId]
//   - Call this after any successful write (POST/PUT/DELETE) affecting a patient
// ------------------------------------------------------------
