# Sweep Food Database Notes

`DATABASE.txt` is the canonical MVP data contract. It is the source of truth for tables, fields, enums, and relationships. Redis stores only short-lived OTP challenges, rate limits, distributed locks, and worker coordination.

## Data Ownership and Authentication

- All IDs are UUIDs. All persisted timestamps are UTC. Expiration notifications use the fixed product timezone `Asia/Ho_Chi_Minh`; timezones are not stored per user in this MVP.
- A user-owned record must be authorized through its direct `user_id` or an owned parent record. Admin users are created by the Python seed script; no public admin CRUD endpoint exists.
- `users.phone_e164` is unique. `users.email` is unique when present. Phone plus password is the only standard sign-in method; a verified email is an OTP destination for recovery and identity changes, never an alternate sign-in identifier in this MVP.
- `users.password_hash` is required for every user and stores an Argon2id password hash only. Password plaintext is never persisted, logged, placed in a token, or returned by any API.
- OTP plaintext, verification grants, provider credentials, and raw OCR/ASR/barcode input or output are never persisted. Redis challenges are scoped to an `OTPChannel` and `OTPPurpose`.
- `auth_sessions.refresh_token_hash` is the only stored refresh-token representation. On refresh-token reuse, revoke sessions sharing the token family.

## Catalog and Seed Rules

- Ingredient and recipe seed data is upserted by a documented deterministic natural key, such as normalized ingredient name plus category and normalized recipe name. The seed file must not create duplicate catalog rows when rerun.
- `ingredient_aliases.normalized_alias` is unique. It maps a user/provider synonym to exactly one master ingredient.
- A shelf-life rule targets exactly one master ingredient or one category. Ingredient-level rules take precedence over category-level rules. The seed data must not contain duplicate target/storage-mode rules.
- `recipe_ingredients.required_quantity` and `recipes.default_servings` must be greater than zero.
- Unit compatibility is inferred from `MeasurementUnit`: `GRAM`/`KG` are mass; `ML`/`LITER` are volume; `PIECE`/`PACK`/`OTHER` do not have automatic cross-unit conversion.

## Inventory, FEFO, and Ledger Rules

- Each `inventory_batches` row is one real batch. Purchases or packages with different expiration dates must stay separate.
- A batch requires exactly one of `master_ingredient_id` and `custom_name`.
- `initial_quantity > 0` and `current_quantity >= 0`. A zero balance becomes `DEPLETED`; discard and archive use their explicit status values.
- A manufacturer date takes precedence and sets `expiration_source = MANUFACTURER`. Otherwise the backend estimates a date using the matching shelf-life rule and records `ESTIMATED`; user edits use `USER_OVERRIDE`; unavailable dates use `UNKNOWN` with null `expires_at`.
- Freshness is computed at query time: expired, expiring soon, safe, or unknown. It is not a stored source-of-truth field.
- FEFO selects active, non-expired, unit-compatible batches by `expires_at`, then `created_at`, with null expiration dates last. Completion revalidates and locks selected batches.
- Every quantity mutation is transactional and creates an immutable `inventory_ledger_entries` record. `quantity_after = quantity_before + quantity_delta` and the batch balance must match the completed mutation.
- `idempotency_key` is unique within its user/operation scope. A retry must not duplicate a cooking consumption or ledger entry.
- A leftover creates a `COOKED_FOOD` batch with `source = LEFTOVER`, linked to its completed cooking session, and a `LEFTOVER_CREATED` ledger entry.

## Recommendations, Plans, Cooking, and Shopping

- `recommendation_items.rank` is unique within a recommendation run. The run records the provider and optional model version; MVP uses `RULE_BASED_MVP` and later supports XGBoost or LightGBM.
- Recommendation interaction events are intentionally not persisted in MVP. Future model training may add them in a separate migration.
- A meal-plan item date must fall within its parent plan range. `(meal_plan_id, planned_for, meal_slot)` is unique.
- Cooking completion creates exact `cooking_consumptions`, matching `COOKING_CONSUMPTION` ledger records, and updates the cooking session atomically.
- A shopping-list item requires a master ingredient or custom name. `source_metadata` keeps the generated recipe context; manually edited values remain user-owned.
- `(user_id, recipe_id)` is unique in `favorite_recipes`. Favorite-menu recipes use creation order; ordering is not stored separately in MVP.

