from flask import Flask, render_template, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------------------------
# Blueprints
# ---------------------------------------------------------------------------
# Uncomment each import and registration as the blueprint is implemented.

from api.patients import patients_bp
from api.notes import notes_bp
from api.vaccines import vaccines_bp
from api.visits import visits_bp
from api.biometrics import biometrics_bp
from api.grooming import grooming_bp
from api.telehealth import telehealth_bp
from api.gamification import gamification_bp
from api.facts import facts_bp
from api.locations import locations_bp
from api.users import users_bp

app.register_blueprint(patients_bp,    url_prefix="/api/patients")
app.register_blueprint(notes_bp,       url_prefix="/api/notes")
app.register_blueprint(vaccines_bp,    url_prefix="/api/vaccines")
app.register_blueprint(visits_bp,      url_prefix="/api/visits")
app.register_blueprint(biometrics_bp,  url_prefix="/api/biometrics")
app.register_blueprint(grooming_bp,    url_prefix="/api/grooming")
app.register_blueprint(telehealth_bp,  url_prefix="/api/telehealth")
app.register_blueprint(gamification_bp, url_prefix="/api/gamification")
app.register_blueprint(facts_bp,       url_prefix="/api/facts")
app.register_blueprint(locations_bp,   url_prefix="/api/locations")
app.register_blueprint(users_bp,       url_prefix="/api/users")

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Main entry point — renders the patient dashboard shell."""
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/scan")
def scan():
    return render_template("scan.html")

@app.route("/images/<path:filename>")
def serve_image(filename):
    return send_from_directory("images", filename)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
