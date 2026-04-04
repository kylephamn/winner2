from flask import Blueprint, jsonify, request

gamification_bp = Blueprint("gamification", __name__)

# ---------------------------------------------------------------------------
# Gamification system
# ---------------------------------------------------------------------------
# Points are awarded across ALL ages for any health event:
#   - Completed vaccination, wellness visit, lab work, grooming appointment, etc.
#
# Older pets receive age-appropriate milestones that celebrate longevity
# and consistent care (e.g. "Senior Wellness Champion", "10-Year Health Star").
#
# Badges and milestones are designed to be motivating for owners, not
# prescriptive — the tone should be warm and celebratory.
# ---------------------------------------------------------------------------


@gamification_bp.route("/", methods=["GET"])
def get_progress():
    # TODO: return points total, earned badges, and next milestone for a patient
    pass


@gamification_bp.route("/award", methods=["POST"])
def award_points():
    # TODO: award points for a health event; check for newly unlocked badges
    pass


@gamification_bp.route("/badges", methods=["GET"])
def list_badges():
    # TODO: return all available badges with earned/locked status for a patient
    pass


@gamification_bp.route("/milestones", methods=["GET"])
def list_milestones():
    # TODO: return age-appropriate milestones for a patient
    pass
