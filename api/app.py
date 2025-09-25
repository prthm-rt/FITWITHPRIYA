import os
import re
import datetime
from flask import Flask, render_template, jsonify, request
from flask_wtf import CSRFProtect
from forms import ContactForm

# app.py lives in api/, your assets are one level up
app = Flask(__name__, static_folder="../static", template_folder="../templates")

# Needed for Flask-WTF (use a real secret in prod)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret")
csrf = CSRFProtect(app)

@app.get("/")
def index():
    form = ContactForm()
    return render_template("index.html", contact_form=form)

@app.get("/api/hello")
def hello():
    return jsonify({"message": "Hello from Flask"})

@app.get("/api/health")
def health():
    return jsonify(ok=True)

# Optional: serve home with a fresh form on 404
@app.errorhandler(404)
def not_found(e):
    return render_template("index.html", contact_form=ContactForm()), 404

# --- Reviews API: in-memory demo storage ---
reviews = []

@csrf.exempt
@app.route("/reviews", methods=["GET", "POST"])
def reviews_handler():
    if request.method == "GET":
        return jsonify(success=True, reviews=reviews)

    # POST
    name = (request.form.get("name") or "").strip()
    comment = (request.form.get("comment") or "").strip()
    rating_raw = (request.form.get("rating") or "").strip()

    # Accept values like "5 / 5" or "5"; extract first number
    match = re.search(r"\d+", rating_raw)
    rating_val = int(match.group()) if match else None

    if not (name and comment and rating_val):
        return jsonify(success=False, errors={"form": "Missing fields"}), 400

    # optional duplicate check
    if any(r.get("name") == name and r.get("comment") == comment for r in reviews):
        return jsonify(success=False, errors={"duplicate": "Duplicate review"}), 400

    review = {
        "name": name,
        "comment": comment,
        "rating": rating_val,
        "date": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }
    reviews.append(review)
    return jsonify(success=True)