## Devices and Notifications

- Encrypt FCM tokens and use the hash only for lookup/deduplication. A permanent FCM failure disables the corresponding device; notification history remains intact.
- Each user has at most one `user_notification_preferences` row. A null `warning_days` uses the category/storage default.
- `notifications.deduplication_key` is unique and derives from batch, notification type, and effective date in `Asia/Ho_Chi_Minh`.
- Notification delivery failures update retry/delivery state only; they never roll back inventory or cooking transactions.

## Required Indexes

- Unique `users(phone_e164)` and non-null `users(email)`; do not index `users.password_hash`.
- `auth_sessions(user_id, expires_at)` and `auth_sessions(token_family_id)`.
- `master_ingredients(category_id)`, unique `ingredient_aliases(normalized_alias)`, and shelf-life lookup by ingredient/category plus storage mode.
- `recipe_ingredients(recipe_id)` and `recipe_ingredients(master_ingredient_id)`.
- `inventory_batches(user_id, status, expires_at, created_at)` for FEFO, plus user/ingredient and user/storage-mode filtering.
- `inventory_ledger_entries(inventory_batch_id, created_at)` and user/time history.
- Recommendation run/item indexes by user/run/recipe and creation time.
- Meal-plan/user/date, cooking-session/user/status/time, consumption/session/batch, shopping-list/user/status, and shopping-item/list indexes.
- Unique favorite recipe pair, favorite-menu item pair, device token hash, notification preference user, notification deduplication key, and notification user/status/created-time indexes.

## Migration Mapping and Order

The legacy conceptual names below are mapping aids only. `DATABASE.txt` remains the source of truth for the migration and model names.

| Original conceptual item | Approved destination | Migration decision |
|---|---|---|
| `user` | `users` | Renamed and expanded for phone/email verification, password hash, role, status, preferences, and timestamps. |
| `master_ingredient` | `ingredient_categories` + `master_ingredients` | Category is normalized into its own table; nutrition and default storage remain on the ingredient. |
| `user_ingredient` | `inventory_batches` + `inventory_ledger_entries` | Split into operational batch balance and immutable quantity history to support FEFO. |
| `media` | Direct `media_url` fields | Removed; the MVP does not need a shared media entity. |
| `recipe` | `recipes` | Renamed; recipe instructions, nutrition, tags, and servings are retained. |
| `recipe_ingredient` | `recipe_ingredients` | Renamed and extended with optional/preparation information. |
| `ai_meal_plan` | `recommendation_runs`, `recommendation_items`, `meal_plans`, `meal_plan_items` | Split between ranked recommendations and explicit user meal selections. |
| `shoopping_plan` | `shopping_lists`, `shopping_list_items` | Split into list header and editable line items. |
| `cooking_history` | `cooking_sessions`, `cooking_consumptions` | Split into cooking header and exact batch consumption records. |
| `user_favorite_recipe` | `favorite_recipes` | Renamed. |
| `user_favorite_menu`, `user_favorite_menu_item` | `favorite_menus`, `favorite_menu_items` | Renamed; MVP uses creation order rather than a stored position. |
| No original equivalent | `auth_sessions`, `ingredient_aliases`, `shelf_life_rules`, `device_registrations`, `user_notification_preferences`, `notifications` | Added because they are required by the approved PRD flows. |

Create migrations in this dependency order:

1. Create the 22 PostgreSQL enums, then `users` and `auth_sessions`.
2. Create `ingredient_categories`, `master_ingredients`, `ingredient_aliases`, and `shelf_life_rules`.
3. Create `recipes` and `recipe_ingredients`.
4. Create `recommendation_runs`, `recommendation_items`, `meal_plans`, and `meal_plan_items`.
5. Create `cooking_sessions`, then `inventory_batches`, `cooking_consumptions`, and `inventory_ledger_entries`. Add the nullable `inventory_batches.source_cooking_session_id` constraint after `cooking_sessions` exists to resolve the circular leftover relationship.
6. Create `shopping_lists`, `shopping_list_items`, favorites, devices, notification preferences, and notifications.
7. Add indexes, unique/check constraints, immutable-ledger protection, and seed the admin/catalog data only after the tables exist.

