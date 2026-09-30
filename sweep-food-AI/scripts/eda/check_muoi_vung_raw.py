import json


PATH = "data/raw/viendinhduong/food_nutrition_raw.json"

with open(PATH, "r", encoding="utf-8") as file:
    data = json.load(file)


def search(obj, target="15074"):
    if isinstance(obj, dict):
        text = " ".join(str(value) for value in obj.values())

        if target in text or "Muối vừng" in text:
            print(obj)
            print("-" * 80)

        for value in obj.values():
            search(value, target)

    elif isinstance(obj, list):
        for item in obj:
            search(item, target)


print("[1] RAW DATA FOR MUOI VUNG")
search(data)