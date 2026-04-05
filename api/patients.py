import uuid
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Blueprint, jsonify, request
from api.schemas import new_pet
from db import db
from datetime import date

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
    patients = [{"id": doc.id, **doc.to_dict()} for doc in db.collection("pets").stream()]
    return jsonify(patients)



@patients_bp.route("/<patient_id>", methods=["GET"])
def get_patient(patient_id):
    doc = db.collection("pets").document(patient_id).get()
    if not doc.exists:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"id": doc.id, **doc.to_dict()})


@patients_bp.route("/", methods=["POST"])
def create_patient():
    data = request.get_json()
    pet_id = str(uuid.uuid4())
    pet = new_pet(data)         # enforces the shape
    pet["petID"] = pet_id
    db.collection("pets").document(pet_id).set(pet)
    return jsonify(pet), 201


@patients_bp.route("/<patient_id>", methods=["PUT"])
def update_patient(patient_id):
    data = request.get_json()
    db.collection("pets").document(patient_id).update(data)
    return jsonify({"id": patient_id, **data})


@patients_bp.route("/<patient_id>", methods=["DELETE"])
def delete_patient(patient_id):
    db.collection("pets").document(patient_id).delete()
    return jsonify({"deleted": patient_id})

def mood_score(doc):
    dob = doc.get("dob")  # assumes dob is a string like "2018-03-15"
    if not dob:
        return None

    age = (date.today() - date.fromisoformat(dob)).days // 365

    if age < 5:
        return "/images/face1.png"
    elif age <= 10:
        return "/images/face2.png"
    else:
        return "/images/face3.png"


@patients_bp.route("/<patient_id>", methods=["POST"])
def calculate_patients_mood(patient_id):
    doc = db.collection("pets").document(patient_id).get()
    if not doc.exists:
        return jsonify({"error": "Not found"}), 404

    data = doc.to_dict()
    return jsonify({"id": doc.id, "mood_image": mood_score(data), **data})