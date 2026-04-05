// ============================================================
// locations.js — nearby veterinary hospitals and emergency ERs
// ============================================================

const LOCATION_CACHE_KEY = "vet_location_cache";
const LOCATION_CACHE_TTL = 900000; // 15 minutes

let _lastResults = { emergency: [], general: [] };
let _userCoords = null;
let _currentMode = "standard";

// ── Cache helpers ────────────────────────────────────────────

function cacheLastLocation(lat, lng) {
  localStorage.setItem(LOCATION_CACHE_KEY, JSON.stringify({ lat, lng, timestamp: Date.now() }));
}

function loadCachedLocation() {
  try {
    const entry = JSON.parse(localStorage.getItem(LOCATION_CACHE_KEY) || "null");
    if (entry && (Date.now() - entry.timestamp) < LOCATION_CACHE_TTL) {
      return { lat: entry.lat, lng: entry.lng };
    }
  } catch (e) {}
  return null;
}

// ── Entry point ──────────────────────────────────────────────

function openLocationFinder(mode = "standard") {
  _currentMode = mode;
  const modal = document.getElementById("location-finder-modal");
  modal.classList.remove("hidden");
  document.body.style.overflow = "hidden";

  if (mode === "emergency") {
    renderEmergencyMode();
  } else {
    renderStandardMode();
  }

  const cached = loadCachedLocation();
  if (cached) {
    _userCoords = cached;
    if (mode === "emergency") {
      fetchNearbyEmergency(cached.lat, cached.lng);
    } else {
      fetchNearbyVets(cached.lat, cached.lng);
    }
  } else {
    requestGeolocation(mode);
  }
}

function closeLocationFinder() {
  const modal = document.getElementById("location-finder-modal");
  modal.classList.add("hidden");
  document.body.style.overflow = "";
}

function handleBackdropClick(e) {
  if (e.target === document.getElementById("location-finder-modal")) {
    closeLocationFinder();
  }
}

// ── Geolocation ──────────────────────────────────────────────

function requestGeolocation(mode) {
  showLocationStatus("Detecting your location\u2026");

  if (!navigator.geolocation) {
    showZipFallback(mode);
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const { latitude: lat, longitude: lng } = pos.coords;
      _userCoords = { lat, lng };
      cacheLastLocation(lat, lng);
      if (mode === "emergency") {
        fetchNearbyEmergency(lat, lng);
      } else {
        fetchNearbyVets(lat, lng);
      }
    },
    () => {
      showZipFallback(mode);
    },
    { timeout: 8000, maximumAge: 60000 }
  );
}

// ── ZIP fallback ─────────────────────────────────────────────

function showZipFallback(mode) {
  const status = document.getElementById("loc-status");
  status.innerHTML = `
    <p class="loc-zip-label">Enter your ZIP code to find nearby vaccine clinics:</p>
    <div class="loc-zip-row">
      <input type="text" id="loc-zip-input" class="loc-zip-input"
        placeholder="e.g.\u00a080521" maxlength="10" inputmode="numeric" />
      <button class="loc-zip-btn" onclick="submitZipcode('${mode}')">Search</button>
    </div>
    <p class="loc-zip-error hidden" id="loc-zip-error"></p>
  `;

  const input = document.getElementById("loc-zip-input");
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") submitZipcode(mode);
  });
  input.focus();
}

async function submitZipcode(mode) {
  const input = document.getElementById("loc-zip-input");
  const errEl = document.getElementById("loc-zip-error");
  const zip = input ? input.value.trim() : "";

  if (!zip) {
    if (errEl) { errEl.textContent = "Please enter a ZIP code."; errEl.classList.remove("hidden"); }
    return;
  }

  showLocationStatus("Looking up ZIP code\u2026");

  try {
    const resp = await fetch(`/api/locations/geocode?zipcode=${encodeURIComponent(zip)}`);
    const data = await resp.json();
    if (!resp.ok) {
      showZipFallback(mode);
      const e2 = document.getElementById("loc-zip-error");
      if (e2) { e2.textContent = data.error || "ZIP code not found."; e2.classList.remove("hidden"); }
      return;
    }
    _userCoords = { lat: data.lat, lng: data.lng };
    if (mode === "emergency") {
      fetchNearbyEmergency(data.lat, data.lng);
    } else {
      fetchNearbyVets(data.lat, data.lng);
    }
  } catch (e) {
    showZipFallback(mode);
    const e2 = document.getElementById("loc-zip-error");
    if (e2) { e2.textContent = "Could not look up ZIP code. Try again."; e2.classList.remove("hidden"); }
  }
}

