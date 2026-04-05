from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Users  (/users/<user_id>)
# ---------------------------------------------------------------------------

def new_user(data):
    return {
        "first_name":   data.get("first_name", ""),
        "last_name":    data.get("last_name", ""),
        "email":        data.get("email", ""),
        "phone":        data.get("phone", ""),
        "address": {
            "street": data.get("address", {}).get("street", ""),
            "city":   data.get("address", {}).get("city", ""),
            "state":  data.get("address", {}).get("state", ""),
            "zip":    data.get("address", {}).get("zip", ""),
        },
        "dob":          data.get("dob", ""),
        "gamification": {
            "points":      0,
            "badges":      [],
            "redemptions": [],
        },
        "pet_ids":    [],
        "created_at": _now(),
    }


# ---------------------------------------------------------------------------
# Pets  (/pets/<pet_id>)
# ---------------------------------------------------------------------------

def new_pet(data):
    return {
        "petID":               data.get("petID"),
        "name":                data.get("name"),
        "species":             data.get("species"),
        "breed":               data.get("breed"),
        "sex":                 data.get("sex"),
        "dob":                 data.get("dob"),
        "color":               data.get("color"),
        "neutered":            data.get("neutered", False),
        "microchip_id":        data.get("microchip_id"),
        "insurance_id":        data.get("insurance_id"),
        "weight":              data.get("weight"),
        "photo_url":           data.get("photo_url"),
        "allergies":           data.get("allergies", []),
        "current_medications": data.get("current_medications", []),
        "vaccine_list":        data.get("vaccine_list", []),
        "reminders":           data.get("reminders", []),
        "ui_preference":       data.get("ui_preference"),
        "created_at":          _now(),
    }


# ---------------------------------------------------------------------------
# Vaccines  (/vaccines/<vaccine_id>)
# ---------------------------------------------------------------------------

def new_vaccine(data):
    return {
        "patient_id":        data.get("patient_id"),
        "name":              data.get("name"),
        "manufacturer":      data.get("manufacturer"),
        "administered_date": data.get("administered_date"),
        "due_date":          data.get("due_date"),
        "administered_by":   data.get("administered_by"),
        "lot_number":        data.get("lot_number"),
        "site":              data.get("site"),       # e.g. "left hind leg", "scruff"
        "reaction":          data.get("reaction"),   # any adverse reaction noted
    }


# ---------------------------------------------------------------------------
# Notes  (/notes/<note_id>)
# ---------------------------------------------------------------------------

def new_note(data):
    return {
        "patient_id": data.get("patient_id"),
        "note_type":  data.get("note_type", "general"),  # "soap" | "behavioral" | "general"
        "author":     data.get("author"),
        "text":       data.get("text", ""),
        "risk_tags":  data.get("risk_tags", []),
        "created_at": _now(),
        "updated_at": _now(),
    }


# ---------------------------------------------------------------------------
# Visits  (/visits/<visit_id>)
# ---------------------------------------------------------------------------

def new_visit(data):
    return {
        "patient_id":    data.get("patient_id"),
        "visit_date":    data.get("visit_date"),
        "visit_type":    data.get("visit_type", "wellness"),  # "wellness" | "sick" | "emergency" | "follow_up"
        "attending_vet": data.get("attending_vet"),
        "reason":        data.get("reason", ""),
        "diagnoses":     data.get("diagnoses", []),
        "treatments":    data.get("treatments", []),
        "notes":         data.get("notes", ""),
        "follow_up_date": data.get("follow_up_date"),
        "vitals": {
            "heart_rate":       data.get("vitals", {}).get("heart_rate"),
            "temperature":      data.get("vitals", {}).get("temperature"),
            "blood_pressure":   data.get("vitals", {}).get("blood_pressure"),
            "respiratory_rate": data.get("vitals", {}).get("respiratory_rate"),
            "weight":           data.get("vitals", {}).get("weight"),
        },
        "created_at": _now(),
    }


# ---------------------------------------------------------------------------
# Biometrics  (/biometrics/<biometric_id>)
# ---------------------------------------------------------------------------
# Supported types: "CBC", "chemistry_panel", "urinalysis", "thyroid",
#                  "blood_pressure", "weight", "other"

def new_biometric(data):
    return {
        "patient_id":  data.get("patient_id"),
        "type":        data.get("type"),
        "recorded_at": data.get("recorded_at", _now()),
        "values":      data.get("values", {}),   # flexible key/value map per test type
        "notes":       data.get("notes", ""),
        "ordered_by":  data.get("ordered_by"),
        "lab":         data.get("lab"),
    }


# ---------------------------------------------------------------------------
# Grooming  (/grooming/<patient_id>)  — one document per patient
# ---------------------------------------------------------------------------

def new_grooming(data):
    return {
        "patient_id":        data.get("patient_id"),
        "groomer_name":      data.get("groomer_name"),
        "last_groomed_date": data.get("last_groomed_date"),
        "services":          data.get("services", []),    # e.g. ["bath", "haircut", "nail_trim", "ear_clean"]
        "coat_condition":    data.get("coat_condition"),  # e.g. "good", "matted", "fair"
        "next_appointment":  data.get("next_appointment"),
        "notes":             data.get("notes", ""),
        "updated_at":        _now(),
    }


# ---------------------------------------------------------------------------
# Telehealth sessions  (/telehealth_sessions/<session_id>)
# ---------------------------------------------------------------------------
# status progression:
#   "initiated" → "triage_submitted" → "scheduled" | "instant" → "in_progress" → "completed"

def new_telehealth_session(data):
    return {
        "patient_id":     data.get("patient_id"),
        "user_id":        data.get("user_id"),
        "status":         "initiated",
        "created_at":     _now(),
        "urgency":        None,   # set during triage: "low" | "medium" | "high"
        "concern":        None,   # free-text from triage step
        "scheduled_slot": None,   # ISO datetime string or "instant"
        "vet_name":       None,   # assigned after scheduling
        "session_notes":  None,   # filled by vet during/after consult
        "follow_up":      None,   # follow-up recommendation from post-consult
        "ended_at":       None,
    }
