from flask import Blueprint, jsonify, request

patients_bp = Blueprint("patients", __name__)

# ---------------------------------------------------------------------------
# TODO: Patient routes
# ---------------------------------------------------------------------------
# GET    /api/patients/        — list all patients
# GET    /api/patients/<id>    — get a single patient record
# POST   /api/patients/        — create a new patient
# PUT    /api/patients/<id>    — update a patient record
# DELETE /api/patients/<id>    — remove a patient record
#
# Patient record fields:
#   Basic info:    name, species, breed, age, weight, sex
#   Owner info:    name, phone, email, address
#   Medical:       diagnoses, allergies, current medications
#   Vitals:        heart rate, temperature, blood pressure, respiratory rate, weight
#   History:       visit dates, attending vet, SOAP notes
#   Records:       lab results, imaging, vaccine history
# ---------------------------------------------------------------------------


@patients_bp.route("/", methods=["GET"])
def list_patients():
    # TODO: query database and return paginated patient list
    pass


@patients_bp.route("/<int:patient_id>", methods=["GET"])
def get_patient(patient_id):
    # TODO: return full patient record including vitals, meds, allergies, and flags
    pass


@patients_bp.route("/", methods=["POST"])
def create_patient():
    # TODO: validate and persist a new patient record
    pass


@patients_bp.route("/<int:patient_id>", methods=["PUT"])
def update_patient(patient_id):
    # TODO: update patient fields; invalidate client-side cache for this patient
    pass


@patients_bp.route("/<int:patient_id>", methods=["DELETE"])
def delete_patient(patient_id):
    # TODO: soft-delete or hard-delete patient record
    pass
