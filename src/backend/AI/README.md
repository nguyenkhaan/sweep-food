# AI

Single home for every AI workload hosted by the Sweep Food backend. The backend serves these
capabilities in-process; there is no separate AI service.

## Layout

| Path | Purpose |
| --- | --- |
| `catalog/` | Importer (`python -m AI.catalog.importer [--dry-run]`) and the cached in-memory snapshot loaded from Postgres |
| `recommendation/` | Candidate retrieval, scenario filters, LightGBM ranking (heuristic fallback), result formatting |
| `extraction/` | OpenAI vision OCR, Groq Whisper ASR, receipt/label/speech parsers |
| `smart_parser/` | Four-tier pantry text parser: dictionary, brand stripping, OpenAI LLM, regex fallback with freshness enrichment |
| `llm/` | Shared typed OpenAI client |
| `data/catalog/` | Published recipe catalog (`recipes`, `recipe_ingredients`, canonical mapping, manifest) |
| `data/master_ingredients/` | Master ingredient nutrition table and code redirects |
| `data/training/` | LightGBM ranker (`lgbm_contextual.txt`), `metadata.json`, and training datasets |

Source of the bundled data: `sweep-food-AI/data/main` (catalog `catalog-r1259-n31-2e025e6abc8e`).
The `data/` tree is byte-preserved (`.gitattributes`); do not reformat it.
