# /api/app.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/")
def home():
    return "Hello from Flask on Vercel"

@app.get("/api/health")
def health():
    return jsonify(ok=True)