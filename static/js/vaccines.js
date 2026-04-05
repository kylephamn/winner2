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

async function readVaccinePaper() {
    const fileInput = document.getElementById("vaccine-image");
    const file = fileInput.files[0];
    if (!file) {
        alert("Please select an image file first.");
        return;
    }

    const statusEl = document.getElementById("scan-status");
    const resultsEl = document.getElementById("scan-results");
    if (statusEl) statusEl.textContent = "Scanning…";
    if (resultsEl) resultsEl.innerHTML = "";

    const reader = new FileReader();
    reader.onload = async () => {
        const base64 = reader.result.split(",")[1];  // strip the data:image/... prefix

        try {
            const response = await fetch("/api/vaccines/scan", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ image: base64 })
            });

            const data = await response.json();

            if (!response.ok) {
                if (statusEl) statusEl.textContent = "Error: " + (data.error || response.statusText);
                return;
            }

            const records = data.records || [];
            const raw = data.lines || [];

            if (records.length > 0) {
                if (statusEl) statusEl.textContent = `Parsed ${records.length} vaccine record(s):`;
                if (resultsEl) {
                    records.forEach(r => {
                        const p = document.createElement("p");
                        p.textContent = `${r.administered_date}  |  ${r.nickname}  |  ${r.name}`;
                        resultsEl.appendChild(p);
                    });
                }
            } else {
                if (statusEl) statusEl.textContent = `No structured records found. Raw OCR (${raw.length} line(s)):`;
                if (resultsEl) {
                    raw.forEach(line => {
                        const p = document.createElement("p");
                        p.textContent = line;
                        resultsEl.appendChild(p);
                    });
                }
            }
        } catch (err) {
            if (statusEl) statusEl.textContent = "Request failed: " + err.message;
        }
    };
    reader.readAsDataURL(file);
}

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
