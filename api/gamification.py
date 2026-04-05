from flask import Blueprint, jsonify, request
from db import db

gamification_bp = Blueprint("gamification", __name__)

# ---------------------------------------------------------------------------
# Gamification system
# ---------------------------------------------------------------------------
# Points are awarded across ALL ages for any health event:
#   - Completed vaccination, wellness visit, biometric/lab work, grooming appointment, etc.
#
# Points place users in a percentile ranking across all app users.
# Badges and milestones celebrate consistent care in a warm, motivating tone.
# ---------------------------------------------------------------------------

BADGE_MILESTONES = [
    {"id": "first_steps",       "name": "First Steps",       "description": "Awarded your first health points.",             "threshold": 100},
    {"id": "health_starter",    "name": "Health Starter",    "description": "Keeping up with pet care — great start!",       "threshold": 300},
    {"id": "wellness_champion", "name": "Wellness Champion", "description": "Consistently prioritizing your pet's health.",   "threshold": 500},
    {"id": "dedicated_owner",   "name": "Dedicated Owner",   "description": "Top-tier commitment to your pet's wellbeing.",  "threshold": 1000},
    {"id": "pet_health_hero",   "name": "Pet Health Hero",   "description": "An inspiration to pet owners everywhere.",      "threshold": 2000},
]

POINTS_PER_EVENT = {
    "vaccination":    100,
    "wellness_visit": 150,
    "biometrics":      75,
    "grooming":        50,
}


def _compute_percentile(user_points, all_points):
    """Return the percentage of users scoring strictly below user_points (0–100)."""
    if not all_points:
        return 100.0
    below = sum(1 for p in all_points if p < user_points)
    return round(below / len(all_points) * 100, 1)


def _unlocked_badges(points):
    return [b for b in BADGE_MILESTONES if points >= b["threshold"]]


@gamification_bp.route("/", methods=["GET"])
def get_progress():
    """Return points total, percentile rank, earned badges, and next milestone for a user.

    Query param: user_id
    """
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id query param is required"}), 400

    doc = db.collection("users").document(user_id).get()
    if not doc.exists:
        return jsonify({"error": "User not found"}), 404

    gamification = doc.to_dict().get("gamification", {"points": 0, "badges": [], "redemptions": []})
    points = gamification.get("points", 0)

    # Compute percentile across all users
    all_docs = db.collection("users").stream()
    all_points = [
        d.to_dict().get("gamification", {}).get("points", 0)
        for d in all_docs
    ]
    percentile = _compute_percentile(points, all_points)

    # Next milestone
    next_milestone = next(
        (b for b in BADGE_MILESTONES if points < b["threshold"]),
        None,
    )

    return jsonify({
        "user_id": user_id,
        "points": points,
        "percentile": percentile,
        "badges": gamification.get("badges", []),
        "next_milestone": (
            {"name": next_milestone["name"], "points_needed": next_milestone["threshold"] - points}
            if next_milestone else None
        ),
    }), 200


@gamification_bp.route("/award", methods=["POST"])
def award_points():
    """Award points for a health event and check for newly unlocked badges.

    Request body:
    {
      "user_id":    str,
      "event_type": str,   # "vaccination" | "wellness_visit" | "biometrics" | "grooming"
      "event_id":   str
    }
    """
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    event_type = data.get("event_type")
    event_id = data.get("event_id")

    if not user_id or not event_type or not event_id:
        return jsonify({"error": "user_id, event_type, and event_id are required"}), 400

    points_to_award = POINTS_PER_EVENT.get(event_type)
    if points_to_award is None:
        return jsonify({"error": f"Unknown event_type '{event_type}'"}), 400

    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()
    if not doc.exists:
        return jsonify({"error": "User not found"}), 404

    gamification = doc.to_dict().get("gamification", {"points": 0, "badges": [], "redemptions": []})
    previous_points = gamification.get("points", 0)
    new_points = previous_points + points_to_award

    existing_badge_ids = {b["id"] for b in gamification.get("badges", [])}
    new_badges = [
        b for b in _unlocked_badges(new_points)
        if b["id"] not in existing_badge_ids
    ]
    updated_badges = gamification.get("badges", []) + [
        {"id": b["id"], "name": b["name"], "earned_at": b.get("earned_at", "")}
        for b in new_badges
    ]

    doc_ref.update({
        "gamification.points": new_points,
        "gamification.badges": updated_badges,
    })

    return jsonify({
        "points": new_points,
        "points_awarded": points_to_award,
        "new_badges": new_badges,
    }), 200


@gamification_bp.route("/badges", methods=["GET"])
def list_badges():
    """Return all badges with earned/locked status for a user.

    Query param: user_id
    """
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id query param is required"}), 400

    doc = db.collection("users").document(user_id).get()
    if not doc.exists:
        return jsonify({"error": "User not found"}), 404

    gamification = doc.to_dict().get("gamification", {"points": 0, "badges": []})
    earned = {b["id"]: b for b in gamification.get("badges", [])}

    badges = []
    for b in BADGE_MILESTONES:
        entry = {
            "id":          b["id"],
            "name":        b["name"],
            "description": b["description"],
            "earned":      b["id"] in earned,
            "earned_at":   earned[b["id"]].get("earned_at") if b["id"] in earned else None,
        }
        badges.append(entry)

    return jsonify({"badges": badges}), 200


@gamification_bp.route("/milestones", methods=["GET"])
def list_milestones():
    """Return all milestones with completion status for a user.

    Query param: user_id
    """
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id query param is required"}), 400

    doc = db.collection("users").document(user_id).get()
    if not doc.exists:
        return jsonify({"error": "User not found"}), 404

    points = doc.to_dict().get("gamification", {}).get("points", 0)

    milestones = [
        {
            "name":            b["name"],
            "description":     b["description"],
            "points_required": b["threshold"],
            "completed":       points >= b["threshold"],
        }
        for b in BADGE_MILESTONES
    ]
    return jsonify({"milestones": milestones}), 200


@gamification_bp.route("/leaderboard", methods=["GET"])
def leaderboard():
    """Return all users ranked by points with their percentile.

    Query params:
      limit (int, default 50) — number of top users to return
    """
    try:
        limit = int(request.args.get("limit", 50))
    except ValueError:
        return jsonify({"error": "limit must be an integer"}), 400

    docs = list(db.collection("users").stream())
    all_points = [d.to_dict().get("gamification", {}).get("points", 0) for d in docs]

    ranked = sorted(
        [
            {
                "user_id":    d.id,
                "first_name": d.to_dict().get("first_name", ""),
                "last_name":  d.to_dict().get("last_name", ""),
                "points":     d.to_dict().get("gamification", {}).get("points", 0),
            }
            for d in docs
        ],
        key=lambda x: x["points"],
        reverse=True,
    )

    for entry in ranked:
        entry["percentile"] = _compute_percentile(entry["points"], all_points)

    return jsonify({"leaderboard": ranked[:limit]}), 200
