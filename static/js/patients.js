// ============================================================
// patients.js — patient list and detail panel
// ============================================================

async function createPatient() {
    const response = await fetch("http://localhost:5000/api/patients/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: "Buddy",
                species: "Dog",
                breed: "Labrador",
                sex: "M",
                dob: "2020-01-01",
                neutered: true,
                insurance_id: "INS123",
                weight: 65
            })
        });

    const data = await response.json();
    console.log(data);
}


// ------------------------------------------------------------
// TODO: Fetch patient list on page load
//   - GET /api/patients/
//   - Call showLoading() before fetch, hideLoading() after
//   - On success, call renderPatientList(patients)
//   - On error, call renderError(msg)
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Render sidebar patient cards
//   - For each patient, create a .patient-item element
//   - Include a risk flag icon if patient has any active risk_tags
//   - Include a vaccine status dot (colored per worst bucket: red > orange > gold)
//   - Attach mouseenter handler → prefetchOnHover(patient.id)
//   - Attach click handler → loadPatientDetail(patient.id)
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Fetch and render patient detail panel
//   function loadPatientDetail(patientId)
//   - On click, read from cache first: getCachedPatient(patientId)
//   - If cache hit (not expired), render immediately from cache
//   - If cache miss or TTL expired, fetch GET /api/patients/<id>
//     then write result to cache before rendering
//   - Call each section renderer: renderRiskFlags, renderBasicInfo,
//     renderMedsAllergies, renderVaccineCard, renderVitals,
//     renderVisitTimeline, renderLabsGrooming, renderGamification
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Prefetch on hover
//   - On mouseenter of a patient card, fire GET /api/patients/<id>
//     in the background (do not await in the UI thread)
//   - Write result to the patient cache keyed by patient ID
//   - This is handled via ui.js prefetchOnHover(patientId)
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: Cache invalidation on write
//   - After any POST/PUT/DELETE that modifies a patient record,
//     call invalidateCache(patientId) from ui.js
//   - Then re-fetch fresh data and re-render the detail panel
// ------------------------------------------------------------
