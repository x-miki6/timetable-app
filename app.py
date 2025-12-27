from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return "API server running"

@app.route("/api/classes")
def classes():
    return jsonify({
        "classes": []
    })

if __name__ == "__main__":
    app.run(debug=True)
