"""Extended Vietnamese life-situation pantry generator (annotation only).

`pantry_simulator.generate_vietnamese_pantry` covers eight household archetypes.
That is too narrow to teach a ranker what "phù hợp" means across real Vietnamese
life: it has no sick day, no post-partum mother, no diabetic, no flood week, no
Tết leftovers, no night-shift worker.

This module adds twenty situations in a declarative table. It is kept separate
from `pantry_simulator` on purpose — that module's index->pantry mapping is
baked into the existing LTR split, and changing it would silently invalidate
every stored dataset.

Cooking time is deliberately absent. `estimated_cooking_minutes` is a platform
constant for a large share of the corpus, so a time constraint would ask the
annotator to judge against a fabricated number.

Each scenario carries a `constraint` string shown to the annotator — the
situation's real rule (low salt, soft texture, no animal protein, one pot only).
"""

from __future__ import annotations

import random
from typing import Any

from src.recommendation.pantry_simulator import STAPLE_POOL, _make_item

# name, master code, (min_g, max_g)
Pool = list[tuple[str, str, tuple[int, int]]]

PROTEIN: dict[str, tuple[str, str, tuple[int, int]]] = {
    "trứng gà": ("trứng gà", "9001", (100, 300)),
    "trứng vịt": ("trứng vịt", "9004", (150, 350)),
    "đậu phụ": ("đậu phụ", "3025", (150, 500)),
    "thịt băm": ("thịt băm", "7028", (120, 300)),
    "ba chỉ": ("ba chỉ", "7028", (250, 600)),
    "sườn heo": ("sườn heo", "7053", (300, 700)),
    "thịt gà ta": ("thịt gà ta", "7013", (400, 1000)),
    "ức gà": ("ức gà", "7089", (250, 600)),
    "thịt bò": ("thịt bò", "7001", (150, 450)),
    "cá chép": ("cá chép", "8016", (300, 800)),
    "cá basa": ("cá basa", "8092", (250, 600)),
    "cá thu": ("cá thu", "8026", (250, 500)),
    "cá nục": ("cá nục", "8021", (250, 500)),
    "tôm": ("tôm", "8051", (150, 450)),
    "mực": ("mực", "8040", (200, 400)),
    "ngao": ("ngao", "8066", (300, 700)),
    "cua đồng": ("cua đồng", "8034", (200, 500)),
    "giò lụa": ("giò lụa", "7069", (150, 350)),
    "lạp xưởng": ("lạp xưởng", "20075", (100, 250)),
    "xúc xích": ("xúc xích", "7077", (100, 250)),
    "cá khô": ("cá khô", "8012", (80, 200)),
    "mực khô": ("mực khô", "8039", (60, 150)),
    "gan lợn": ("gan lợn", "7041", (150, 300)),
    "thịt gà hộp": ("thịt gà hộp", "11018", (150, 300)),
    "cá thu hộp": ("cá thu hộp", "11015", (150, 300)),
    "sữa chua": ("sữa chua không đường", "10036", (200, 400)),
    "phô mai": ("phô mai", "10009", (80, 200)),
}

