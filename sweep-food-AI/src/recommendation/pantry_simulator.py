"""Rich Vietnamese Household Pantry Simulator.

Models authentic daily culinary habits across Vietnam based on demographic & cultural research:
1. Sinh viên / Người trẻ ở trọ (Student Budget & Dorm: Trứng, đậu phụ, cá hộp, rau muống luộc làm canh)
2. Bữa cơm gia đình Miền Bắc (Northern Family: Thịt luộc, sườn xào chua ngọt, cá kho dưa, canh sấu, cà pháo)
3. Bữa cơm gia đình Miền Trung (Central Family: Cá nục kho tiêu, thịt kho nghệ, canh bầu nấu tôm, sả ớt)
4. Bữa cơm gia đình Miền Nam (Southern Family: Canh chua cá lóc, cá kho tộ, thịt kho hột vịt, khổ qua)
5. Dân văn phòng bận rộn / Eat Clean (Office & Fitness: Ức gà, bò áp chảo, nấm, súp lơ, salad)
6. Vét tủ lạnh cuối tuần (Zero-Waste Clear-Out: Thực phẩm sắp hết hạn trong 12h-36h)
7. Cuối tháng chưa lương (End-of-Month Deficit: Trứng, mì, đậu hũ, cơm chiên)
8. Mâm cơm chay thanh tịnh (Vegetarian / Rằm & Mùng 1: Đậu non, nấm, hạt sen, cải thìa)
"""

from __future__ import annotations

import random
from typing import Any

# Extended ingredient pools matching real Vietnamese grocery habits
STAPLE_POOL = [
    ("nước mắm", "13032", 500),
    ("muối", "13032", 300),
    ("đường", "13032", 400),
    ("hạt nêm", "13032", 250),
    ("tiêu", "13032", 50),
    ("dầu ăn", "6002", 500),
    ("tỏi", "4103", 100),
    ("hành tím", "4037", 100),
    ("hành lá", "4038", 50),
    ("ớt", "4061", 30),
    ("nước tương", "13032", 300),
]


def _make_item(name: str, code: str, qty_g: float, hours_exp: float, is_staple: bool = False) -> dict[str, Any]:
    return {
        "name": name,
        "code": code,
        "quantity_g": round(float(qty_g), 1),
        "hours_to_expire": round(float(hours_exp), 1),
        "is_staple": is_staple
    }


