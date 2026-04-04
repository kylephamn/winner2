// ============================================================
// locations.js — nearby veterinary hospitals and emergency ERs
// ============================================================
//
// This feature is standalone — it does not require a patient to be selected.
// A panicking owner should be able to get an address and phone number in
// under 10 seconds. Speed and clarity are the absolute priority.
//
// Entry points:
//   1. Header "Find Emergency Care" button → openLocationFinder("emergency")
//   2. Patient detail referral link        → openLocationFinder("standard")
//   3. Telehealth triage high urgency      → openLocationFinder("emergency")
// ============================================================

// ------------------------------------------------------------
// TODO: openLocationFinder(mode)
//   - mode: "emergency" | "standard"
//   - Show #location-finder-modal
//   - If mode === "emergency", call renderEmergencyMode() first
//   - Try loadCachedLocation() — if valid coords exist, skip geolocation prompt
//     and immediately call fetchNearbyEmergency() or fetchNearbyVets()
//   - Otherwise call requestGeolocation()
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: requestGeolocation()
//   - Call navigator.geolocation.getCurrentPosition()
//   - On success: call cacheLastLocation(lat, lng), then fetch results
//   - On denial or error: show ZIP code / city text input as fallback
//   - Do not require login or account at any point
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: fetchNearbyVets(lat, lng, filters)
//   - GET /api/locations/nearby?lat=<lat>&lng=<lng>&...filters
//   - filters: { emergencyOnly, openNow, specialty }
//   - On success: call renderResultsList(results)
//   - On error: call renderError() with a fallback message (see UX notes)
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: fetchNearbyEmergency(lat, lng)
//   - GET /api/locations/emergency?lat=<lat>&lng=<lng>
//   - Fast path — no filter params, minimal payload
//   - On success: call renderResultsList({ emergency: results, general: [] })
//   - On error: show fallback with ASPCA Poison Control (888-426-4435)
//     and suggestion to call 911 for immediate danger
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: renderResultsList(results)
//   - results: { emergency: [...], general: [...] }
//   - Render "Emergency / 24-Hour Care" section first (always, even if empty)
//   - Render "General Veterinary Clinics" section second
//   - Each item rendered via renderResultCard(location)
//   - If both arrays are empty, show zero-results fallback message:
//       ASPCA Animal Poison Control: 888-426-4435
//       "If your animal is in immediate danger, call 911."
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: renderResultCard(location)
//   - Render a single clinic card with:
//       Clinic name (bold)
//       Distance in miles from user location (e.g. "1.2 mi")
//       Address (full street address)
//       Phone number — tap-to-call <a href="tel:..."> on mobile, large touch target
//       Hours / open status: "Open now", "Closes at 6pm", "24 Hours", "Closed"
//       "Get Directions" button → getDirectionsLink(address, lat, lng)
//       Specialty badge(s) if applicable (Oncology, Cardiology, etc.)
//   - ER cards get a red left border; general cards get a green left border
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: renderMap(results, userLocation)
//   - Render an embedded map inside #map-container
//   - ER locations: red pins
//   - General clinics: green pins
//   - User location: blue dot
//   - On mobile: map collapses by default (list shown first)
//   - Clicking a pin calls handlePinClick(locationId)
//   - TODO: decide on map provider (Google Maps JS SDK, Leaflet + OSM, Mapbox)
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: handlePinClick(locationId)
//   - Scroll to and visually highlight the matching result card in the list
//   - Apply a highlighted/active state class to the card
//   - Remove highlight from any previously highlighted card
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: applyFilters(filters)
//   - filters: { emergencyOnly: bool, openNow: bool, specialty: string }
//   - Client-side: re-filter the last fetched results array (no new network call)
//   - Re-render result list and map pins with filtered set
//   - "Emergency only" hides general clinics entirely
//   - "Open now" hides any location where is_open_now === false
//   - Specialty filters to locations where specialties[] includes the value
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: renderEmergencyMode()
//   - Apply red accent color scheme to the modal (add .emergency-mode class)
//   - Increase font size for phone numbers — large, tap-to-call
//   - Show prominent disclaimer at top of modal:
//     "For life-threatening emergencies, call your nearest 24-hour animal hospital directly."
//   - Hide general clinics section by default
//   - Hide filter bar (emergency mode is not the time to filter)
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: getDirectionsLink(address, lat, lng)
//   - Detect platform: iOS (navigator.platform / userAgent)
//   - iOS:   return "maps://maps.apple.com/?daddr=<encoded address>"
//   - Other: return "https://www.google.com/maps/dir/?api=1&destination=<lat,lng>"
//   - Prefer coordinates over address string for accuracy
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: cacheLastLocation(lat, lng)
//   - Write to localStorage: { lat, lng, timestamp: Date.now() }
//   - Key: "vet_location_cache"
//   - TTL: 15 minutes (900000ms) — location changes slowly, but not never
// ------------------------------------------------------------

// ------------------------------------------------------------
// TODO: loadCachedLocation()
//   - Read localStorage["vet_location_cache"]
//   - If entry exists and (Date.now() - timestamp) < 900000, return { lat, lng }
//   - Otherwise return null
// ------------------------------------------------------------
