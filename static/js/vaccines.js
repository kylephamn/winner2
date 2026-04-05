// ============================================================
// vaccines.js — vaccine schedule, status badges, and reminders
// ============================================================

function bucketVaccineStatus(dueDateStr) {
  if (!dueDateStr) return "current";
  const due = new Date(dueDateStr);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const delta = Math.floor((due - today) / 86400000);
  if (delta < 0) return "overdue";
  if (delta <= 7) return "due-soon";
  if (delta <= 30) return "upcoming";
  return "current";
}

function renderVaccineBadge(status) {
  const badge = document.createElement("span");
  badge.className = "badge badge-" + status;
  const labels = { overdue: "Overdue", "due-soon": "Due Soon", upcoming: "Upcoming", current: "Current" };
  badge.textContent = labels[status] || status;
  return badge;
}

async function fetchVaccines(patientId) {
  const res = await fetch(`/api/vaccines/?patient_id=${encodeURIComponent(patientId)}`);
  if (!res.ok) throw new Error("Failed to fetch vaccines");
  return res.json();
}

function renderVaccineCard(vaccines, patientId) {
  const container = document.getElementById("vaccine-card");
  if (!container) return;

  const bucketOrder = { overdue: 0, "due-soon": 1, upcoming: 2, current: 3 };
  vaccines.sort((a, b) => {
    return (bucketOrder[bucketVaccineStatus(a.due_date)] ?? 3)
         - (bucketOrder[bucketVaccineStatus(b.due_date)] ?? 3);
  });

  container.innerHTML = "";

  const card = document.createElement("div");
  card.className = "card";

  // --- Header ---
  const header = document.createElement("div");
  header.className = "card-header";
  header.innerHTML = "<h2>Vaccines</h2>";
  const scanBtn = document.createElement("button");
  scanBtn.className = "btn btn-secondary";
  scanBtn.textContent = "Scan Paper Record";
  scanBtn.onclick = () => {
    const panel = card.querySelector(".vaccine-scan-panel");
    if (panel) panel.style.display = panel.style.display === "none" ? "block" : "none";
  };
  header.appendChild(scanBtn);
  card.appendChild(header);

  // --- Vaccine list ---
  const body = document.createElement("div");
  body.className = "card-body";

  if (vaccines.length === 0) {
    body.innerHTML = `<p class="vaccine-empty">No vaccine records on file.</p>`;
  } else {
    const list = document.createElement("ul");
    list.className = "vaccine-list";
    vaccines.forEach(v => {
      const status = bucketVaccineStatus(v.due_date);
      const li = document.createElement("li");
      li.className = "vaccine-row";

      const info = document.createElement("div");
      info.className = "vaccine-info";
      const nickname = v.nickname ? ` <span class="vaccine-nickname">(${v.nickname})</span>` : "";
      const given = v.administered_date ? `Given: ${v.administered_date}` : "";
      const due   = v.due_date          ? `Due: ${v.due_date}`           : "";
      const sep   = given && due ? " · " : "";
      info.innerHTML = `
        <div class="vaccine-name">${v.name}${nickname}</div>
        <div class="vaccine-dates">${given}${sep}${due}</div>
      `;
      li.appendChild(info);
      li.appendChild(renderVaccineBadge(status));
      list.appendChild(li);
    });
    body.appendChild(list);
  }
  card.appendChild(body);

  // --- Scan panel (hidden by default) ---
  const scanPanel = document.createElement("div");
  scanPanel.className = "vaccine-scan-panel";
  scanPanel.style.display = "none";
  scanPanel.innerHTML = `
    <label class="scan-label">Upload vaccine record image</label>
    <input type="file" id="vaccine-image" accept="image/*" class="scan-file-input" />
    <div class="scan-actions">
      <button class="btn btn-primary" id="scan-save-btn">Scan &amp; Save</button>
    </div>
    <div id="scan-status" class="scan-status"></div>
    <div id="scan-results" class="scan-results"></div>
  `;
  card.appendChild(scanPanel);

  container.appendChild(card);

  // Bind after DOM insertion so the element exists
  card.querySelector("#scan-save-btn").onclick = () => scanAndSave(patientId);
}

