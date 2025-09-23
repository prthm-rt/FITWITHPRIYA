# /api/app.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from Flask on Vercel"

@app.route("/api/health")
def health():
    return jsonify(ok=True)