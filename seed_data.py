"""
Seed script — creates a test user and two test pets in Firestore.
Cleans up existing pets for the test user before re-seeding.
Run with:  python seed_data.py
"""
import uuid
from datetime import datetime, timezone
from db import db


def now():
    return datetime.now(timezone.utc).isoformat()


user_id = "test-user-001"

# ── Wipe all pets in the collection ───────────────────────────
print("Wiping all pets...")
for doc in db.collection("pets").stream():
    doc.reference.delete()
    print(f"  Deleted pet: {doc.id}")

# ── Test user ──────────────────────────────────────────────────
user = {
    "first_name": "Kyle",
    "last_name":  "Test",
    "email":      "kyle@test.com",
    "phone":      "555-867-5309",
    "address": {
        "street": "123 Main St",
        "city":   "San Luis Obispo",
        "state":  "CA",
        "zip":    "93401",
    },
    "dob": "1995-06-15",
    "gamification": {
        "points":      250,
        "badges":      ["first_steps", "health_starter"],
        "redemptions": [],
    },
    "pet_ids":    [],
    "created_at": now(),
}

db.collection("users").document(user_id).set(user)
print(f"Created user: {user_id} ({user['first_name']} {user['last_name']})")


# ── Pet 1: Buddy the Golden Retriever ─────────────────────────
buddy_id = str(uuid.uuid4())
buddy = {
    "petID":               buddy_id,
    "name":                "Buddy",
    "species":             "Dog",
    "breed":               "Golden Retriever",
    "sex":                 "Male",
    "dob":                 "2020-03-10",
    "color":               "Golden",
    "neutered":            True,
    "microchip_id":        "985112345678901",
    "insurance_id":        "INS-TEST-001",
    "weight":              65.0,
    "photo_url":           None,
    "allergies":           ["chicken"],
    "current_medications": [],
    "vaccine_list":        [],
    "reminders":           [],
    "ui_preference":       None,
    "created_at":          now(),
}

db.collection("pets").document(buddy_id).set(buddy)
print(f"Created dog: {buddy_id} ({buddy['name']} the {buddy['breed']})")


# ── Pet 2: Baja Blast the Orange Cat ──────────────────────────
baja_id = str(uuid.uuid4())
baja = {
    "petID":               baja_id,
    "name":                "Baja Blast",
    "species":             "cat",
    "breed":               "Orange",
    "sex":                 "Male",
    "dob":                 "2025-09-28",
    "color":               "Orange",
    "neutered":            False,
    "microchip_id":        "985198765432100",
    "insurance_id":        "INS-TEST-002",
    "weight":              8.5,
    "photo_url":           None,
    "allergies":           [],
    "current_medications": [],
    "vaccine_list":        [],
    "reminders":           [],
    "ui_preference":       None,
    "created_at":          now(),
}

db.collection("pets").document(baja_id).set(baja)
print(f"Created cat: {baja_id} ({baja['name']} the {baja['breed']} cat)")

# ── Vaccines for Baja Blast ────────────────────────────────────
parvo_id = str(uuid.uuid4())
parvo_vaccine = {
    "patient_id":        baja_id,
    "name":              "Parvovirus",
    "nickname":          "parvo",
    "administered_date": "2025-10-15",
    "due_date":          "2026-10-15",
    "administered_by":   "Dr. Walker",
    "lot_number":        None,
}
db.collection("vaccines").document(parvo_id).set(parvo_vaccine)
print(f"Created parvo vaccine record for {baja['name']}")


# ── Link both pets to user ─────────────────────────────────────
db.collection("users").document(user_id).update({"pet_ids": [buddy_id, baja_id]})
print(f"Linked {buddy['name']} and {baja['name']} to user {user_id}")
print("\nDone! Refresh the app to see your pets.")
