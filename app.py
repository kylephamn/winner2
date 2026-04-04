from flask import Flask, render_template

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Blueprints
# ---------------------------------------------------------------------------
# Register API blueprints here as they're built out.
# Example:
#   from api.patients import patients_bp
#   app.register_blueprint(patients_bp, url_prefix="/api/patients")

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
