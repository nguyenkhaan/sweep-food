# Sweep Food Backend Product Requirements Document

**Document status:** Approved for MVP planning  
**Product:** Sweep Food  
**Component:** Backend API and supporting services  
**Version:** 1.0  
**Last updated:** 2026-08-29  
**Primary audience:** Backend engineers, mobile/frontend engineers, QA, data/ML engineers, and product stakeholders

## 1. Executive Summary

Sweep Food is a personal kitchen inventory and meal-planning application. Its backend helps one user maintain an accurate inventory, prioritize ingredients that will expire soon, choose suitable recipes, estimate nutrition and missing ingredients, and update inventory after cooking.

The MVP centers on one complete and reliable workflow:

1. A user signs in.
2. The user manually records an ingredient batch.
3. The backend monitors that batch's shelf life.
4. The backend recommends recipes from an admin-seeded catalog.
5. The user selects and cooks a recipe.
6. The backend deducts ingredients from the earliest-expiring eligible batches using FEFO.
7. The backend can produce a shopping list for missing ingredients.

Manual inventory entry must be production-ready in the first MVP. Voice/ASR, image/OCR, invoice extraction, and barcode lookup are experimental extraction endpoints: they accept input and return extracted or normalized output, but they do not persist that output to inventory. Meal recommendations use database-backed mock/rule-based ranking until an XGBoost or LightGBM model is delivered.

## 2. Product Intent

### 2.1 Problem statement

A person managing food at home repeatedly has to answer two difficult questions:

- What should I cook with what I already have?
- Which ingredients should I use first so they do not expire or spoil?

Inventory is often fragmented across memory, packaging, receipts, and the refrigerator. Conventional recipe search does not understand the user's actual inventory or expiration pressure. Sweep Food connects ingredient batches, shelf-life urgency, recipes, cooking consumption, and shopping needs in one backend.

### 2.2 How might we statement

How might we help one person decide what to cook and use expiring ingredients first, without requiring them to manually compare every recipe against every batch in their kitchen?

### 2.3 Target user

The MVP serves a single individual account that manages one personal inventory. A user is not part of a household, family, team, or shared inventory.

### 2.4 Product outcomes

The backend must enable the user to:

- Maintain accurate ingredient quantities by purchase/storage batch.
- See which batches are expired, near expiry, or safe.
- Receive timely expiration notifications.
- Obtain three to five relevant recipes from a seeded recipe catalog.
- Understand recipe coverage, missing ingredients, expected nutrition, and estimated extra cost.
- Consume inventory safely and deterministically using FEFO.
- Save cooked leftovers as a new cooked-food batch.
- Produce a shopping list without duplicating ingredients already available.

### 2.5 MVP success indicators

The MVP is successful when all of the following are demonstrable in an end-to-end test environment:

- A user can register through phone OTP verification and password creation, sign in with phone and password, and optionally verify an email address.
- A user can create, read, edit, consume, and archive ingredient batches through manual-entry APIs.
- Two batches of the same ingredient remain distinct and are consumed in expiration order.
- Expiration status and recommendation inputs are computed consistently.
- Recommendation endpoints return three to five seeded recipes with an explainable score breakdown.
- Completing a cooking session updates inventory atomically and creates an auditable consumption record.
- OCR, ASR, and barcode endpoints return a documented extraction response without writing inventory records.
- A background job identifies qualifying near-expiry batches and creates deduplicated notifications.
- Automated tests cover the critical authentication, FEFO, recommendation, and cooking paths.

## 3. Scope

### 3.1 In scope for MVP

- Single-user personal inventory.
- User registration through phone OTP verification followed by password creation.
- User sign-in by phone number and password.
- Optional email verification; verified email is an OTP destination for password recovery and sensitive identity changes, not an alternate sign-in channel.
- Admin account seeded separately; authorization support for the `admin` role.
- Manual inventory batch CRUD.
- Master ingredient, recipe, and recipe-ingredient catalogs seeded by a Python script.
- Four storage modes: immediate use, refrigerator, freezer, and dry-goods shelf.
- Manufacturer expiration date precedence and estimated shelf-life fallback.
- Batch-level FEFO consumption.
- Database-backed mock/rule-based recipe recommendations.
- A stable recommendation-provider interface for future XGBoost/LightGBM integration.
- Recipe details, nutrition estimates, favorites, meal selections, cooking history, and leftovers.
- Shopping list generation based on selected recipes and current inventory.
- Daily expiration checks and FCM push notifications.
- Experimental ASR through LiveKit/external AI, OCR through an external API, and barcode lookup.
- WireMock-based local/CI simulation of external integrations.
- eSMS sandbox integration for staging and eSMS Brandname OTP for production.

### 3.2 Explicitly out of scope for MVP

- Shared household or family inventories.
- Multiple inventories per user.
- Social features, recipe sharing, or collaboration.
- Admin dashboard and admin CRUD APIs.
- Training or serving the final XGBoost/LightGBM model.
- Persisting OCR, ASR, invoice, or barcode extraction results to inventory.
- Automatic reconciliation between extracted data and master ingredients.
- Guaranteeing nutritional or medical suitability.
- Payments, subscriptions, grocery ordering, or retailer checkout.
- Real-time price integrations.
- Automatic stock deduction without explicit user confirmation.
- Offline synchronization conflict resolution.

## 4. Product Principles and Business Rules

### 4.1 Single ownership

Every user-owned resource must contain a `user_id`. An authenticated user may only access resources belonging to that user. Admin role support must not imply access to user inventory unless a future, explicitly authorized support feature is added.

### 4.2 Batch-first inventory

Inventory is stored as batches, not only as an aggregate quantity. Two purchases of the same master ingredient remain separate when their expiration date, storage mode, acquisition date, unit cost, or source differs.

The read API may aggregate batches for display, but write and consumption operations always target batch records.

### 4.3 FEFO consumption

FEFO means First Expired, First Out. When a recipe consumes an ingredient, the backend selects eligible batches in this order:

1. Earliest non-null `expires_at`.
2. Oldest `created_at` when expiration dates are equal.
3. Batches without an expiration date after dated batches, ordered by oldest `created_at`.

Expired batches are excluded by default and cannot be consumed unless the user explicitly overrides a safety warning. The MVP may reject expired-batch consumption entirely; the recommended default is rejection.

### 4.4 Expiration precedence

If the manufacturer provides an expiration date, that date is authoritative. The backend must not replace it with a category estimate.

If no manufacturer expiration date exists, the backend estimates `expires_at` from:

