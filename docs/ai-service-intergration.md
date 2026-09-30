## Recommendation

Use a **backend-owned Anti-Corruption Layer (ACL)**—implemented with provider adapters—while deploying `sweep-food-AI` as a separate private service.

The main backend remains the public BFF: it owns authentication, user context, database writes, stable public DTOs, and error semantics. The AI service owns inference, OCR/ASR, candidate generation, and scoring.

```text
Mobile Client
     |
     v
Main Backend / Public BFF
  - authentication
  - inventory/preferences lookup
  - request assembly
  - AI contract adapter
  - response normalization
  - persistence
     |
     | private HTTP + request/trace ID
     v
sweep-food-AI
  - recommendation inference
  - OCR / ASR
  - model lifecycle
  - read-only catalog snapshot
     |
     v
PostgreSQL ai_serving.v1_* views
```

Do not use generic HTTP middleware for this. These transformations are route-specific business logic, not cross-cutting middleware concerns. A third standalone “integration service” would add deployment and failure complexity without value at the current scale.

The current backend already has the right seams: recommendations are isolated in a service/dependency boundary, and extractions are isolated behind service functions. They currently return mock data in [recommendation_service.py](/home/cloud/workspace/project/mobile/sweep-food/src/backend/src/module/recommendations/recommendation_service.py:20) and [extraction_service.py](/home/cloud/workspace/project/mobile/sweep-food/src/backend/src/module/extractions/extraction_service.py:66).

## 1. Service and contract boundaries

Create one typed backend client, conceptually:

```text
SweepFoodAIClient
  recommend(request) -> AIRecommendationResponse
  extract_ocr(file, document_type) -> AIOcrResponse
  extract_asr(file, engine) -> AIAsrResponse
```

The client should:

- Call only versioned internal AI endpoints.
- Validate every AI response before mapping it.
- Propagate `X-Request-ID` and `traceparent`.
- Apply route-specific connect/read timeouts.
- Translate transport failures into `502`, `503`, or `504`.
- Never expose raw AI errors, stack traces, GPU details, or upstream schemas to mobile clients.

Do not share Pydantic classes as a Python package between repositories. That creates release coupling. Instead, maintain an explicit OpenAPI/JSON contract and consumer contract tests.

## 2. Live database strategy

### Ownership model

| Data | Owner | How AI receives it |
|---|---|---|
| User inventory and expiry | Main backend | Backend queries it and sends only the authenticated user’s request-scoped pantry |
| User preferences | Main backend | Backend validates and sends a typed subset |
| Recipe/master-ingredient catalog | Main backend database | AI reads versioned, read-only serving views |
| Recommendation history | Main backend | Backend writes validated results |
| Model weights and metadata | AI deployment | Versioned immutable artifacts, not database rows |

The AI service should not receive access to `users`, inventory ownership, authentication, recommendation history, or other transactional tables.

### Versioned database views

Expose a dedicated schema such as:

```text
ai_serving.recipes_v1
ai_serving.recipe_ingredients_v1
ai_serving.master_ingredients_v1
ai_serving.catalog_revision
```

The views should present the dictionary shape the existing AI engine already consumes. For example, `master_ingredient_id::text` can be exposed as `master_ingredient_code`. That lets `CandidateGenerator` continue working without knowing backend ORM models or table structure.

This fits the existing identity model well: AI recipe IDs are already UUIDs and the backend importer preserves those UUIDs, so recipe results can map directly without a new identity table.

Give the AI a separate PostgreSQL role:

- `SELECT` only on `ai_serving`.
- No base-table, user-table, sequence, or write permissions.
- TLS required.
- Small connection pool and statement timeout.
- Credential stored in deployment secrets.
- Prefer the primary database when strict freshness is required; use a replica only if replica lag is within the agreed freshness SLO.

### Catalog refresh

The AI currently loads recipe and ingredient JSON into process globals during import in [web/app.py](/home/cloud/workspace/project/mobile/sweep-food/sweep-food-AI/web/app.py:78). Replace only that loading step:

1. Read `catalog_revision`.
2. Load all serving views in one repeatable-read transaction.
3. Build `CandidateGenerator`, recipe maps, instructions, and autocomplete data.
4. Atomically replace the active in-memory snapshot.
5. Keep the last good snapshot if a refresh fails.
6. Mark readiness false only when no valid snapshot has ever loaded.

For near-real-time freshness, check the lightweight revision row before recommendations and reload only when it changes. PostgreSQL `LISTEN/NOTIFY` may later reduce polling, but should not be the only mechanism because notifications can be missed.

Keep the XGBoost model and feature metadata as deployment artifacts. “Dynamic data” does not require dynamically mutating the trained model.