// ── Status display ────────────────────────────────────────────

function showLocationStatus(msg) {
  const status = document.getElementById("loc-status");
  status.innerHTML = `<p class="loc-status-msg">${msg}</p>`;
}

// ── Fetch helpers ─────────────────────────────────────────────

async function fetchNearbyVets(lat, lng, filters = {}) {
  showLocationStatus("Finding nearby vaccine clinics\u2026");
  try {
    let url = `/api/locations/nearby?lat=${lat}&lng=${lng}`;
    if (filters.radius) url += `&radius=${filters.radius}`;
    const resp = await fetch(url);
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "Failed to fetch clinics");
    _lastResults = data;
    renderResultsList(data, filters);
  } catch (e) {
    renderError(e.message);
  }
}

async function fetchNearbyEmergency(lat, lng) {
  showLocationStatus("Finding emergency vaccine clinics\u2026");
  try {
    const resp = await fetch(`/api/locations/emergency?lat=${lat}&lng=${lng}`);
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "Failed to fetch emergency clinics");
    _lastResults = { emergency: data.emergency || [], general: [] };
    renderResultsList(_lastResults);
  } catch (e) {
    renderError(e.message);
  }
}

// ── Mode rendering ────────────────────────────────────────────

function renderEmergencyMode() {
  const modal = document.getElementById("location-finder-modal");
  modal.classList.add("emergency-mode");
  modal.classList.remove("standard-mode");

  const title = document.getElementById("loc-modal-title");
  if (title) title.textContent = "Emergency Care Nearby";

  const disclaimer = document.getElementById("loc-disclaimer");
  if (disclaimer) {
    disclaimer.textContent = "For life-threatening emergencies, call your nearest 24-hour animal hospital directly.";
    disclaimer.style.display = "block";
  }

  const filterBar = document.getElementById("loc-filter-bar");
  if (filterBar) filterBar.style.display = "none";
}

function renderStandardMode() {
  const modal = document.getElementById("location-finder-modal");
  modal.classList.remove("emergency-mode");
  modal.classList.add("standard-mode");

  const title = document.getElementById("loc-modal-title");
  if (title) title.textContent = "Find a Vaccine Clinic";

  const disclaimer = document.getElementById("loc-disclaimer");
  if (disclaimer) disclaimer.style.display = "none";

  const filterBar = document.getElementById("loc-filter-bar");
  if (filterBar) filterBar.style.display = "flex";
}

// ── Result list ───────────────────────────────────────────────

function renderResultsList(results, filters = {}) {
  document.getElementById("loc-status").innerHTML = "";

  const list = document.getElementById("loc-results-list");
  list.innerHTML = "";

  const emergency = results.emergency || [];
  const general = filters.emergencyOnly ? [] : (results.general || []);

  const filterFn = (loc) => {
    if (filters.openNow && !loc.is_open_now && !loc.is_24_hours) return false;
    return true;
  };

  const filteredEmergency = emergency.filter(filterFn);
  const filteredGeneral = general.filter(filterFn);

  if (filteredEmergency.length === 0 && filteredGeneral.length === 0) {
    renderZeroResults(list);
    return;
  }

  if (filteredEmergency.length > 0) {
    const section = document.createElement("div");
    section.className = "loc-section";
    section.innerHTML = `<h4 class="loc-section-title loc-section-title--emergency">Emergency / 24-Hour Care</h4>`;
    filteredEmergency.forEach(loc => section.appendChild(renderResultCard(loc, true)));
    list.appendChild(section);
  }

  if (filteredGeneral.length > 0) {
    const section = document.createElement("div");
    section.className = "loc-section";
    section.innerHTML = `<h4 class="loc-section-title">Vaccine Clinics</h4>`;
    filteredGeneral.forEach(loc => section.appendChild(renderResultCard(loc, false)));
    list.appendChild(section);
  }
}

