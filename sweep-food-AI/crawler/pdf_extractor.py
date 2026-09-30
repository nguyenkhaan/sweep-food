"""Nutritional PDF Table and Component Extractor.

Extracts text and tabular nutritional components from PDF documents
using pypdf and regex pattern matching. Designed to process nutritional
leaflets, laboratory test reports, or food composition sheets.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

from pypdf import PdfReader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("pdf_extractor")

# Regex pattern matching nutrient rows: e.g. "Chất đạm (Protein)  g  3.4"
ROW_PATTERN = re.compile(
    r"^([A-Za-zÀ-ỹ0-9\s,\-\(\)\/\.]+?)\s{2,}([a-zA-Z\%\/]+|\-\-)\s{2,}([0-9]+(?:\.[0-9]+)?|[0-9]+(?:\,[0-9]+)?)$"
)


class NutritionalPdfExtractor:
    """Extractor for extracting nutritional tables from PDF documents."""

    def __init__(self, pdf_path: str | Path) -> None:
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        self.reader = PdfReader(str(self.pdf_path))

    def extract_raw_text(self) -> str:
        """Extract combined plain text across all pages in the PDF."""
        text_parts: list[str] = []
        for idx, page in enumerate(self.reader.pages):
            page_text = page.extract_text() or ""
            text_parts.append(f"--- PAGE {idx + 1} ---\n{page_text}")
        return "\n".join(text_parts)

    def extract_nutritional_components(self) -> list[dict[str, Any]]:
        """Parse text lines to detect nutrient names, units, and values."""
        components: list[dict[str, Any]] = []
        for page_idx, page in enumerate(self.reader.pages):
            text = page.extract_text() or ""
            lines = text.splitlines()

            for line in lines:
                cleaned = line.strip()
                if not cleaned:
                    continue

                # Try tabular regex match
                match = ROW_PATTERN.match(cleaned)
                if match:
                    nutrient_name = match.group(1).strip()
                    unit = match.group(2).strip()
                    val_str = match.group(3).strip().replace(",", ".")
                    try:
                        val = float(val_str)
                    except ValueError:
                        val = None

                    components.append({
                        "page": page_idx + 1,
                        "nutrient_name": nutrient_name,
                        "unit": unit,
                        "value": val,
                        "raw_line": cleaned,
                    })
                else:
                    # Fallback colon-separated: e.g. "Năng lượng: 120 kcal"
                    if ":" in cleaned:
                        parts = cleaned.split(":", 1)
                        name_candidate = parts[0].strip()
                        val_candidate = parts[1].strip()

                        # Extract first numeric value
                        num_match = re.search(r"([0-9]+(?:\.[0-9]+)?|[0-9]+(?:\,[0-9]+)?)", val_candidate)
                        unit_match = re.search(r"(kcal|cal|mg|mcg|g|kg|ml|l|%)", val_candidate, re.IGNORECASE)

                        if num_match:
                            val = float(num_match.group(1).replace(",", "."))
                            unit = unit_match.group(1) if unit_match else ""
                            components.append({
                                "page": page_idx + 1,
                                "nutrient_name": name_candidate,
                                "unit": unit,
                                "value": val,
                                "raw_line": cleaned,
                            })

        logger.info("Extracted %d nutrient items from %s", len(components), self.pdf_path.name)
        return components

    def export_json(self, output_path: str | Path) -> None:
        """Export extracted components to a JSON file."""
        data = {
            "source_file": self.pdf_path.name,
            "total_pages": len(self.reader.pages),
            "nutrients": self.extract_nutritional_components(),
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Exported JSON to: %s", output_path)

    def export_csv(self, output_path: str | Path) -> None:
        """Export extracted components to a CSV file."""
        items = self.extract_nutritional_components()
        if not items:
            logger.warning("No items to export to CSV.")
            return

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["page", "nutrient_name", "unit", "value", "raw_line"])
            writer.writeheader()
            writer.writerows(items)
        logger.info("Exported CSV to: %s", output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract nutritional components from PDF files.")
    parser.add_argument("pdf_path", help="Path to target PDF document")
    parser.add_argument("-o", "--output", help="Output path (CSV or JSON)")
    args = parser.parse_args()

    extractor = NutritionalPdfExtractor(args.pdf_path)

    if args.output:
        out = Path(args.output)
        if out.suffix.lower() == ".json":
            extractor.export_json(out)
        else:
            extractor.export_csv(out)
    else:
        results = extractor.extract_nutritional_components()
        print("\nExtracted Nutrients:")
        print("-" * 50)
        for r in results:
            print(f"- {r['nutrient_name']}: {r['value']} {r['unit']}")


if __name__ == "__main__":
    main()
