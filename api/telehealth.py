import uuid
from flask import Blueprint, jsonify, request
from db import db
from api.schemas import new_telehealth_session, _now

telehealth_bp = Blueprint("telehealth", __name__)

# ---------------------------------------------------------------------------
# Telehealth consult flow — 6 steps
# ---------------------------------------------------------------------------
# 1. Patient selection  — pre-fill from dashboard or show picker
# 2. Triage            — concern input + urgency selector (friendly language)
# 3. Scheduling        — slot picker OR instant connect path based on urgency
# 4. Pre-consult       — display checklist (meds on hand, quiet space, camera check)
# 5. Consult room      — video placeholder, patient info sidebar, notes field, end button
# 6. Post-consult      — summary: vet name, session notes, follow-up booking prompt
# ---------------------------------------------------------------------------

URGENCY_LEVELS = {"low", "medium", "high"}

# Static available slots (in production these would come from a scheduling service)
AVAILABLE_SLOTS = [
    {"slot_id": "slot_001", "datetime": "2026-04-05T09:00:00-05:00", "vet": "Dr. Rivera"},
    {"slot_id": "slot_002", "datetime": "2026-04-05T11:30:00-05:00", "vet": "Dr. Pham"},
    {"slot_id": "slot_003", "datetime": "2026-04-05T14:00:00-05:00", "vet": "Dr. Chen"},
    {"slot_id": "slot_004", "datetime": "2026-04-06T10:00:00-05:00", "vet": "Dr. Rivera"},
    {"slot_id": "slot_005", "datetime": "2026-04-06T13:00:00-05:00", "vet": "Dr. Pham"},
]

BASE_CHECKLIST = [
    "Ensure you are in a quiet, well-lit space.",
    "Have your pet's current medications nearby.",
    "Check that your camera and microphone are working.",
    "Have a recent weight measurement ready if available.",
    "Write down any symptoms or changes you've noticed.",
]

SPECIES_CHECKLIST = {
    "dog": ["Have your dog on a leash or securely held for the exam."],
    "cat": ["Place your cat in a carrier or enclosed space to minimize escape risk."],
    "bird": ["Keep the cage or enclosure covered until the consult begins to reduce stress."],
    "rabbit": ["Limit handling — rabbits can injure themselves if they kick. Keep them calm."],
}


def _get_session(session_id):
    doc = db.collection("telehealth_sessions").document(session_id).get()
    return doc if doc.exists else None


@telehealth_bp.route("/session", methods=["POST"])
def start_session():
    data = request.get_json(silent=True) or {}
    patient_id = data.get("patient_id")
    if not patient_id:
        return jsonify({"error": "patient_id is required"}), 400

    session_id = str(uuid.uuid4())
    session = new_telehealth_session({"patient_id": patient_id})
    db.collection("telehealth_sessions").document(session_id).set(session)
    return jsonify({"session_id": session_id, **session}), 201


@telehealth_bp.route("/session/<session_id>", methods=["GET"])
def get_session(session_id):
    doc = _get_session(session_id)
    if not doc:
        return jsonify({"error": "Session not found"}), 404

    # Attach patient context
    session_data = {"session_id": doc.id, **doc.to_dict()}
    patient_id = session_data.get("patient_id")
    if patient_id:
        pet_doc = db.collection("pets").document(patient_id).get()
        if pet_doc.exists:
            session_data["patient"] = {"id": pet_doc.id, **pet_doc.to_dict()}

    return jsonify(session_data), 200


@telehealth_bp.route("/session/<session_id>/triage", methods=["POST"])
def submit_triage(session_id):
    doc_ref = db.collection("telehealth_sessions").document(session_id)
    if not doc_ref.get().exists:
        return jsonify({"error": "Session not found"}), 404

    data = request.get_json(silent=True) or {}
    urgency = data.get("urgency")
    concern = data.get("concern")

    if not urgency or urgency not in URGENCY_LEVELS:
        return jsonify({"error": f"urgency must be one of: {sorted(URGENCY_LEVELS)}"}), 400
    if not concern:
        return jsonify({"error": "concern is required"}), 400

    doc_ref.update({
        "urgency": urgency,
        "concern": concern,
        "status": "triage_submitted",
    })

    # High urgency → recommend instant connect
    routing = "instant" if urgency == "high" else "schedule"
    return jsonify({"session_id": session_id, "urgency": urgency, "routing": routing}), 200


@telehealth_bp.route("/session/<session_id>/schedule", methods=["POST"])
def schedule_or_connect(session_id):
    doc_ref = db.collection("telehealth_sessions").document(session_id)
    doc = doc_ref.get()
    if not doc.exists:
        return jsonify({"error": "Session not found"}), 404

    session = doc.to_dict()
    data = request.get_json(silent=True) or {}

    if session.get("urgency") == "high":
        # Instant connect — skip slot selection
        doc_ref.update({"scheduled_slot": "instant", "status": "instant"})
        return jsonify({"session_id": session_id, "mode": "instant"}), 200

    slot_id = data.get("slot_id")
    slot = next((s for s in AVAILABLE_SLOTS if s["slot_id"] == slot_id), None)
    if not slot:
        return jsonify({"error": "Invalid or unavailable slot_id"}), 400

    doc_ref.update({
        "scheduled_slot": slot["datetime"],
        "vet_name": slot["vet"],
        "status": "scheduled",
    })
    return jsonify({"session_id": session_id, "slot": slot}), 200


@telehealth_bp.route("/session/<session_id>/checklist", methods=["GET"])
def get_checklist(session_id):
    doc = _get_session(session_id)
    if not doc:
        return jsonify({"error": "Session not found"}), 404

    patient_id = doc.to_dict().get("patient_id")
    checklist = list(BASE_CHECKLIST)

    if patient_id:
        pet_doc = db.collection("pets").document(patient_id).get()
        if pet_doc.exists:
            species = (pet_doc.to_dict().get("species") or "").lower()
            checklist += SPECIES_CHECKLIST.get(species, [])

    return jsonify({"session_id": session_id, "checklist": checklist}), 200


@telehealth_bp.route("/session/<session_id>/end", methods=["POST"])
def end_session(session_id):
    doc_ref = db.collection("telehealth_sessions").document(session_id)
    if not doc_ref.get().exists:
        return jsonify({"error": "Session not found"}), 404

    data = request.get_json(silent=True) or {}
    doc_ref.update({
        "session_notes": data.get("session_notes", ""),
        "vet_name":      data.get("vet_name"),
        "follow_up":     data.get("follow_up"),
        "status":        "completed",
        "ended_at":      _now(),
    })
    updated = doc_ref.get()
    return jsonify({"session_id": session_id, **updated.to_dict()}), 200


@telehealth_bp.route("/session/<session_id>/summary", methods=["GET"])
def get_summary(session_id):
    doc = _get_session(session_id)
    if not doc:
        return jsonify({"error": "Session not found"}), 404

    session = doc.to_dict()
    if session.get("status") != "completed":
        return jsonify({"error": "Session has not ended yet"}), 400

    summary = {
        "session_id":    session_id,
        "vet_name":      session.get("vet_name"),
        "session_notes": session.get("session_notes"),
        "follow_up":     session.get("follow_up"),
        "ended_at":      session.get("ended_at"),
    }
    return jsonify(summary), 200


@telehealth_bp.route("/slots", methods=["GET"])
def list_slots():
    return jsonify({"slots": AVAILABLE_SLOTS}), 200