VEG: dict[str, tuple[str, str, tuple[int, int]]] = {
    "rau muống": ("rau muống", "4083", (150, 450)),
    "rau ngót": ("rau ngót", "4086", (120, 300)),
    "mồng tơi": ("mồng tơi", "4080", (150, 350)),
    "cải thìa": ("cải thìa", "4015", (150, 400)),
    "bắp cải": ("bắp cải", "4010", (200, 600)),
    "súp lơ xanh": ("súp lơ xanh", "4100", (150, 400)),
    "cà chua": ("cà chua", "4005", (100, 350)),
    "cà rốt": ("cà rốt", "4007", (100, 300)),
    "khoai tây": ("khoai tây", "2014", (200, 600)),
    "khoai lang": ("khoai lang", "2008", (200, 600)),
    "bí xanh": ("bí xanh", "4002", (250, 700)),
    "bầu": ("bầu", "4001", (250, 600)),
    "mướp": ("mướp", "4054", (200, 450)),
    "mướp đắng": ("mướp đắng", "4055", (200, 450)),
    "dưa chuột": ("dưa chuột", "4027", (100, 300)),
    "giá đỗ": ("giá đỗ", "4036", (100, 300)),
    "đậu bắp": ("đậu bắp", "4032", (100, 250)),
    "dọc mùng": ("dọc mùng", "4026", (150, 300)),
    "nấm rơm": ("nấm rơm", "4129", (120, 300)),
    "nấm hương": ("nấm hương", "4127", (80, 200)),
    "nấm kim châm": ("nấm kim châm", "4133", (100, 250)),
    "măng tre": ("măng tre", "4053", (200, 450)),
    "dưa cải chua": ("dưa cải chua", "4116", (150, 350)),
    "hoa chuối": ("hoa chuối", "4043", (150, 350)),
    "hạt sen": ("hạt sen", "4040", (100, 250)),
    "đu đủ xanh": ("đu đủ xanh", "4033", (200, 450)),
    "chuối xanh": ("chuối xanh", "4019", (200, 400)),
}

STARCH: dict[str, tuple[str, str, tuple[int, int]]] = {
    "gạo tẻ": ("gạo tẻ", "1004", (500, 2000)),
    "bún tươi": ("bún tươi", "1020", (300, 700)),
    "bánh phở": ("bánh phở", "1013", (300, 700)),
    "miến dong": ("miến dong", "2015", (100, 250)),
    "mì trứng": ("mì trứng", "20087", (150, 400)),
    "bánh mì": ("bánh mì", "1012", (100, 300)),
    "đậu xanh": ("đậu xanh", "3010", (150, 400)),
    "đậu đen": ("đậu đen", "3004", (150, 400)),
    "lạc": ("lạc hạt", "3017", (100, 250)),
    "bột gạo": ("bột gạo", "1017", (200, 500)),
    "khoai lang": ("khoai lang", "2008", (300, 800)),
    "khoai tây": ("khoai tây", "2014", (300, 800)),
}

FRUIT: dict[str, tuple[str, str, tuple[int, int]]] = {
    "chuối chín": ("chuối tiêu", "5007", (200, 500)),
    "đu đủ chín": ("đu đủ chín", "5017", (300, 700)),
    "dưa hấu": ("dưa hấu", "5011", (400, 1200)),
    "táo đỏ": ("táo đỏ khô", "20012", (50, 150)),
}


def _pick(pool: dict[str, tuple[str, str, tuple[int, int]]], names: list[str],
          k: tuple[int, int], expiry: tuple[int, int], rng: random.Random) -> list[dict[str, Any]]:
    chosen = rng.sample(names, min(len(names), rng.randint(*k)))
    out = []
    for key in chosen:
        name, code, (lo, hi) = pool[key]
        out.append(_make_item(name, code, rng.randint(lo, hi), rng.randint(*expiry)))
    return out


