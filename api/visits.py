from flask import Blueprint, jsonify, request

visits_bp = Blueprint("visits", __name__)

# ---------------------------------------------------------------------------
# TODO: Visit routes
# ---------------------------------------------------------------------------
# GET  /api/visits/         — list all visits for a patient (patient_id query param)
# GET  /api/visits/<id>     — get a single visit record
# POST /api/visits/         — log a new visit
# PUT  /api/visits/<id>     — update visit notes or details
# ---------------------------------------------------------------------------


@visits_bp.route("/", methods=["GET"])
def list_visits():
    # TODO: return visit history for a patient, ordered chronologically
    pass


@visits_bp.route("/<int:visit_id>", methods=["GET"])
def get_visit(visit_id):
    # TODO: return a single visit record including vet name, notes, vitals snapshot
    pass


@visits_bp.route("/", methods=["POST"])
def create_visit():
    # TODO: log a new visit; include attending vet, reason, notes, vitals
    pass


@visits_bp.route("/<int:visit_id>", methods=["PUT"])
def update_visit(visit_id):
    # TODO: update visit record (add notes, correct data, etc.)
    pass
