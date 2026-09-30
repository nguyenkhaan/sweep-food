"""Matching-link integrity; no ranking, replacement or confidence policy."""

from nlp.nutrition import NUTRITION_FIELDS, scale_nutrition

MATCH_FIELDS = ('master_ingredient_code', 'master_ingredient_name',
                'match_method', 'match_confidence')


def missing_link_value(value):
    return value is None or str(value).strip().casefold() in ('', 'none', 'null', 'nan')


def has_master_link(row):
    """A populated code OR name must not be replaced merely due to stale status."""
    return any(not missing_link_value(row.get(field)) for field in MATCH_FIELDS[:2])


def catalog_match_fields(code, name, method, confidence, catalog):
    """Validate code existence, retaining the caller's existing identity/score policy."""
    if missing_link_value(code) or str(code).strip() not in catalog:
        return None
    return dict(zip(MATCH_FIELDS, (str(code).strip(), name, method, confidence)))


def validate_catalog_codes(candidates, catalog):
    """Reject invalid hard-coded entries before a pipeline can publish them."""
    for query, candidate in candidates.items():
        if missing_link_value(candidate.get('code')) or str(candidate['code']).strip() not in catalog:
            raise ValueError(f'Unknown master code for hard-coded candidate {query!r}: {candidate.get("code")!r}')


def _norm_name(value):
    return ' '.join(str(value or '').strip().split()).casefold()


def stage_qwen_update(row, catalog, weight, match_fields=None, cleaned_name=None):
    """Build the whole patch before mutation, including fallible nutrient scaling.

    Weight/nutrition-only patches contain no matching fields. Existing links and
    their confidence remain byte-for-byte unchanged when no new match is accepted.

    Existence alone is not identity validation: a candidate is rejected not only
    when its code is absent from the catalog, but also when the catalog's current
    name_vi for that code disagrees with the candidate's name -- a code can be
    silently repointed to a different ingredient over time, and a caller passing
    a stale name for it must not be allowed to publish that stale identity.
    """
    updates = {'estimated_weight_g': str(round(weight, 1))}
    if match_fields is not None:
        catalog_row = catalog.get(match_fields.get('master_ingredient_code'))
        if (set(match_fields) != set(MATCH_FIELDS) or catalog_row is None
                or _norm_name(catalog_row.get('name_vi')) != _norm_name(match_fields['master_ingredient_name'])):
            raise ValueError('Incomplete or invalid matching-field update')
        updates.update(match_fields)
        if cleaned_name is not None:
            updates['cleaned_name'] = cleaned_name
    code = str(updates.get('master_ingredient_code', row.get('master_ingredient_code')) or '').strip()
    if code in catalog:
        for field, source in NUTRITION_FIELDS.items():
            value = scale_nutrition(catalog[code].get(source), float(weight) / 100.0, 1)
            updates[field] = None if value is None else str(value)
    return updates
