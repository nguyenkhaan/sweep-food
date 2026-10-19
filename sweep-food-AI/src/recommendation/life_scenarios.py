"""Vietnamese pantry scenarios for ranking training data, with a student focus.

Each scenario is a declarative profile: who cooks, with what equipment, on what
budget, under which health or diet rule, and which ingredients that kind of
kitchen realistically holds. `generate_life_pantry(index)` turns a profile into
one concrete pantry (items with grams and hours-to-expiry) deterministically.

Profile fields (consumed by `scenario_rules`):

* ``group``          coarse segment, e.g. ``sinh_vien`` (students), ``gia_dinh``.
* ``equipment``      ``rice_cooker`` (only a rice cooker), ``one_burner`` (one
                     induction/gas ring, no oven) or ``full``.
* ``budget``         ``tight`` / ``normal`` / ``generous``: how much an extra
                     shopping item hurts.
* ``no_shopping``    True when the cook cannot buy anything (storm, broke).
* ``prefer_methods`` / ``avoid_methods``  values of ``recipes.cooking_method``.
* ``prefer_dish``    values of ``recipes.dish_type``.
* ``diet``           ``vegetarian`` or None.
* ``health``         subset of ``low_sugar``, ``low_sodium``, ``gout``,
                     ``low_carb``, ``gentle_stomach``, ``no_spicy``.
* ``kcal_band``      soft energy target for one serving of the dish itself
                     (kcal, rice eaten alongside not included).
* ``high_protein``   prefers dishes with >= 25 g protein per serving.
* ``beginner``       penalises complex dishes.
* ``rescue_weight``  how much using food that expires within 24 h matters.

Pantry pools use master codes that the curated catalog actually cooks with.
"""

from __future__ import annotations

import random
from typing import Any

from src.recommendation.pantry_simulator import _make_item

# key -> (pantry name, master code, (min_g, max_g) for two people)
Pool = dict[str, tuple[str, str, tuple[int, int]]]

PROTEIN: Pool = {
    "trứng gà": ("trứng gà", "9001", (120, 360)),
    "trứng vịt": ("trứng vịt", "9004", (140, 350)),
    "trứng cút": ("trứng cút", "9007", (100, 250)),
    "đậu phụ": ("đậu phụ", "3025", (150, 500)),
    "đậu phụ non": ("đậu phụ non", "3038", (150, 400)),
    "đậu hũ chiên": ("đậu hũ chiên", "20352", (150, 350)),
    "tàu hũ ky": ("tàu hũ ky", "3026", (60, 200)),
    "thịt chay": ("thịt chay", "20039", (100, 300)),
    "chả lụa chay": ("chả lụa chay", "20040", (100, 300)),
    "thịt băm": ("thịt heo xay", "20441", (150, 400)),
    "thịt nạc": ("thịt nạc heo", "7017", (150, 450)),
    "nạc vai": ("thịt nạc vai heo", "7083", (200, 500)),
    "ba chỉ": ("thịt ba chỉ", "7018", (200, 600)),
    "sườn heo": ("sườn heo", "7053", (300, 800)),
    "chân giò": ("chân giò heo", "7032", (500, 1200)),
    "giò sống": ("giò sống", "20001", (150, 400)),
    "thịt bò": ("thịt bò nạc", "7003", (150, 450)),
    "thăn bò": ("thịt thăn bò", "7005", (150, 400)),
    "bắp bò": ("thịt bắp bò", "7094", (300, 700)),
    "thịt gà ta": ("thịt gà ta", "7013", (500, 1300)),
    "đùi gà": ("đùi gà", "7088", (300, 700)),
    "cánh gà": ("cánh gà", "7087", (300, 700)),
    "ức gà": ("ức gà", "7089", (200, 600)),
    "thịt vịt": ("thịt vịt", "7028", (500, 1200)),
    "tôm": ("tôm", "8051", (150, 500)),
    "tôm khô": ("tôm khô", "8053", (30, 100)),
    "mực": ("mực", "8040", (200, 500)),
    "ngao": ("ngao", "8066", (300, 1000)),
    "cua đồng": ("cua đồng", "8034", (200, 500)),
    "cá basa": ("cá basa", "8092", (250, 600)),
    "cá lóc": ("cá lóc", "8022", (400, 900)),
    "cá chép": ("cá chép", "8003", (500, 1000)),
    "cá hồi": ("cá hồi", "8011", (200, 500)),
    "cá thu": ("cá thu", "8026", (250, 500)),
    "cá nục": ("cá nục", "8020", (300, 600)),
    "cá hộp": ("cá hộp", "20681", (150, 300)),
    "cá khô": ("cá khô", "8012", (80, 200)),
    "mực khô": ("mực khô", "8039", (60, 150)),
    "giò lụa": ("giò lụa", "7069", (150, 400)),
    "xúc xích": ("xúc xích", "7077", (100, 300)),
    "lạp xưởng": ("lạp xưởng", "20075", (100, 250)),
    "gan lợn": ("gan lợn", "7041", (150, 300)),
    "sữa tươi": ("sữa tươi không đường", "10001", (180, 1000)),
    "phô mai": ("phô mai", "10009", (60, 200)),
}

