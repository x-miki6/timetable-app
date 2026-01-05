import csv
import json

csv_file = "timetable-app_授業一覧.csv"
json_file = "classes.json"

classes = []

with open(csv_file, encoding="utf-8-sig") as f:  # ← ここ重要
    reader = csv.DictReader(f)
    for row in reader:
        row["id"] = int(row["id"])
        row["term"] = int(row["term"])
        row["period"] = int(row["period"])
        classes.append(row)

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(classes, f, ensure_ascii=False, indent=2)

print("classes.json を作成しました")
