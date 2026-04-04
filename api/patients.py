from flask import Blueprint, jsonify

patients_bp = Blueprint("patients", __name__)

# ---------------------------------------------------------------------------
# TODO: Patient routes
# ---------------------------------------------------------------------------
# GET  /api/patients/          — list all patients
# GET  /api/patients/<id>      — get a single patient record
# POST /api/patients/          — create a new patient
# PUT  /api/patients/<id>      — update a patient record
# DELETE /api/patients/<id>    — remove a patient record
#
# Patient record will include fields such as:
#   - Basic info: name, species, breed, age, weight, sex
#   - Owner info: name, contact details
#   - Medical history: diagnoses, allergies, medications
#   - Visit history: dates, notes, attending vet
#   - Vitals: heart rate, temperature, blood pressure, etc.
#   - Lab results, imaging, vaccines
# ---------------------------------------------------------------------------


@patients_bp.route("/", methods=["GET"])
def list_patients():
    # TODO: query database and return patient list
    return jsonify({"patients": [], "message": "not implemented"})