VEG: Pool = {
    "cà chua": ("cà chua", "4005", (100, 400)),
    "hành tây": ("hành tây", "4039", (100, 300)),
    "cà rốt": ("cà rốt", "4007", (100, 350)),
    "khoai tây": ("khoai tây", "2014", (200, 600)),
    "dưa chuột": ("dưa chuột", "4027", (150, 400)),
    "giá đỗ": ("giá đỗ", "4036", (100, 300)),
    "rau muống": ("rau muống", "4083", (200, 500)),
    "rau ngót": ("rau ngót", "20115", (150, 300)),
    "mồng tơi": ("mồng tơi", "4080", (150, 350)),
    "cải thìa": ("cải thìa", "4015", (150, 400)),
    "cải ngọt": ("cải ngọt", "4108", (200, 450)),
    "cải xanh": ("cải xanh", "4016", (200, 450)),
    "bắp cải": ("bắp cải", "4010", (300, 800)),
    "cải thảo": ("cải thảo", "4109", (300, 700)),
    "súp lơ xanh": ("súp lơ xanh", "4100", (200, 450)),
    "súp lơ trắng": ("súp lơ trắng", "4099", (200, 450)),
    "bí đao": ("bí đao", "4002", (300, 800)),
    "bí đỏ": ("bí đỏ", "4003", (300, 800)),
    "bầu": ("bầu", "4001", (300, 700)),
    "mướp": ("mướp", "4054", (200, 500)),
    "mướp đắng": ("mướp đắng", "4055", (200, 450)),
    "su su": ("su su", "4098", (200, 500)),
    "su hào": ("su hào", "4096", (200, 500)),
    "củ cải trắng": ("củ cải trắng", "4021", (300, 700)),
    "đậu cô ve": ("đậu cô ve", "4029", (150, 400)),
    "đậu bắp": ("đậu bắp", "20086", (150, 350)),
    "ớt chuông": ("ớt chuông", "20014", (100, 300)),
    "cần tây": ("cần tây", "4018", (100, 250)),
    "nấm rơm": ("nấm rơm", "4129", (150, 300)),
    "nấm hương": ("nấm hương", "4127", (80, 200)),
    "nấm hương khô": ("nấm hương khô", "4126", (20, 60)),
    "mộc nhĩ": ("mộc nhĩ", "4125", (20, 60)),
    "nấm kim châm": ("nấm kim châm", "20006", (100, 300)),
    "nấm đùi gà": ("nấm đùi gà", "20007", (150, 400)),
    "măng tre": ("măng tre", "4053", (200, 500)),
    "măng chua": ("măng chua", "4050", (200, 400)),
    "dưa cải chua": ("dưa cải chua", "4116", (200, 400)),
    "hoa chuối": ("hoa chuối", "4043", (150, 350)),
    "dọc mùng": ("dọc mùng", "4026", (150, 300)),
    "ngô ngọt": ("ngô ngọt", "20905", (200, 500)),
    "khoai môn": ("khoai môn", "2010", (200, 500)),
    "hạt sen": ("hạt sen", "4040", (100, 250)),
    "xà lách": ("xà lách", "4090", (100, 300)),
    "dứa": ("dứa", "5014", (200, 600)),
    "măng tây": ("măng tây", "20033", (150, 350)),
    "đu đủ xanh": ("đu đủ xanh", "4033", (300, 700)),
}

STARCH: Pool = {
    "gạo tẻ": ("gạo tẻ", "1004", (1000, 5000)),
    "gạo nếp": ("gạo nếp", "1001", (500, 2000)),
    "bún tươi": ("bún tươi", "1020", (300, 800)),
    "bún khô": ("bún gạo khô", "20609", (200, 500)),
    "miến dong": ("miến dong", "2015", (100, 300)),
    "mì trứng": ("mì trứng", "20087", (150, 400)),
    "mì ăn liền": ("mì ăn liền", "1043", (150, 450)),
    "nui": ("nui", "20085", (200, 500)),
    "bánh mì": ("bánh mì", "1012", (100, 300)),
    "khoai lang": ("khoai lang", "2008", (300, 800)),
    "khoai tây": ("khoai tây", "2014", (300, 800)),
    "bột mì": ("bột mì", "1018", (300, 1000)),
}

# Seasonings and aromatics. Students in a dorm keep only the first five.
STAPLES_BASIC = [
    ("muối", "13005", 200),
    ("đường", "12014", 300),
    ("dầu ăn", "6002", 400),
    ("nước mắm", "13017", 400),
    ("hạt nêm", "13026", 200),
]
STAPLES_EXTRA = [
    ("mì chính", "13029", 150),
    ("tiêu", "13004", 50),
    ("tỏi", "4103", 100),
    ("hành tím", "4037", 100),
    ("hành lá", "4038", 50),
    ("ớt", "13039", 30),
    ("nước tương", "13022", 300),
    ("dầu hào", "13027", 250),
    ("gừng", "13003", 60),
    ("sả", "13024", 80),
]
VEGETARIAN_STAPLES = [
    ("muối", "13005", 200),
    ("đường", "12014", 300),
    ("dầu ăn", "6002", 400),
    ("nước tương", "13022", 300),
    ("hạt nêm chay", "EXT023", 200),
]

STUDENT = "sinh_vien"


def _s(key: str, label: str, constraint: str, group: str, **profile: Any) -> dict[str, Any]:
    base = {
        "key": key, "label": label, "constraint": constraint, "group": group,
        "equipment": "full", "budget": "normal", "no_shopping": False,
        "prefer_methods": [], "avoid_methods": [], "prefer_dish": [],
        "diet": None, "health": [], "kcal_band": (120, 800), "high_protein": False,
        "beginner": False, "rescue_weight": 0.15, "household": [2, 3, 4],
        "proteins": [], "n_protein": (1, 2), "vegs": [], "n_veg": (1, 3),
        "starches": ["gạo tẻ"], "n_starch": (1, 1), "urgent": None,
        "staples": "full",
    }
    base.update(profile)
    return base


