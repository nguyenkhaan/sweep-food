"""Build the versioned FreshCheck knowledge-base artifact."""

from __future__ import annotations

import hashlib
import io
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypeAlias

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = REPO_ROOT / "build"
ARCHETYPES_DIR = REPO_ROOT / "archetypes"
INGREDIENTS_DIR = REPO_ROOT / "ingredients"
CLAIMS_DIR = REPO_ROOT / "claims"

KB_VERSION = "0.4.0"
CHECKSUM_EXCLUDED_KEYS = frozenset({"checksum", "generated_at"})
COMMIT_SHA_PATTERN = re.compile(r"[0-9a-f]{40}")

JsonRecord: TypeAlias = dict[str, Any]


@dataclass(frozen=True)
class KnowledgeBase:
    """The validated source records that form one FreshCheck release."""

    sources: list[JsonRecord]
    claims: list[JsonRecord]
    archetypes: dict[str, JsonRecord]
    ingredients: dict[str, JsonRecord]


def load_yaml(file_path: Path) -> object:
    if not file_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")
    yaml_data: object = yaml.safe_load(file_path.read_text(encoding="utf-8"))
    return yaml_data


def load_yaml_records(file_path: Path) -> list[JsonRecord]:
    yaml_data = load_yaml(file_path)
    if not isinstance(yaml_data, list) or not all(
        isinstance(item, dict) for item in yaml_data
    ):
        raise ValueError(f"{file_path} phải chứa danh sách record YAML")
    return [dict(item) for item in yaml_data]


def load_yaml_record(file_path: Path) -> JsonRecord:
    yaml_data = load_yaml(file_path)
    if not isinstance(yaml_data, dict):
        raise TypeError(f"{file_path} phải chứa một record YAML")
    return dict(yaml_data)


def load_knowledge_base() -> KnowledgeBase:
    sources = load_yaml_records(CLAIMS_DIR / "sources.yaml")
    claims = load_yaml_records(CLAIMS_DIR / "claims.yaml")

    archetypes: dict[str, JsonRecord] = {}
    for archetype_file in sorted(ARCHETYPES_DIR.glob("*.yaml")):
        archetype = load_yaml_record(archetype_file)
        archetype_id = archetype.get("archetype")
        if not isinstance(archetype_id, str):
            raise TypeError(f"{archetype_file} thiếu archetype hợp lệ")
        if archetype_id in archetypes:
            raise ValueError(f"Archetype trùng lặp: {archetype_id}")
        archetypes[archetype_id] = archetype

    ingredients: dict[str, JsonRecord] = {}
    for ingredient_file in sorted(INGREDIENTS_DIR.glob("*.yaml")):
        for ingredient in load_yaml_records(ingredient_file):
            ingredient_id = ingredient.get("id")
            if not isinstance(ingredient_id, str):
                raise TypeError(f"{ingredient_file} có nguyên liệu thiếu id hợp lệ")
            if ingredient_id in ingredients:
                raise ValueError(f"Nguyên liệu trùng lặp: {ingredient_id}")
            ingredients[ingredient_id] = ingredient

    return KnowledgeBase(sources, claims, archetypes, ingredients)


