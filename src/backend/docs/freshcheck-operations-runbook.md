# FreshCheck release and rollback runbook

This runbook deploys a reviewed FreshCheck knowledge-base release to the Neon
PostgreSQL database configured by `DATABASE_URL`. PostgreSQL remains the runtime
source of truth. YAML is reviewed source material and
`data_freshness/build/freshcheck_kb.json` is the immutable release artifact.

## Safety rules

- Run every command from the directory shown in its section.
- Confirm the intended Neon project and branch before any write operation.
- Never print, paste into command history, or commit `DATABASE_URL`.
- Create a Neon branch or restorable backup before migration and activation.
- Keep the prior release artifact; rollback verifies its version and checksum.
- Do not delete prior KB rows or FreshCheck assessments during a data rollback.

## 1. Build and validate the artifact

From `data_freshness`:

```bash
uv sync --all-groups --frozen
uv run python scripts/build_kb.py
timeout 100s uv run pytest -q tests
uv run ruff check scripts/build_kb.py tests/test_kb_invariants.py
uv run ruff format --check scripts/build_kb.py tests/test_kb_invariants.py
uv run mypy --strict scripts/build_kb.py
```

Record the printed `kb_version`, `source_commit`, checksum, and record counts in
the release note. Do not edit the generated JSON by hand.

## 2. Pre-deployment record and backup

Before changing Neon, record:

- deployment commit SHA;
- current Alembic revision from `uv run alembic current`;
- active KB version and checksum from `freshcheck_kb_versions`;
- the Neon project/branch name and backup or branch identifier;
- the prior release artifact location.

Stop if the configured database, active KB, or migration revision differs from
the approved release record.

## 3. Validate, migrate, stage, and activate

From `src/backend`, with `DATABASE_URL` already provided by the deployment
secret store:

### Primary recommended release path (atomic stage, preserve mappings, and activate)

1. Apply database migrations (ensures all schema tables exist before catalog queries):

```bash
uv run alembic upgrade head
```

2. Build the immutable release artifact and dry-run to verify record counts, mapping preservation, and coverage:

```bash
uv run python src/seed_freshness.py --dry-run
```

3. Atomically stage the release artifact, carry forward active mappings with reviewed manifest overrides, seed exact candidates, and activate the new release:

```bash
uv run python src/seed_freshness.py --apply --actor "release:<deployment-id>"
```

### Release inspection

To inspect the artifact without database connection, run:

```bash
uv run python -m scripts.sync_freshcheck_kb \
  --artifact ../../data_freshness/build/freshcheck_kb.json \
  --dry-run
```

All production database writes must use `src/seed_freshness.py` to ensure that existing active mappings are carried forward and coverage is preserved.
## 4. Smoke verification

Use a non-sensitive owner account and verify:

1. `GET /api/freshness/questions` returns the active `kb_version` for a reviewed
   mapping.
2. Assessment of a mapped batch without a printed expiry writes one immutable
   assessment, one zero-delta metadata audit, and a conservative expiry.
3. Repeating the assessment with the same idempotency key creates no second
   assessment or audit.
4. A manufacturer expiry is unchanged.
5. The notification scan creates one classification for the saved expiry and a
   repeated scan creates no duplicate.
6. Recommendation inference receives `hours_to_expire` derived from the
   earliest owned active batch expiry; inventory quantity and FEFO ordering are
   unchanged.

## 5. Roll back KB data

Use the exact previously recorded artifact. The command rejects a different
checksum, a never-activated staged release, or a missing version.

```bash
uv run python -m scripts.sync_freshcheck_kb \
  --artifact <path-to-previous-freshcheck_kb.json> \
  --dry-run

uv run python -m scripts.sync_freshcheck_kb \
  --artifact <path-to-previous-freshcheck_kb.json> \
  --rollback \
  --actor "rollback:<incident-id>"
```

After rollback, repeat the question and assessment smoke checks. Existing
assessments retain their original KB/rule versions and must not be rewritten.

## 6. Roll back application or schema

- Roll back application code by redeploying the previously recorded commit.
- Prefer leaving additive FreshCheck tables in place during an application
  rollback so assessment history remains available.
- Run an Alembic downgrade only with owner approval and a verified backup. The
  assessment migration downgrade removes assessment history, so it is not the
  normal rollback path.
- Never repair a failed migration with ad-hoc destructive SQL.

## 7. Offline recommendation report

`sweepfood_tools/fridge_report.py` is an offline post-release evaluation tool,
not a production API component. Run it only on synthetic test fridges or data
that has been anonymized and approved for evaluation. Do not commit input JSON,
`fridge_top3.csv`, names, tokens, or other user-identifying fields. Store and
delete report output according to the project's data-retention policy.
