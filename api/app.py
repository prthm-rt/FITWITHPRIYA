from flask import Flask, jsonify, render_template

app = Flask(__name__, static_folder="../static", template_folder="../templates")

@app.get("/")
def index():
    # If you have a templates/index.html, this will serve it:
    # return render_template("index.html")
    # Or just return JSON/text for now:
    return jsonify({"status": "ok", "app": "flask"})

@app.get("/api/hello")
def hello():
    return jsonify({"message": "Hello from Flask"})

@app.get("/api/health")
def health():
    return jsonify(ok=True)

if __name__ == "__main__":
    app.run(debug=True)