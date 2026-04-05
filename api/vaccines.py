import uuid
import base64
import io
import re
from datetime import date, datetime

import easyocr
import numpy as np
from PIL import Image
from flask import Blueprint, jsonify, request
from db import db

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

_ocr_reader = None  # lazy-init so the module loads fast


def _get_ocr_reader():
    global _ocr_reader
    if _ocr_reader is None:
        _ocr_reader = easyocr.Reader(["en"], gpu=False)
    return _ocr_reader


def _reminder_bucket(due_date_str):
    """Return 'overdue', 'due_soon', 'upcoming', or None for a due_date ISO string."""
    if not due_date_str:
        return None
    try:
        due = date.fromisoformat(due_date_str)
    except ValueError:
        return None
    today = date.today()
    delta = (due - today).days
    if delta < 0:
        return "overdue"
    if delta <= 7:
        return "due_soon"
    if delta <= 30:
        return "upcoming"
    return None


# ---------------------------------------------------------------------------
# OCR — scan a paper vaccine record
# ---------------------------------------------------------------------------

def _try_parse_date(s):
    for fmt in ("%b %d, %Y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s.strip(), fmt).date().isoformat()
        except ValueError:
            continue
    return None


def put_scans_into_format(results):
    """
    Parse OCR results from vet reminder tables.
    Expects dates, nicknames, and full names as separate lines (3 lines per record).
    Returns list of dicts: {administered_date, nickname, name}
    """
    # Find where reminders start
    try:
        start = next(i for i, line in enumerate(results) if "REMINDERS" in line)
    except StopIteration:
        return []

    lines = [l.strip() for l in results[start + 1:] if l.strip()]

    structured = []
    # Each record is 3 consecutive lines: date, nickname, full name
    for i in range(0, len(lines) - 2, 3):
        date_iso = _try_parse_date(lines[i])
        if date_iso is None:
            break  # past the reminders section
        structured.append({
            "administered_date": date_iso,
            "nickname": lines[i + 1],
            "name": lines[i + 2],
        })

    return structured


@vaccines_bp.route("/scan", methods=["POST"])
def read_vaccines_paper():
    """Accept a base64-encoded image and return OCR-extracted text lines."""
    data = request.get_json()
    if not data or "image" not in data:
        return jsonify({"error": "image field (base64) is required"}), 400

    try:
        image_bytes = base64.b64decode(data["image"])
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_np = np.array(image)
    except Exception as e:
        return jsonify({"error": f"Invalid image data: {e}"}), 400
    reader = _get_ocr_reader()
    raw_lines = reader.readtext(image_np, detail=0)  # detail=0 → plain text list
    structured = put_scans_into_format(raw_lines)

    return jsonify({"records": structured, "lines": raw_lines})


@vaccines_bp.route("/scan/save", methods=["POST"])
def scan_and_save_vaccines():
    """OCR a vaccine record image and persist each parsed entry to Firebase."""
    data = request.get_json()
    if not data or "image" not in data:
        return jsonify({"error": "image field (base64) is required"}), 400

    patient_id = data.get("patient_id")
    if not patient_id:
        return jsonify({"error": "patient_id is required"}), 400

    try:
        image_bytes = base64.b64decode(data["image"])
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_np = np.array(image)
    except Exception as e:
        return jsonify({"error": f"Invalid image data: {e}"}), 400

    reader = _get_ocr_reader()
    raw_lines = reader.readtext(image_np, detail=0)
    structured = put_scans_into_format(raw_lines)

    if not structured:
        return jsonify({"error": "No vaccine records found in image", "lines": raw_lines}), 422

    saved = []
    for entry in structured:
        vaccine_id = str(uuid.uuid4())
        record = {
            "patient_id": patient_id,
            "name": entry["name"],
            "nickname": entry.get("nickname"),
            "administered_date": entry.get("administered_date"),
            "due_date": None,
            "administered_by": None,
            "lot_number": None,
        }
        db.collection("vaccines").document(vaccine_id).set(record)
        record["id"] = vaccine_id
        record["reminder_bucket"] = _reminder_bucket(record.get("due_date"))
        saved.append(record)

    return jsonify({"saved": saved, "count": len(saved)}), 201


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

@vaccines_bp.route("/", methods=["GET"])
def list_vaccines():
    patient_id = request.args.get("patient_id")
    if not patient_id:
        return jsonify({"error": "patient_id query parameter is required"}), 400

    docs = (
        db.collection("vaccines")
        .where("patient_id", "==", patient_id)
        .stream()
    )
    vaccines = []
    for doc in docs:
        record = {"id": doc.id, **doc.to_dict()}
        record["reminder_bucket"] = _reminder_bucket(record.get("due_date"))
        vaccines.append(record)

    return jsonify(vaccines)


@vaccines_bp.route("/<vaccine_id>", methods=["GET"])
def get_vaccine(vaccine_id):
    doc = db.collection("vaccines").document(vaccine_id).get()
    if not doc.exists:
        return jsonify({"error": "Not found"}), 404
    record = {"id": doc.id, **doc.to_dict()}
    record["reminder_bucket"] = _reminder_bucket(record.get("due_date"))
    return jsonify(record)


@vaccines_bp.route("/", methods=["POST"])
def create_vaccine():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    patient_id = data.get("patient_id")
    if not patient_id:
        return jsonify({"error": "patient_id is required"}), 400

    name = data.get("name")
    if not name:
        return jsonify({"error": "name is required"}), 400

    record = {
        "patient_id": patient_id,
        "name": name,
        "administered_date": data.get("administered_date"),
        "due_date": data.get("due_date"),
        "administered_by": data.get("administered_by"),
        "lot_number": data.get("lot_number"),
    }

    vaccine_id = str(uuid.uuid4())
    db.collection("vaccines").document(vaccine_id).set(record)

    record["id"] = vaccine_id
    record["reminder_bucket"] = _reminder_bucket(record.get("due_date"))
    return jsonify(record), 201


@vaccines_bp.route("/<vaccine_id>", methods=["PUT"])
def update_vaccine(vaccine_id):
    doc_ref = db.collection("vaccines").document(vaccine_id)
    if not doc_ref.get().exists:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    allowed = {"name", "administered_date", "due_date", "administered_by", "lot_number"}
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return jsonify({"error": "No updatable fields provided"}), 400

    doc_ref.update(updates)
    updated = doc_ref.get()
    record = {"id": updated.id, **updated.to_dict()}
    record["reminder_bucket"] = _reminder_bucket(record.get("due_date"))
    return jsonify(record)


@vaccines_bp.route("/<vaccine_id>", methods=["DELETE"])
def delete_vaccine(vaccine_id):
    doc_ref = db.collection("vaccines").document(vaccine_id)
    if not doc_ref.get().exists:
        return jsonify({"error": "Not found"}), 404

    doc_ref.delete()
    return "", 204
