from flask import Blueprint, jsonify, request

biometrics_bp = Blueprint("biometrics", __name__)

# ---------------------------------------------------------------------------
# TODO: Biometrics / lab result routes
# ---------------------------------------------------------------------------
# GET  /api/biometrics/   — list biometric/lab results for a patient (patient_id query param)
# POST /api/biometrics/   — upload or record a new biometric/lab result
# ---------------------------------------------------------------------------


@biometrics_bp.route("/", methods=["GET"])
def list_biometrics():
    # TODO: return biometric/lab results for a patient, newest first
    pass


@biometrics_bp.route("/", methods=["POST"])
def create_biometric():
    # TODO: record a new biometric/lab result (CBC, chemistry panel, urinalysis, etc.)
    pass