- Master ingredient category.
- Storage mode.
- `stored_at` or `purchased_at` date.
- Seeded shelf-life rule.

An estimated expiration must be marked with `expiration_source = ESTIMATED`; manufacturer input uses `MANUFACTURER`; user override uses `USER_OVERRIDE` and retains an audit event.

### 4.5 Storage modes

| Mode | Code | Intent |
|---|---|---|
| Room temperature | `ROOM_TEMPERATURE` | Shelf-stable ingredients kept outside refrigerator/freezer |
| Refrigerator | `REFRIGERATED` | Chilled ingredients with category-based short shelf life |
| Freezer | `FROZEN` | Frozen meat, fish, seafood, and other eligible foods |
| Dry-goods shelf | `DRY_SHELF` | Spices, canned food, instant noodles, grains, and shelf-stable food |

Reference shelf-life values are configuration/seed data, not hard-coded domain constants. Initial seed guidance may include leafy vegetables for 3–5 days, root vegetables/fruits/mushrooms for 7–10 days, and fresh meat/fish/seafood for 2–3 days when refrigerated.

### 4.6 Units and conversions

Canonical units are `GRAM`, `KG`, `ML`, `LITER`, `PIECE`, `PACK`, and `OTHER`.

- Mass conversion is supported between gram and kilogram.
- Volume conversion is supported between milliliter and liter.
- `PIECE`, `PACK`, and `OTHER` are not converted unless the master ingredient defines an explicit conversion factor.
- A recipe and inventory batch must use compatible units before automatic deduction.
- Quantities must be positive decimal values on creation and must never become negative.

### 4.7 Nutrition calculation

For nutrient `n`, recipe nutrition is calculated as:

`total_nutrient_n = sum((ingredient_weight_grams / 100) * nutrient_n_per_100g)`

Seeded recipe totals may be denormalized for fast reads, but the seed process must be able to recalculate them from recipe ingredients. Nutrition is an estimate and must be labeled as such in API responses.

### 4.8 Idempotency and atomicity

- OTP requests, cooking completion, extraction requests, notification delivery, and shopping-list generation must tolerate retries.
- Cooking completion must run in one database transaction and lock affected batches so concurrent requests cannot consume the same quantity twice.
- Mutating endpoints that can produce duplicate side effects must accept an `Idempotency-Key` header.

## 5. Users, Roles, and Authorization

### 5.1 Roles

| Role | Creation | MVP permissions |
|---|---|---|
| `user` | Created after phone OTP verification and password creation | Manage only their profile, inventory, recommendations, meal selections, shopping list, favorites, device registrations, and cooking history |
| `admin` | Created by seed/configuration only | Reserved for future catalog administration; no public admin CRUD API in MVP |

### 5.2 Account status

| Status | Meaning |
|---|---|
| `ACTIVE` | Account is verified and may use protected APIs |
| `BANNED` | Authentication and protected access are denied |

### 5.3 Authorization requirements

- Protected endpoints require a valid access token.
- Resource ownership must be enforced in the database query, not only after retrieval.
- Role claims are authorization hints; the backend must verify current account status for sensitive operations.
- A banned user cannot refresh tokens or request application data.
- Admin role checks must exist as reusable policy/middleware even though admin APIs are out of scope.

## 6. Authentication and Verification

### 6.1 Supported identity channels

- Phone number is required for initial account registration and standard sign-in; it is stored in E.164 format, e.g. `+84901234567`.
- Password is required to complete registration. The backend stores only an Argon2id password hash; plaintext passwords must never be logged, persisted, or returned.
- Email is nullable. A verified email may receive OTPs for password recovery and sensitive identity changes, but cannot be used as a sign-in identifier in this MVP.
- Adding or changing a phone number or email requires verification of the new destination.

### 6.2 Registration, sign-in, and sensitive-change flows

1. **Registration:** submit phone, password, and optional profile information. The backend stores the password hash on an `UNVERIFIED` user and issues a `REGISTER` SMS OTP. Submitting the phone and a valid OTP activates the user without creating tokens or a session.
2. **Sign-in:** submit phone number and password. A successful password verification creates access and refresh JWTs plus a revocable refresh-token session; it does not send an OTP.
3. **Password reset or change:** request an OTP sent to the current phone number or a verified email, then submit the destination, OTP, purpose, and new password. The backend consumes an internal purpose-bound grant and revokes active refresh-token sessions.
4. **Phone or email change:** the authenticated user requests and verifies an OTP sent to the new destination, then consumes the matching verification grant to update that identity field.
5. **Step-up authentication:** sensitive operations may require a fresh OTP verification with purpose `STEP_UP_AUTH`; the endpoint defines when this is required and consumes the resulting grant.

### 6.3 OTP ownership

The Sweep Food backend owns OTP generation and validation. SMS/email providers only deliver messages.

- Production OTP: six random numeric digits generated with a cryptographically secure generator.
- Only an OTP hash is stored.
- Default TTL: five minutes.
- Maximum verification attempts per challenge: five.
- A successful verification consumes the challenge immediately.
- Issuing a replacement OTP overwrites and invalidates the previous active OTP for the same channel, purpose, and destination; no public challenge identifier is used.
- A successful verification returns a short-lived, single-use verification grant bound to the challenge's purpose and destination. A grant authorizes only its matching follow-up operation and never creates a session by itself.
- OTP values, hashes, access tokens, and provider secrets must never appear in production logs.

### 6.4 OTP purposes

`REGISTER`, `VERIFY_EMAIL`, `CHANGE_PHONE`, `CHANGE_EMAIL`, `RESET_PASSWORD`, `CHANGE_PASSWORD`, and `STEP_UP_AUTH` must be modeled as separate purposes. A challenge or verification grant created for one purpose cannot be used for another. `LOGIN` is not an OTP purpose in this MVP.

### 6.5 Password security and rate limiting

- Passwords must be checked against a configurable strength policy and hashed with Argon2id using environment-configured cost parameters.
- Login attempts must be rate-limited by phone number and IP address. Responses must not reveal whether the phone number exists or whether a password was correct.
- Password reset/change, registration completion, and identity changes must be rate-limited and audited.

Initial policy, configurable by environment:

- One OTP request per destination per 60 seconds.
- Five OTP requests per destination per hour.
- Twenty OTP requests per IP per hour.
- Five verification attempts per challenge.
- Temporary cooldown after repeated failed attempts.

Responses must avoid revealing whether a phone number or email is already registered where that information would enable account enumeration.

### 6.6 Tokens and sessions

