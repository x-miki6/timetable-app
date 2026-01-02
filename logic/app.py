from flask import Flask, jsonify, request
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# =====================
# 初期設定
# =====================
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = os.path.dirname(__file__)
CLASSES_PATH = os.path.join(BASE_DIR, "classes.json")
FAVORITES_PATH = os.path.join(BASE_DIR, "favorites.json")
USERS_PATH = os.path.join(BASE_DIR, "users.json")
COMMENTS_PATH = os.path.join(BASE_DIR, "comments.json")

app = Flask(__name__)

# =====================
# AIコメント生成ロジック
# =====================
def generate_ai_comment(class_info):
    prompt = f"""
あなたは大学生向けの履修アドバイザーです。
次の授業を含む時間割について、前向きなコメントを1〜2文で書いてください。

授業名: {class_info["name"]}
"""

    response = client.responses.create(
        model="gpt-5-nano",
        input=prompt
    )

    return response.output_text or "とてもバランスの良い時間割ですね！"

# =====================
# 動作確認
# =====================
@app.route("/")
def index():
    return "API server running"

# =====================
# 授業検索API
# =====================
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

# =====================
# お気に入り取得（JOIN）
# =====================
@app.route("/api/favorites", methods=["GET"])
def get_favorites():
    user_id = int(request.args.get("user_id"))

    with open(FAVORITES_PATH, encoding="utf-8") as f:
        favorites = json.load(f)["favorites"]

    with open(CLASSES_PATH, encoding="utf-8") as f:
        classes = json.load(f)

    result = []
    for fav in favorites:
        if fav["user_id"] != user_id:
            continue

        class_data = next((c for c in classes if c["id"] == fav["class_id"]), None)
        if class_data:
            result.append({
                "favorite_id": fav["id"],
                "class": class_data
            })

    return jsonify({"favorites": result})

# =====================
# お気に入り追加
# =====================
@app.route("/api/favorites", methods=["POST"])
def add_favorite():
    body = request.get_json()
    user_id = body["user_id"]
    class_id = body["class_id"]

    with open(FAVORITES_PATH, encoding="utf-8") as f:
        data = json.load(f)

    for favo in data["favorites"]:
        if favo["user_id"] == user_id and favo["class_id"] == class_id:
            return jsonify({"error": "already favorited"}), 400

    new_id = len(data["favorites"]) + 1
    data["favorites"].append({
        "id": new_id,
        "user_id": user_id,
        "class_id": class_id
    })

    with open(FAVORITES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return jsonify({"status": "ok"})

# =====================
# コメントAPI
# =====================
@app.route("/api/comments", methods=["GET"])
def get_comments():
    class_id = int(request.args.get("class_id"))

    with open(COMMENTS_PATH, encoding="utf-8") as f:
        comments = json.load(f)["comments"]

    return jsonify({
        "comments": [c for c in comments if c["class_id"] == class_id]
    })

@app.route("/api/comments", methods=["POST"])
def add_comment():
    body = request.get_json()

    with open(COMMENTS_PATH, encoding="utf-8") as f:
        data = json.load(f)

    new_id = len(data["comments"]) + 1
    data["comments"].append({
        "id": new_id,
        "user_id": body["user_id"],
        "class_id": body["class_id"],
        "content": body["content"]
    })

    with open(COMMENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return jsonify({"status": "ok"})

# =====================
# AIコメントAPI
# =====================
@app.route("/api/ai-comment")
def ai_comment():
    class_id = int(request.args.get("class_id"))

    with open(CLASSES_PATH, encoding="utf-8") as f:
        classes = json.load(f)

    class_info = next(c for c in classes if c["id"] == class_id)
    ai_text = generate_ai_comment(class_info)

    return jsonify({
        "success": True,
        "comment": ai_text
    })

# =====================
# 起動
# =====================
if __name__ == "__main__":
    app.run(port=5002, debug=True)
