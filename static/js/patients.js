// ============================================================
// patients.js — patient list and detail panel
// ============================================================

async function createPatient() {
    const response = await fetch("/api/patients/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            name: document.getElementById("name").value,
            species: document.getElementById("species").value,
            breed: document.getElementById("breed").value,
            sex: document.getElementById("sex").value,
            dob: document.getElementById("dob").value,
            neutered: document.getElementById("neutered").checked,
            insurance_id: document.getElementById("insurance_id").value,
            weight: parseFloat(document.getElementById("weight").value)
        })
    });

    if (!response.ok) {
        console.error("Error:", response.status, await response.text());
        return;
    }

    const data = await response.json();
    console.log("Created:", data);
    document.getElementById("result").textContent = JSON.stringify(data, null, 2);
}

async function delete_patient() {

    const response = await fetch("http://localhost:5000/api/patients/", {
            method: "DELETE",
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
// Patient list — load on page load
// ------------------------------------------------------------

async function loadPatients() {
  const listEl = document.getElementById("patient-list");
  try {
    const res = await fetch("/api/patients/");
    if (!res.ok) throw new Error(res.statusText);
    const patients = await res.json();
    renderPatientList(patients);
  } catch (err) {
    if (listEl) listEl.innerHTML = `<p style="color:#c0392b;padding:16px;font-size:13px;">Failed to load patients.</p>`;
  }
}

function renderPatientList(patients) {
  const listEl = document.getElementById("patient-list");
  if (!listEl) return;
  listEl.innerHTML = "";

  if (patients.length === 0) {
    listEl.innerHTML = `<p style="padding:16px;font-size:13px;color:var(--csu-mid);">No patients on file.</p>`;
    return;
  }

  patients.forEach(patient => {
    const item = document.createElement("div");
    item.className = "patient-item";
    item.innerHTML = `
      <div class="patient-name">${patient.name || "Unknown"}</div>
      <div class="patient-meta">${[patient.species, patient.breed].filter(Boolean).join(" · ")}</div>
    `;
    item.onclick = () => loadPatientDetail(patient.id);
    listEl.appendChild(item);
  });
}

// ------------------------------------------------------------
// Patient detail — fetch mood + info, render panel
// ------------------------------------------------------------

async function loadPatientDetail(patientId) {
  const infoEl = document.getElementById("patient-info");
  if (infoEl) infoEl.innerHTML = `<p style="color:var(--csu-mid);font-size:13px;padding:16px;">Loading…</p>`;

  try {
    // POST to calculate_patients_mood — returns patient data + mood_image
    const res = await fetch(`/api/patients/${patientId}`, { method: "POST" });
    if (!res.ok) throw new Error(res.statusText);
    const patient = await res.json();
    renderPatientInfo(patient);
    if (typeof loadVaccineCard === "function") loadVaccineCard(patientId);
  } catch (err) {
    if (infoEl) infoEl.innerHTML = `<p style="color:#c0392b;font-size:13px;padding:16px;">Failed to load patient.</p>`;
  }
}

function renderPatientInfo(patient) {
  const infoEl = document.getElementById("patient-info");
  if (!infoEl) return;

  const moodLabel = {
    "/images/face1.png": "Doing great",
    "/images/face2.png": "Doing well",
    "/images/face3.png": "Needs extra care",
  };

  const moodHTML = patient.mood_image
    ? `<div class="mood-widget">
         <img src="${patient.mood_image}" alt="Mood" class="mood-face" />
         <span class="mood-label">${moodLabel[patient.mood_image] || "Unknown"}</span>
       </div>`
    : "";

  const fields = [
    ["Species",  patient.species],
    ["Breed",    patient.breed],
    ["Sex",      patient.sex],
    ["DOB",      patient.dob],
    ["Weight",   patient.weight ? `${patient.weight} lbs` : null],
    ["Neutered", patient.neutered != null ? (patient.neutered ? "Yes" : "No") : null],
  ].filter(([, v]) => v != null);

  infoEl.innerHTML = `
    <div class="card">
      <div class="card-header">
        <h2>${patient.name || "Patient"}</h2>
        ${moodHTML}
      </div>
      <div class="card-body">
        <dl class="patient-fields">
          ${fields.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("")}
        </dl>
      </div>
    </div>`;
}

// Kick off patient list on page load
if (document.getElementById("patient-list")) {
  loadPatients();
}
