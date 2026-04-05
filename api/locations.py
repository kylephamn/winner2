import os
import math
import requests
from flask import Blueprint, jsonify, request

locations_bp = Blueprint("locations", __name__)

GOOGLE_PLACES_KEY = os.environ.get("GOOGLE_PLACES_API_KEY")
PLACES_NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
PLACES_DETAIL_URL = "https://maps.googleapis.com/maps/api/place/details/json"


def _miles_to_meters(miles):
    return int(miles * 1609.34)


def _haversine_miles(lat1, lng1, lat2, lng2):
    """Approximate straight-line distance in miles between two lat/lng points."""
    R = 3958.8  # Earth radius in miles
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _is_24_hours(place):
    periods = place.get("opening_hours", {}).get("periods", [])
    # A single period covering all 7 days with no close time = 24/7
    return len(periods) == 1 and "close" not in periods[0]


def _format_place(place, user_lat, user_lng):
    loc = place.get("geometry", {}).get("location", {})
    distance = _haversine_miles(user_lat, user_lng, loc.get("lat", 0), loc.get("lng", 0))
    address = place.get("vicinity", "")
    directions_url = (
        f"https://www.google.com/maps/dir/?api=1"
        f"&destination={loc.get('lat')},{loc.get('lng')}"
        f"&destination_place_id={place.get('place_id', '')}"
    )
    return {
        "id":             place.get("place_id"),
        "name":           place.get("name"),
        "address":        address,
        "phone":          place.get("formatted_phone_number"),  # only in Detail results
        "distance_miles": round(distance, 2),
        "is_open_now":    place.get("opening_hours", {}).get("open_now"),
        "is_24_hours":    _is_24_hours(place),
        "directions_url": directions_url,
        "specialties":    place.get("types", []),
    }


def _fetch_places(lat, lng, radius_meters, keyword=None):
    if not GOOGLE_PLACES_KEY:
        return None, "GOOGLE_PLACES_API_KEY environment variable is not set"

    params = {
        "location": f"{lat},{lng}",
        "radius":   radius_meters,
        "type":     "veterinary_care",
        "key":      GOOGLE_PLACES_KEY,
    }
    if keyword:
        params["keyword"] = keyword

    resp = requests.get(PLACES_NEARBY_URL, params=params, timeout=10)
    if resp.status_code != 200:
        return None, f"Google Places API error: {resp.status_code}"

    data = resp.json()
    if data.get("status") not in ("OK", "ZERO_RESULTS"):
        return None, f"Google Places error: {data.get('status')}"

    return data.get("results", []), None


@locations_bp.route("/nearby", methods=["GET"])
def find_nearby_vets():
    try:
        lat = float(request.args["lat"])
        lng = float(request.args["lng"])
    except (KeyError, ValueError):
        return jsonify({"error": "lat and lng query params are required and must be numbers"}), 400

    try:
        radius = float(request.args.get("radius", 10))
    except ValueError:
        return jsonify({"error": "radius must be a number (miles)"}), 400

    radius_meters = _miles_to_meters(radius)

    # Fetch all vets and emergency-keyword vets in parallel-ish
    all_places, err = _fetch_places(lat, lng, radius_meters)
    if err:
        return jsonify({"error": err}), 502

    emergency_places, _ = _fetch_places(lat, lng, radius_meters, keyword="emergency 24 hour")

    emergency_ids = {p["place_id"] for p in (emergency_places or [])}

    emergency = []
    general = []
    for place in all_places:
        formatted = _format_place(place, lat, lng)
        if place["place_id"] in emergency_ids or formatted["is_24_hours"]:
            emergency.append(formatted)
        else:
            general.append(formatted)

    # Also include emergency-only results not in the main list
    all_ids = {p["place_id"] for p in all_places}
    for place in (emergency_places or []):
        if place["place_id"] not in all_ids:
            emergency.append(_format_place(place, lat, lng))

    emergency.sort(key=lambda x: x["distance_miles"])
    general.sort(key=lambda x: x["distance_miles"])

    return jsonify({"emergency": emergency, "general": general}), 200


@locations_bp.route("/emergency", methods=["GET"])
def find_nearby_emergency():
    try:
        lat = float(request.args["lat"])
        lng = float(request.args["lng"])
    except (KeyError, ValueError):
        return jsonify({"error": "lat and lng query params are required and must be numbers"}), 400

    places, err = _fetch_places(lat, lng, _miles_to_meters(25), keyword="emergency 24 hour")
    if err:
        return jsonify({"error": err}), 502

    results = sorted(
        [
            {
                "id":             p.get("place_id"),
                "name":           p.get("name"),
                "address":        p.get("vicinity"),
                "phone":          p.get("formatted_phone_number"),
                "distance_miles": round(
                    _haversine_miles(
                        lat, lng,
                        p.get("geometry", {}).get("location", {}).get("lat", 0),
                        p.get("geometry", {}).get("location", {}).get("lng", 0),
                    ), 2
                ),
                "is_open_now": p.get("opening_hours", {}).get("open_now"),
            }
            for p in places
        ],
        key=lambda x: x["distance_miles"],
    )
    return jsonify({"emergency": results}), 200


@locations_bp.route("/<location_id>", methods=["GET"])
def get_location_detail(location_id):
    if not GOOGLE_PLACES_KEY:
        return jsonify({"error": "GOOGLE_PLACES_API_KEY environment variable is not set"}), 500

    params = {
        "place_id": location_id,
        "fields":   (
            "place_id,name,formatted_address,formatted_phone_number,"
            "opening_hours,website,rating,reviews,types,url"
        ),
        "key": GOOGLE_PLACES_KEY,
    }
    resp = requests.get(PLACES_DETAIL_URL, params=params, timeout=10)
    if resp.status_code != 200:
        return jsonify({"error": f"Google Places API error: {resp.status_code}"}), 502

    data = resp.json()
    if data.get("status") == "NOT_FOUND":
        return jsonify({"error": "Location not found"}), 404
    if data.get("status") != "OK":
        return jsonify({"error": f"Google Places error: {data.get('status')}"}), 502

    result = data.get("result", {})
    hours_by_day = result.get("opening_hours", {}).get("weekday_text", [])

    return jsonify({
        "id":            result.get("place_id"),
        "name":          result.get("name"),
        "address":       result.get("formatted_address"),
        "phone":         result.get("formatted_phone_number"),
        "hours":         hours_by_day,
        "website":       result.get("website"),
        "rating":        result.get("rating"),
        "reviews":       result.get("reviews", []),
        "specialties":   result.get("types", []),
        "directions_url": result.get("url"),
        "google_place_id": result.get("place_id"),
    }), 200
