from flask import Blueprint, jsonify, request

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


@telehealth_bp.route("/session", methods=["POST"])
def start_session():
    # TODO: initiate a new telehealth session for a patient; return session ID
    pass


@telehealth_bp.route("/session/<session_id>", methods=["GET"])
def get_session(session_id):
    # TODO: return current session state and patient context
    pass


@telehealth_bp.route("/session/<session_id>/triage", methods=["POST"])
def submit_triage(session_id):
    # TODO: accept triage form data (concern text, urgency level); route accordingly
    pass


@telehealth_bp.route("/session/<session_id>/schedule", methods=["POST"])
def schedule_or_connect(session_id):
    # TODO: book a time slot or flag for instant connect based on triage urgency
    pass


@telehealth_bp.route("/session/<session_id>/checklist", methods=["GET"])
def get_checklist(session_id):
    # TODO: return pre-consult checklist items (species-aware where relevant)
    pass


@telehealth_bp.route("/session/<session_id>/end", methods=["POST"])
def end_session(session_id):
    # TODO: close the consult room; persist vet notes and generate post-consult summary
    pass


@telehealth_bp.route("/session/<session_id>/summary", methods=["GET"])
def get_summary(session_id):
    # TODO: return post-consult summary (vet name, notes, follow-up recommendation)
    pass


@telehealth_bp.route("/slots", methods=["GET"])
def list_slots():
    # TODO: return available appointment slots for scheduling step
    pass