SCENARIOS: list[dict[str, Any]] = [
    # ---------------------------------------------------------------- students
    _s("sinh_vien_o_tro", "Sinh viên ở trọ, bếp từ 1 ổ, ngân sách hẹp",
       "Nấu ít dụng cụ, rẻ, 1-2 người ăn.", STUDENT,
       equipment="one_burner", budget="tight", household=[1, 2],
       prefer_methods=["Xào", "Canh/Súp", "Kho"], kcal_band=(150, 850), beginner=True,
       proteins=["trứng gà", "đậu phụ", "thịt băm", "xúc xích"], n_protein=(1, 2),
       vegs=["rau muống", "cà chua", "bắp cải", "giá đỗ", "dưa chuột", "cải ngọt"], n_veg=(1, 3),
       starches=["gạo tẻ", "mì ăn liền"], n_starch=(1, 2), staples="basic_plus"),
    _s("sinh_vien_ktx_noi_com_dien", "Sinh viên ký túc xá chỉ có nồi cơm điện",
       "Chỉ luộc/hấp/nấu canh/kho trong nồi cơm điện; không chiên, xào, nướng.", STUDENT,
       equipment="rice_cooker", budget="tight", household=[1, 2],
       prefer_methods=["Canh/Súp", "Luộc", "Hấp"], kcal_band=(150, 850), beginner=True,
       proteins=["trứng gà", "xúc xích", "đậu phụ", "cá hộp", "giò lụa", "trứng cút"], n_protein=(1, 2),
       vegs=["bắp cải", "cà rốt", "khoai tây", "cà chua", "su su", "bí đỏ"], n_veg=(1, 2),
       starches=["gạo tẻ", "mì ăn liền"], n_starch=(1, 2), staples="basic"),
    _s("sinh_vien_cuoi_thang_het_tien", "Sinh viên cuối tháng hết tiền",
       "Không mua thêm; tận dụng trứng, đậu, rau rẻ đang có.", STUDENT,
       equipment="one_burner", budget="tight", no_shopping=True, household=[1, 2],
       kcal_band=(150, 850), beginner=True,
       proteins=["trứng gà", "đậu phụ", "trứng vịt"], n_protein=(1, 2),
       vegs=["rau muống", "bắp cải", "giá đỗ", "cà chua", "bí đao"], n_veg=(1, 2),
       starches=["gạo tẻ", "mì ăn liền"], n_starch=(1, 2), staples="basic"),
    _s("sinh_vien_nau_chung_nhom", "Nhóm sinh viên góp tiền nấu chung",
       "3-5 người, ngân sách góp hạn chế, cần mâm cơm no đủ.", STUDENT,
       equipment="one_burner", budget="tight", household=[3, 4, 5],
       prefer_dish=["Món chính", "Canh"], kcal_band=(150, 900),
       proteins=["ba chỉ", "thịt băm", "trứng gà", "đậu phụ", "cá basa", "đùi gà"], n_protein=(1, 3),
       vegs=["rau muống", "cải ngọt", "bí đao", "cà chua", "khoai tây", "mướp", "bắp cải"], n_veg=(2, 4),
       staples="full"),
    _s("sinh_vien_mua_thi", "Sinh viên mùa thi, ít thời gian",
       "Món nhanh, ít bước, đủ năng lượng.", STUDENT,
       equipment="one_burner", budget="tight", household=[1, 2],
       kcal_band=(200, 900), beginner=True, avoid_methods=["Nướng"],
       proteins=["trứng gà", "xúc xích", "thịt băm", "cá hộp"], n_protein=(1, 2),
       vegs=["cà chua", "giá đỗ", "cải ngọt", "dưa chuột"], n_veg=(1, 2),
       starches=["gạo tẻ", "mì ăn liền", "bánh mì"], n_starch=(1, 2), staples="basic_plus"),
    _s("sinh_vien_lam_them_ve_khuya", "Sinh viên đi làm thêm về khuya",
       "Một nồi/một chảo, nấu nhanh, ăn khuya nhẹ.", STUDENT,
       equipment="one_burner", budget="tight", household=[1],
       prefer_methods=["Canh/Súp", "Xào"], kcal_band=(150, 750), beginner=True,
       proteins=["trứng gà", "xúc xích", "thịt băm", "giò lụa"], n_protein=(1, 1),
       vegs=["cải ngọt", "giá đỗ", "cà chua", "rau muống"], n_veg=(1, 2),
       starches=["mì ăn liền", "gạo tẻ", "mì trứng"], n_starch=(1, 2), staples="basic"),
    _s("sinh_vien_do_que_gui_len", "Sinh viên nhận đồ quê gửi lên",
       "Gà ta, giò, lạc, rau nhà trồng gửi lên phải nấu sớm.", STUDENT,
       equipment="one_burner", budget="tight", household=[1, 2, 3],
       rescue_weight=0.3,
       proteins=["thịt gà ta", "giò lụa", "trứng gà", "cá khô", "ba chỉ"], n_protein=(1, 3),
       vegs=["rau muống", "bí đỏ", "su su", "mướp", "rau ngót"], n_veg=(1, 3),
       starches=["gạo tẻ", "gạo nếp"], n_starch=(1, 2),
       urgent=(1, ["thịt gà ta", "ba chỉ"]), staples="basic_plus"),
    _s("sinh_vien_tap_gym", "Sinh viên tập gym, ngân sách hẹp",
       "Đạm cao từ trứng, ức gà, đậu phụ; rẻ; hạn chế chiên ngập dầu.", STUDENT,
       equipment="one_burner", budget="tight", household=[1, 2],
       high_protein=True, avoid_methods=["Chiên/Rán"], kcal_band=(200, 900),
       proteins=["trứng gà", "ức gà", "đậu phụ", "thịt nạc", "cá basa"], n_protein=(2, 3),
       vegs=["súp lơ xanh", "cải ngọt", "cà rốt", "dưa chuột"], n_veg=(1, 3),
       starches=["gạo tẻ", "khoai lang"], n_starch=(1, 2), staples="basic_plus"),
    _s("sinh_vien_an_chay", "Sinh viên ăn chay",
       "Không đạm động vật, không mắm cá; rẻ, nấu nhanh.", STUDENT,
       equipment="one_burner", budget="tight", diet="vegetarian",
       household=[1, 2], kcal_band=(120, 800),
       proteins=["đậu phụ", "đậu hũ chiên", "thịt chay", "tàu hũ ky"], n_protein=(1, 2),
       vegs=["nấm rơm", "cải ngọt", "cà chua", "bắp cải", "nấm đùi gà", "su su"], n_veg=(2, 3),
       staples="vegetarian"),
    _s("tan_sinh_vien_moi_tap_nau", "Tân sinh viên mới tập nấu",
       "Món dễ, ít nguyên liệu, ít bước; tránh chiên ngập dầu.", STUDENT,
       equipment="one_burner", budget="tight", household=[1, 2],
       beginner=True, avoid_methods=["Chiên/Rán", "Nướng"], kcal_band=(150, 850),
       proteins=["trứng gà", "thịt băm", "đậu phụ"], n_protein=(1, 2),
       vegs=["cà chua", "rau muống", "bắp cải", "cải ngọt"], n_veg=(1, 2),
       staples="basic"),
    _s("sinh_vien_meal_prep_cuoi_tuan", "Sinh viên nấu sẵn cuối tuần ăn cả tuần",
       "Món kho/rim để được lâu, nấu một lần nhiều phần.", STUDENT,
       equipment="one_burner", budget="tight", household=[3, 4],
       prefer_methods=["Kho"], avoid_methods=["Canh/Súp", "Trộn/Gỏi"], kcal_band=(150, 900),
       proteins=["ba chỉ", "thịt nạc", "trứng gà", "trứng cút", "cá basa", "đùi gà"], n_protein=(2, 3),
       vegs=["củ cải trắng", "cà rốt", "khoai tây", "đậu cô ve"], n_veg=(1, 2),
       staples="basic_plus"),
    _s("sinh_vien_bua_sang_truoc_gio_hoc", "Sinh viên bữa sáng trước giờ học",
       "Gọn, ít bước, đủ no đến trưa.", STUDENT,
       equipment="one_burner", budget="tight", household=[1],
       beginner=True, kcal_band=(150, 700),
       proteins=["trứng gà", "xúc xích", "giò lụa"], n_protein=(1, 2),
       vegs=["cà chua", "dưa chuột", "xà lách"], n_veg=(0, 2),
       starches=["bánh mì", "mì ăn liền"], n_starch=(1, 1), staples="basic"),
    _s("sinh_vien_tro_mua_nong", "Sinh viên ở trọ mùa nóng",
       "Canh mát, món nhẹ, ít dầu, không đứng bếp lâu.", STUDENT,
       equipment="one_burner", budget="tight", household=[1, 2],
       prefer_methods=["Canh/Súp", "Luộc", "Trộn/Gỏi"], avoid_methods=["Chiên/Rán", "Nướng"],
       kcal_band=(100, 650),
       proteins=["trứng gà", "đậu phụ", "thịt băm", "tôm"], n_protein=(1, 2),
       vegs=["mồng tơi", "bí đao", "mướp", "dưa chuột", "rau ngót"], n_veg=(1, 3),
       staples="basic_plus"),
    _s("sinh_vien_om_xa_nha", "Sinh viên ốm xa nhà",
       "Tự nấu món loãng, ấm, dễ ăn bằng đồ sẵn có.", STUDENT,
       equipment="one_burner", budget="tight", household=[1],
       prefer_methods=["Canh/Súp"], prefer_dish=["Canh"], avoid_methods=["Chiên/Rán", "Nướng"],
       health=["no_spicy"], kcal_band=(80, 600),
       proteins=["thịt băm", "trứng gà", "đậu phụ"], n_protein=(1, 1),
       vegs=["rau ngót", "bí đao", "cà rốt", "cải ngọt"], n_veg=(1, 2),
       staples="basic"),
    _s("sinh_vien_thuc_tap_mang_com", "Sinh viên thực tập mang cơm trưa",
       "Món mặn để hộp được, không chảy nước, hâm lại vẫn ngon.", STUDENT,
       equipment="one_burner", budget="tight", household=[1, 2],
       prefer_methods=["Kho", "Xào"], avoid_methods=["Canh/Súp", "Trộn/Gỏi"], kcal_band=(150, 900),
       proteins=["thịt nạc", "ba chỉ", "trứng gà", "đùi gà", "cá basa"], n_protein=(1, 2),
       vegs=["đậu cô ve", "bắp cải", "cà rốt", "su su", "súp lơ xanh"], n_veg=(1, 3),
       staples="basic_plus"),
    # ---------------------------------------------------------------- families
    _s("cuoi_thang_chua_luong", "Gia đình cuối tháng chưa có lương",
       "Không mua thêm gì đáng kể; tận dụng tối đa thứ đang có.", "gia_dinh",
       budget="tight", no_shopping=True, household=[2, 3, 4],
       proteins=["trứng gà", "đậu phụ", "thịt băm"], n_protein=(1, 2),
       vegs=["rau muống", "bắp cải", "giá đỗ", "bí đao"], n_veg=(1, 3)),
    _s("vet_tu_lanh_cuoi_tuan", "Vét tủ lạnh cuối tuần",
       "Ưu tiên tuyệt đối món tiêu thụ hết đồ sắp hỏng.", "gia_dinh",
       household=[2, 3, 4], rescue_weight=0.45,
       proteins=["thịt bò", "cá basa", "ba chỉ", "tôm", "đùi gà"], n_protein=(1, 3),
       vegs=["rau muống", "cà chua", "bắp cải", "cà rốt", "nấm rơm", "ớt chuông"], n_veg=(2, 4),
       urgent=(2, ["thịt bò", "cá basa", "tôm", "ba chỉ", "đùi gà"])),
    _s("com_gia_dinh_mien_bac", "Mâm cơm gia đình miền Bắc",
       "Cơm - canh - mặn - rau, vị thanh.", "gia_dinh",
       household=[3, 4, 5], prefer_dish=["Canh", "Món chính"],
       proteins=["sườn heo", "ba chỉ", "thịt gà ta", "cá chép", "đậu phụ", "thịt nạc"], n_protein=(1, 2),
       vegs=["rau muống", "rau ngót", "mồng tơi", "bí đao", "dưa cải chua", "cà chua", "su hào"], n_veg=(2, 4)),
    _s("com_gia_dinh_mien_trung", "Mâm cơm gia đình miền Trung",
       "Vị đậm, cay, nhiều món kho.", "gia_dinh",
       household=[3, 4, 5], prefer_methods=["Kho"],
       proteins=["cá nục", "cá thu", "ba chỉ", "tôm", "mực"], n_protein=(1, 2),
       vegs=["mướp đắng", "cà chua", "dưa cải chua", "bầu", "đậu bắp", "rau muống"], n_veg=(2, 3)),
    _s("com_gia_dinh_mien_nam", "Mâm cơm gia đình miền Nam",
       "Vị ngọt béo, canh chua, món kho nước dừa.", "gia_dinh",
       household=[3, 4, 5], prefer_methods=["Kho", "Canh/Súp"],
       proteins=["cá basa", "cá lóc", "ba chỉ", "trứng vịt", "tôm"], n_protein=(1, 2),
       vegs=["dọc mùng", "đậu bắp", "giá đỗ", "cà chua", "mướp đắng", "dứa"], n_veg=(2, 4)),
    _s("vo_chong_tre_moi_cuoi", "Vợ chồng trẻ mới cưới, đi làm cả ngày",
       "2 người, nấu tối sau giờ làm, ít rửa dọn.", "gia_dinh",
       household=[2], prefer_dish=["Món chính", "Canh"],
       proteins=["thịt bò", "ba chỉ", "tôm", "đùi gà", "cá hồi", "trứng gà"], n_protein=(1, 2),
       vegs=["cải ngọt", "súp lơ xanh", "cà chua", "nấm kim châm", "ớt chuông"], n_veg=(2, 3)),
    _s("gia_dinh_co_tre_nho", "Gia đình có con nhỏ đi mẫu giáo",
       "Món mềm, vị nhạt, không cay; cả nhà ăn chung được.", "gia_dinh",
       household=[3, 4], health=["no_spicy"], avoid_methods=["Nướng"],
       proteins=["thịt băm", "trứng gà", "tôm", "cá hồi", "ức gà"], n_protein=(1, 2),
       vegs=["cà rốt", "bí đỏ", "khoai tây", "súp lơ xanh", "ngô ngọt"], n_veg=(2, 3)),
    _s("nguoi_gia_song_mot_minh", "Người già sống một mình",
       "1 người, món mềm, ít dầu, khẩu phần nhỏ.", "gia_dinh",
       household=[1], prefer_methods=["Canh/Súp", "Hấp", "Kho"],
       avoid_methods=["Chiên/Rán", "Nướng"], kcal_band=(80, 600),
       proteins=["thịt băm", "cá basa", "đậu phụ", "trứng gà"], n_protein=(1, 1),
       vegs=["bí đao", "rau ngót", "cà rốt", "mồng tơi"], n_veg=(1, 2)),
    _s("dan_van_phong_mang_com", "Dân văn phòng nấu cơm mang đi làm",
       "Món để hộp được, hâm lại vẫn ngon; nấu tối hôm trước.", "lao_dong",
       household=[1, 2], prefer_methods=["Kho", "Xào"],
       avoid_methods=["Canh/Súp", "Trộn/Gỏi"],
       proteins=["thịt nạc", "ức gà", "thịt bò", "cá basa", "trứng gà"], n_protein=(1, 2),
       vegs=["đậu cô ve", "súp lơ xanh", "cà rốt", "bắp cải", "ớt chuông"], n_veg=(1, 3)),
    _s("dan_van_phong_eat_clean", "Dân văn phòng ăn eat-clean",
       "Nhiều đạm nạc, ít dầu mỡ, ít tinh bột tinh luyện.", "lao_dong",
       household=[1, 2], high_protein=True,
       avoid_methods=["Chiên/Rán"], kcal_band=(100, 550),
       proteins=["ức gà", "thịt bò", "trứng gà", "cá basa", "cá hồi"], n_protein=(1, 2),
       vegs=["súp lơ xanh", "cải thìa", "nấm kim châm", "cà rốt", "dưa chuột", "măng tây"], n_veg=(2, 4),
       starches=["khoai lang"], n_starch=(0, 1)),
    _s("cong_nhan_khu_cong_nghiep", "Công nhân khu công nghiệp ở trọ",
       "Ngân sách hẹp, bếp 1 ổ, cần no lâu để làm ca.", "lao_dong",
       equipment="one_burner", budget="tight", household=[1, 2, 3],
       kcal_band=(200, 950),
       proteins=["trứng gà", "ba chỉ", "đậu phụ", "cá nục", "thịt băm"], n_protein=(1, 2),
       vegs=["rau muống", "bắp cải", "cà chua", "bí đao", "su su"], n_veg=(1, 3),
       staples="basic_plus"),
    _s("cong_nhan_tang_ca_khuya", "Công nhân tăng ca về khuya",
       "Ăn khuya, một nồi/một chảo, no nhanh.", "lao_dong",
       equipment="one_burner", budget="tight", household=[1, 2],
       proteins=["trứng gà", "xúc xích", "thịt băm", "cá hộp"], n_protein=(1, 2),
       vegs=["cải ngọt", "giá đỗ", "cà chua"], n_veg=(1, 2),
       starches=["mì ăn liền", "gạo tẻ", "mì trứng"], n_starch=(1, 2), staples="basic_plus"),
    _s("tap_gym_tang_co", "Người đi làm tập gym tăng cơ",
       "Đạm cao, đủ tinh bột phức, hạn chế chiên ngập dầu.", "lao_dong",
       household=[1, 2], high_protein=True, avoid_methods=["Chiên/Rán"], kcal_band=(200, 950),
       proteins=["ức gà", "thịt bò", "trứng gà", "cá basa", "thăn bò"], n_protein=(2, 3),
       vegs=["súp lơ xanh", "cải thìa", "cà rốt", "nấm kim châm"], n_veg=(2, 3),
       starches=["gạo tẻ", "khoai lang"], n_starch=(1, 2)),
    # ---------------------------------------------------------------- health
    _s("an_chay_ram_mung_mot", "Ăn chay ngày rằm / mùng một",
       "TUYỆT ĐỐI không đạm động vật, không mắm cá.", "suc_khoe",
       diet="vegetarian", household=[2, 4],
       proteins=["đậu phụ", "đậu hũ chiên", "tàu hũ ky", "thịt chay", "chả lụa chay"], n_protein=(1, 2),
       vegs=["nấm rơm", "nấm hương", "cải thìa", "cà rốt", "mướp", "hạt sen", "măng tre", "nấm đùi gà"], n_veg=(3, 5),
       starches=["gạo tẻ", "miến dong"], n_starch=(1, 2), staples="vegetarian"),
    _s("me_bau", "Nhà có bà bầu",
       "Đủ đạm, rau; tránh món tái sống, gỏi, nhiều dầu mỡ.", "suc_khoe",
       household=[2, 3], avoid_methods=["Trộn/Gỏi", "Chiên/Rán"], prefer_dish=["Canh", "Món chính"],
       proteins=["cá hồi", "thịt nạc", "trứng gà", "tôm", "thịt bò"], n_protein=(1, 2),
       vegs=["rau ngót", "súp lơ xanh", "bí đỏ", "cà rốt", "cải ngọt"], n_veg=(2, 3)),
    _s("me_sau_sinh", "Mẹ sau sinh, ở cữ",
       "Lợi sữa, ít gia vị cay, tránh đồ tanh lạnh.", "suc_khoe",
       household=[2, 3], health=["no_spicy"], prefer_methods=["Canh/Súp", "Kho"],
       avoid_methods=["Trộn/Gỏi"],
       proteins=["thịt gà ta", "chân giò", "thịt nạc", "trứng gà"], n_protein=(1, 2),
       vegs=["rau ngót", "đu đủ xanh", "cà rốt", "hạt sen", "nấm hương"], n_veg=(2, 4),
       urgent=(1, ["chân giò", "thịt gà ta"])),
    _s("nguoi_om_cam_sot", "Người ốm, cảm sốt",
       "Món loãng, dễ nuốt, ấm; tránh dầu mỡ nặng bụng.", "suc_khoe",
       household=[1, 2, 3], prefer_methods=["Canh/Súp"], prefer_dish=["Canh"],
       avoid_methods=["Chiên/Rán", "Nướng"], kcal_band=(80, 550),
       proteins=["thịt băm", "trứng gà", "thịt gà ta"], n_protein=(1, 1),
       vegs=["rau ngót", "cà rốt", "bí đao", "nấm hương"], n_veg=(1, 3),
       starches=["gạo tẻ", "miến dong"], n_starch=(1, 2)),
    _s("nguoi_tieu_duong", "Người tiểu đường trong nhà",
       "Kiểm soát đường và tinh bột nhanh; ưu tiên chất xơ, đạm nạc.", "suc_khoe",
       health=["low_sugar"], kcal_band=(100, 600),
       proteins=["ức gà", "cá basa", "đậu phụ", "trứng gà", "thịt nạc"], n_protein=(1, 2),
       vegs=["mướp đắng", "súp lơ xanh", "cải thìa", "bắp cải", "nấm kim châm", "đậu bắp"], n_veg=(3, 5),
       n_starch=(0, 1)),
    _s("nguoi_cao_huyet_ap", "Người cao huyết áp trong nhà",
       "Giảm muối/mắm tối đa; tránh món kho mặn, dưa muối.", "suc_khoe",
       health=["low_sodium"], avoid_methods=["Kho", "Ngâm/Muối chua"],
       proteins=["cá basa", "ức gà", "đậu phụ", "thịt nạc"], n_protein=(1, 2),
       vegs=["bí đao", "bầu", "mồng tơi", "cà chua", "cà rốt", "su su"], n_veg=(2, 4)),
    _s("nguoi_benh_gout", "Người bệnh Gout (Acid Uric cao)",
       "Tuyệt đối kiêng thịt đỏ, hải sản vỏ cứng, nội tạng; ưu tiên trứng/sữa, rau củ.", "suc_khoe",
       health=["gout"], household=[2, 3],
       proteins=["trứng gà", "đậu phụ", "sữa tươi", "phô mai", "ức gà"], n_protein=(1, 2),
       vegs=["dưa chuột", "cà chua", "bí đao", "bầu", "cà rốt", "su su"], n_veg=(3, 4),
       starches=["gạo tẻ", "khoai tây", "khoai lang"], n_starch=(1, 2)),
    _s("nguoi_dau_da_day", "Người đau dạ dày / Trào ngược",
       "Món mềm lỏng, dễ tiêu; kiêng cay nóng, chua và chiên xào.", "suc_khoe",
       health=["gentle_stomach", "no_spicy"], household=[2, 3],
       prefer_methods=["Canh/Súp", "Hấp", "Luộc"], avoid_methods=["Xào", "Trộn/Gỏi"],
       proteins=["thịt băm", "ức gà", "cá basa", "trứng gà", "đậu phụ"], n_protein=(1, 2),
       vegs=["bí đao", "bầu", "cà rốt", "khoai tây", "mồng tơi"], n_veg=(2, 3),
       starches=["gạo tẻ", "miến dong", "khoai lang"], n_starch=(1, 2)),
    _s("nguoi_gia_rang_yeu", "Ông bà răng yếu",
       "Món mềm, hầm nhừ, dễ nhai; tránh đồ dai cứng.", "suc_khoe",
       household=[2, 3], prefer_methods=["Canh/Súp", "Hấp", "Kho"], avoid_methods=["Chiên/Rán", "Nướng"],
       proteins=["sườn heo", "thịt băm", "đậu phụ", "cá basa", "đậu phụ non"], n_protein=(1, 2),
       vegs=["bí đao", "cà rốt", "khoai tây", "hạt sen", "bí đỏ"], n_veg=(2, 4),
       starches=["gạo tẻ", "miến dong"], n_starch=(1, 2)),
    _s("tre_nho_bieng_an", "Trẻ nhỏ biếng ăn",
       "Vị nhạt, không cay, dễ ăn, bắt mắt.", "suc_khoe",
       household=[3, 4], health=["no_spicy"],
       proteins=["trứng gà", "thịt băm", "tôm", "phô mai", "trứng cút"], n_protein=(1, 2),
       vegs=["cà rốt", "bí đỏ", "súp lơ xanh", "khoai tây", "ngô ngọt"], n_veg=(2, 3),
       starches=["gạo tẻ", "nui", "bánh mì"], n_starch=(1, 2)),
    _s("an_kieng_keto_lowcarb", "Ăn kiêng Keto / Low-carb",
       "Cắt giảm tối đa tinh bột và đường; giàu đạm và chất béo.", "suc_khoe",
       health=["low_carb"], household=[1, 2], high_protein=True, kcal_band=(150, 850),
       proteins=["ba chỉ", "ức gà", "trứng gà", "thịt bò", "phô mai", "cá hồi"], n_protein=(2, 3),
       vegs=["súp lơ xanh", "rau muống", "dưa chuột", "cải thìa", "măng tây"], n_veg=(2, 4),
       starches=[], n_starch=(0, 0)),
    _s("bua_toi_giam_can_nhe_bung", "Bữa tối nhẹ bụng giữ dáng",
       "Ít calo, giàu chất xơ; hạn chế tinh bột trắng buổi tối.", "suc_khoe",
       household=[1, 2], avoid_methods=["Chiên/Rán"], kcal_band=(80, 450),
       proteins=["ức gà", "đậu phụ", "tôm", "trứng gà", "cá basa"], n_protein=(1, 2),
       vegs=["súp lơ xanh", "cải thìa", "dưa chuột", "cà chua", "nấm kim châm", "xà lách"], n_veg=(3, 4),
       starches=["khoai lang"], n_starch=(0, 1)),
    # ---------------------------------------------------------------- occasions
    _s("mua_bao_khong_di_cho", "Mưa bão, không ra chợ được",
       "Chỉ dùng đồ khô, đồ hộp, đồ trữ được; không mua thêm.", "dip_dac_biet",
       no_shopping=True,
       proteins=["cá hộp", "cá khô", "trứng gà", "xúc xích", "lạp xưởng", "tôm khô"], n_protein=(2, 3),
       vegs=["bắp cải", "cà rốt", "khoai tây", "bí đỏ"], n_veg=(1, 3),
       starches=["gạo tẻ", "mì ăn liền", "miến dong"], n_starch=(2, 3)),
    _s("nha_co_khach_bat_ngo", "Nhà có khách bất ngờ",
       "Thêm món nhanh từ đồ có sẵn để đãi khách.", "dip_dac_biet",
       household=[4, 5, 6], prefer_dish=["Món chính"],
       proteins=["thịt bò", "tôm", "ba chỉ", "trứng gà", "mực", "đùi gà"], n_protein=(2, 3),
       vegs=["cà chua", "hành tây", "ớt chuông", "dưa chuột", "súp lơ xanh"], n_veg=(2, 3)),
    _s("di_cho_cuoi_tuan_du_do", "Đi siêu thị cuối tuần, tủ lạnh đầy đồ",
       "Đồ tươi đầy đủ, nấu món ngon cho cả nhà.", "dip_dac_biet",
       budget="generous", household=[3, 4, 5],
       proteins=["sườn heo", "thịt bò", "cá hồi", "tôm", "thịt gà ta", "mực", "ba chỉ"], n_protein=(2, 4),
       vegs=["súp lơ xanh", "cà rốt", "nấm đùi gà", "cải thìa", "ngô ngọt", "khoai tây", "ớt chuông"], n_veg=(3, 5)),
    _s("nhau_cuoi_tuan_ban_be", "Nhậu cuối tuần với bạn",
       "Món nhắm, đậm đà, chia phần được cho nhiều người.", "dip_dac_biet",
       household=[4, 5, 6], prefer_dish=["Món khai vị / Gỏi", "Món chính"],
       prefer_methods=["Nướng", "Xào", "Trộn/Gỏi", "Chiên/Rán"],
       proteins=["mực", "ngao", "ba chỉ", "thịt gà ta", "mực khô", "tôm", "chân giò"], n_protein=(2, 3),
       vegs=["dưa chuột", "hoa chuối", "cà chua", "nấm rơm", "xà lách"], n_veg=(1, 3),
       starches=["bánh mì"], n_starch=(0, 1)),
    _s("ngay_gio_cung_gia_tien", "Ngày giỗ, cỗ cúng gia tiên",
       "Mâm cỗ truyền thống, nhiều món, khẩu phần lớn.", "dip_dac_biet",
       budget="generous", household=[6, 8, 10],
       proteins=["thịt gà ta", "giò lụa", "sườn heo", "tôm", "ba chỉ", "chân giò"], n_protein=(3, 4),
       vegs=["măng tre", "nấm hương", "cà rốt", "hạt sen", "bắp cải", "su hào"], n_veg=(3, 4),
       starches=["gạo tẻ", "gạo nếp", "miến dong"], n_starch=(2, 3)),
    _s("sau_tet_thua_do", "Sau Tết, thừa giò, lạp xưởng",
       "Phải xử lý đồ Tết còn tồn; ưu tiên món giải ngấy.", "dip_dac_biet",
       household=[3, 4, 5], rescue_weight=0.35,
       proteins=["giò lụa", "lạp xưởng", "ba chỉ", "trứng gà", "chân giò"], n_protein=(2, 3),
       vegs=["dưa cải chua", "bắp cải", "su hào", "hoa chuối", "cà rốt"], n_veg=(2, 3),
       urgent=(1, ["giò lụa", "chân giò"])),
    _s("tiec_sinh_nhat_tai_nha", "Tiệc sinh nhật, họp mặt tại nhà",
       "Món đãi tiệc, dễ chia phần, bắt mắt, đủ món mặn và món phụ.", "dip_dac_biet",
       budget="generous", household=[4, 5, 6],
       proteins=["sườn heo", "thịt gà ta", "tôm", "thịt bò", "mực", "cánh gà"], n_protein=(2, 3),
       vegs=["dưa chuột", "cà chua", "súp lơ xanh", "bắp cải", "nấm rơm", "ớt chuông"], n_veg=(2, 4)),
    _s("an_lau_cuoi_tuan", "Cuối tuần ăn lẩu gia đình",
       "Nước dùng thanh ngọt, nhiều rau nhúng, thịt bò/hải sản thái mỏng.", "dip_dac_biet",
       household=[4, 5, 6], prefer_methods=["Canh/Súp", "Khác"],
       proteins=["thịt bò", "tôm", "mực", "đậu phụ", "cá basa", "ngao"], n_protein=(2, 3),
       vegs=["rau muống", "cải thìa", "nấm kim châm", "bắp cải", "nấm rơm", "cải thảo"], n_veg=(3, 5),
       starches=["mì trứng", "bún tươi", "miến dong"], n_starch=(1, 2)),
    _s("thoi_tiet_nang_nong_mua_he", "Mùa hè oi bức, thanh nhiệt",
       "Canh thanh mát, dễ trôi cơm, hạn chế chiên nướng dầu mỡ.", "dip_dac_biet",
       household=[3, 4], prefer_methods=["Canh/Súp", "Luộc"], avoid_methods=["Chiên/Rán", "Nướng"],
       proteins=["cua đồng", "tôm", "thịt băm", "đậu phụ", "ngao"], n_protein=(1, 2),
       vegs=["mồng tơi", "mướp", "rau ngót", "bí đao", "bầu", "rau muống"], n_veg=(3, 4)),
    _s("mua_dong_troi_lanh", "Mùa đông miền Bắc / Trời lạnh",
       "Món kho đậm đà, hầm nóng, có gia vị ấm (gừng, tiêu, ớt).", "dip_dac_biet",
       household=[3, 4, 5], prefer_methods=["Kho", "Canh/Súp"], avoid_methods=["Trộn/Gỏi"],
       proteins=["ba chỉ", "sườn heo", "thịt bò", "cá chép", "cá nục", "bắp bò"], n_protein=(2, 3),
       vegs=["bắp cải", "cà rốt", "khoai tây", "nấm hương", "củ cải trắng"], n_veg=(2, 3)),
    _s("di_da_ngoai_picnic", "Đồ ăn mang đi dã ngoại / Picnic",
       "Món khô ráo, tiện đóng hộp mang đi, để được ở nhiệt độ thường.", "dip_dac_biet",
       household=[3, 4, 6], prefer_methods=["Chiên/Rán", "Nướng", "Kho"],
       avoid_methods=["Canh/Súp"],
       proteins=["đùi gà", "giò lụa", "ba chỉ", "trứng gà", "xúc xích", "cánh gà"], n_protein=(2, 3),
       vegs=["dưa chuột", "cà rốt", "xà lách"], n_veg=(1, 3),
       starches=["bánh mì", "gạo tẻ", "gạo nếp"], n_starch=(1, 2)),
]

