"""PantryParser facade orchestrating 4-tier culinary extraction and resolution."""

from __future__ import annotations

import asyncio
import concurrent.futures
import json
import logging
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from AI.llm.openai_client import OpenAIClient
from AI.smart_parser.enrichment import PantryEnricher
from AI.smart_parser.llm_tier import LLMExtractor
from AI.smart_parser.matching import PantryMatcher, count_master_usage
from AI.smart_parser.normalization import (
    detect_storage_mode,
    parse_quantity_and_clean_name,
)

logger = logging.getLogger(__name__)

DEFAULT_FRESH_KB_PATH = Path(__file__).resolve().parent / "data" / "freshcheck_kb.json"

_PARSER_INSTANCE: PantryParser | None = None


def _load_fresh_kb(path: Path | None = None) -> dict[str, Any]:
    kb_path = path or DEFAULT_FRESH_KB_PATH
    if kb_path.exists():
        try:
            with kb_path.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            logger.warning("Failed loading freshcheck_kb (%s)", type(exc).__name__)
    return {}


class PantryParser:
    """Unified 4-tier culinary parser for manual text, supermarket OCR, and voice speech."""

    def __init__(
        self,
        *,
        master_alias_index: (
            Mapping[str, tuple[str, ...] | list[str] | set[str]] | None
        ) = None,
        master_by_code: Mapping[str, dict[str, Any]] | None = None,
        fresh_kb: dict[str, Any] | None = None,
        openai_client: OpenAIClient | None = None,
        master_usage: Mapping[str, int] | None = None,
    ) -> None:
        self.fresh_kb = fresh_kb if fresh_kb is not None else _load_fresh_kb()
        self.matcher = PantryMatcher(
            master_alias_index=master_alias_index,
            master_by_code=master_by_code,
            fresh_kb=self.fresh_kb,
            master_usage=master_usage,
        )
        self.enricher = PantryEnricher(self.matcher, fresh_kb=self.fresh_kb)
        self.llm_extractor = LLMExtractor(openai_client=openai_client)

    def resolve_master_ingredient(self, query: str) -> dict[str, Any] | None:
        """Resolve ingredient name to master catalog details (Tier 1 & Tier 2)."""
        return self.matcher.resolve_master_ingredient(query)

    def enrich_item(self, raw_item: dict[str, Any]) -> dict[str, Any]:
        """Enrich extracted entity with master metadata and FreshCheck guidelines (Tier 4)."""
        return self.enricher.enrich_item(raw_item)

    async def aparse_input_to_pantry(
        self, input_text: str, prefer_llm: bool = True
    ) -> list[dict[str, Any]]:
        """Asynchronously parse raw input text into standardized pantry items."""
        if not input_text or not input_text.strip():
            return []

        text = input_text.strip()
        parsed_raw_items: list[dict[str, Any]] = []

        is_complex = len(text.splitlines()) > 1 or len(text.split()) > 4 or any(
            k in text.lower()
            for k in [
                "hôm nay",
                "đi chợ",
                "mua",
                "tủ lạnh",
                "ngăn mát",
                "ngăn đá",
                "khay",
                "kg",
                "lạng",
                "cân",
                "với",
                "và",
            ]
        )

        if prefer_llm and is_complex:
            parsed_raw_items = await self.llm_extractor.aextract_items(text)

        # Fallback to local heuristic regex parsing if LLM is skipped, timed out, or returned empty
        if not parsed_raw_items:
            parsed_raw_items = self._fallback_parse_text(text)

        # Enrich all extracted items through Tier 4
        enriched: list[dict[str, Any]] = []
        for it in parsed_raw_items:
            if it.get("name"):
                enriched.append(self.enrich_item(it))

        return enriched

    def parse_input_to_pantry(
        self, input_text: str, prefer_llm: bool = True
    ) -> list[dict[str, Any]]:
        """Synchronously parse raw input text into standardized pantry items.

        Thread-safe and event-loop safe: can be called in sync scripts or within
        active event loops.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                fut = pool.submit(
                    asyncio.run, self.aparse_input_to_pantry(input_text, prefer_llm)
                )
                return fut.result(timeout=60.0)
        return asyncio.run(self.aparse_input_to_pantry(input_text, prefer_llm))

    def _fallback_parse_text(self, text: str) -> list[dict[str, Any]]:
        """Local heuristic parser for receipts, conversational speech, and simple strings."""
        storage_mode = detect_storage_mode(text)
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        # Multi-line receipt format
        if len(lines) > 1:
            items: list[dict[str, Any]] = []
            for line in lines:
                # Remove line numbering (e.g. '1. ') and price tokens (e.g. '45.000d', '59,000đ')
                cleaned_line = re.sub(r"^\d+[\.\)]\s*", "", line)
                cleaned_line = re.sub(r"\b\d+(?:[\.,]\d+)?\s*(?:đ|d|vnd)\b", "", cleaned_line, flags=re.IGNORECASE)
                name, qty_g, qty_source = parse_quantity_and_clean_name(cleaned_line)
                if name and len(name) >= 2:
                    items.append(
                        {
                            "name": name,
                            "raw_text": line,
                            "quantity_g": qty_g,
                            "quantity_source": qty_source,
                            "storage_mode": storage_mode,
                        }
                    )
            if items:
                return items

        # Conversational speech splitting (e.g. 'nửa cân thịt ba rọi với hai lạng tôm biển với 3 quả cà chua')
        cleaned_speech = re.sub(
            r"^(?:sáng nay|hôm nay|chiều nay|tôi|mình|em)?\s*(?:đi chợ)?\s*(?:mua|có)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        ).strip()
        cleaned_speech = re.sub(r"\b(?:để|cất|bỏ|cho vào)\s+(?:ngăn mát|ngăn đá|tủ lạnh|bếp|ngoài)\b.*$", "", cleaned_speech, flags=re.IGNORECASE).strip()

        # Split on delimiters: 'với', 'và', 'cùng', ',', ';'
        parts = re.split(r"\s+(?:với|và|cùng)\s+|[,;]+", cleaned_speech)
        items = []
        for part in parts:
            p_clean = part.strip()
            if not p_clean or len(p_clean) < 2:
                continue
            name, qty_g, qty_source = parse_quantity_and_clean_name(p_clean)
            if name and len(name) >= 2:
                items.append(
                    {
                        "name": name,
                        "raw_text": p_clean,
                        "quantity_g": qty_g,
                        "quantity_source": qty_source,
                        "storage_mode": storage_mode,
                    }
                )

        if items:
            return items

        # Fallback single item
        name, qty_g, qty_source = parse_quantity_and_clean_name(text)
        return [
            {
                "name": name,
                "raw_text": text,
                "quantity_g": qty_g,
                "quantity_source": qty_source,
                "storage_mode": storage_mode,
            }
        ]


def get_pantry_parser(
    *,
    snapshot_dir: str | Path | None = None,
    openai_client: OpenAIClient | None = None,
) -> PantryParser:
    """Singleton/cached factory to obtain the configured PantryParser."""
    global _PARSER_INSTANCE
    if _PARSER_INSTANCE is None:
        try:
            from AI.catalog.snapshot import load_snapshot_from_bundle

            snapshot = load_snapshot_from_bundle(snapshot_dir)
            _PARSER_INSTANCE = PantryParser(
                master_alias_index=snapshot.master_alias_index,
                master_by_code=snapshot.master_by_code,
                master_usage=count_master_usage(snapshot.ingredients),
                openai_client=openai_client,
            )
        except (OSError, FileNotFoundError, json.JSONDecodeError, ValueError, KeyError) as exc:
            logger.warning(
                "Could not load catalog snapshot for PantryParser (%s), starting with empty master",
                type(exc).__name__,
            )
            _PARSER_INSTANCE = PantryParser(openai_client=openai_client)
    return _PARSER_INSTANCE