def validate_kb(knowledge_base: KnowledgeBase) -> None:
    """Validate the KB invariants required before a release artifact is emitted."""
    print("-> Bắt đầu kiểm định bất biến KB...")

    sources = knowledge_base.sources
    claims = knowledge_base.claims
    archetypes = knowledge_base.archetypes
    ingredients = knowledge_base.ingredients

    # 1. Kiểm tra nguồn (Sources)
    assert len(sources) > 0, "Danh sách sources rỗng"
    source_ids = {s["id"]: s for s in sources}

    # 2. Kiểm tra bằng chứng (Claims)
    assert len(claims) > 0, "Danh sách claims rỗng"
    claim_ids = {c["id"]: c for c in claims}

    for cid, c in claim_ids.items():
        assert c["source"] in source_ids, (
            f"Claim {cid} tham chiếu source không tồn tại: {c['source']}"
        )
        assert c.get("status") == "reviewed", f"Claim {cid} chưa có status: reviewed"

    # 3. Kiểm tra Archetypes
    assert len(archetypes) >= 8, (
        f"Yêu cầu tối thiểu 8 archetypes, hiện có {len(archetypes)}"
    )
    for arch_name, arch in archetypes.items():
        tiers = arch.get("sensory_tiers", {})
        assert len(tiers) == 4, f"{arch_name} thiếu tier (yêu cầu 4 tier)"

        # Tiers liền mạch trong [0.0, 10.0]
        ranges = []
        for tname, tinfo in tiers.items():
            lo, hi = tinfo["score_range"]
            assert 0.0 <= lo < hi <= 10.0, (
                f"Dải điểm không hợp lệ {arch_name} {tname}: {tinfo['score_range']}"
            )
            ranges.append((lo, hi))

        # Mỗi archetype phải có ít nhất 1 option hard_stop: true
        has_hard_stop = False
        rubric = arch.get("inspection_rubric", [])
        assert len(rubric) > 0, f"{arch_name} thiếu inspection_rubric"
        for axis in rubric:
            for opt in axis.get("options", []):
                if opt.get("hard_stop"):
                    has_hard_stop = True
                cid = opt.get("claim")
                if cid:
                    assert cid in claim_ids, (
                        f"Option {opt.get('value')} trong {arch_name} thiếu claim: {cid}"
                    )
        assert has_hard_stop, f"{arch_name} thiếu luật dừng (hard_stop: true)"

    # 4. Kiểm tra Ingredients
    assert len(ingredients) >= 30, (
        f"Yêu cầu tối thiểu 30-35 nguyên liệu P0, hiện có {len(ingredients)}"
    )
    for ing_id, ing in ingredients.items():
        ingredient_archetype = ing.get("archetype")
        assert ingredient_archetype in archetypes, (
            f"Nguyên liệu {ing_id} trỏ tới archetype không rõ: {ingredient_archetype}"
        )
        assert not ing.get("needs_review", False), (
            f"Nguyên liệu {ing_id} còn mang cờ needs_review"
        )

        shelf = ing.get("base_shelf_life_hours", {})
        assert len(shelf) > 0, f"Nguyên liệu {ing_id} thiếu base_shelf_life_hours"

        for env_name, env_data in shelf.items():
            cid = env_data.get("claim")
            assert cid in claim_ids, (
                f"Nguyên liệu {ing_id} [{env_name}] trỏ tới claim thiếu: {cid}"
            )
            assert claim_ids[cid]["status"] == "reviewed", (
                f"Claim {cid} chưa được reviewed"
            )
            assert env_data.get("value", 0) > 0, (
                f"Giá trị giờ phải dương: {ing_id} [{env_name}]"
            )

        # Bất biến nhiệt độ: fridge <= soft_freeze <= freezer
        if "fridge_2_4c" in shelf and "soft_freeze_-3c" in shelf:
            assert shelf["fridge_2_4c"]["value"] <= shelf["soft_freeze_-3c"]["value"], (
                f"Lỗi logic nhiệt độ ({ing_id}): fridge > soft_freeze"
            )
        if "soft_freeze_-3c" in shelf and "freezer_-18c" in shelf:
            assert (
                shelf["soft_freeze_-3c"]["value"] <= shelf["freezer_-18c"]["value"]
            ), f"Lỗi logic nhiệt độ ({ing_id}): soft_freeze > freezer"
        if "fridge_2_4c" in shelf and "freezer_-18c" in shelf:
            assert shelf["fridge_2_4c"]["value"] <= shelf["freezer_-18c"]["value"], (
                f"Lỗi logic nhiệt độ ({ing_id}): fridge > freezer"
            )

    print("-> Xác thực toàn bộ bất biến KB: ĐẠT 100% (Green).")


def get_source_commit() -> str:
    git_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    source_commit = git_result.stdout.strip()
    if git_result.returncode or not COMMIT_SHA_PATTERN.fullmatch(source_commit):
        raise RuntimeError("Không xác định được Git commit cho bản phát hành KB")
    return source_commit


def calculate_checksum(payload: JsonRecord) -> str:
    checksum_payload = {
        key: value
        for key, value in payload.items()
        if key not in CHECKSUM_EXCLUDED_KEYS
    }
    serialized_payload = json.dumps(
        checksum_payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(serialized_payload).hexdigest()}"


def build_payload(knowledge_base: KnowledgeBase, source_commit: str) -> JsonRecord:
    payload: JsonRecord = {
        "kb_version": KB_VERSION,
        "source_commit": source_commit,
        "generated_at": datetime.now(UTC).isoformat(),
        "stats": {
            "total_archetypes": len(knowledge_base.archetypes),
            "total_ingredients": len(knowledge_base.ingredients),
            "total_claims": len(knowledge_base.claims),
            "total_sources": len(knowledge_base.sources),
        },
        "sources": knowledge_base.sources,
        "claims": knowledge_base.claims,
        "archetypes": knowledge_base.archetypes,
        "ingredients": knowledge_base.ingredients,
    }
    payload["checksum"] = calculate_checksum(payload)
    return payload


def write_artifact(payload: JsonRecord) -> Path:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    artifact_path = BUILD_DIR / "freshcheck_kb.json"
    artifact_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return artifact_path


def build_kb() -> Path:
    print(f"=== Bắt đầu build FreshCheck KB (v{KB_VERSION}) ===")

    knowledge_base = load_knowledge_base()
    print(
        "Loaded "
        f"{len(knowledge_base.sources)} sources, "
        f"{len(knowledge_base.claims)} claims, "
        f"{len(knowledge_base.archetypes)} archetypes, and "
        f"{len(knowledge_base.ingredients)} ingredients."
    )

    validate_kb(knowledge_base)
    payload = build_payload(knowledge_base, get_source_commit())
    out_file = write_artifact(payload)

    size_kb = out_file.stat().st_size / 1024
    print(f"\n=> Xuất thành công artifact: {out_file} ({size_kb:.1f} KB)")
    print(f"   kb_version: {KB_VERSION}")
    print(f"   source_commit: {payload['source_commit']}")
    print(f"   checksum   : {payload['checksum']}")
    print(f"   Archetypes : {len(knowledge_base.archetypes)}")
    print(f"   Ingredients: {len(knowledge_base.ingredients)}")
    print(f"   Claims     : {len(knowledge_base.claims)}")
    print(f"   Sources    : {len(knowledge_base.sources)}")
    return out_file


if __name__ == "__main__":
    # Windows consoles default to a legacy code page that cannot print Vietnamese.
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    build_kb()
