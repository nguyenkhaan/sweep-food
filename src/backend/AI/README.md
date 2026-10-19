# AI

Single home for every AI workload hosted by the Sweep Food backend. The backend serves these
capabilities in-process; there is no separate AI service.

## Layout

| Path | Purpose |
| --- | --- |
| `catalog/` | Importer (`python -m AI.catalog.importer [--dry-run]`), media builder (`python -m AI.catalog.media_builder`), and the cached in-memory snapshot loaded from Postgres |
| `recommendation/` | Candidate retrieval, scenario filters, LightGBM ranking (heuristic fallback), result formatting |
| `extraction/` | OpenAI vision OCR, Groq Whisper ASR, receipt/label/speech parsers |
| `smart_parser/` | Four-tier pantry text parser: dictionary, brand stripping, OpenAI LLM, regex fallback with freshness enrichment |
| `llm/` | Shared typed OpenAI client |
| `data/catalog/` | Published recipe catalog (`recipes`, `recipe_ingredients`, `recipe_media.json`, canonical mapping, manifest) |
| `data/master_ingredients/` | Master ingredient nutrition table and code redirects |
| `data/training/` | LightGBM ranker (`lgbm_contextual.txt`), `metadata.json`, and training datasets |

Source of the bundled data: `sweep-food-AI/data/main` (catalog `catalog-r1259-n31-2e025e6abc8e`).
The `data/` tree is byte-preserved (`.gitattributes`); do not reformat it.

## Recipe Media and Cooking Steps (`recipe_media.json`)

The catalog artifact `AI/data/catalog/recipe_media.json` enriches the factual recipe catalog with validated image URLs (`media_url`, `media_source`), structured cooking steps (`steps`), and optional chef tips (`chef_tips`).

### Rebuilding `recipe_media.json`

To regenerate or update `recipe_media.json`, run the media builder CLI:

```bash
python -m AI.catalog.media_builder \
  --raw /path/to/recipes_raw_scraped.json \
  --detailed /path/to/recipes_restructured_detailed.json \
  [--bundle-dir AI/data] \
  [--output AI/data/catalog/recipe_media.json] \
  [--no-network]
```

The builder:
1. Matches catalog recipes to structured instructions from `recipes_restructured_detailed.json` (or raw scraped instructions as fallback).
2. Extracts raw media URLs and scrapes missing images directly from article pages (`source_url`) using JSON-LD, `og:image`, and `twitter:image` metadata with bounded concurrency (<= 4) and polite delays.
3. Validates every candidate image URL over HTTP (status 200/206 with `image/*` MIME type, concurrency <= 8). Failed validations set `media_url` to `null`.
4. Atomically writes the sorted JSON artifact.

### Source Repository Commits

Inputs are retrieved from the `sweep-food-AI` repository history:
- **Raw scraped snapshot:** `sweep-food-AI` commit `c131067^:data/raw/recipes_raw_scraped.json` (crawl snapshot with source URLs, raw media URLs, and raw instructions).
- **Detailed structured steps:** `sweep-food-AI` commit `fc7a2d7^:data/processed/recipes/recipes_restructured_detailed.json` (normalized and structured step-by-step procedures).

### Attribution & Licensing Constraints

Recipe images are hot-linked directly from their original third-party hosting platforms (`monngonmoingay.com`, `dienmayxanh.com`, `cookpad.com`, `vnexpress.net`, etc.), and recipe instruction text derives from the originating articles.

Per `sweep-food-AI/ATTRIBUTION.md` and `DATA_LICENSE` (CC BY 4.0):
> *"Users who wish to access the original recipe pages (instructions, photos, descriptions) must obtain them directly from the source websites under those sites' own terms of service. Those materials are the property of their respective owners and are not part of this release."*
>
> *"It does NOT redistribute the copyrighted expressive content of the source websites: original step-by-step instruction prose, editorial descriptions, photographs, or original creative titles are NOT included in the released data... The `data/raw/recipes_raw_scraped.json` snapshot, which contains verbatim source text and media URLs, is retained only locally for reproducibility and is excluded from the published/tracked dataset."*

When recipes are imported into PostgreSQL and rendered by the frontend, `source_url` and `source_platform` are preserved for traceability back to the original source.
