from flask import Blueprint, jsonify, request

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


@notes_bp.route("/", methods=["GET"])
def list_notes():
    # TODO: query notes for a given patient (patient_id from query string)
    pass


@notes_bp.route("/<int:note_id>", methods=["GET"])
def get_note(note_id):
    # TODO: return a single note record by ID, including risk_tags array
    pass


@notes_bp.route("/", methods=["POST"])
def create_note():
    # TODO: create a new note; accept risk_tags array in request body
    pass


@notes_bp.route("/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    # TODO: update note text and/or risk_tags; invalidate client cache for patient
    pass


@notes_bp.route("/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    # TODO: delete a note by ID
    pass
