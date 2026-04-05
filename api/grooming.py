from flask import Blueprint, jsonify, request
from db import db
from api.schemas import new_grooming

grooming_bp = Blueprint("grooming", __name__)

# Grooming documents are keyed by patient_id (one record per patient).


@grooming_bp.route("/", methods=["GET"])
def get_grooming():
    patient_id = request.args.get("patient_id")
    if not patient_id:
        return jsonify({"error": "patient_id query parameter is required"}), 400

    doc = db.collection("grooming").document(patient_id).get()
    if not doc.exists:
        return jsonify({"error": "Grooming record not found"}), 404
    return jsonify({"id": doc.id, **doc.to_dict()}), 200


@grooming_bp.route("/", methods=["PUT"])
def update_grooming():
    data = request.get_json(silent=True) or {}
    patient_id = data.get("patient_id")
    if not patient_id:
        return jsonify({"error": "patient_id is required"}), 400

    doc_ref = db.collection("grooming").document(patient_id)
    allowed = {"last_groomed_date", "coat_condition", "next_appointment", "notes"}
    updates = {k: v for k, v in data.items() if k in allowed}

    if not doc_ref.get().exists:
        # Create on first update
        record = new_grooming(data)
        doc_ref.set(record)
        return jsonify({"id": patient_id, **record}), 201

    if not updates:
        return jsonify({"error": "No updatable fields provided"}), 400

    from api.schemas import _now
    updates["updated_at"] = _now()
    doc_ref.update(updates)
    updated = doc_ref.get()
    return jsonify({"id": updated.id, **updated.to_dict()}), 200