- Short-lived signed access token: recommended 15 minutes.
- Rotating refresh token: recommended 30 days.
- Refresh tokens are stored as hashes and associated with a session/device.
- Refresh token reuse revokes the affected token family.
- Users can list and revoke active sessions.

### 6.7 Environment behavior

| Environment | Delivery adapter | Expected behavior |
|---|---|---|
| Local/CI | WireMock Docker service | Accept all valid requests; use fixed OTP `123456`; support deterministic success/failure fixtures |
| Staging | eSMS Sandbox | Exercise provider contract without fees or delivery to a real phone |
| Production | eSMS SMS Brandname OTP | Deliver registered transactional OTP templates to the user's phone |

Email OTP uses a provider adapter with the same internal interface. The concrete production email provider may be selected during implementation; local/CI must use a non-delivering mock adapter. Fixed local/CI OTP `123456` applies only to OTP-gated flows, not password sign-in.

## 7. Functional Requirements

### 7.1 User profile

The user can:

- Retrieve their profile.
- Update their display name and preferences.
- Add or replace an email address through verification.
- Select locale, dietary preferences, disliked ingredients, maximum cooking time, and optional nutrition preferences.
- Manage notification preferences.
- List and revoke sessions.

All persisted timestamps use UTC. MVP notification dates and warning windows use the fixed product timezone `Asia/Ho_Chi_Minh`; no timezone is stored per user.

### 7.2 Master ingredient catalog

The catalog provides canonical ingredient identity and metadata for inventory, recipes, nutrition, expiration estimation, and future ML features.

Each master ingredient includes:

- Canonical name and optional aliases.
- Category.
- Description.
- Default image URL.
- Canonical unit.
- Nutrition per 100 grams when applicable.
- Additional nutrition JSON for non-core nutrients.
- Eligible/default storage modes.
- Shelf-life rule references.

Users may search the catalog by name or alias. Manual inventory entry may also use a custom ingredient with no master match, but custom ingredients have limited nutrition, recommendation, and automatic conversion behavior.

### 7.3 Manual inventory entry

Manual entry is a complete MVP feature. A user can create a batch with:

- `master_ingredient_id` or `custom_name`.
- Quantity and unit.
- Storage mode.
- Optional purchase date, packaging date, stored date, manufacturer expiration date, price, note, and image reference.

Validation rules:

- Exactly one of `master_ingredient_id` and `custom_name` is required.
- Quantity must be greater than zero.
- Unit must be compatible with the master ingredient when a master ingredient is selected.
- Packaging, purchase, and stored dates cannot be unreasonably in the future.
- Expiration date may be in the past for data capture, but the batch is immediately classified as expired.
- Manufacturer expiration date sets `expiration_source = MANUFACTURER`.
- If expiration is omitted and a shelf-life rule is available, the backend calculates and returns an estimated expiration.
- If expiration cannot be determined, the batch remains valid with `expires_at = null` and an `UNKNOWN` freshness state.

### 7.4 Inventory views and lifecycle

The API must support:

- Batch list with filtering by ingredient, category, storage mode, freshness state, and date range.
- Aggregated inventory grouped by master ingredient/custom name and compatible unit.
- Batch detail.
- Batch update with audit history.
- Quantity adjustment with an event type.
- Move to another storage mode and recalculate estimated expiration when appropriate.
- Archive an empty, discarded, or removed batch.

Batch statuses are `ACTIVE`, `DEPLETED`, `DISCARDED`, and `ARCHIVED`. Freshness is computed, not manually stored as a source of truth:

- `EXPIRED`: `expires_at < now`.
- `EXPIRING_SOON`: within the configured warning window.
- `SAFE`: beyond the warning window.
- `UNKNOWN`: no expiration date.

Default warning windows may vary by category and storage mode. A user-level override may specify the number of days before expiry for notifications.

### 7.5 Inventory ledger

Every quantity change creates an immutable ledger entry:

- `INITIAL_STOCK`
- `MANUAL_ADJUSTMENT`
- `COOKING_CONSUMPTION`
- `DISCARDED`
- `LEFTOVER_CREATED`
- `CORRECTION`

The ledger records quantity before/after, delta, unit, related cooking session when applicable, idempotency key, and timestamp. The current batch quantity is the operational value; the ledger provides traceability.

### 7.6 Recipe catalog

Recipes are seeded and read-only through public MVP APIs. A recipe contains:

- Name, description, instructions, image URL, category/tags.
- Default servings and estimated cooking time.
- Estimated cost in VND.
- Denormalized nutrition totals.
- Required ingredients, quantity, unit, and whether each item is optional.

Recipe responses must scale required quantities and nutrition when requested servings differ from default servings.

### 7.7 Recipe recommendations

The recommendation endpoint returns three to five recipes. It must not present an unexplained long list.

The planned scoring model is:

`Score = 0.4E + 0.3A + 0.2P + 0.1U`

Each component is normalized to `[0, 1]`:

- `E` — expiration utilization: proportion and urgency-weighted amount of required ingredients sourced from near-expiry batches.
- `A` — availability: proportion of required ingredient quantity already available in eligible inventory.
- `P` — preference fit: serving, dietary preference, disliked ingredient, cooking-time, and nutrition fit.
- `U` — purchase minimization: inverse of normalized missing-ingredient count/cost.

The response includes total score and component scores so users and developers can understand why a recipe was recommended.

#### MVP recommendation provider

Until the ML model is available, the backend uses a database-backed deterministic provider:

- Candidate recipes come from seeded recipes.
- Hard exclusions remove incompatible dietary/disliked ingredients when configured.
- The provider computes available and missing quantities using unit conversion.
- It applies the score above where data exists.
- If a component lacks data, documented neutral/default behavior is applied.
- Results use deterministic tie-breaking by fewer missing ingredients, greater expiration utilization, then recipe ID.

This implementation may be called mock/rule-based, but it must use real seeded recipe and inventory data and return a stable contract.

#### Future ML provider

The recommendation application service must call a `RecommendationProvider` interface. A future XGBoost or LightGBM adapter can replace the mock provider without changing public endpoints.

The future feature vector may include:

- Available ingredient ratios.
- Expiration urgency by ingredient/category.
- Missing ingredient count and estimated cost.
- User favorites and cooking history.
- Cooking time and serving fit.
- Dietary/nutrition preference matches.
- Prior impressions, selections, completions, and dismissals.

Recommendation interaction events are deferred until the future ML training phase. The MVP avoids storing raw sensitive extraction inputs.

### 7.8 Meal selection and planning

The user may:

- Request recommendations for a target date/meal and serving count.
- Select a recommended or catalog recipe.
- Build a simple weekly meal plan from selected recipes.
- Replace or remove planned meals.
- Request a shopping list derived from planned meals.

