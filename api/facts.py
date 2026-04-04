from flask import Blueprint, jsonify

facts_bp = Blueprint("facts", __name__)

# ---------------------------------------------------------------------------
# Veterinary fun facts
# ---------------------------------------------------------------------------
# Facts should be:
#   - Short: 1–2 sentences maximum
#   - Friendly and engaging (not overly clinical)
#   - Veterinary-relevant (animal health, anatomy, behavior, care tips)
#   - Rotated on repeated loads — avoid serving the same fact twice in a row
# ---------------------------------------------------------------------------


@facts_bp.route("/", methods=["GET"])
def get_fact():
    # TODO: return a random (non-repeating) veterinary fun fact
    pass
