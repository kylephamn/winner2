import uuid

from flask import Blueprint, jsonify, request
from api.schemas import new_pet

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
def create_patient(db):
    #request.get_json()
    data = {
        "name": "Buddy",
        "species": "Dog",
        "breed": "Labrador",
        "sex": "M",
        "dob": "2020-01-01",
        "neutered": True,
        "insurance_id": "INS123",
        "weight": 65,
        "vaccine_list": [],
        "reminders": [],
        "ui_preference": None,
    }
    pet_id = str(uuid.uuid4())
    pet = new_pet(data)         # enforces the shape
    pet["petID"] = pet_id
    db.collection("pets").document(pet_id).set(pet)
    return jsonify(pet), 201


@patients_bp.route("/<int:patient_id>", methods=["PUT"])
def update_patient(patient_id):
    # TODO: update patient fields; invalidate client-side cache for this patient
    pass


@patients_bp.route("/<int:patient_id>", methods=["DELETE"])
def delete_patient(patient_id,db):
    # TODO: soft-delete or hard-delete patient record
    db.collection('Pet').document(patient_id).delete()
    return "", 204