SCENARIO_BY_KEY: dict[str, dict[str, Any]] = {s["key"]: s for s in SCENARIOS}

# Students get two slots per cycle so roughly a third of generated pantries are
# student kitchens while every other situation still appears.
SCHEDULE: list[str] = [s["key"] for s in SCENARIOS] + [
    s["key"] for s in SCENARIOS if s["group"] == STUDENT
]


def _scale(household: int) -> float:
    """Pool ranges are for two people; scale stock with household size."""
    return min(3.0, max(0.6, household / 2.0))


def _pick(pool: Pool, names: list[str], k: tuple[int, int], expiry: tuple[int, int],
          scale: float, rng: random.Random) -> list[dict[str, Any]]:
    if not names or k[1] <= 0:
        return []
    count = min(len(names), rng.randint(*k))
    out = []
    for key in rng.sample(names, count):
        name, code, (lo, hi) = pool[key]
        out.append(_make_item(name, code, rng.randint(lo, hi) * scale, rng.randint(*expiry)))
    return out


def _staples(kind: str, rng: random.Random) -> list[tuple[str, str, int]]:
    if kind == "vegetarian":
        chosen = list(VEGETARIAN_STAPLES)
        chosen += [s for s in STAPLES_EXTRA if s[0] in ("tiêu", "gừng", "sả", "ớt") and rng.random() < 0.6]
        return chosen
    chosen = list(STAPLES_BASIC)
    if kind == "basic":
        chosen += rng.sample(STAPLES_EXTRA, rng.randint(1, 3))
    elif kind == "basic_plus":
        chosen += rng.sample(STAPLES_EXTRA, rng.randint(3, 6))
    else:
        chosen += rng.sample(STAPLES_EXTRA, rng.randint(6, len(STAPLES_EXTRA)))
    return chosen


