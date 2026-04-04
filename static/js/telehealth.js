// ============================================================
// telehealth.js — 6-step virtual consult flow
// ============================================================
//
// Philosophy:
//   The goal is to reduce stress for both pet and owner.
//   Maintain a calm, approachable, warm tone throughout all steps.
//   Avoid clinical or alarming language — favor plain, friendly copy.
//   Surface the "cheaper and more convenient than an in-person visit"
//   value proposition near entry points (header button, step 1 intro).
//   For cats specifically, include stress-reduction messaging (e.g.,
//   "No carrier needed", "Your cat stays in their safe space").
// ============================================================

// ------------------------------------------------------------
// STEP 1 — Entry point
// TODO: Open the telehealth flow modal or panel
//   - If a patient is already selected in the dashboard, pre-fill patient
//   - If no patient is selected, show a patient picker (search/dropdown)
//   - Display a brief friendly intro + value prop copy
//   - "Start Consult" button advances to step 2
// ------------------------------------------------------------

// ------------------------------------------------------------
// STEP 2 — Triage form
// TODO: Render concern input + urgency selector
//   - Free-text field: "What's going on with [pet name] today?"
//   - Urgency selector with friendly labels (not clinical):
//       "Just a question"  → low
//       "Something's off"  → medium
//       "I'm worried"      → high
//       "Emergency"        → critical
//   - "Next" button advances to step 3
// ------------------------------------------------------------

// ------------------------------------------------------------
// STEP 3 — Scheduling or instant connect
// TODO: Route based on urgency from step 2
//   - low / medium  → show appointment slot picker (GET /api/telehealth/slots)
//   - high          → offer instant connect option prominently, slot picker secondary
//   - critical      → show urgent warning, redirect to emergency resources,
//                     do not proceed with standard telehealth flow
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Urgency routing logic
//   function routeByUrgency(urgencyLevel)
//   - "critical": display a prominent warning modal with emergency contact info
//     Do NOT allow the user to proceed into the consult flow
//   - "high": show instant connect CTA above the slot picker
//   - "low" / "medium": show slot picker only
// ------------------------------------------------------------

// ------------------------------------------------------------
// STEP 4 — Pre-consult checklist
// TODO: Fetch and display pre-consult checklist
//   - GET /api/telehealth/session/<id>/checklist
//   - Render as a friendly checklist (not a form — just items to read)
//   - Example items: "Have your pet's medications nearby",
//     "Find a quiet room", "Check your camera and microphone"
//   - Species-aware copy: for cats, add "Keep your cat in a familiar space"
// ------------------------------------------------------------

// ------------------------------------------------------------
// STEP 5 — Consult room
// TODO: Render mock consult room UI
//   - Video placeholder area (e.g., gray box with camera icon)
//   - Sidebar: patient name, species, key flags (risk tags, allergies)
//   - Notes field: "Vet's notes" (editable, auto-saved)
//   - "End Consult" button → POST /api/telehealth/session/<id>/end
// ------------------------------------------------------------

// ------------------------------------------------------------
// STEP 6 — Post-consult summary
// TODO: Fetch and render post-consult summary
//   - GET /api/telehealth/session/<id>/summary
//   - Display: vet name, session date/time, consult notes
//   - "Book follow-up" button → opens scheduling flow again (step 3)
//   - "Done" button closes the telehealth panel and returns to dashboard
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Species-aware copy helper
//   function getSpeciesCopy(species, step)
//   - Returns step-specific messaging tailored to the species
//   - Cats: emphasize low-stress, no-travel, in-home comfort
//   - Dogs: energetic, reassuring tone
//   - Exotic/other: neutral, informative tone
// ------------------------------------------------------------
