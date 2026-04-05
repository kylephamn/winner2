import uuid
from flask import Blueprint, jsonify, request
from db import db
from api.schemas import new_visit

visits_bp = Blueprint("visits", __name__)


@visits_bp.route("/", methods=["GET"])
def list_visits():
    patient_id = request.args.get("patient_id")
    if not patient_id:
        return jsonify({"error": "patient_id query parameter is required"}), 400

    docs = (
        db.collection("visits")
        .where("patient_id", "==", patient_id)
        .stream()
    )
    visits = sorted(
        [{"id": doc.id, **doc.to_dict()} for doc in docs],
        key=lambda v: v.get("visit_date", ""),
    )
    return jsonify(visits), 200


@visits_bp.route("/<string:visit_id>", methods=["GET"])
def get_visit(visit_id):
    doc = db.collection("visits").document(visit_id).get()
    if not doc.exists:
        return jsonify({"error": "Visit not found"}), 404
    return jsonify({"id": doc.id, **doc.to_dict()}), 200


@visits_bp.route("/", methods=["POST"])
def create_visit():
    data = request.get_json(silent=True) or {}
    if not data.get("patient_id"):
        return jsonify({"error": "patient_id is required"}), 400
    if not data.get("visit_date"):
        return jsonify({"error": "visit_date is required"}), 400

    visit_id = str(uuid.uuid4())
    record = new_visit(data)
    db.collection("visits").document(visit_id).set(record)
    return jsonify({"id": visit_id, **record}), 201


@visits_bp.route("/<string:visit_id>", methods=["PUT"])
def update_visit(visit_id):
    doc_ref = db.collection("visits").document(visit_id)
    if not doc_ref.get().exists:
        return jsonify({"error": "Visit not found"}), 404

    data = request.get_json(silent=True) or {}
    allowed = {"visit_date", "attending_vet", "reason", "notes", "vitals"}
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return jsonify({"error": "No updatable fields provided"}), 400

    doc_ref.update(updates)
    updated = doc_ref.get()
    return jsonify({"id": updated.id, **updated.to_dict()}), 200