Fields documented as `// table.id` in `DATABASE.txt` are relationship constraints in the implementation migration. Nullable references use `SET NULL` only where preserving historical data is required; user-owned data is not cascade-deleted in MVP.

## Required Invariants and Constraints

- Use database foreign keys for every documented relationship, except the explicitly deferred self/circular relationship while its target table is being created; add it before the migration is complete.
- `users.phone_e164` is unique; `users.email` is unique when non-null; `users.password_hash` is non-null; an `ACTIVE` user has `phone_verified_at`; one `user_notification_preferences` row exists per user.
- A registration, password-reset, password-change, phone-change, email-change, or step-up operation must consume a single-use OTP verification grant with the matching purpose and destination. Password reset/change revokes the affected user's active refresh-token sessions.
- Category names, master ingredient names within a category, and recipe names are unique case-insensitively. `ingredient_aliases.normalized_alias` is unique.
- A `shelf_life_rules` row has exactly one non-null target (`master_ingredient_id` or `category_id`), and that target/storage-mode pair is unique.
- A recipe ingredient, meal-plan item serving, cooking session serving, cooking consumption, and shopping quantities must be positive. `meal_plans.starts_on <= ends_on`; a planned item date lies in that inclusive range.
- An inventory batch has exactly one non-null identity (`master_ingredient_id` or `custom_name`), `initial_quantity > 0`, `current_quantity >= 0`, and a valid batch/status/source combination. A leftover references its completed source cooking session.
- Ledger rows are append-only. Enforce this with database permissions or a trigger that rejects `UPDATE` and `DELETE`; no application endpoint may bypass the inventory service. Ensure the before/delta/after arithmetic agrees with the batch mutation in the same transaction.
- `cooking_sessions(user_id, idempotency_key)` is unique when the key is supplied. Ledger idempotency must be unique per user, key, batch, and event type so one cooking request may safely deduct multiple batches.
- Recommendation rank is unique within its run. Favorite recipe pairs and favorite-menu recipe pairs are unique. One meal slot per plan/date is allowed.
- A device token hash and notification deduplication key are unique. Notification delivery failures cannot alter inventory, cooking, or ledger data.

## MVP Flow Review

| PRD flow | Approved storage | Review result |
|---|---|---|
| Phone/password sign-in, OTP-gated registration and sensitive changes, refresh sessions | `users`, `auth_sessions`; OTP, verification grants, and rate limits in Redis | Covered; password/OTP plaintext never persists. |
| Seeded catalog search and aliases | `ingredient_categories`, `master_ingredients`, `ingredient_aliases` | Covered. |
| Estimated expiration | `shelf_life_rules`, `inventory_batches` | Covered; manufacturer date has precedence. |
| Manual batch entry, separate expiry batches, FEFO, and audit | `inventory_batches`, `inventory_ledger_entries` | Covered; batch rows remain separate and ledger is immutable. |
| Seeded recipes and nutrition | `recipes`, `recipe_ingredients` | Covered. |
| Rule-based recommendation and future model adapter | `recommendation_runs`, `recommendation_items` | Covered; recommendation interaction events are intentionally deferred. |
| Explicit meal selection and shopping list | `meal_plans`, `meal_plan_items`, `shopping_lists`, `shopping_list_items` | Covered. |
| Cooking preview/completion and leftovers | `cooking_sessions`, `cooking_consumptions`, `inventory_batches`, ledger | Covered; exact batch deductions and leftover source are traceable. |
| Favorites and cooking history | Favorite tables plus cooking sessions/consumptions | Covered. |
| Expiry preferences and FCM delivery | `user_notification_preferences`, `device_registrations`, `notifications` | Covered; daily windows use `Asia/Ho_Chi_Minh`. |
| OCR, ASR, invoice, and barcode extraction | Redis/transient provider processing only | Covered; no database write is allowed. |

## Non-persisting MVP Extraction

ASR (LiveKit plus an external AI provider), OCR, invoice extraction, and barcode lookup return their normalized result only. They do not create inventory, catalog, ledger, recommendation-interaction, or raw-media records in this MVP.
