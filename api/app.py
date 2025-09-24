from flask import Flask, render_template, jsonify

# app.py lives in api/, your assets are one level up
app = Flask(__name__, static_folder="../static", template_folder="../templates")

@app.get("/")
def index():
    return render_template("index.html")  # serve your real homepage

@app.get("/api/hello")
def hello():
    return jsonify({"message": "Hello from Flask"})

@app.get("/api/health")
def health():
    return jsonify(ok=True)