The MVP does not automatically schedule a full week with AI. It stores explicit user selections and can calculate their ingredient requirements.

### 7.9 Cooking workflow

Cooking is a confirmable two-step process.

#### Preview

The user selects a recipe and serving count. The backend returns:

- Scaled recipe requirements.
- Eligible inventory batches in FEFO order.
- Proposed deduction per batch.
- Missing quantities.
- Nutrition estimate.
- Warnings for expired, unknown, or incompatible-unit stock.

Preview does not change inventory.

#### Completion

After cooking, the user chooses one of these consumption modes:

- `EXACT`: consume the planned recipe quantities.
- `HALF`: consume half of planned quantities.
- `USE_ALL_MATCHED`: consume all quantities from the explicitly matched batches, subject to confirmation.
- `CUSTOM`: submit actual consumed quantities.

On completion, the backend:

1. Revalidates available quantities.
2. Locks affected batches.
3. Applies FEFO deductions.
4. Creates inventory ledger entries.
5. Creates cooking history and consumed-ingredient records.
6. Marks depleted batches accordingly.
7. Returns updated quantities.

The operation is atomic and idempotent.

### 7.10 Cooked leftovers

After completing a cooking session, the user may save remaining cooked food as a new batch.

- The batch type is `COOKED_FOOD`.
- It references the cooking session and recipe.
- The user provides quantity/unit and may provide an expiration/reminder time.
- If no expiration is provided, the backend may apply a configurable short cooked-food shelf-life estimate.
- Leftovers participate in expiration notifications and can be manually consumed/discarded.
- Leftovers are not automatically decomposed back into raw ingredients.

### 7.11 Shopping list

The backend generates a shopping list from selected weekly recipes:

1. Sum scaled requirements across planned recipes.
2. Normalize compatible units.
3. Subtract usable, non-expired inventory.
4. Return only positive missing quantities.
5. Merge duplicate master ingredients.

The user can manually add, edit, check, and remove shopping items. Generated items retain links to the recipes that created the requirement. Estimated cost is optional and based on seed/reference data; it is not a live retailer price.

### 7.12 Favorites and history

The user can favorite recipes and create named favorite menus containing recipes. Cooking history records completed cooking sessions, servings, actual consumption, and timestamps. Favorites and history can later become features for the ML recommendation provider.

### 7.13 Expiration notifications

A scheduled background process runs at least daily and:

1. Selects active batches entering their user-configured warning window.
2. Excludes depleted, discarded, archived, and already-expired-notified batches as configured.
3. Creates a notification record with a deduplication key.
4. Sends a push message through FCM to active registered devices.
5. Stores delivery status and retry count.

Recommended notification types:

- `EXPIRING_SOON`
- `EXPIRES_TODAY`
- `EXPIRED`
- `LEFTOVER_REMINDER`

Retries use bounded exponential backoff. Invalid FCM tokens are disabled. Notification failures must not affect inventory transactions.

### 7.14 Experimental extraction endpoints

OCR, ASR, invoice, and barcode features are contract-validation integrations in MVP. They do not create or update inventory.

All extraction endpoints return a common envelope:

```json
{
  "request_id": "uuid",
  "status": "SUCCEEDED",
  "provider": "provider-name",
  "raw_text": "provider output or transcript",
  "fields": {
    "ingredient_name": "Milk",
    "quantity": 1,
    "unit": "LITER",
    "packaged_at": null,
    "expires_at": "2026-09-05",
    "price": 35000,
    "currency": "VND",
    "barcode": null
  },
  "confidence": {},
  "warnings": [],
  "persisted": false
}
```

Fields may be null. The output must explicitly state `persisted: false`.

#### ASR / voice

- Receive audio or a completed LiveKit recording/reference supported by the selected integration.
- Validate content type, size, and duration.
- Send the input to the configured external ASR provider.
- Return transcript and any parsed ingredient fields.
- Do not retain raw audio beyond request processing unless transient provider behavior requires it and is disclosed.

#### OCR / image and invoice

- Receive a supported image upload.
- Validate MIME type, file signature, dimensions, and size.
- Call an external OCR provider.
- Return raw text plus best-effort label or invoice fields.
- For invoices, return detected line items as an array.
- Do not persist the image or extracted inventory records in MVP.

#### Barcode

- Receive a normalized barcode value and format when available.
- Query the selected product-data provider or local mock.
- Return product metadata and normalized candidate fields.
- Return `NOT_FOUND` as a valid domain result rather than an internal server error.
- Do not persist lookup results or inventory records in MVP.

#### Failure and sandbox behavior

- Provider timeouts, invalid media, unsupported formats, low-confidence extraction, and rate limits have distinct error codes.
- Local/CI uses WireMock fixtures for success, malformed response, timeout, provider error, and low-confidence cases.
- Sensitive files and extracted personal data must not be included in application logs.

## 8. API Requirements

### 8.1 Conventions

- Base path: `/api`.
- JSON uses `snake_case`.
- Dates use ISO 8601; timestamps include timezone and are returned in UTC.
- Phone numbers use E.164.
- Pagination uses cursor-based pagination for potentially large collections.
- Protected endpoints use `Authorization: Bearer <access_token>`.
- Responses include `request_id` for traceability.
- OpenAPI documentation is generated from FastAPI schemas.

### 8.2 Error format

```json
{
  "status_code": 409,
  "detail": "The requested cooking quantities are no longer available.",
  "path": "/api/cooking/sessions/example/complete"
}
```

Validation errors use the same envelope. Internal stack traces are never returned.

### 8.3 Endpoint inventory

#### Health

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health/liveness` | Process liveness; returns JSON |
| `GET` | `/health/error` | Raises a deterministic HTTP exception for error-envelope verification |
| `GET` | `/health/text` | Returns the approved plain-text message |

#### Authentication

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/auth/register` | Create an `UNVERIFIED` phone/password account and send its registration OTP |
| `POST` | `/auth/register/resend-otp` | Send a replacement registration OTP for an `UNVERIFIED` account |
| `POST` | `/auth/verify/register` | Verify registration OTP, activate the account, and return a plain-text acknowledgement |
| `POST` | `/auth/login` | Sign in with phone number and password |
| `POST` | `/auth/password/reset` | Send a password-reset OTP to the submitted phone |
| `POST` | `/auth/password/change` | Send a password-change OTP to the authenticated user's phone |
| `POST` | `/auth/verify/change-password` | Verify reset/change OTP, replace password, and revoke sessions |
| `POST` | `/auth/token/refresh` | Use a refresh JWT to create a new access JWT |
| `POST` | `/auth/logout` | Revoke current session and return `Logout successfully` as plain text |
| `GET` | `/auth/sessions` | List active user sessions |
| `DELETE` | `/auth/sessions/{session_id}` | Revoke a session |

