from flask import Blueprint, jsonify, request

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


@users_bp.route("/", methods=["GET"])
def list_users():
    # TODO: query Firestore /users collection and return paginated list
    # Query params: page, limit
    pass


@users_bp.route("/<string:user_id>", methods=["GET"])
def get_user(user_id):
    # TODO: return full user record including gamification state and pet_ids
    pass


@users_bp.route("/", methods=["POST"])
def create_user():
    # TODO: validate and persist a new user document in Firestore
    # Required fields: first_name, last_name, phone, address, dob
    # Initializes gamification: { points: 0, badges: [], redemptions: [] }
    # Initializes pet_ids: []
    # Returns: created user document with generated user_id
    pass


@users_bp.route("/<string:user_id>", methods=["PUT"])
def update_user(user_id):
    # TODO: update allowed user fields (first_name, last_name, phone, address, dob)
    # Gamification and pet_ids are managed via their own endpoints
    pass


@users_bp.route("/<string:user_id>", methods=["DELETE"])
def delete_user(user_id):
    # TODO: soft-delete or hard-delete user record
    pass


# ---------------------------------------------------------------------------
# Pet associations
# ---------------------------------------------------------------------------

@users_bp.route("/<string:user_id>/pets", methods=["GET"])
def list_user_pets(user_id):
    # TODO: return the list of pet_ids for this user
    # Optionally expand: ?expand=true fetches each patient record and returns full objects
    pass


@users_bp.route("/<string:user_id>/pets", methods=["POST"])
def add_pet(user_id):
    # TODO: append a pet_id to the user's pet_ids list
    # Request body: { "pet_id": str }
    # Error: 409 if pet_id already linked, 404 if user not found
    pass


@users_bp.route("/<string:user_id>/pets/<string:pet_id>", methods=["DELETE"])
def remove_pet(user_id, pet_id):
    # TODO: remove a pet_id from the user's pet_ids list
    # Error: 404 if user or pet_id not found in list
    pass


# ---------------------------------------------------------------------------
# Gamification (user-scoped)
# ---------------------------------------------------------------------------

@users_bp.route("/<string:user_id>/gamification", methods=["GET"])
def get_user_gamification(user_id):
    # TODO: return the user's gamification sub-document
    # { points, badges, redemptions }
    pass


@users_bp.route("/<string:user_id>/gamification/award", methods=["POST"])
def award_user_points(user_id):
    # TODO: award points to the user for a health event tied to one of their pets
    # Request body:
    # {
    #   "pet_id":     str,
    #   "event_type": str,   # e.g. "vaccination", "wellness_visit", "grooming"
    #   "event_id":   str    # reference to the source record
    # }
    # Validates that pet_id is in user's pet_ids list before awarding
    # Checks for newly unlocked badges after awarding
    pass
