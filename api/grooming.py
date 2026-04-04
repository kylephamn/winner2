from flask import Blueprint, jsonify, request

grooming_bp = Blueprint("grooming", __name__)

# ---------------------------------------------------------------------------
# TODO: Grooming routes
# ---------------------------------------------------------------------------
# GET /api/grooming/   — get grooming record for a patient (patient_id query param)
# PUT /api/grooming/   — update grooming record (last groomed date, notes, next appt)
# ---------------------------------------------------------------------------


@grooming_bp.route("/", methods=["GET"])
def get_grooming():
    # TODO: return grooming record for a patient
    pass


@grooming_bp.route("/", methods=["PUT"])
def update_grooming():
    # TODO: update grooming details (last groomed, coat condition, next appointment)
    pass
