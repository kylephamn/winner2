import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, render_template

cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


app = Flask(__name__)

# ---------------------------------------------------------------------------
# Blueprints
# ---------------------------------------------------------------------------
# Uncomment each import and registration as the blueprint is implemented.

# from api.patients import patients_bp
# app.register_blueprint(patients_bp, url_prefix="/api/patients")

# from api.notes import notes_bp
# app.register_blueprint(notes_bp, url_prefix="/api/notes")

# from api.vaccines import vaccines_bp
# app.register_blueprint(vaccines_bp, url_prefix="/api/vaccines")

# from api.visits import visits_bp
# app.register_blueprint(visits_bp, url_prefix="/api/visits")

# from api.labs import labs_bp
# app.register_blueprint(labs_bp, url_prefix="/api/labs")

# from api.grooming import grooming_bp
# app.register_blueprint(grooming_bp, url_prefix="/api/grooming")

# from api.telehealth import telehealth_bp
# app.register_blueprint(telehealth_bp, url_prefix="/api/telehealth")

# from api.gamification import gamification_bp
# app.register_blueprint(gamification_bp, url_prefix="/api/gamification")

# from api.facts import facts_bp
# app.register_blueprint(facts_bp, url_prefix="/api/facts")

# from api.locations import locations_bp
# app.register_blueprint(locations_bp, url_prefix="/api/locations")

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Main entry point — renders the patient dashboard shell."""
    return render_template("index.html")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
