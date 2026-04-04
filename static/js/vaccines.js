// ============================================================
// vaccines.js — vaccine schedule, status badges, and reminders
// ============================================================

// ------------------------------------------------------------
// TODO: Fetch vaccine schedule into patient detail
//   - GET /api/vaccines/?patient_id=<id>
//   - Called when a patient is loaded into the detail panel
//   - Pass result to renderVaccineCard()
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Render vaccine card (#vaccine-card section)
//   - List each vaccine with name, last administered date, next due date
//   - Render a colored status badge next to each vaccine (see bucketing below)
//   - Group by status: overdue first, then due soon, then upcoming, then current
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Render notification bell with overdue count in header
//   - Count vaccines overdue across ALL patients
//   - Display count badge on the bell icon in the header
//   - Update on page load and after any vaccine write
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Render reminder dropdown
//   - On bell click, open a dropdown listing affected patients
//   - Each row shows patient name, vaccine name, days overdue/until due
//   - Clicking a row navigates to that patient's detail panel
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Client-side status bucketing by due date
//   function bucketVaccineStatus(dueDateStr)
//   - Returns "overdue", "due-soon", "upcoming", or "current"
//   - overdue:   due date is in the past
//   - due-soon:  due within 7 days
//   - upcoming:  due within 30 days
//   - current:   due more than 30 days away
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Render colored status badge component
//   function renderVaccineBadge(status)
//   - "overdue"  → red badge
//   - "due-soon" → orange badge
//   - "upcoming" → gold badge
//   - "current"  → green badge
//   - Returns an HTML element (not a string)
// ------------------------------------------------------------