# Twenty situations. `urgent` = (how many items get a <=24h clock, pool to draw
# them from). `constraint` is the rule the annotator grades against.
SCENARIOS: list[dict[str, Any]] = [
    {
        "key": "sinh_vien_o_tro", "label": "Sinh viên ở trọ, bếp từ 1 ổ, ngân sách hẹp",
        "constraint": "Nấu ít dụng cụ, rẻ, 1-2 người ăn.",
        "household": [1, 2], "proteins": ["trứng gà", "đậu phụ", "thịt băm"], "n_protein": (1, 2),
        "vegs": ["rau muống", "cà chua", "bắp cải", "giá đỗ", "dưa chuột"], "n_veg": (1, 3),
        "starches": ["gạo tẻ", "mì trứng"], "n_starch": (0, 1),
    },
    {
        "key": "cuoi_thang_chua_luong", "label": "Cuối tháng chưa có lương",
        "constraint": "Không mua thêm gì đáng kể; tận dụng tối đa thứ đang có.",
        "household": [1, 2], "proteins": ["trứng gà", "đậu phụ"], "n_protein": (1, 2),
        "vegs": ["rau muống", "bắp cải", "giá đỗ"], "n_veg": (1, 2),
        "starches": ["gạo tẻ"], "n_starch": (1, 1),
    },
    {
        "key": "vet_tu_lanh_cuoi_tuan", "label": "Vét tủ lạnh cuối tuần",
        "constraint": "Ưu tiên tuyệt đối món tiêu thụ hết đồ sắp hỏng.",
        "household": [2, 3, 4], "proteins": ["thịt bò", "cá basa", "ba chỉ", "tôm"], "n_protein": (1, 2),
        "vegs": ["rau muống", "cà chua", "bắp cải", "cà rốt", "nấm rơm"], "n_veg": (2, 4),
        "starches": ["gạo tẻ"], "n_starch": (1, 1),
        "urgent": (2, ["thịt bò", "cá basa", "tôm"]),
    },
    {
        "key": "com_gia_dinh_mien_bac", "label": "Mâm cơm gia đình miền Bắc",
        "constraint": "Cơm - canh - mặn - rau, vị thanh.",
        "household": [3, 4, 5], "proteins": ["sườn heo", "ba chỉ", "thịt gà ta", "cá chép", "đậu phụ"],
        "n_protein": (1, 2),
        "vegs": ["rau muống", "rau ngót", "mồng tơi", "bí xanh", "dưa cải chua", "cà chua"], "n_veg": (2, 4),
        "starches": ["gạo tẻ"], "n_starch": (1, 1),
    },
    {
        "key": "com_gia_dinh_mien_trung", "label": "Mâm cơm gia đình miền Trung",
        "constraint": "Vị đậm, cay, nhiều món kho.",
        "household": [3, 4, 5], "proteins": ["cá nục", "cá thu", "ba chỉ", "tôm"], "n_protein": (1, 2),
        "vegs": ["mướp đắng", "cà chua", "dưa cải chua", "bầu", "đậu bắp"], "n_veg": (2, 3),
        "starches": ["gạo tẻ"], "n_starch": (1, 1),
    },
    {
        "key": "com_gia_dinh_mien_nam", "label": "Mâm cơm gia đình miền Nam",
        "constraint": "Vị ngọt béo, canh chua, món kho nước dừa.",
        "household": [3, 4, 5], "proteins": ["cá basa", "ba chỉ", "trứng vịt", "tôm"], "n_protein": (1, 2),
        "vegs": ["dọc mùng", "đậu bắp", "giá đỗ", "cà chua", "mướp đắng"], "n_veg": (2, 4),
        "starches": ["gạo tẻ"], "n_starch": (1, 1),
    },
    {
        "key": "dan_van_phong_eat_clean", "label": "Dân văn phòng ăn eat-clean",
        "constraint": "Nhiều đạm nạc, ít dầu mỡ, ít tinh bột tinh luyện.",
        "household": [1, 2], "proteins": ["ức gà", "thịt bò", "trứng gà", "cá basa"], "n_protein": (1, 2),
        "vegs": ["súp lơ xanh", "cải thìa", "nấm kim châm", "cà rốt", "dưa chuột"], "n_veg": (2, 4),
        "starches": ["khoai lang"], "n_starch": (0, 1),
    },
    {
        "key": "an_chay_ram_mung_mot", "label": "Ăn chay ngày rằm / mùng một",
        "constraint": "TUYỆT ĐỐI không đạm động vật, không mắm cá.",
        "household": [2, 4], "proteins": ["đậu phụ"], "n_protein": (1, 1),
        "vegs": ["nấm rơm", "nấm hương", "cải thìa", "cà rốt", "mướp", "hạt sen", "măng tre"], "n_veg": (3, 5),
        "starches": ["gạo tẻ", "miến dong", "đậu xanh"], "n_starch": (1, 2),
    },
    {
        "key": "me_sau_sinh", "label": "Mẹ sau sinh, ở cữ",
        "constraint": "Lợi sữa, ít gia vị cay, tránh đồ tanh lạnh.",
        "household": [2, 3], "proteins": ["thịt gà ta", "sườn heo", "thịt băm", "trứng gà"], "n_protein": (1, 2),
        "vegs": ["rau ngót", "đu đủ xanh", "cà rốt", "hạt sen", "nấm hương"], "n_veg": (2, 4),
        "starches": ["gạo tẻ", "đậu đen"], "n_starch": (1, 2),
    },
    {
        "key": "nguoi_om_cam_sot", "label": "Người ốm, cảm sốt",
        "constraint": "Món loãng, dễ nuốt, ấm; tránh dầu mỡ nặng bụng.",
        "household": [1, 2], "proteins": ["thịt băm", "trứng gà", "thịt gà ta"], "n_protein": (1, 1),
        "vegs": ["rau ngót", "cà rốt", "bí xanh", "nấm hương"], "n_veg": (1, 3),
        "starches": ["gạo tẻ", "miến dong"], "n_starch": (1, 2),
    },
    {
        "key": "nguoi_tieu_duong", "label": "Người tiểu đường trong nhà",
        "constraint": "Kiểm soát đường và tinh bột nhanh; ưu tiên chất xơ, đạm nạc.",
        "household": [2, 3, 4], "proteins": ["ức gà", "cá basa", "đậu phụ", "trứng gà"], "n_protein": (1, 2),
        "vegs": ["mướp đắng", "súp lơ xanh", "cải thìa", "bắp cải", "nấm kim châm", "đậu bắp"], "n_veg": (3, 5),
        "starches": ["gạo tẻ", "đậu đen"], "n_starch": (0, 1),
    },
    {
        "key": "nguoi_cao_huyet_ap", "label": "Người cao huyết áp trong nhà",
        "constraint": "Giảm muối/mắm tối đa; tránh món kho mặn, dưa muối.",
        "household": [2, 3, 4], "proteins": ["cá basa", "ức gà", "đậu phụ"], "n_protein": (1, 2),
        "vegs": ["bí xanh", "bầu", "mồng tơi", "cà chua", "cà rốt"], "n_veg": (2, 4),
        "starches": ["gạo tẻ"], "n_starch": (1, 1),
    },
    {
        "key": "nguoi_gia_rang_yeu", "label": "Ông bà răng yếu",
        "constraint": "Món mềm, hầm nhừ, dễ nhai; tránh đồ dai cứng.",
        "household": [2, 3], "proteins": ["sườn heo", "thịt băm", "đậu phụ", "cá basa"], "n_protein": (1, 2),
        "vegs": ["bí xanh", "cà rốt", "khoai tây", "hạt sen", "nấm hương"], "n_veg": (2, 4),
        "starches": ["gạo tẻ", "miến dong"], "n_starch": (1, 2),
    },
    {
        "key": "tre_nho_bieng_an", "label": "Trẻ nhỏ biếng ăn",
        "constraint": "Vị nhạt, không cay, dễ ăn, bắt mắt.",
        "household": [3, 4], "proteins": ["trứng gà", "thịt băm", "tôm", "phô mai"], "n_protein": (1, 2),
        "vegs": ["cà rốt", "bí xanh", "súp lơ xanh", "khoai tây"], "n_veg": (2, 3),
        "starches": ["gạo tẻ", "mì trứng", "bánh mì"], "n_starch": (1, 2),
    },
    {
        "key": "mua_bao_khong_di_cho", "label": "Mưa bão, không ra chợ được",
        "constraint": "Chỉ dùng đồ khô / đồ hộp / đồ trữ được; không giả định mua thêm.",
        "household": [2, 3, 4], "proteins": ["cá thu hộp", "thịt gà hộp", "cá khô", "trứng gà", "xúc xích"],
        "n_protein": (2, 3),
        "vegs": ["bắp cải", "cà rốt", "khoai tây", "măng tre"], "n_veg": (1, 3),
        "starches": ["gạo tẻ", "mì trứng", "miến dong"], "n_starch": (2, 3),
    },
    {
        "key": "nhau_cuoi_tuan_ban_be", "label": "Nhậu cuối tuần với bạn",
        "constraint": "Món nhắm, đậm đà, chia phần được cho nhiều người.",
        "household": [4, 5, 6], "proteins": ["mực", "ngao", "ba chỉ", "thịt gà ta", "mực khô", "tôm"],
        "n_protein": (2, 3),
        "vegs": ["dưa chuột", "hoa chuối", "cà chua", "nấm rơm"], "n_veg": (1, 3),
        "starches": ["lạc", "bánh mì"], "n_starch": (1, 2),
    },
    {
        "key": "ngay_gio_cung_gia_tien", "label": "Ngày giỗ, cỗ cúng gia tiên",
        "constraint": "Mâm cỗ truyền thống, nhiều món, khẩu phần lớn.",
        "household": [6, 8, 10], "proteins": ["thịt gà ta", "giò lụa", "sườn heo", "tôm", "ba chỉ"],
        "n_protein": (3, 4),
        "vegs": ["măng tre", "nấm hương", "cà rốt", "hạt sen", "bắp cải"], "n_veg": (3, 4),
        "starches": ["gạo tẻ", "miến dong", "đậu xanh"], "n_starch": (2, 3),
    },
    {
        "key": "sau_tet_thua_do", "label": "Sau Tết, thừa bánh chưng và giò",
        "constraint": "Phải xử lý đồ Tết còn tồn; ưu tiên món giải ngấy.",
        "household": [3, 4, 5], "proteins": ["giò lụa", "lạp xưởng", "ba chỉ", "trứng gà"], "n_protein": (2, 3),
        "vegs": ["dưa cải chua", "bắp cải", "su hào" if False else "cà rốt", "hoa chuối"], "n_veg": (2, 3),
        "starches": ["gạo tẻ", "bột gạo"], "n_starch": (1, 2),
        "urgent": (1, ["giò lụa", "lạp xưởng"]),
    },
    {
        "key": "cong_nhan_tang_ca_khuya", "label": "Công nhân tăng ca về khuya",
        "constraint": "Ăn khuya, một nồi/một chảo, no nhanh.",
        "household": [1, 2], "proteins": ["trứng gà", "xúc xích", "thịt băm", "cá thu hộp"], "n_protein": (1, 2),
        "vegs": ["cải thìa", "giá đỗ", "cà chua"], "n_veg": (1, 2),
        "starches": ["mì trứng", "gạo tẻ", "bánh phở"], "n_starch": (1, 2),
    },
    {
        "key": "tap_gym_tang_co", "label": "Tập gym tăng cơ",
        "constraint": "Đạm cao, đủ tinh bột phức, hạn chế chiên ngập dầu.",
        "household": [1, 2], "proteins": ["ức gà", "thịt bò", "trứng gà", "cá basa", "sữa chua"],
        "n_protein": (2, 3),
        "vegs": ["súp lơ xanh", "cải thìa", "cà rốt", "nấm kim châm"], "n_veg": (2, 3),
        "starches": ["gạo tẻ", "khoai lang"], "n_starch": (1, 2),
    },
    {
        "key": "tiec_sinh_nhat_tai_nha", "label": "Tiệc sinh nhật, họp mặt tại nhà",
        "constraint": "Món ngon đãi tiệc, dễ chia phần, màu sắc bắt mắt, đủ món mặn và món phụ.",
        "household": [4, 5, 6], "proteins": ["sườn heo", "thịt gà ta", "tôm", "thịt bò", "mực"], "n_protein": (2, 3),
        "vegs": ["dưa chuột", "cà chua", "súp lơ xanh", "bắp cải", "nấm rơm"], "n_veg": (2, 4),
        "starches": ["khoai tây", "bánh mì", "mì trứng"], "n_starch": (1, 2),
    },
    {
        "key": "an_lau_cuoi_tuan", "label": "Cuối tuần ăn lẩu gia đình",
        "constraint": "Nước dùng thanh ngọt, nhiều rau nhúng, thịt bò/hải sản thái mỏng.",
        "household": [4, 5, 6], "proteins": ["thịt bò", "tôm", "mực", "đậu phụ", "cá basa"], "n_protein": (2, 3),
        "vegs": ["rau muống", "cải thìa", "nấm kim châm", "bắp cải", "nấm rơm"], "n_veg": (3, 5),
        "starches": ["mì trứng", "bún tươi", "miến dong"], "n_starch": (1, 2),
    },
    {
        "key": "an_kieng_keto_lowcarb", "label": "Ăn kiêng Keto / Low-carb",
        "constraint": "Cắt giảm tối đa tinh bột và đường; giàu đạm nạc và chất béo lành mạnh.",
        "household": [1, 2], "proteins": ["ba chỉ", "ức gà", "trứng gà", "thịt bò", "phô mai"], "n_protein": (2, 3),
        "vegs": ["súp lơ xanh", "rau muống", "dưa chuột", "cải thìa", "măng tre"], "n_veg": (2, 4),
        "starches": ["lạc"], "n_starch": (0, 1),
    },
    {
        "key": "bua_sang_nhanh_gon", "label": "Bữa sáng nhanh gọn dưới 15 phút",
        "constraint": "Nấu nhanh, ít dầu mỡ, gọn gàng, đủ năng lượng đi làm/đi học.",
        "household": [1, 2, 3], "proteins": ["trứng gà", "xúc xích", "thịt băm", "giò lụa"], "n_protein": (1, 2),
        "vegs": ["dưa chuột", "cà chua", "giá đỗ"], "n_veg": (1, 2),
        "starches": ["bánh mì", "bánh phở", "mì trứng"], "n_starch": (1, 2),
    },
    {
        "key": "thoi_tiet_nang_nong_mua_he", "label": "Mùa hè oi bức, thanh nhiệt",
        "constraint": "Canh thanh mát, giải nhiệt, dễ trôi cơm, hạn chế món chiên nướng dầu mỡ.",
        "household": [3, 4], "proteins": ["cua đồng", "tôm", "thịt băm", "đậu phụ", "ngao"], "n_protein": (1, 2),
        "vegs": ["mồng tơi", "mướp", "rau ngót", "bí xanh", "bầu"], "n_veg": (3, 4),
        "starches": ["gạo tẻ"], "n_starch": (1, 1),
    },
    {
        "key": "mua_dong_troi_lanh", "label": "Mùa đông miền Bắc / Trời lạnh",
        "constraint": "Món kho đậm đà, hầm nóng hổi, có gia vị ấm nóng (gừng, tiêu, ớt).",
        "household": [3, 4, 5], "proteins": ["ba chỉ", "sườn heo", "thịt bò", "cá chép", "cá nục"], "n_protein": (2, 3),
        "vegs": ["bắp cải", "cà rốt", "khoai tây", "nấm hương"], "n_veg": (2, 3),
        "starches": ["gạo tẻ", "khoai lang"], "n_starch": (1, 2),
    },
    {
        "key": "di_da_ngoai_picnic", "label": "Đồ ăn mang đi dã ngoại / Picnic",
        "constraint": "Món khô ráo, tiện đóng hộp mang đi, giữ được lâu ở nhiệt độ thường.",
        "household": [3, 4, 6], "proteins": ["thịt gà ta", "giò lụa", "ba chỉ", "trứng gà", "xúc xích"], "n_protein": (2, 3),
        "vegs": ["dưa chuột", "cà rốt", "bắp cải"], "n_veg": (2, 3),
        "starches": ["bánh mì", "gạo tẻ", "khoai lang"], "n_starch": (1, 2),
    },
    {
        "key": "nguoi_benh_gout", "label": "Người bệnh Gout (Acid Uric cao)",
        "constraint": "Tuyệt đối kiêng thịt đỏ, hải sản vỏ cứng, nội tạng; ưu tiên đạm trứng/sữa và rau củ.",
        "household": [2, 3], "proteins": ["trứng gà", "đậu phụ", "ức gà", "phô mai"], "n_protein": (1, 2),
        "vegs": ["dưa chuột", "cà chua", "bí xanh", "bầu", "cà rốt"], "n_veg": (3, 4),
        "starches": ["gạo tẻ", "khoai tây", "khoai lang"], "n_starch": (1, 2),
    },
    {
        "key": "nguoi_dau_da_day", "label": "Người đau dạ dày / Trào ngược",
        "constraint": "Món mềm lỏng, dễ tiêu hóa; kiêng cay nóng (tiêu/ớt), chua (chanh/giấm) và chiên xào.",
        "household": [2, 3], "proteins": ["thịt băm", "ức gà", "cá basa", "trứng gà", "đậu phụ"], "n_protein": (1, 2),
        "vegs": ["bí xanh", "bầu", "cà rốt", "khoai tây", "mồng tơi"], "n_veg": (2, 3),
        "starches": ["gạo tẻ", "miến dong", "khoai lang"], "n_starch": (1, 2),
    },
    {
        "key": "bua_toi_giam_can_nhe_bung", "label": "Bữa tối nhẹ bụng giữ dáng",
        "constraint": "Ít calo, giàu chất xơ, không gây đầy bụng khó ngủ; hạn chế tinh bột trắng buổi tối.",
        "household": [1, 2], "proteins": ["ức gà", "đậu phụ", "tôm", "trứng gà", "cá basa"], "n_protein": (1, 2),
        "vegs": ["súp lơ xanh", "cải thìa", "dưa chuột", "cà chua", "nấm kim châm"], "n_veg": (3, 4),
        "starches": ["khoai lang", "đậu đen"], "n_starch": (0, 1),
    },
]

