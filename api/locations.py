from flask import Blueprint, jsonify, request

locations_bp = Blueprint("locations", __name__)

# ---------------------------------------------------------------------------
# Nearby veterinary locations
# ---------------------------------------------------------------------------
# Results are split into two types:
#
#   Emergency / 24-Hour  — ERs and 24-hour hospitals; always listed first.
#                          Used for the fast-path emergency finder and any
#                          urgency-routed telehealth triage.
#
#   General Clinics      — Standard practices; listed second. Used for
#                          non-emergency referrals, specialist searches,
#                          and after-hours planning.
#
# Recommended data source: Google Places API (Text Search / Nearby Search).
#   - Best accuracy for hours, phone numbers, and open/closed status.
#   - Supports type filtering (veterinary_care) and keyword filtering (emergency).
#
# TODO: Configure API key via environment variable — NEVER hardcode it.
#   Load with:  import os; GOOGLE_PLACES_KEY = os.environ["GOOGLE_PLACES_API_KEY"]
#
# Alternative sources to evaluate:
#   - Yelp Fusion API  (good reviews data, weaker hours reliability)
#   - Vetted static dataset (full control, but requires ongoing maintenance)
# ---------------------------------------------------------------------------


@locations_bp.route("/nearby", methods=["GET"])
def find_nearby_vets():
    # TODO: Accept lat, lng, radius (miles), and optional filters via query params
    #       Return results split into { emergency: [...], general: [...] }
    #       Each result includes: id, name, address, phone, distance_miles,
    #       hours, is_open_now, is_24_hours, specialties[], directions_url
    pass


@locations_bp.route("/emergency", methods=["GET"])
def find_nearby_emergency():
    # TODO: Accept lat, lng query params — emergency/24-hour results only
    #       Optimized for speed: minimal fields, no specialty filtering
    #       Returns: id, name, address, phone, distance_miles, is_open_now
    pass


@locations_bp.route("/<location_id>", methods=["GET"])
def get_location_detail(location_id):
    # TODO: Return full detail for a single clinic
    #       Fields: name, address, phone, full hours by day, specialties,
    #       website, reviews summary, Google Place ID
    pass
