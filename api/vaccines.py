from flask import Blueprint, jsonify, request
import easyocr
import easyocr
import base64
import numpy as np
from PIL import Image
import io

vaccines_bp = Blueprint("vaccines", __name__)

# ---------------------------------------------------------------------------
# Vaccine reminder buckets
# ---------------------------------------------------------------------------
# Vaccines are sorted into three reminder buckets based on due date:
#
#   Upcoming  — due within 30 days  → gold badge
#   Due soon  — due within 7 days   → orange badge
#   Overdue   — past due date       → red badge
#
# Schedule adapts based on the patient's lifestyle (indoor/outdoor),
# breed, and age. Core vaccines differ from lifestyle-based boosters.
# ---------------------------------------------------------------------------


@vaccines_bp.route("/", methods=["POST"])
def read_vaccines_paper():
    # TODO: Easy ocr will read the data returned from the .js frontend
    data = request.get_json()
    image_data = base64.b64decode(data["image"])
    image = Image.open(io.BytesIO(image_data))

    pass

@vaccines_bp.route("/", methods=["GET"])
def list_vaccines():
    # TODO: return full vaccine schedule for a patient (patient_id from query string)
    pass


@vaccines_bp.route("/<int:vaccine_id>", methods=["GET"])
def get_vaccine(vaccine_id):
    # TODO: return a single vaccine record by ID
    pass


@vaccines_bp.route("/", methods=["POST"])
def create_vaccine():
    # TODO: create a new vaccine record for a patient
    pass


@vaccines_bp.route("/<int:vaccine_id>", methods=["PUT"])
def update_vaccine(vaccine_id):
    # TODO: update vaccine details or mark as administered
    pass


@vaccines_bp.route("/<int:vaccine_id>", methods=["DELETE"])
def delete_vaccine(vaccine_id):
    # TODO: remove a vaccine record
    pass
