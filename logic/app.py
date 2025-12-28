from flask import Flask, jsonify, request
import json

app = Flask(__name__)

@app.route("/")
def index():
    return "API server running"

@app.route("/api/classes")
def get_classes():
    with open("classes.json", encoding="utf-8") as f:
        classes = json.load(f)

    # クエリパラメータ取得
    keyword = request.args.get("keyword")
    day = request.args.get("day")
    period = request.args.get("period")
    term = request.args.get("term")

    # 授業名検索
    if keyword:
        classes = [
            c for c in classes
            if keyword in c["name"]
        ]

    # 曜日検索
    if day:
        classes = [
            c for c in classes
            if c["day"] == day
        ]

    # 時限検索（数値なので int に変換）
    if period:
        classes = [
            c for c in classes
            if c["period"] == int(period)
        ]

    # 学期検索（数値）
    if term:
        classes = [
            c for c in classes
            if c["term"] == int(term)
        ]

    return jsonify({"classes": classes})

if __name__ == "__main__":
    app.run(port=5002, debug=True)
