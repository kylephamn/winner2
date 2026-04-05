import uuid
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from db import db

users_bp = Blueprint("users", __name__)

# ---------------------------------------------------------------------------
# User record schema (Firestore document: /users/<user_id>)
# ---------------------------------------------------------------------------
# {
#   "user_id":      str,           # auto-generated Firestore document ID
#   "first_name":   str,
#   "last_name":    str,
#   "phone":        str,           # E.164 format recommended, e.g. "+15551234567"
#   "address":      {
#                     "street": str,
#                     "city":   str,
#                     "state":  str,
#                     "zip":    str
#                   },
#   "dob":          str,           # ISO 8601 date, e.g. "1990-04-15"
#   "gamification": {
#                     "points":       int,
#                     "badges":       [{ "id": str, "name": str, "earned_at": str }],
#                     "redemptions":  [str]   # redemption record IDs
#                   },
#   "pet_ids":      [str]          # list of patient/pet document IDs
# }
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = {"first_name", "last_name", "phone", "address", "dob"}
UPDATABLE_FIELDS = {"first_name", "last_name", "phone", "address", "dob"}

# Points awarded per event type
POINTS_PER_EVENT = {
    "vaccination":    100,
    "wellness_visit": 150,
    "biometrics":      75,
    "grooming":        50,
}

# Badge definitions: (id, name, points_threshold)
BADGE_MILESTONES = [
    {"id": "first_steps",        "name": "First Steps",        "threshold": 100},
    {"id": "health_starter",     "name": "Health Starter",     "threshold": 300},
    {"id": "wellness_champion",  "name": "Wellness Champion",  "threshold": 500},
    {"id": "dedicated_owner",    "name": "Dedicated Owner",    "threshold": 1000},
    {"id": "pet_health_hero",    "name": "Pet Health Hero",    "threshold": 2000},
]


def _check_new_badges(current_points, previous_points, existing_badge_ids):
    """Return list of newly unlocked badge dicts."""
    now = datetime.now(timezone.utc).isoformat()
    new_badges = []
    for badge in BADGE_MILESTONES:
        if (
            badge["id"] not in existing_badge_ids
            and previous_points < badge["threshold"] <= current_points
        ):
            new_badges.append({
                "id": badge["id"],
                "name": badge["name"],
                "earned_at": now,
            })
    return new_badges


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

@users_bp.route("/", methods=["GET"])
def list_users():
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
    except ValueError:
        return jsonify({"error": "page and limit must be integers"}), 400

    offset = (page - 1) * limit
    docs = db.collection("users").limit(limit).offset(offset).stream()
    users = [{"user_id": doc.id, **doc.to_dict()} for doc in docs]
    return jsonify({"page": page, "limit": limit, "users": users}), 200


@users_bp.route("/<string:user_id>", methods=["GET"])
def get_user(user_id):
    doc = db.collection("users").document(user_id).get()
    if not doc.exists:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user_id": doc.id, **doc.to_dict()}), 200


@users_bp.route("/", methods=["POST"])
def create_user():
    data = request.get_json(silent=True) or {}
    missing = REQUIRED_FIELDS - data.keys()
    if missing:
        return jsonify({"error": f"Missing required fields: {sorted(missing)}"}), 400

    user_id = str(uuid.uuid4())
    user = {
        "first_name":   data["first_name"],
        "last_name":    data["last_name"],
        "phone":        data["phone"],
        "address":      data["address"],
        "dob":          data["dob"],
        "gamification": {"points": 0, "badges": [], "redemptions": []},
        "pet_ids":      [],
    }
    db.collection("users").document(user_id).set(user)
    return jsonify({"user_id": user_id, **user}), 201


@users_bp.route("/<string:user_id>", methods=["PUT"])
def update_user(user_id):
    doc_ref = db.collection("users").document(user_id)
    if not doc_ref.get().exists:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}
    updates = {k: v for k, v in data.items() if k in UPDATABLE_FIELDS}
    if not updates:
        return jsonify({"error": "No updatable fields provided"}), 400

    doc_ref.update(updates)
    updated = doc_ref.get()
    return jsonify({"user_id": updated.id, **updated.to_dict()}), 200