Example registration OTP issuance response:

```json
{
  "otp": "654321",
  "expires_in_seconds": 300
}
```

Example registration OTP verification request:

```json
{
  "phone": "+84901234567",
  "otp": "654321"
}
```

OTP is generated internally by the registration and password routes, stored as a hash in Redis, sent through the configured provider, and returned as `otp` with `expires_in_seconds` for the current MVP client flow. Verification requests submit the phone and OTP without a challenge identifier. The generated OTP remains the primary value; local/CI additionally accepts `DEFAULT_OTP=123456`. Registration verification activates the `UNVERIFIED` account and returns only `verify account successfully`; tokens are created by login. Password verification replaces the password and revokes active sessions.

Access and refresh tokens are JWTs with the same identity claims (`sub`, `roles`) and a distinguishing `purpose` claim (`access` or `refresh`). Access JWTs use `JWT_ACCESS_SECRET`; refresh JWTs use `JWT_REFRESH_SECRET`. Refresh JWT hashes remain attached to revocable database sessions. Login does not accept `device_label`.

#### User profile and devices

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/users/me` | Read the current JWT identity (`user_id` and `roles`) |
| `GET` | `/users/profile` | Read the authenticated user's profile |
| `PATCH` | `/users/profile` | Update profile/preferences |
| `POST` | `/users/me/email/request-verification` | Start email verification |
| `POST` | `/users/me/email/verify` | Verify the pending email OTP and return a plain-text acknowledgement |
| `POST` | `/users/me/phone/request-change` | Start phone-number change verification for a new phone; also email the OTP when the account has an email |
| `POST` | `/users/me/phone/confirm-change` | Verify the pending phone OTP and return a plain-text acknowledgement |
| `POST` | `/users/me/devices` | Register/update an FCM device token |
| `DELETE` | `/users/me/devices/{device_id}` | Disable a device registration |

#### Master ingredients and recipes

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/ingredients` | Search/list master ingredients |
| `GET` | `/ingredients/{ingredient_id}` | Read master ingredient details |
| `GET` | `/recipes` | Browse/filter seeded recipes |
| `GET` | `/recipes/{recipe_id}` | Read recipe details and scaled nutrition |
| `PUT` | `/recipes/{recipe_id}/favorite` | Favorite a recipe |
| `DELETE` | `/recipes/{recipe_id}/favorite` | Remove favorite |

#### Inventory

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/inventory/batches` | Manually create a batch |
| `GET` | `/inventory/batches` | List/filter batches |
| `GET` | `/inventory/batches/{batch_id}` | Read batch details |
| `PATCH` | `/inventory/batches/{batch_id}` | Edit batch metadata |
| `POST` | `/inventory/batches/{batch_id}/adjustments` | Adjust, consume, or discard quantity |
| `POST` | `/inventory/batches/{batch_id}/move` | Change storage mode |
| `DELETE` | `/inventory/batches/{batch_id}` | Archive a batch |
| `GET` | `/inventory/summary` | Aggregated inventory view |
| `GET` | `/inventory/ledger` | Read quantity-change history |

#### Recommendations and meal planning

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/recommendations` | Return three to five ranked recipes |
| `POST` | `/meal-plans` | Create a meal plan |
| `GET` | `/meal-plans/{meal_plan_id}` | Read a meal plan |
| `POST` | `/meal-plans/{meal_plan_id}/items` | Add a selected recipe/date/meal |
| `PATCH` | `/meal-plans/{meal_plan_id}/items/{item_id}` | Replace/reschedule a meal |
| `DELETE` | `/meal-plans/{meal_plan_id}/items/{item_id}` | Remove a meal |

Example recommendation item:

```json
{
  "recipe_id": "uuid",
  "rank": 1,
  "score": 0.86,
  "score_components": {
    "expiration_utilization": 0.95,
    "availability": 0.88,
    "preference_fit": 0.72,
    "purchase_minimization": 0.75
  },
  "available_ratio": 0.88,
  "missing_ingredients": [],
  "expiring_batches_used": ["uuid"],
  "provider": "RULE_BASED_MVP"
}
```

#### Cooking

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/cooking/preview` | Preview FEFO allocation and missing quantities |
| `POST` | `/cooking/sessions` | Create a planned cooking session |
| `POST` | `/cooking/sessions/{session_id}/complete` | Atomically record actual use and deduct stock |
| `POST` | `/cooking/sessions/{session_id}/leftovers` | Add cooked leftovers as a batch |
| `GET` | `/cooking/history` | List completed cooking history |
| `GET` | `/cooking/history/{session_id}` | Read cooking and consumption detail |

#### Shopping lists

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/shopping-lists/generate` | Generate from a meal plan and inventory |
| `GET` | `/shopping-lists/{list_id}` | Read list and source recipes |
| `POST` | `/shopping-lists/{list_id}/items` | Add manual item |
| `PATCH` | `/shopping-lists/{list_id}/items/{item_id}` | Edit/check an item |
| `DELETE` | `/shopping-lists/{list_id}/items/{item_id}` | Remove an item |

#### Experimental extraction

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/extractions/asr` | Transcribe voice/audio and return parsed fields |
| `POST` | `/extractions/ocr/label` | Extract a product label |
| `POST` | `/extractions/ocr/invoice` | Extract invoice line items |
| `POST` | `/extractions/barcode` | Look up and normalize barcode metadata |

#### Notifications

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/notifications` | List in-app notification records |
| `PATCH` | `/notifications/{notification_id}` | Mark read/dismissed |

## 9. Data Model

Neon PostgreSQL is the system of record. Redis stores ephemeral OTP challenges, rate-limit counters, locks, and background-job coordination. UUIDs are used for public primary keys.

### 9.1 Core identity tables

#### `users`

- `id uuid PK`
- `name varchar nullable`
- `phone_e164 varchar unique not null`
- `phone_verified_at timestamptz nullable`
- `email citext unique nullable`
- `email_verified_at timestamptz nullable`
- `password_hash varchar not null` (Argon2id hash only)
- `role enum(user, admin) not null`
- `status enum(active, banned) not null`
- `preferences jsonb not null default '{}'`
- `created_at`, `updated_at timestamptz`

#### `auth_sessions`