def generate_vietnamese_pantry(pantry_idx: int) -> dict[str, Any]:
    """Generates an authentic Vietnamese household pantry based on real culinary habits."""
    archetype = random.choices(
        [
            "sinh_vien",              # 20%
            "gia_dinh_mien_bac",     # 18%
            "gia_dinh_mien_nam",     # 18%
            "gia_dinh_mien_trung",   # 12%
            "dan_van_phong_eat_clean", # 14%
            "vet_tu_zero_waste",      # 10%
            "cuoi_thang_chua_luong",  # 4%
            "an_chay_thanh_tinh"      # 4%
        ],
        weights=[0.20, 0.18, 0.18, 0.12, 0.14, 0.10, 0.04, 0.04]
    )[0]

    pantry_id = f"pantry_{pantry_idx:06d}"
    items = []

    # 1. Base Vietnamese staples (4-7 items)
    num_staples = random.randint(4, len(STAPLE_POOL))
    for name, code, default_g in random.sample(STAPLE_POOL, num_staples):
        items.append(_make_item(name, code, default_g, random.randint(240, 720), is_staple=True))

    household_size = 4
    max_time_min = 45

    # --------------------------------------------------------------------------
    # 2. Archetype-Specific Scenarios
    # --------------------------------------------------------------------------
    if archetype == "sinh_vien":
        # Sinh viên: 1-2 người, nấu nhanh (< 25p), ngân sách tiết kiệm
        household_size = random.choice([1, 2])
        max_time_min = random.choice([15, 20, 25])

        # Đạm rẻ tiền: Trứng (luôn có), đậu phụ, thịt băm hoặc cá hộp
        items.append(_make_item("trứng gà", "9001", random.randint(150, 300), random.randint(48, 168)))
        if random.random() < 0.70:
            items.append(_make_item("đậu phụ", "3025", random.randint(200, 400), random.randint(24, 72)))
        if random.random() < 0.60:
            items.append(_make_item("thịt băm", "7028", random.randint(150, 250), random.randint(36, 72)))

        # Rau củ rẻ, dễ bảo quản: rau muống (luộc lấy nước làm canh), cà chua, dưa leo, bắp cải
        veggies = [
            ("rau muống", "4083", (150, 350)),  # có thể chỉ có nửa bó!
            ("cà chua", "4005", (100, 200)),
            ("bắp cải", "4010", (200, 400)),
            ("giá đỗ", "4036", (100, 200)),
            ("dưa chuột", "4027", (100, 250)),
        ]
        for v_name, v_code, v_range in random.sample(veggies, random.randint(1, 3)):
            items.append(_make_item(v_name, v_code, random.randint(*v_range), random.randint(36, 96)))

    elif archetype == "gia_dinh_mien_bac":
        # Gia đình miền Bắc: 3-5 người, mâm cơm thanh tao, dưa cà, canh thanh
        household_size = random.choice([3, 4, 5])
        max_time_min = random.choice([35, 45, 60])

        # Đạm đặc trưng: Sườn heo, thịt ba chỉ, cá trắm, thịt gà ta
        p_candidates = [
            ("sườn heo", "7053", (400, 700)),
            ("ba chỉ", "7028", (300, 600)),
            ("thịt gà ta", "7013", (500, 1000)),
            ("cá chép", "8016", (500, 900)),
            ("đậu phụ", "3025", (200, 400)),
        ]
        for p_name, p_code, p_range in random.sample(p_candidates, random.randint(1, 2)):
            items.append(_make_item(p_name, p_code, random.randint(*p_range), random.randint(48, 96)))

        # Rau củ & canh: Cà pháo muối, dưa cải chua, rau muống, bí xanh, sấu
        v_candidates = [
            ("rau muống", "4083", (250, 450)),
            ("dưa cải chua", "4116", (150, 300)),
            ("cà chua", "4005", (150, 300)),
            ("bí xanh", "4002", (300, 600)),
            ("mồng tơi", "4080", (200, 350)),
            ("bắp cải", "4010", (300, 600)),
        ]
        for v_name, v_code, v_range in random.sample(v_candidates, random.randint(2, 3)):
            items.append(_make_item(v_name, v_code, random.randint(*v_range), random.randint(48, 120)))

    elif archetype == "gia_dinh_mien_trung":
        # Gia đình miền Trung: 3-4 người, vị đậm đà, cay nồng, cá kho biển
        household_size = random.choice([3, 4, 5])
        max_time_min = random.choice([35, 45, 50])

        # Đạm đặc trưng: Cá nục, cá thu, tôm, thịt ba chỉ, sườn heo
        p_candidates = [
            ("cá nục", "8016", (300, 600)),
            ("cá thu", "8016", (300, 500)),
            ("tôm", "8016", (200, 400)),
            ("ba chỉ", "7028", (300, 500)),
            ("thịt bò", "7001", (250, 450)),
        ]
        for p_name, p_code, p_range in random.sample(p_candidates, random.randint(1, 2)):
            items.append(_make_item(p_name, p_code, random.randint(*p_range), random.randint(48, 96)))

        # Rau củ & gia vị đậm: Bầu, bí đao, rau ngót, dưa leo, nghệ tươi
        v_candidates = [
            ("bầu", "4001", (300, 500)),
            ("rau ngót", "4086", (150, 300)),
            ("khổ qua", "4050", (200, 400)),
            ("cà chua", "4005", (150, 250)),
            ("đậu cô ve", "4029", (150, 300)),
        ]
        for v_name, v_code, v_range in random.sample(v_candidates, random.randint(2, 3)):
            items.append(_make_item(v_name, v_code, random.randint(*v_range), random.randint(48, 96)))

    elif archetype == "gia_dinh_mien_nam":
        # Gia đình miền Nam: 3-5 người, ngọt béo, canh chua cá lóc, thịt kho hột vịt
        household_size = random.choice([3, 4, 5])
        max_time_min = random.choice([40, 50, 60])

        # Đạm đặc trưng: Cá lóc, cá hú, thịt ba rọi, trứng vịt, tôm sú
        p_candidates = [
            ("cá lóc", "8016", (400, 700)),
            ("ba chỉ", "7028", (400, 700)),
            ("trứng vịt", "9004", (200, 400)),
            ("tôm", "8016", (250, 500)),
            ("thịt heo", "7028", (300, 600)),
        ]
        for p_name, p_code, p_range in random.sample(p_candidates, random.randint(1, 2)):
            items.append(_make_item(p_name, p_code, random.randint(*p_range), random.randint(48, 96)))

        # Rau củ canh chua: Dọc mùng, dứa (thơm), đậu bắp, giá đỗ, cà chua, khổ qua
        v_candidates = [
            ("dọc mùng", "4026", (150, 300)),
            ("dứa ta", "5014", (150, 300)),
            ("đậu bắp", "4032", (100, 250)),
            ("giá đỗ", "4036", (150, 250)),
            ("cà chua", "4005", (150, 300)),
            ("khổ qua", "4050", (250, 500)),
        ]
        for v_name, v_code, v_range in random.sample(v_candidates, random.randint(2, 4)):
            items.append(_make_item(v_name, v_code, random.randint(*v_range), random.randint(48, 96)))

    elif archetype == "dan_van_phong_eat_clean":
        # Dân văn phòng / Eat Clean: 1-2 người, ức gà, bò mềm, nấm, súp lơ, ít calo
        household_size = random.choice([1, 2])
        max_time_min = random.choice([20, 25, 30])

        p_candidates = [
            ("ức gà", "7089", (300, 600)),
            ("thịt bò", "7001", (200, 400)),
            ("trứng gà", "9001", (150, 300)),
            ("cá hồi", "8016", (200, 400)),
            ("tôm", "8016", (200, 400)),
        ]
        for p_name, p_code, p_range in random.sample(p_candidates, random.randint(1, 2)):
            items.append(_make_item(p_name, p_code, random.randint(*p_range), random.randint(48, 120)))

        v_candidates = [
            ("bắp cải", "4010", (200, 400)),
            ("súp lơ xanh", "4100", (200, 400)),
            ("nấm kim châm", "4133", (100, 200)),
            ("nấm đùi gà", "20007", (150, 300)),
            ("cà rốt", "4007", (100, 250)),
            ("cải thìa", "4015", (150, 300)),
        ]
        for v_name, v_code, v_range in random.sample(v_candidates, random.randint(2, 3)):
            items.append(_make_item(v_name, v_code, random.randint(*v_range), random.randint(48, 96)))

    elif archetype == "vet_tu_zero_waste":
        # Vét tủ lạnh: Có 1-2 món khẩn cấp sắp hỏng trong 12h - 36h!
        household_size = random.choice([2, 3, 4])
        max_time_min = random.choice([30, 40, 50])

        urgent_candidates = [
            ("thịt bò", "7001", (150, 350)),
            ("cá lóc", "8016", (200, 400)),
            ("thịt heo", "7028", (200, 400)),
            ("tôm", "8016", (150, 300)),
            ("rau muống", "4083", (100, 250)),  # rau ngót ngót
            ("cà chua", "4005", (100, 200)),
        ]
        for name, code, q_range in random.sample(urgent_candidates, random.randint(1, 2)):
            items.append(_make_item(name, code, random.randint(*q_range), random.randint(8, 36)))

        # Kèm thêm 1-2 món đồ tươi còn lại
        extras = [
            ("trứng gà", "9001", (100, 250)),
            ("đậu phụ", "3025", (150, 300)),
            ("bắp cải", "4010", (200, 350)),
        ]
        for name, code, q_range in random.sample(extras, random.randint(1, 2)):
            items.append(_make_item(name, code, random.randint(*q_range), random.randint(48, 96)))

    elif archetype == "cuoi_thang_chua_luong":
        # Cuối tháng: Chỉ còn đồ rẻ hoặc đồ sót lại
        household_size = random.choice([1, 2])
        max_time_min = 20
        items.append(_make_item("trứng gà", "9001", random.randint(100, 200), random.randint(48, 120)))
        items.append(_make_item("đậu phụ", "3025", random.randint(150, 300), random.randint(24, 48)))
        items.append(_make_item("rau muống", "4083", random.randint(100, 200), random.randint(24, 72)))

    elif archetype == "an_chay_thanh_tinh":
        # Ăn chay: Đậu phụ, nấm rơm, hạt sen, rau cải
        household_size = random.choice([2, 4])
        max_time_min = random.choice([30, 40])
        veg_items = [
            ("đậu phụ", "3025", (250, 500)),
            ("nấm rơm", "4129", (150, 300)),
            ("nấm đùi gà", "20007", (150, 300)),
            ("cải thìa", "4015", (200, 400)),
            ("cà rốt", "4007", (100, 250)),
            ("mướp", "4054", (200, 400)),
        ]
        for name, code, q_range in random.sample(veg_items, random.randint(3, 5)):
            items.append(_make_item(name, code, random.randint(*q_range), random.randint(48, 96)))

    return {
        "pantry_id": pantry_id,
        "scenario_type": archetype,
        "items": items,
        "household_size": household_size,
        "max_cooking_time_min": max_time_min
    }


def generate_pantry_batch(count: int = 50000) -> list[dict[str, Any]]:
    """Generates a batch of distinct, realistic Vietnamese pantry simulation states."""
    random.seed(42)  # For strict deterministic reproducibility
    return [generate_vietnamese_pantry(i) for i in range(count)]
