import os
from flask import Flask, render_template, jsonify
from flask_wtf import CSRFProtect
from forms import ContactForm

# app.py lives in api/, your assets are one level up
app = Flask(__name__, static_folder="../static", template_folder="../templates")

# Needed for Flask-WTF (use a real secret in prod)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret")
CSRFProtect(app)

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