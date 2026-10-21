# SweepFood AI — Experimental Agent Test Mock

> **For AI agent/component testing only. This interface is incomplete, is not a finished SweepFood application, and is not production-ready.**
>
> `mock_web/` is a local test harness for exercising recommendation, OCR, ASR and pantry-input components. “Mock” describes the interaction surface, not the inference: requests can run real models and call real external services. Outputs can be incorrect or incomplete and must be reviewed. They are not medical, dietary or food-safety advice.

## Purpose and boundaries

Use this interface to inspect inputs and outputs, reproduce integration issues, and manually test how AI components work together. It is not the product frontend, a stable backend contract, a deployment reference, or proof that the underlying agents are complete or reliable.

- The UI and API contracts are experimental and may change.
- Some controls, status displays and integration paths are incomplete or only partially connected.
- A successful response or startup message is not an accuracy, safety, latency or GPU-execution guarantee.
- Use non-sensitive test receipts, images, text and recordings. Cloud-backed engines may send those inputs to external providers and incur usage charges.
- Keep the server bound to localhost. Do not expose it publicly or use it as a production service. The optional tunnel helper is for deliberate temporary testing only, not deployment.

## Run locally

Run commands from the repository root, not from inside `mock_web/`.

Use a Python 3.10+ environment with FastAPI, Uvicorn, `python-multipart`, NumPy, pandas, LightGBM, and the dependencies imported by `smart_input/service.py` and the selected OCR/ASR engine. This directory is not a self-contained application package; the root dependency list alone does not describe every optional engine. On the existing development workstation, these components are available in the `ocr_env` Conda environment.

```powershell
conda activate ocr_env
python -m uvicorn mock_web.app:app --host 127.0.0.1 --port 8000
```

For local source reload:

```powershell
python -m uvicorn mock_web.app:app --host 127.0.0.1 --port 8000 --reload
```

Alternatively:

```powershell
python -X utf8 mock_web/app.py
```

Open:

- Interface: <http://127.0.0.1:8000/>
- Experimental API documentation: <http://127.0.0.1:8000/docs>
- OpenAPI description: <http://127.0.0.1:8000/openapi.json>

The interface displays an English experimental-testing notice. The existing functional controls remain primarily Vietnamese.

## What the mock actually loads

Renaming the directory does not change its data sources or model behavior.

| Component | Current input |
| --- | --- |
| Recipes | `data/processed/recipes/recipes.json` — the full corpus, not just the curated catalog |
| Recipe ingredients | `data/processed/recipes/recipe_ingredients.json` |
| Master ingredient lookup | `data/processed/viendinhduong/master_ingredients_nutrition.csv` |
| Ranker weights | `data/training/lgbm_contextual.txt` |
| Feature order | `src/recommendation/contextual_features.py` (`FEATURE_COLS`, currently nine pantry/recipe features) |
| Detailed instructions | Optional processed details, with raw scraped instructions used when available |
| Static interface | `mock_web/static/` served at `/static/` |

The curated handoff bundle remains under `data/main/`. The mock does **not** automatically switch to that bundle. Restart the server after changing its input files or model weights; the service loads them into memory at startup.

Recommendation uses local data and weights. Cloud OCR/ASR paths require the relevant credentials, network access and provider availability; local engine paths require their own dependencies. Camera and microphone access also depend on browser permissions and a secure context such as localhost.

## Known limitations

- **Not a model benchmark:** displayed recommendation order includes feasibility tiers and urgency/diversity heuristics after model scoring. UI order is not a direct measurement of the ranker alone.
- **Incomplete constraints:** existing hard filters cover only selected scenarios. Equipment constraints are not fully enforced. The ranker has no scenario-context features.
- **Cooking time is not ranked:** the maximum-cooking-time control is still visible, but unreliable cooking-time data is not used as a ranking feature.
- **Train/serve differences:** inference can include recipe steps in `prep_complexity`, while training passes no steps. Do not assume exact feature parity across those paths.
- **Estimated nutrition:** missing ingredient weights, incomplete nutrient values, uncertain serving sizes and proxies can affect totals. A low displayed value does not establish that a dish is suitable for a diet or medical condition.
- **Partial status reporting:** hardware availability and warm-up flags do not establish that each model ran on a GPU, that a cloud request succeeded, or that cold-start latency is zero.
- **Engine and input variability:** OCR/ASR quality depends on the selected engine, credentials, image/audio quality and language. Review recognized ingredients, quantities and units before using them.
- **No production-readiness claim:** this harness is not a hardened public service or an accepted product API. Its behavior must be validated separately before reuse in a real application.

## Manual smoke checks

1. Start the service using `mock_web.app:app` and confirm that the experimental-testing warning appears on the page and in the startup output.
2. Open `/docs` and confirm that the service is identified as an incomplete AI test mock.
3. Check `/api/stats`, `/api/autocomplete?q=trứng` and `/api/system/status` to inspect the data and components actually loaded.
4. Submit a typed pantry request to `/api/recommend`; inspect the reported ranker, returned recipe IDs, ingredient matches and quantities. This checks the recommendation path without requiring an image/audio provider call.
5. Test OCR and ASR separately with non-sensitive inputs and the intended engine. Do not treat a successful recommendation request as verification of either input pipeline.
6. When checking camera, microphone or uploads, verify permissions and inspect the recognized text before adding items to the pantry.

Example request body for `POST /api/recommend`:

```json
{
  "items": [
    {"name": "trứng gà", "quantity_g": 240, "hours_to_expire": 96},
    {"name": "bắp cải", "quantity_g": 400, "hours_to_expire": 72}
  ],
  "household_size": 1,
  "scenario_type": "custom"
}
```

If port 8000 is already in use, choose another local port with `--port 8080`. Do not terminate unrelated processes to free a port. Stop the test server when verification is complete.

## Verification scope of the directory rename

The renamed module (`mock_web.app:app`) and direct script (`mock_web/app.py`) were launched locally. HTTP smoke checks covered the page, static JavaScript/CSS, OpenAPI/docs, dataset stats, autocomplete, system status and a typed pantry recommendation using the loaded LightGBM model. The English scope notice was visually checked in desktop and mobile browser viewports.

These checks do **not** validate cloud OCR/ASR, recognition accuracy, nutritional correctness or production readiness. Direct script startup also emits a FastAPI deprecation warning because the existing startup hook uses `on_event`; this rename does not change that lifecycle implementation.