- `id uuid PK`
- `user_id uuid FK`
- `refresh_token_hash varchar`
- `token_family_id uuid`
- `device_label`, `ip_address`, `user_agent nullable`
- `expires_at`, `revoked_at`, `created_at`, `last_used_at`

OTP challenges are preferably stored in Redis due to TTL. If persistence/audit requirements require a table, store metadata and hash only, never the clear OTP.

### 9.2 Catalog tables

#### `master_ingredients`

- `id uuid PK`
- `name`, `description`
- `category_id uuid FK`
- `default_media_url nullable`
- `canonical_unit`
- `calories`, `protein_g`, `fat_g`, `carbs_g`, `sugar_g`, `sodium_mg nullable`
- `other_nutrients jsonb`
- `default_storage_mode nullable`
- timestamps

#### `ingredient_aliases`

- `id uuid PK`
- `master_ingredient_id uuid FK`
- `alias`, `normalized_alias`
- unique normalized alias constraint as appropriate

#### `shelf_life_rules`

- `id uuid PK`
- `ingredient_id nullable FK`
- `category_id nullable FK`
- `storage_mode`
- `min_days`, `max_days`, `default_days`

Ingredient-specific rules take precedence over category rules.

#### `recipes`

- `id uuid PK`
- `name`, `description`, `instructions jsonb`
- `media_url nullable`
- `default_servings decimal`
- `estimated_cooking_minutes integer`
- `estimated_cost decimal nullable`
- denormalized nutrition columns and `other_nutrients jsonb`
- `tags jsonb`
- timestamps

#### `recipe_ingredients`

- `id uuid PK`
- `recipe_id uuid FK`
- `master_ingredient_id uuid FK`
- `required_quantity decimal`
- `unit`
- `is_optional boolean`
- `preparation_note nullable`
- unique `(recipe_id, master_ingredient_id, preparation_note)` where suitable

### 9.3 Inventory tables

#### `inventory_batches`

- `id uuid PK`
- `user_id uuid FK`
- `master_ingredient_id uuid nullable FK`
- `custom_name varchar nullable`
- `batch_type enum(raw_ingredient, cooked_food)`
- `initial_quantity decimal`
- `current_quantity decimal`
- `unit`
- `storage_mode`
- `status`
- `purchased_at`, `packaged_at`, `stored_at nullable`
- `expires_at timestamptz nullable`
- `expiration_source enum(manufacturer, estimated, user_override, unknown)`
- `unit_cost decimal nullable`
- `note nullable`, `media_url nullable`
- `source enum(manual, leftover)` for persisted MVP batches
- `source_cooking_session_id uuid nullable FK`
- timestamps and optional `archived_at`

Constraints:

- Master ingredient or custom name is required.
- `initial_quantity > 0`.
- `current_quantity >= 0`.
- A depleted batch has `current_quantity = 0`.
- User/ingredient/status/expiration indexes support inventory and expiration queries.

#### `inventory_ledger_entries`

- `id uuid PK`
- `user_id`, `batch_id`
- `event_type`
- `quantity_before`, `quantity_delta`, `quantity_after`, `unit`
- `cooking_session_id nullable`
- `idempotency_key nullable`
- `created_at`

### 9.4 Recommendation, planning, and cooking tables

#### `recommendation_runs`

- `id uuid PK`
- `user_id uuid FK`
- `criteria jsonb`
- `provider enum(rule_based_mvp, xgboost, lightgbm)`
- `model_version nullable`
- `summary nullable`
- `created_at`

#### `recommendation_items`

- `id uuid PK`
- `recommendation_run_id uuid FK`
- `recipe_id uuid FK`
- `rank`, `total_score`
- score components
- `explanation jsonb`
- unique `(recommendation_run_id, rank)`

#### `meal_plans` and `meal_plan_items`

Meal plans belong to one user and cover a start/end date. Items connect a date/meal slot, recipe, servings, and status.

#### `cooking_sessions`

- `id uuid PK`
- `user_id`, `recipe_id`
- `meal_plan_item_id nullable`
- `servings`
- `status enum(planned, completed, cancelled)`
- `consumption_mode nullable`
- `nutrition_snapshot jsonb`
- `completed_at nullable`, timestamps
- unique idempotency key scoped to user

#### `cooking_consumptions`

- `id uuid PK`
- `cooking_session_id`, `recipe_ingredient_id nullable`
- `inventory_batch_id`
- `quantity`, `unit`
- `created_at`

### 9.5 Shopping, favorites, and notifications

- `shopping_lists`: user, optional meal plan, status, generated timestamp.
- `shopping_list_items`: master/custom ingredient, required/available/missing quantities, unit, estimated cost, checked flag, source metadata.
- `favorite_recipes`: unique user/recipe pair.
- `favorite_menus`: user-owned name and description.
- `favorite_menu_items`: menu/recipe relation; creation order is used in MVP.
- `device_registrations`: user, FCM token hash/encrypted token, platform, enabled status, last seen.
- `user_notification_preferences`: one row per user with warning-window and notification-type settings.
- `notifications`: user, type, title/body, payload, deduplication key, read/delivery status, scheduled/sent timestamps, retry count.

## 10. Seed Data Requirements

Seed data is created through one Python entry file, recommended at `src/backend/scripts/seed.py`.

The seed process must:

- Create the admin account from environment-provided identity data; secrets are never committed.
- Seed ingredient categories, master ingredients, aliases, shelf-life rules, recipes, and recipe ingredients.
- Use deterministic natural keys and upserts so it is safe to rerun.
- Run inside a transaction per dataset or release unit.
- Validate units, positive quantities, ingredient references, and recipe nutrition.
- Report created, updated, unchanged, and rejected records.
- Support a dry-run validation mode.
- Never delete user inventory.

The initial file may contain a small curated dataset. Future scraped data can replace or expand the dataset through the same validated seed pipeline.

## 11. System Architecture

### 11.1 Logical components

- **FastAPI application:** HTTP API, authentication, validation, orchestration, and OpenAPI.
- **Neon PostgreSQL:** authoritative persistent data.
- **Redis:** OTP TTL, rate limits, distributed locks, cache, and worker coordination.
- **Background worker/scheduler:** expiration scans, FCM delivery, retries, and asynchronous extraction when required.
- **Provider adapters:** SMS, email, FCM, ASR/LiveKit, OCR, barcode, and recommendation provider.
- **WireMock:** deterministic local/CI external-provider simulation.

### 11.2 Module boundaries

Recommended backend modules:

- `auth`
- `users`
- `catalog`
- `inventory`
- `recipes`
- `recommendations`
- `meal_plans`
- `cooking`
- `shopping`
- `extractions`
- `notifications`
- `integrations`