### Strict-independence alternative

If sharing even versioned views is unacceptable, use an outbox/CDC pipeline into an AI-owned read database. That gives stronger physical isolation but adds infrastructure and eventual consistency. It is not the best first implementation for this repository.

## 3. Route-by-route gap resolution

### `POST /api/recommendations`

The public request currently contains only free text in [recommendation_dto.py](/home/cloud/workspace/project/mobile/sweep-food/src/backend/src/module/recommendations/recommendation_dto.py:12), while AI expects structured pantry items, household size, and cooking time in [web/app.py](/home/cloud/workspace/project/mobile/sweep-food/sweep-food-AI/web/app.py:223).

Backend orchestration should:

1. Query the authenticated user’s active, non-empty inventory batches.
2. Join master ingredients.
3. Aggregate compatible batches by `master_ingredient_id`.
4. Build each AI item:

```json
{
  "name": "Thịt bò",
  "code": "<master-ingredient-uuid>",
  "quantity_g": 450,
  "hours_to_expire": 18,
  "is_staple": false
}
```

5. Read validated preferences such as:
   - `household_size`
   - `max_cooking_time_min`
   - `dietary_tags`
   - `excluded_master_ingredient_ids`
6. Call `/api/recommend`.
7. Batch-load returned recipe UUIDs from the backend database and build the authoritative recipe summaries.
8. Persist the validated run and ranked items in one transaction.

Important normalization rules:

- Reuse the backend’s existing mass conversion logic in [fefo_service.py](/home/cloud/workspace/project/mobile/sweep-food/src/backend/src/service/fefo_service.py:170).
- Do not silently treat milliliters, pieces, or packs as grams. Add per-ingredient conversion factors, or exclude their quantitative value with a warning until one exists.
- Unknown expiry must mean “not known,” not the AI’s current 72-hour default.
- Use `master_ingredient_id` as the stable matching code; use normalized name matching only for custom inventory entries.

Minimal AI response additions are required:

- Include ingredient `code` in matched/missing ingredients.
- Return `model_version` and `catalog_revision`.
- Return well-defined score components.
- Return a calibrated `[0,1]` score, because the backend contract requires that range at [recommendation_dto.py](/home/cloud/workspace/project/mobile/sweep-food/src/backend/src/module/recommendations/recommendation_dto.py:66). Raw XGBoost ranking scores are not automatically probabilities.

The AI currently does not apply dietary or exclusion preferences. Household size and cooking time are used, but full “preference fit” is not implemented. Do not manufacture a preference score. Add filtering/scoring support in the AI recommendation boundary before claiming this capability.

The free-text request should be retained for audit and explanation, but should not be treated as the pantry. If phrases such as “vegetarian” or “under 20 minutes” must affect ranking, add typed optional overrides to the public request or a separate intent-parsing stage.

### `POST /api/extractions/ocr/label`

The file upload already maps closely to the AI `file` field.

The backend adapter should:

- Send the image to `/api/smart-input/ocr-upload`.
- Preferably send an optional `document_type=label` form value so classification is not dependent only on OCR keywords.
- Map the first detected label item into `ExtractionFields`.
- Convert `quantity_g` into `quantity` plus unit `GRAM`.
- Normalize `DD/MM/YYYY` into ISO `YYYY-MM-DD`.
- Generate the public `request_id`.
- Preserve `persisted=false`.

One minimal AI transport change is needed: the label parser already knows expiry and production dates, but the service currently reduces them to a textual `note` in [service.py](/home/cloud/workspace/project/mobile/sweep-food/sweep-food-AI/smart_input/service.py:193). Preserve `expiry_date`, `production_date`, and confidence in the returned item. This is a serialization change, not an AI-core rewrite.

### `POST /api/extractions/ocr/invoice`

Call the same OCR endpoint with `document_type=invoice`, then map:

```text
AI item.name        -> line_item.name
AI item.quantity_g  -> line_item.quantity
"GRAM"              -> line_item.unit
AI store_name       -> vendor_name
AI raw_text         -> raw_text
```

The current receipt parser does not return unit price, line total, invoice total, invoice date, or currency. Therefore the first integration must:

- Return available line items.
- Set unavailable financial fields to `null`.
- Mark the response `PARTIAL`.
- Include explicit warnings such as `TOTAL_AMOUNT_NOT_EXTRACTED`.
- Never invent prices or report `SUCCEEDED`.

To fully satisfy the backend invoice contract in [extraction_dto.py](/home/cloud/workspace/project/mobile/sweep-food/src/backend/src/module/extractions/extraction_dto.py:49), the AI receipt parser must later be extended to associate OCR lines with prices, totals, vendor, currency, and date. This is the one route where an adapter alone cannot close the functional gap.

