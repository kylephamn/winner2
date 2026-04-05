import uuid
from flask import Blueprint, jsonify, request
from db import db

notes_bp = Blueprint("notes", __name__)

# ---------------------------------------------------------------------------
# Risk tag field on notes
# ---------------------------------------------------------------------------
# `risk_tags` is an optional array field on each note record. It accepts
# one or more of the following predefined behavioral flag strings:
#
#   "Aggressive with other dogs"
#   "Aggressive with cats"
#   "Bite risk"
#   "Scratch risk"
#   "Anxious / easily stressed"
#   "Reactive to handling"
#   "Requires muzzle"
#   "Requires sedation for exams"
#   "Fearful of strangers"
#   "Separation anxiety"
#
# A free-text custom tag is also supported as a fallback for unlisted flags.
# ---------------------------------------------------------------------------

VALID_RISK_TAGS = {
    "Aggressive with other dogs",
    "Aggressive with cats",
    "Bite risk",
    "Scratch risk",
    "Anxious / easily stressed",
    "Reactive to handling",
    "Requires muzzle",
    "Requires sedation for exams",
    "Fearful of strangers",
    "Separation anxiety",
}


def _validate_risk_tags(tags):
    """Return tags as-is (predefined or custom strings). Raises ValueError if not a list."""
    if not isinstance(tags, list):
        raise ValueError("risk_tags must be an array")
    if not all(isinstance(t, str) for t in tags):
        raise ValueError("each risk tag must be a string")
    return tags


@notes_bp.route("/", methods=["GET"])
def list_notes():
    patient_id = request.args.get("patient_id")
    if not patient_id:
        return jsonify({"error": "patient_id query parameter is required"}), 400

    query = db.collection("notes").where("patient_id", "==", patient_id)
    notes = [{"id": doc.id, **doc.to_dict()} for doc in query.stream()]
    return jsonify(notes)


@notes_bp.route("/<note_id>", methods=["GET"])
def get_note(note_id):
    doc = db.collection("notes").document(note_id).get()
    if not doc.exists:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"id": doc.id, **doc.to_dict()})


@notes_bp.route("/", methods=["POST"])
def create_note():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    patient_id = data.get("patient_id")
    if not patient_id:
        return jsonify({"error": "patient_id is required"}), 400

    text = data.get("text", "")
    risk_tags = data.get("risk_tags", [])

    try:
        risk_tags = _validate_risk_tags(risk_tags)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    note_id = str(uuid.uuid4())
    note = {
        "patient_id": patient_id,
        "text": text,
        "risk_tags": risk_tags,
    }
    db.collection("notes").document(note_id).set(note)
    return jsonify({"id": note_id, **note}), 201


@notes_bp.route("/<note_id>", methods=["PUT"])
def update_note(note_id):
    doc_ref = db.collection("notes").document(note_id)
    if not doc_ref.get().exists:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    updates = {}
    if "text" in data:
        updates["text"] = data["text"]
    if "risk_tags" in data:
        try:
            updates["risk_tags"] = _validate_risk_tags(data["risk_tags"])
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    if not updates:
        return jsonify({"error": "No updatable fields provided"}), 400

    doc_ref.update(updates)
    updated = doc_ref.get()
    return jsonify({"id": updated.id, **updated.to_dict()})


@notes_bp.route("/<note_id>", methods=["DELETE"])
def delete_note(note_id):
    doc_ref = db.collection("notes").document(note_id)
    if not doc_ref.get().exists:
        return jsonify({"error": "Not found"}), 404

    doc_ref.delete()
    return "", 204
