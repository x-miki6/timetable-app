import json
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return "API server running"

@app.route("/api/classes")
def get_classes():
    with open("classes.json", encoding="utf-8") as f:
        classes = json.load(f)
    return jsonify({"classes": classes})

if __name__ == "__main__":
    app.run(port=5002, debug=True)