### `POST /api/extractions/asr`

The upload adaptation is straightforward:

```text
backend multipart field "file" -> AI multipart field "audio"
backend configuration          -> AI form field "engine"
```

The AI response contains a transcript and multiple ingredients in [service.py](/home/cloud/workspace/project/mobile/sweep-food/sweep-food-AI/smart_input/service.py:334), while the backend currently has only one singular `fields` object.

Use a dedicated ASR response:

```json
{
  "request_id": "...",
  "status": "SUCCEEDED",
  "provider": "GROQ_WHISPER",
  "raw_text": "...",
  "items": [
    {
      "ingredient_name": "Thịt bò",
      "quantity": 500,
      "unit": "GRAM"
    }
  ],
  "confidence": {},
  "warnings": [],
  "persisted": false
}
```

Because these routes are marked experimental, correcting the schema now is preferable. If clients already depend on the singular field, add `items` while retaining `fields` as the first item for one compatibility release.

Do not convert AI-estimated `hours_to_expire` into an extracted expiry date. Those values are heuristic defaults, not facts spoken by the user.

## 4. Observability and failure handling

Operate the two services independently:

- Separate container/image versions, health checks, dashboards, logs, and alerts.
- Backend metrics: upstream request count, latency, timeout count, invalid-response count, status by operation.
- AI metrics: model version, catalog revision, catalog age, inference duration, OCR/ASR duration, GPU memory, reload failures.
- Correlate them with request and trace IDs.
- Never log uploaded media, transcripts, free text, or full pantry contents by default.

AI readiness should require:

- Model loaded.
- At least one valid catalog snapshot loaded.
- OCR/ASR dependencies available for the applicable operation.

Use separate timeouts for recommendation, OCR, and ASR. Do not blindly retry expensive uploads. A synchronous flow is sufficient initially; introduce `202 Accepted` plus job polling only if measured OCR/ASR latency exceeds client request limits.

## 5. Implementation sequence

1. **Freeze contracts**
   - Define versioned internal AI request/response schemas.
   - Decide freshness SLO, unit-conversion policy, ASR plural schema, and fallback behavior.
   - Remove duplicate Smart Input route declarations currently present in the AI app before freezing OpenAPI.

2. **Create database serving views**
   - Add `ai_serving.v1_*` views and a catalog revision mechanism.
   - Create and test the read-only AI database role.
   - Verify recipe and ingredient UUID consistency.

3. **Replace AI static catalog loading**
   - Add one PostgreSQL loader that returns the existing `recipes_list`, `ingredients_list`, instruction map, and autocomplete shapes.
   - Build and atomically swap snapshots.
   - Leave candidate generation, feature extraction, and ranking logic unchanged.

4. **Harden the AI HTTP boundary**
   - Add liveness/readiness endpoints and internal service authentication.
   - Enforce upload sizes and MIME allowlists independently.
   - Add `document_type`.
   - Preserve label dates and ingredient codes.
   - Include model/catalog versions in recommendation responses.

5. **Add the backend AI client**
   - Use an explicit runtime HTTP dependency.
   - Add `AI_BASE_URL`, credentials, route-specific timeouts, and provider feature flags.
   - Define strict upstream DTOs with `extra="forbid"`.

6. **Implement recommendation assembly**
   - Query inventory, expiry, master identities, and typed preferences.
   - Normalize units and aggregate batches.
   - Call AI, validate recipe IDs, enrich summaries from the backend DB, and persist runs/items.

7. **Implement extraction mappers**
   - Replace mock provider calls in the existing extraction service.
   - Keep current upload validation.
   - Add label, invoice, and ASR-specific response mapping.
   - Return honest `PARTIAL`/`FAILED` results.

8. **Add tests**
   - Mapper unit tests for missing/null/invalid fields.
   - HTTP client tests for timeout, malformed response, and unavailable AI.
   - Contract tests against AI OpenAPI.
   - Integration tests against PostgreSQL serving views.
   - End-to-end tests for all four routes.

9. **Deploy independently**
   - Build separate backend and AI images.
   - Put AI on an internal network with no public ingress.
   - Configure GPU resources only for AI.
   - Deploy DB views before the AI version that consumes them.

10. **Roll out safely**
    - Run recommendation calls in shadow mode first and compare results.
    - Enable routes independently through feature flags.
    - Keep mock/rule-based fallback visibly labeled; never silently return mock extraction data as production AI output.

This design keeps nearly all schema adaptation in the backend. The unavoidable AI changes are limited to database-backed catalog loading, production hardening, preserving fields the AI already computes, and adding the preference/invoice capabilities that do not currently exist.