function _buildScanResultsHTML(records) {
  if (!records || records.length === 0) return "<p class='scan-no-records'>No vaccine records found in image.</p>";
  return `
    <table class="scan-results-table">
      <thead><tr><th>Vaccine Name</th><th>Nickname</th><th>Date Administered</th></tr></thead>
      <tbody>
        ${records.map(r => `
          <tr>
            <td>${r.name || "—"}</td>
            <td>${r.nickname || "—"}</td>
            <td>${r.administered_date || "—"}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>`;
}

async function scanAndSave(patientId) {
  const fileInput = document.getElementById("vaccine-image");
  const file = fileInput?.files[0];
  if (!file) { alert("Please select an image file."); return; }

  const statusEl  = document.getElementById("scan-status");
  const resultsEl = document.getElementById("scan-results");
  if (statusEl)  statusEl.textContent = "Scanning…";
  if (resultsEl) resultsEl.innerHTML  = "";

  const reader = new FileReader();
  reader.onload = async () => {
    const base64 = reader.result.split(",")[1];
    try {
      const res  = await fetch("/api/vaccines/scan/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: base64, patient_id: patientId }),
      });
      const data = await res.json();

      if (!res.ok) {
        if (statusEl) statusEl.textContent = "Error: " + (data.error || res.statusText);
        if (resultsEl && data.lines && data.lines.length) {
          resultsEl.innerHTML = `<p class="scan-raw-label">Raw OCR lines:</p><ul class="scan-raw-lines">${data.lines.map(l => `<li>${l}</li>`).join("")}</ul>`;
        }
        return;
      }

      const savedMsg   = `Saved ${data.count} vaccine record(s).`;
      const savedHTML  = _buildScanResultsHTML(data.saved);

      // Refresh vaccine list then restore the scan panel state
      const vaccines = await fetchVaccines(patientId);
      renderVaccineCard(vaccines, patientId);

      // renderVaccineCard replaced the DOM — grab fresh references
      const container = document.getElementById("vaccine-card");
      if (container) {
        const panel = container.querySelector(".vaccine-scan-panel");
        if (panel) panel.style.display = "block";
        const newStatus  = container.querySelector("#scan-status");
        const newResults = container.querySelector("#scan-results");
        if (newStatus)  newStatus.textContent = savedMsg;
        if (newResults) newResults.innerHTML  = savedHTML;
      }
    } catch (err) {
      if (statusEl) statusEl.textContent = "Request failed: " + err.message;
    }
  };
  reader.readAsDataURL(file);
}

// Called by scan.html standalone page — scan only, no save
async function readVaccinePaper() {
  const fileInput = document.getElementById("vaccine-image");
  const file = fileInput?.files[0];
  if (!file) { alert("Please select an image file."); return; }

  const statusEl  = document.getElementById("scan-status");
  const resultsEl = document.getElementById("scan-results");
  if (statusEl)  statusEl.textContent = "Scanning…";
  if (resultsEl) resultsEl.innerHTML  = "";

  const reader = new FileReader();
  reader.onload = async () => {
    const base64 = reader.result.split(",")[1];
    try {
      const res  = await fetch("/api/vaccines/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: base64 }),
      });
      const data = await res.json();

      if (!res.ok) {
        if (statusEl) statusEl.textContent = "Error: " + (data.error || res.statusText);
        return;
      }

      if (statusEl) statusEl.textContent = `Found ${data.records.length} record(s).`;
      if (resultsEl) resultsEl.innerHTML = _buildScanResultsHTML(data.records);
    } catch (err) {
      if (statusEl) statusEl.textContent = "Request failed: " + err.message;
    }
  };
  reader.readAsDataURL(file);
}

// Called by patients.js when a patient is selected
async function loadVaccineCard(patientId) {
  const container = document.getElementById("vaccine-card");
  if (container) container.innerHTML = `<p style="color:var(--csu-mid);font-size:13px;padding:16px;">Loading vaccines…</p>`;
  try {
    const vaccines = await fetchVaccines(patientId);
    renderVaccineCard(vaccines, patientId);
  } catch (err) {
    if (container) container.innerHTML = `<p style="color:#c0392b;font-size:13px;padding:16px;">Failed to load vaccines.</p>`;
  }
}