SCENARIO_BY_KEY = {s["key"]: s for s in SCENARIOS}


def generate_life_pantry(index: int) -> dict[str, Any]:
    """Deterministic for a given index. Scenarios are cycled, not sampled, so a
    2,000-pair task file is balanced across all twenty situations by construction."""
    rng = random.Random(1_000_003 + index * 7919)
    scenario = SCENARIOS[index % len(SCENARIOS)]

    items: list[dict[str, Any]] = []
    # Core kitchen essentials present in every Vietnamese home
    core_staples = [
        ("muối", "13005", 300),
        ("đường", "12014", 400),
        ("dầu ăn", "6002", 500),
        ("tiêu", "13004", 50),
        ("hạt nêm", "13026", 250),
        ("hành tím", "4037", 100),
        ("ớt", "4061", 30),
    ]
    if scenario["key"] == "an_chay_ram_mung_mot":
        core_staples.append(("nước tương", "13022", 300))
    else:
        core_staples.append(("nước mắm", "13014", 500))

    for name, code, grams in core_staples:
        items.append(_make_item(name, code, grams, rng.randint(240, 720), is_staple=True))

    # Additional fresh aromatics / secondary staples (tỏi, hành lá, nước tương...)
    aromatics = [
        ("tỏi", "4103", 100),
        ("hành lá", "4038", 50),
        ("nước tương", "13022", 300),
    ]
    num_aromatics = rng.randint(1, len(aromatics))
    for name, code, grams in rng.sample(aromatics, num_aromatics):
        items.append(_make_item(name, code, grams, rng.randint(240, 720), is_staple=True))

    items += _pick(PROTEIN, scenario["proteins"], scenario["n_protein"], (36, 120), rng)
    items += _pick(VEG, scenario["vegs"], scenario["n_veg"], (36, 120), rng)
    if scenario.get("starches"):
        lo, hi = scenario["n_starch"]
        if hi > 0:
            items += _pick(STARCH, scenario["starches"], (lo, hi), (240, 720), rng)
    if rng.random() < 0.25:
        items += _pick(FRUIT, list(FRUIT), (1, 1), (48, 168), rng)

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
        perishables = [i for i in items if not i["is_staple"]]
        if perishables:
            rng.choice(perishables)["hours_to_expire"] = round(rng.uniform(6.0, 23.0), 1)

    return {
        "pantry_id": f"life_{index:06d}",
        "scenario_type": scenario["key"],
        "scenario_label": scenario["label"],
        "constraint": scenario["constraint"],
        "items": items,
        "household_size": rng.choice(scenario["household"]),
    }