def generate_life_pantry(index: int) -> dict[str, Any]:
    """Deterministic pantry for `index`, cycling `SCHEDULE` so every scenario is
    balanced by construction (student scenarios twice per cycle)."""
    rng = random.Random(1_000_003 + index * 7919)
    scenario = SCENARIO_BY_KEY[SCHEDULE[index % len(SCHEDULE)]]
    household = rng.choice(scenario["household"])
    scale = _scale(household)

    items: list[dict[str, Any]] = []
    for name, code, grams in _staples(scenario["staples"], rng):
        items.append(_make_item(name, code, grams, rng.randint(240, 720), is_staple=True))

    items += _pick(PROTEIN, scenario["proteins"], scenario["n_protein"], (30, 120), scale, rng)
    items += _pick(VEG, scenario["vegs"], scenario["n_veg"], (30, 120), scale, rng)
    items += _pick(STARCH, scenario["starches"], scenario["n_starch"], (240, 720), scale, rng)

    urgent = scenario.get("urgent")
    if urgent:
        count, pool_names = urgent
        wanted = {PROTEIN[n][0] for n in pool_names if n in PROTEIN}
        flagged = 0
        for item in items:
            if flagged >= count:
                break
            if item["name"] in wanted:
                item["hours_to_expire"] = round(rng.uniform(4.0, 22.0), 1)
                flagged += 1
    elif rng.random() < 0.3:
        perishables = [i for i in items if not i["is_staple"] and i["hours_to_expire"] <= 120]
        if perishables:
            rng.choice(perishables)["hours_to_expire"] = round(rng.uniform(6.0, 23.0), 1)

    return {
        "pantry_id": f"life_{index:06d}",
        "scenario_type": scenario["key"],
        "scenario_label": scenario["label"],
        "scenario_group": scenario["group"],
        "constraint": scenario["constraint"],
        "items": items,
        "household_size": household,
    }
