from flask import Blueprint, jsonify, request

labs_bp = Blueprint("labs", __name__)

# ---------------------------------------------------------------------------
# TODO: Lab result routes
# ---------------------------------------------------------------------------
# GET  /api/labs/   — list lab results for a patient (patient_id query param)
# POST /api/labs/   — upload or record a new lab result
# ---------------------------------------------------------------------------


@labs_bp.route("/", methods=["GET"])
def list_labs():
    # TODO: return lab results for a patient, newest first
    pass


@labs_bp.route("/", methods=["POST"])
def create_lab():
    # TODO: record a new lab result (CBC, chemistry panel, urinalysis, etc.)
    pass
