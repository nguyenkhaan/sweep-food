"""Đánh giá gọn phần gợi ý món trên tủ lạnh thật – KHÔNG cần sửa code AI, KHÔNG cần người chấm.

Đầu vào: thư mục fridges/ – mỗi tủ một file JSON đúng định dạng request /api/recommend, ví dụ fridges/tu01.json:
  {"household_size": 1,
   "items": [{"name": "thịt heo nạc", "quantity_g": 300, "hours_to_expire": 20},
             {"name": "cải ngọt", "quantity_g": 250, "hours_to_expire": 40},
             {"name": "nước mắm", "quantity_g": 500, "is_staple": true}]}
  hours_to_expire: số giờ còn dùng được (ước lượng là đủ); đồ khô/gia vị để is_staple = true.

Cần dịch vụ AI đang chạy (mặc định http://127.0.0.1:8000, đổi bằng biến SWEEPFOOD_AI).
Chạy:  python fridge_report.py fridges
Ra:
  - In ra 4 con số cho slide 6.
  - fridge_top3.csv: top 3 món của từng tủ -> gửi lại chủ tủ hỏi "trong 3 món này bạn có nấu món nào không?",
    ghi Có/Không vào cột owner_would_cook rồi chạy lại với --answers fridge_top3.csv để có tỷ lệ.
"""
import csv, glob, json, os, sys, urllib.request

API = os.environ.get("SWEEPFOOD_AI", "http://127.0.0.1:8000") + "/api/recommend"
URGENT_H = 24  # trùng URGENT_HOURS của sweep-food-AI


def recommend(payload):
    req = urllib.request.Request(API, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=90).read()).get("recommendations", [])


def main(fridge_dir, answers=None):
    rows, stats = [], []
    for path in sorted(glob.glob(os.path.join(fridge_dir, "*.json"))):
        fid = os.path.splitext(os.path.basename(path))[0]
        pantry = json.load(open(path, encoding="utf-8"))
        urgent = {i["name"].strip().lower() for i in pantry["items"]
                  if not i.get("is_staple") and i.get("hours_to_expire") is not None and i["hours_to_expire"] <= URGENT_H}
        top3 = recommend(pantry)[:3]
        rescued = {r.strip().lower() for rec in top3 for r in rec.get("rescued_items", [])}
        missing = [len(rec.get("missing_ingredients", [])) for rec in top3]
        ready = sum(1 for rec in top3 if rec.get("status_badge") in ("ready", "elastic"))
        stats.append({"urgent": len(urgent), "rescued": len(rescued), "missing": sum(missing) / max(1, len(top3)),
                      "ready": ready, "n": len(top3)})
        rows.append([fid, " | ".join(r.get("name", "") for r in top3), len(urgent), len(rescued), round(stats[-1]["missing"], 2), ""])

    with_urgent = [s for s in stats if s["urgent"] > 0]
    print(f"Số tủ: {len(stats)} (có đồ còn ≤ {URGENT_H} giờ: {len(with_urgent)})")
    if with_urgent:
        hit = sum(1 for s in with_urgent if s["rescued"] > 0)
        used = sum(s["rescued"] for s in with_urgent) / sum(s["urgent"] for s in with_urgent)
        print(f"(1) Tủ có đồ sắp hỏng mà top 3 dùng được ít nhất 1 thứ: {hit}/{len(with_urgent)}")
        print(f"(2) Tỷ lệ đồ sắp hỏng được top 3 dùng đến: {used:.0%}")
    print(f"(3) Số thứ phải mua thêm trung bình mỗi món trong top 3: {sum(s['missing'] for s in stats) / max(1, len(stats)):.1f}")
    print(f"(4) Món trong top 3 nấu được ngay hoặc chỉ thiếu nhẹ: {sum(s['ready'] for s in stats)}/{sum(s['n'] for s in stats)}")

    if answers:
        ans = list(csv.DictReader(open(answers, encoding="utf-8")))
        yes = [a for a in ans if a.get("owner_would_cook", "").strip().lower() in ("có", "co", "yes", "1")]
        answered = [a for a in ans if a.get("owner_would_cook", "").strip()]
        print(f"(5) Chủ tủ nói sẽ nấu ít nhất 1 món trong top 3: {len(yes)}/{len(answered)}")
    else:
        with open("fridge_top3.csv", "w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows([["fridge_id", "top3", "urgent_items", "urgent_used", "avg_missing", "owner_would_cook"]] + rows)
        print("Đã ghi fridge_top3.csv")


if __name__ == "__main__":
    args = sys.argv[1:]
    answers = args[args.index("--answers") + 1] if "--answers" in args else None
    main(args[0], answers)
