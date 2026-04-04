from flask import Blueprint, jsonify, request

gamification_bp = Blueprint("gamification", __name__)

# ---------------------------------------------------------------------------
# Gamification system
# ---------------------------------------------------------------------------
# Points are awarded across ALL ages for any health event:
#   - Completed vaccination, wellness visit, biometric/lab work, grooming appointment, etc.
#
# Older pets receive age-appropriate milestones that celebrate longevity
# and consistent care (e.g. "Senior Wellness Champion", "10-Year Health Star").
#
# Badges and milestones are designed to be motivating for owners, not
# prescriptive — the tone should be warm and celebratory.
#
# Rewards catalog (redeemable with points):
#   - DISCOUNT_VISIT:    % off next hospital/clinic visit
#   - DISCOUNT_MEDICINE: % off tick, flea, or heartworm medication
#   - DISCOUNT_GROOMING: % off next grooming appointment
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Reward definitions
# ---------------------------------------------------------------------------
REWARDS = {
    "DISCOUNT_VISIT": {
        "id": "DISCOUNT_VISIT",
        "name": "Discounted Hospital Visit",
        "description": "Redeem for 20% off your pet's next clinic or hospital visit.",
        "discount_percent": 20,
        "points_cost": 500,
        "category": "visit",
    },
    "DISCOUNT_MEDICINE": {
        "id": "DISCOUNT_MEDICINE",
        "name": "Discounted Tick & Flea / Heartworm Medicine",
        "description": "Redeem for 15% off tick, flea, or heartworm preventative medication.",
        "discount_percent": 15,
        "points_cost": 300,
        "category": "medicine",
    },
    "DISCOUNT_GROOMING": {
        "id": "DISCOUNT_GROOMING",
        "name": "Discounted Grooming Session",
        "description": "Redeem for 25% off your pet's next grooming appointment.",
        "discount_percent": 25,
        "points_cost": 250,
        "category": "grooming",
    },
}


@gamification_bp.route("/", methods=["GET"])
def get_progress():
    # TODO: return points total, earned badges, and next milestone for a patient
    # Query param: patient_id
    # Response shape:
    # {
    #   "patient_id": <int>,
    #   "points": <int>,
    #   "badges": [{ "id": str, "name": str, "earned_at": str }],
    #   "next_milestone": { "name": str, "points_needed": int }
    # }
    pass


@gamification_bp.route("/award", methods=["POST"])
def award_points():
    # TODO: award points for a health event; check for newly unlocked badges
    # Request body:
    # {
    #   "patient_id": <int>,
    #   "event_type": str,   # e.g. "vaccination", "wellness_visit", "biometrics", "grooming"
    #   "event_id": <int>    # reference to the source record
    # }
    # Response: updated points total + any newly unlocked badges
    pass


@gamification_bp.route("/badges", methods=["GET"])
def list_badges():
    # TODO: return all available badges with earned/locked status for a patient
    # Query param: patient_id
    # Response: list of badges with { id, name, description, earned, earned_at }
    pass


@gamification_bp.route("/milestones", methods=["GET"])
def list_milestones():
    # TODO: return age-appropriate milestones for a patient
    # Query param: patient_id
    # Milestones are selected based on the patient's age (senior pets get longevity milestones)
    # Response: list of milestones with { name, description, points_required, completed }
    pass


# ---------------------------------------------------------------------------
# Rewards / Redemption
# ---------------------------------------------------------------------------

@gamification_bp.route("/rewards", methods=["GET"])
def list_rewards():
    """Return the full rewards catalog with point costs and discount details."""
    return jsonify({"rewards": list(REWARDS.values())}), 200


@gamification_bp.route("/redeem", methods=["POST"])
def redeem_reward():
    # TODO: redeem a reward for a patient
    # Request body:
    # {
    #   "patient_id": <int>,
    #   "reward_id": str    # one of: "DISCOUNT_VISIT", "DISCOUNT_MEDICINE", "DISCOUNT_GROOMING"
    # }
    # Logic:
    #   1. Look up patient's current points balance in Firestore
    #   2. Validate reward_id exists in REWARDS catalog
    #   3. Check patient has enough points (balance >= reward["points_cost"])
    #   4. Deduct points and write a redemption record to Firestore:
    #      {
    #        "patient_id": ...,
    #        "reward_id": ...,
    #        "discount_percent": ...,
    #        "category": ...,          # "visit" | "medicine" | "grooming"
    #        "redeemed_at": <timestamp>,
    #        "used": false             # flipped to true when the discount is applied
    #      }
    #   5. Return the redemption record + updated points balance
    # Errors: 400 if invalid reward_id, 402 if insufficient points, 404 if patient not found
    pass


@gamification_bp.route("/redemptions", methods=["GET"])
def list_redemptions():
    # TODO: return all active (unused) redemptions for a patient
    # Query param: patient_id
    # Optionally filter by category: ?category=visit|medicine|grooming
    # Response: list of redemption records ordered by redeemed_at desc
    pass


@gamification_bp.route("/redemptions/<redemption_id>/use", methods=["POST"])
def use_redemption(redemption_id):
    _ = redemption_id  # used once TODO is implemented
    # TODO: mark a redemption as used when the discount is applied at checkout
    # Sets used=true and used_at=<timestamp> on the redemption record in Firestore
    # Returns the updated redemption record
    # Error: 409 if already used, 404 if not found
    pass