Domain/application logic must not call vendor SDKs directly. Provider interfaces isolate external services, and environment configuration selects adapters.

### 11.3 Data communication

- API communication is synchronous JSON/HTTP except media uploads.
- Extraction endpoints may begin synchronously for MVP, with explicit provider timeouts. The contract should allow future `PENDING` jobs.
- Inventory writes and cooking completion use PostgreSQL transactions.
- Background jobs carry resource IDs, not full sensitive payloads.
- Provider retries must be idempotent and bounded.

## 12. External Integration Contracts

### 12.1 SMS

Internal interface:

`send_otp(destination, template_id, otp, expires_in_seconds, correlation_id) -> delivery_reference`

Production adapter: eSMS SMS Brandname OTP. Staging passes the supported sandbox flag. Provider credentials and Brandname/template IDs are environment secrets.

### 12.2 Email

Internal interface mirrors the SMS delivery contract. A verified email can be used for password recovery and sensitive-change verification. Provider selection is deferred but must not affect public authentication APIs.

### 12.3 FCM

The notification adapter accepts a user/device target, notification type, localized content, and deep-link payload. Provider responses are mapped to delivered, retryable failure, or permanent failure.

### 12.4 ASR and LiveKit

LiveKit handles voice session/media transport as configured. The backend accepts a supported media reference or upload, calls an external ASR provider, and maps the result to the common extraction contract.

### 12.5 OCR and barcode

OCR and product lookup adapters normalize provider-specific responses. Provider selection is configuration. WireMock fixtures define the expected request/response contract before live credentials are available.

### 12.6 Recommendation provider

Internal interface:

`recommend(user_context, inventory_snapshot, candidate_recipes, criteria, limit) -> ranked_recommendations`

Both rule-based MVP and future XGBoost/LightGBM adapters return identical result objects, including provider/model version and explainability metadata.

## 13. Background Jobs

| Job | Frequency/trigger | Idempotency behavior |
|---|---|---|
| Expiration scan | Daily in `Asia/Ho_Chi_Minh` | Deduplicate by batch, notification type, and effective date |
| FCM delivery | On notification creation | Deduplicate by notification/device; bounded retries |
| Invalid device cleanup | After permanent FCM failure | Repeated disable operation is safe |
| Extraction cleanup | Scheduled if temporary files exist | Delete only expired transient objects |
| Refresh/session cleanup | Daily | Remove/revoke expired session records safely |

Only one effective expiration scan may process a given partition/window at a time. Job observability includes run ID, duration, selected count, success count, retry count, and failure count.

## 14. Security and Privacy Requirements

- Follow OWASP API security practices.
- Validate authorization on every user-owned resource.
- Hash refresh tokens and OTPs; use constant-time comparison where applicable.
- Encrypt provider credentials and sensitive configuration outside source control.
- Apply rate limits to authentication and extraction endpoints.
- Validate uploaded file signature, MIME type, dimensions, duration, and size.
- Reject executable/polyglot files and unsafe remote URLs.
- Use parameterized queries/ORM and strict request schemas.
- Redact phone, email, OTP, tokens, raw OCR text, transcripts, and provider secrets from logs.
- Do not store raw voice/images for experimental extraction after request processing.
- Capture security-relevant audit events: login, failed verification thresholds, session revocation, identity changes, account status changes, and inventory overrides.
- Document retention and account-deletion behavior before production launch.
- Nutrition and expiration outputs are guidance, not medical or food-safety guarantees; manufacturer information takes precedence.

## 15. Non-Functional Requirements

### 15.1 Performance targets

Under expected MVP load, measured server-side excluding external-provider latency:

- Read API p95: under 300 ms.
- Standard write API p95: under 500 ms.
- Recommendation p95 with rule-based provider: under 1 second for the seeded catalog target size.
- Cooking completion p95: under 1 second under normal contention.
- Extraction calls: provider-specific timeout, recommended maximum 15 seconds for synchronous MVP calls.

### 15.2 Reliability

- Inventory and cooking operations favor consistency over availability.
- No successful cooking completion may produce negative stock.
- External integration failure cannot corrupt inventory or authentication state.
- Database backups and restore procedures are required before production.
- Readiness checks fail when essential database connectivity is unavailable.

### 15.3 Observability

- Structured JSON logs with request/job correlation IDs.
- Metrics for request latency/error rate, OTP request/verification outcomes, provider delivery status, recommendation latency, FEFO conflicts, extraction failures, and job health.
- Distributed traces or equivalent correlation across API, worker, and provider calls.
- Alerts for sustained authentication/provider failures and missed expiration job windows.

### 15.4 Accessibility and localization support

Backend messages use stable error codes; clients own user-facing localization. Seeded names/descriptions may support localized fields later. Monetary display defaults to VND and all MVP expiration windows use `Asia/Ho_Chi_Minh`.

## 16. Testing Requirements

### 16.1 Unit tests

- Unit conversion and incompatible unit groups.
- Shelf-life rule precedence.
- Freshness-state calculation at boundary timestamps.
- FEFO ordering.
- Recommendation component normalization and weighted score.
- Nutrition scaling.
- Shopping-list aggregation/subtraction.
- OTP expiry, hashing, attempts, and purpose separation.

### 16.2 Integration tests

- PostgreSQL constraints and transactions.
- Concurrent cooking completion cannot double-consume a batch.
- User ownership cannot be bypassed.
- Redis rate limits and challenge expiry.
- Seed idempotency and dry-run behavior.
- Background notification deduplication.

### 16.3 Contract tests

WireMock fixtures must cover:

- SMS accepted, rejected, rate-limited, timeout, and malformed response.
- OCR/ASR success, low confidence, unsupported input, timeout, and provider failure.
- Barcode found and not found.
- FCM success, transient failure, and invalid token.

### 16.4 End-to-end acceptance scenario

1. User registers with phone plus password, verifies either the generated OTP or fixed local fallback `123456`, and signs in with phone plus password.
2. User creates two batches of the same ingredient with different expiration dates.
3. User requests recommendations and receives seeded recipes with score explanations.
4. User previews a recipe and sees the earlier-expiring batch allocated first.
5. User completes cooking twice with the same idempotency key and stock changes only once.
6. User saves a leftover batch.
7. User generates a shopping list that excludes sufficient existing inventory.
8. Expiration job creates one notification per qualifying batch/window.
9. OCR/ASR/barcode calls return normalized results with `persisted: false` and create no inventory batch.

## 17. Acceptance Criteria by Capability

### Authentication

