from flask import Flask, jsonify, request
import json
import os

BASE_DIR = os.path.dirname(__file__)
CLASSES_PATH = os.path.join(BASE_DIR, "classes.json")
FAVORITES_PATH = os.path.join(BASE_DIR, "favorites.json")
USERS_PATH = os.path.join(BASE_DIR, "users.json")

app = Flask(__name__)

@app.route("/")
def index():
    return "API server running"

@app.route("/api/classes")
def get_classes():
    with open(CLASSES_PATH, encoding="utf-8") as f:
        classes = json.load(f)

    keyword = request.args.get("keyword")
    day = request.args.get("day")
    period = request.args.get("period")
    term = request.args.get("term")

    if keyword:
        classes = [c for c in classes if keyword in c["name"]]

    if day:
        classes = [c for c in classes if c["day"] == day]

    if period:
        classes = [c for c in classes if c["period"] == int(period)]

    if term:
        classes = [c for c in classes if c["term"] == int(term)]

    return jsonify({"classes": classes})

@app.route("/api/favorites", methods=["GET"])
def get_favorites():
    # favorites を読む
    with open(FAVORITES_PATH, encoding="utf-8") as f:
        favorites_data = json.load(f)["favorites"]

    # classes を読む
    with open(CLASSES_PATH, encoding="utf-8") as f:
        classes = json.load(f)

    result = []

    for fav in favorites_data:
        # class_id が一致する授業を探す
        class_data = next(
            (c for c in classes if c["id"] == fav["class_id"]),
            None
        )

        if class_data:
            result.append({
                "favorite_id": fav["id"],
                "class": class_data
            })

    return jsonify({ "favorites": result })

@app.route("/api/favorites", methods=["POST"])
def add_favorite():
    new_favorite = request.get_json()

    with open(FAVORITES_PATH, encoding="utf-8") as f:
        data = json.load(f)

    # 🔒 二重チェック
    if any(f["class_id"] == new_favorite["class_id"] for f in data["favorites"]):
        return jsonify({
            "status": "error",
            "message": "already favorited"
        }), 400

    new_id = len(data["favorites"]) + 1
    favorite = {
        "id": new_id,
        "class_id": new_favorite["class_id"]
    }

    data["favorites"].append(favorite)

    with open(FAVORITES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return jsonify({"status": "ok", "favorite": favorite})

@app.route("/api/favorites/<int:favorite_id>", methods=["DELETE"])
def delete_favorite(favorite_id):
    with open(FAVORITES_PATH, encoding="utf-8") as f:
        data = json.load(f)

    data["favorites"] = [
        f for f in data["favorites"] if f["id"] != favorite_id
    ]

    with open(FAVORITES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return jsonify({"status": "deleted"})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    with open(USERS_PATH, encoding="utf-8") as f:
        users = json.load(f)["users"]

    user = next(
        (
            u for u in users
            if u["username"] == data["username"]
            and u["password"] == data["password"]
        ),
        None
    )

    if not user:
        return jsonify({
            "status": "error",
            "message": "invalid credentials"
        }), 401

    return jsonify({
        "status": "ok",
        "user_id": user["id"]
    })

if __name__ == "__main__":
    app.run(port=5002, debug=True)
