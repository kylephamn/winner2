import uuid
from flask import Blueprint, jsonify, request
from db import db
from api.schemas import new_biometric

biometrics_bp = Blueprint("biometrics", __name__)


@biometrics_bp.route("/", methods=["GET"])
def list_biometrics():
    patient_id = request.args.get("patient_id")
    if not patient_id:
        return jsonify({"error": "patient_id query parameter is required"}), 400

    docs = (
        db.collection("biometrics")
        .where("patient_id", "==", patient_id)
        .order_by("recorded_at", direction="DESCENDING")
        .stream()
    )
    results = [{"id": doc.id, **doc.to_dict()} for doc in docs]
    return jsonify(results), 200


@biometrics_bp.route("/", methods=["POST"])
def create_biometric():
    data = request.get_json(silent=True) or {}
    if not data.get("patient_id"):
        return jsonify({"error": "patient_id is required"}), 400
    if not data.get("type"):
        return jsonify({"error": "type is required"}), 400

    biometric_id = str(uuid.uuid4())
    record = new_biometric(data)
    db.collection("biometrics").document(biometric_id).set(record)
    return jsonify({"id": biometric_id, **record}), 201
