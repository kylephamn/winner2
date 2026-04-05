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

DAILY_GOAL_PTS = {
    "breakfast": 50,
    "walk":      100,
    "teeth":     30,
    "checkin":   10,
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


@gamification_bp.route("/pet-rank", methods=["GET"])
def pet_rank():
    """Return a pet's daily-goal points and percentile rank across all pets.

    Query param: pet_id
    """
    pet_id = request.args.get("pet_id")
    if not pet_id:
        return jsonify({"error": "pet_id is required"}), 400

    doc = db.collection("pets").document(pet_id).get()
    if not doc.exists:
        return jsonify({"error": "Pet not found"}), 404

    goal_pts = doc.to_dict().get("gamification", {}).get("daily_goal_points", 0)

    all_pts = [
        d.to_dict().get("gamification", {}).get("daily_goal_points", 0)
        for d in db.collection("pets").stream()
    ]
    percentile = _compute_percentile(goal_pts, all_pts)

    return jsonify({"goal_points": goal_pts, "percentile": percentile}), 200


@gamification_bp.route("/daily-goal", methods=["POST"])
def log_daily_goal():
    """Award points for a daily goal completion (once per goal per day, per pet).

    Body: { "pet_id": str, "goal_id": str, "date": str (YYYY-MM-DD), "checked": bool }
    Returns: { "percentile": float, "goal_points": int, "already_awarded": bool }
    """
    data = request.get_json(silent=True) or {}
    pet_id  = data.get("pet_id")
    goal_id = data.get("goal_id")
    date    = data.get("date")
    checked = data.get("checked", True)

    if not pet_id or not goal_id or not date:
        return jsonify({"error": "pet_id, goal_id, and date are required"}), 400

    pts = DAILY_GOAL_PTS.get(goal_id)
    if pts is None:
        return jsonify({"error": f"Unknown goal_id '{goal_id}'"}), 400

    doc_ref = db.collection("pets").document(pet_id)
    doc = doc_ref.get()
    if not doc.exists:
        return jsonify({"error": "Pet not found"}), 404

    pet_data   = doc.to_dict()
    gamif      = pet_data.get("gamification", {})
    goal_pts   = gamif.get("daily_goal_points", 0)
    daily_log  = gamif.get("daily_goals", {})

    # daily_log structure: { "2025-04-05": { "breakfast": true, ... }, ... }
    day_entry       = daily_log.get(date, {})
    already_awarded = day_entry.get(goal_id, False)

    if checked and not already_awarded:
        goal_pts += pts
        day_entry[goal_id] = True
        doc_ref.update({
            "gamification.daily_goal_points":          goal_pts,
            f"gamification.daily_goals.{date}.{goal_id}": True,
        })
    elif not checked and already_awarded:
        goal_pts = max(0, goal_pts - pts)
        day_entry[goal_id] = False
        doc_ref.update({
            "gamification.daily_goal_points":          goal_pts,
            f"gamification.daily_goals.{date}.{goal_id}": False,
        })

    # Compute percentile across all pets by daily_goal_points
    all_pets_pts = [
        d.to_dict().get("gamification", {}).get("daily_goal_points", 0)
        for d in db.collection("pets").stream()
    ]
    percentile = _compute_percentile(goal_pts, all_pets_pts)

    return jsonify({
        "goal_points":    goal_pts,
        "percentile":     percentile,
        "already_awarded": already_awarded,
    }), 200