- Phone-based registration creates an `UNVERIFIED` password account; OTP verification activates it, and sign-in uses phone plus password.
- Verified email can receive OTPs for password recovery and sensitive changes.
- Unverified email cannot be used for recovery or sensitive identity changes.
- Rate limits and challenge expiry are enforced.
- Local/CI accepts fixed fallback OTP `123456` in addition to the generated Redis-backed OTP; OTP values remain excluded from logs.

### Inventory

- Manual entry persists valid batches and returns calculated expiration metadata.
- Same-ingredient batches remain separately addressable.
- Aggregated view sums compatible active quantities.
- All quantity changes produce ledger entries.
- Cross-user batch access returns a non-disclosing not-found/forbidden response.

### Recommendations

- Endpoint returns no more than five and normally at least three candidates when enough seeded recipes exist.
- Every result includes the four component scores and provider identifier.
- Near-expiry usage and availability influence rank deterministically.
- Public response contract remains compatible with a future ML adapter.

### Cooking

- Preview makes no writes.
- Completion is atomic, idempotent, and FEFO-compliant.
- Insufficient inventory produces a domain conflict without partial deduction.
- Leftovers become distinct cooked-food batches.

### Extraction

- Valid inputs produce raw and structured output.
- Results always indicate they were not persisted.
- No inventory rows are created.
- Provider failures return mapped errors and do not leak provider credentials or raw exceptions.

### Notifications

- Qualifying batches create scheduled notifications once per configured window.
- FCM failures retry safely.
- Invalid device tokens are disabled.

### Seed data

- One Python seed entry file can safely run multiple times.
- Referential and unit errors fail validation with actionable output.
- Admin, master ingredients, recipes, recipe ingredients, and shelf-life rules are seeded without public admin CRUD endpoints.

## 18. Delivery Phases

### Phase 1 — Platform foundation

- Configuration, Neon PostgreSQL, Redis, migrations, request/error conventions.
- Phone OTP-gated registration, phone/password sign-in, verified-email recovery, sessions, roles.
- WireMock SMS fixtures and eSMS adapter boundaries.
- Seed pipeline and initial catalog.

### Phase 2 — Inventory core

- Manual batch CRUD, expiration estimation, summary views, ledger.
- FEFO service and unit conversion.
- Daily expiration job, device registration, FCM adapter.

### Phase 3 — Recipes and consumption

- Recipe APIs and nutrition scaling.
- Rule-based/mock recommendation provider and event tracking.
- Meal selections, cooking preview/completion, leftovers, favorites/history.
- Shopping-list generation.

### Phase 4 — Experimental inputs

- ASR/LiveKit, OCR label/invoice, and barcode provider adapters.
- Common non-persisting extraction contract.
- WireMock contract/failure fixtures.

### Post-MVP

- Train/evaluate and integrate XGBoost or LightGBM.
- Persist user-confirmed extraction results through the manual-entry command path.
- Improve catalog through scraped/curated seed data.
- Consider household sharing only after single-user inventory accuracy is validated.

## 19. Risks and Mitigations

| Risk | Impact | MVP mitigation |
|---|---|---|
| Manual entry is burdensome | Low inventory accuracy/adoption | Keep required fields minimal; return estimates; later convert extraction output into confirmable drafts |
| OCR/ASR output is inaccurate | Bad ingredient data | Do not persist in MVP; return confidence/warnings; require later user confirmation |
| Unit mismatch prevents recipe matching | Weak recommendations | Canonical-unit groups, explicit conversions, validation, and missing-data warnings |
| Shelf-life estimate is unsafe | Food-safety concern | Manufacturer date precedence, source labels, conservative rules, disclaimers, user overrides with audit |
| Mock recommendations appear arbitrary | Low trust | Deterministic scoring and component explanations |
| Future ML model changes API shape | Rework across clients | Stable provider interface and public result contract |
| OTP abuse increases cost | Cost/security incident | Multi-dimensional rate limits, cooldowns, hashed OTPs, provider monitoring |
| SMS delivery is blocked/delayed | Registration or sensitive-change delay | Registered Brandname/template, verified-email recovery, resend controls, provider abstraction |
| Concurrent cooking causes negative stock | Corrupt inventory | Transactional row locks, revalidation, idempotency keys |
| Seed scrape quality is poor | Broken catalog/nutrition | Schema validation, dry run, deterministic natural keys, reject report |

## 20. Open Implementation Decisions

These do not block the product scope but must be decided before their implementation phase:

- Concrete ORM and migration libraries.
- Concrete Redis-backed task worker/scheduler.
- Production email delivery provider.
- OCR, ASR, and barcode providers and their exact quotas/timeouts.
- Object storage provider if persisted media is added later.
- Exact category/storage shelf-life seed values and authoritative source notes.
- Maximum upload size/audio duration and retention guarantees per provider.
- Production load assumptions and scaling thresholds.
- Account deletion and retention periods.

## 21. Glossary

| Term | Definition |
|---|---|
| Batch | A separately tracked quantity of an ingredient sharing acquisition/storage/expiration attributes |
| FEFO | First Expired, First Out; consume the batch with the earliest expiry first |
| Master ingredient | Admin-seeded canonical ingredient used by recipes, nutrition, and matching |
| Custom ingredient | User-entered ingredient without a canonical catalog match |
| Storage mode | Immediate, refrigerated, frozen, or dry-shelf storage context |
| Shelf-life rule | Seeded rule used to estimate expiration when the manufacturer date is absent |
| Recommendation provider | Replaceable component that ranks recipe candidates |
| Extraction | ASR, OCR, invoice, or barcode processing that returns structured candidate data |
| Seed data | Versioned catalog/admin data loaded by the Python seed script |
| FCM | Firebase Cloud Messaging, used for push notification delivery |
| OTP | One-time password used to verify phone or email ownership |
| WireMock | Dockerized local/CI mock for external HTTP provider behavior |

## 22. Definition of Done for the MVP Backend

The backend MVP is done when:

- All in-scope acceptance criteria pass in automated or documented manual tests.
- Database migrations and the idempotent Python seed file work from an empty environment.
- OpenAPI describes every public endpoint and error contract.
- Critical flows have unit, integration, contract, and end-to-end coverage.
- No known path can cross user ownership boundaries or create negative inventory.
- External services can be replaced with WireMock in local/CI.
- Production secrets are externalized and logs are verified for sensitive-data redaction.
- Background expiration processing is observable and deduplicated.
- Deployment and rollback instructions exist.
- Remaining open decisions and post-MVP features are tracked without being silently included in MVP scope.