@users_bp.route("/<string:user_id>", methods=["DELETE"])
def delete_user(user_id):
    doc_ref = db.collection("users").document(user_id)
    if not doc_ref.get().exists:
        return jsonify({"error": "User not found"}), 404
    doc_ref.delete()
    return "", 204


# ---------------------------------------------------------------------------
# Pet associations
# ---------------------------------------------------------------------------

@users_bp.route("/<string:user_id>/pets", methods=["GET"])
def list_user_pets(user_id):
    doc = db.collection("users").document(user_id).get()
    if not doc.exists:
        return jsonify({"error": "User not found"}), 404

    pet_ids = doc.to_dict().get("pet_ids", [])
    expand = request.args.get("expand", "false").lower() == "true"

    if not expand:
        return jsonify({"pet_ids": pet_ids}), 200

    pets = []
    for pid in pet_ids:
        pet_doc = db.collection("pets").document(pid).get()
        if pet_doc.exists:
            pets.append({"id": pet_doc.id, **pet_doc.to_dict()})
    return jsonify({"pets": pets}), 200


@users_bp.route("/<string:user_id>/pets", methods=["POST"])
def add_pet(user_id):
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()
    if not doc.exists:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}
    pet_id = data.get("pet_id")
    if not pet_id:
        return jsonify({"error": "pet_id is required"}), 400

    pet_ids = doc.to_dict().get("pet_ids", [])
    if pet_id in pet_ids:
        return jsonify({"error": "Pet already linked to this user"}), 409

    pet_ids.append(pet_id)
    doc_ref.update({"pet_ids": pet_ids})
    return jsonify({"pet_ids": pet_ids}), 200


@users_bp.route("/<string:user_id>/pets/<string:pet_id>", methods=["DELETE"])
def remove_pet(user_id, pet_id):
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()
    if not doc.exists:
        return jsonify({"error": "User not found"}), 404

    pet_ids = doc.to_dict().get("pet_ids", [])
    if pet_id not in pet_ids:
        return jsonify({"error": "Pet not linked to this user"}), 404

    pet_ids.remove(pet_id)
    doc_ref.update({"pet_ids": pet_ids})
    return "", 204


# ---------------------------------------------------------------------------
# Gamification (user-scoped)
# ---------------------------------------------------------------------------

@users_bp.route("/<string:user_id>/gamification", methods=["GET"])
def get_user_gamification(user_id):
    doc = db.collection("users").document(user_id).get()
    if not doc.exists:
        return jsonify({"error": "User not found"}), 404

    gamification = doc.to_dict().get("gamification", {"points": 0, "badges": [], "redemptions": []})
    return jsonify(gamification), 200


@users_bp.route("/<string:user_id>/gamification/award", methods=["POST"])
def award_user_points(user_id):
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()
    if not doc.exists:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}
    pet_id = data.get("pet_id")
    event_type = data.get("event_type")
    event_id = data.get("event_id")

    if not pet_id or not event_type or not event_id:
        return jsonify({"error": "pet_id, event_type, and event_id are required"}), 400

    user_data = doc.to_dict()
    if pet_id not in user_data.get("pet_ids", []):
        return jsonify({"error": "pet_id is not linked to this user"}), 400

    points_to_award = POINTS_PER_EVENT.get(event_type)
    if points_to_award is None:
        return jsonify({"error": f"Unknown event_type '{event_type}'"}), 400

    gamification = user_data.get("gamification", {"points": 0, "badges": [], "redemptions": []})
    previous_points = gamification.get("points", 0)
    new_points = previous_points + points_to_award

    existing_badge_ids = {b["id"] for b in gamification.get("badges", [])}
    new_badges = _check_new_badges(new_points, previous_points, existing_badge_ids)

    updated_badges = gamification.get("badges", []) + new_badges
    doc_ref.update({
        "gamification.points": new_points,
        "gamification.badges": updated_badges,
    })

    return jsonify({
        "points": new_points,
        "points_awarded": points_to_award,
        "new_badges": new_badges,
        "badges": updated_badges,
    }), 200