function renderResultCard(location, isEmergency) {
  const card = document.createElement("div");
  card.className = `loc-card ${isEmergency ? "loc-card--emergency" : "loc-card--general"}`;
  card.dataset.locationId = location.id;

  let badgeHtml = "";
  if (location.is_24_hours) {
    badgeHtml = `<span class="loc-badge loc-badge--open">24 Hours</span>`;
  } else if (location.is_open_now === true) {
    badgeHtml = `<span class="loc-badge loc-badge--open">Open Now</span>`;
  } else if (location.is_open_now === false) {
    badgeHtml = `<span class="loc-badge loc-badge--closed">Closed</span>`;
  }

  const phoneHtml = location.phone
    ? `<a href="tel:${location.phone}" class="loc-phone-link">${location.phone}</a>`
    : "";

  const directionsUrl = getDirectionsLink(location.address, location.directions_url);
  const directionsHtml = location.directions_url
    ? `<a href="${directionsUrl}" target="_blank" rel="noopener" class="loc-directions-btn">Get Directions</a>`
    : "";

  card.innerHTML = `
    <div class="loc-card-top">
      <span class="loc-card-name">${location.name}</span>
      ${badgeHtml}
    </div>
    <div class="loc-card-dist">${location.distance_miles} mi away</div>
    ${location.address ? `<p class="loc-card-address">${location.address}</p>` : ""}
    <div class="loc-card-actions">
      ${phoneHtml}
      ${directionsHtml}
    </div>
  `;

  if (location.id) enrichCardWithDetails(location.id, card);

  return card;
}

function renderZeroResults(list) {
  list.innerHTML = `
    <div class="loc-zero">
      <p class="loc-zero-title">No vaccine clinics found nearby.</p>
      <p class="loc-zero-sub">ASPCA Animal Poison Control:
        <a href="tel:8884264435" class="loc-phone-link">888-426-4435</a>
      </p>
      <p class="loc-zero-sub">If your animal is in immediate danger, call 911.</p>
    </div>
  `;
}

function renderError(msg) {
  document.getElementById("loc-status").innerHTML =
    `<p class="loc-error-msg">${msg || "Unable to load clinics right now."}</p>`;
  document.getElementById("loc-results-list").innerHTML = `
    <div class="loc-zero">
      <p class="loc-zero-sub">ASPCA Animal Poison Control:
        <a href="tel:8884264435" class="loc-phone-link">888-426-4435</a>
      </p>
      <p class="loc-zero-sub">If your animal is in immediate danger, call 911.</p>
    </div>
  `;
}

// ── Detail enrichment (phone + website) ──────────────────────

const _detailCache = {};

async function enrichCardWithDetails(locationId, card) {
  if (_detailCache[locationId] === undefined) {
    _detailCache[locationId] = null; // mark in-flight
    try {
      const resp = await fetch(`/api/locations/${locationId}`);
      _detailCache[locationId] = resp.ok ? await resp.json() : null;
    } catch (e) {
      _detailCache[locationId] = null;
    }
  }

  const detail = _detailCache[locationId];
  if (!detail) return;

  const actionsEl = card.querySelector(".loc-card-actions");
  if (!actionsEl) return;

  if (detail.phone && !actionsEl.querySelector(".loc-phone-link")) {
    const a = document.createElement("a");
    a.href = `tel:${detail.phone}`;
    a.className = "loc-phone-link";
    a.textContent = detail.phone;
    actionsEl.prepend(a);
  }

  if (detail.website && !actionsEl.querySelector(".loc-website-link")) {
    const a = document.createElement("a");
    a.href = detail.website;
    a.target = "_blank";
    a.rel = "noopener";
    a.className = "loc-website-link";
    a.textContent = "Website";
    const directionsBtn = actionsEl.querySelector(".loc-directions-btn");
    if (directionsBtn) actionsEl.insertBefore(a, directionsBtn);
    else actionsEl.appendChild(a);
  }
}

// ── Directions ────────────────────────────────────────────────

function getDirectionsLink(address, fallbackUrl) {
  const isIOS = /iP(hone|ad|od)/.test(navigator.userAgent);
  if (isIOS && address) {
    return `maps://maps.apple.com/?daddr=${encodeURIComponent(address)}`;
  }
  return fallbackUrl || `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(address || "")}`;
}

// ── Filters ───────────────────────────────────────────────────

function applyFilters() {
  if (!_lastResults || !_userCoords) return;
  const emergencyOnly = document.getElementById("filter-emergency")?.checked || false;
  const openNow = document.getElementById("filter-open-now")?.checked || false;
  renderResultsList(_lastResults, { emergencyOnly, openNow });
}
