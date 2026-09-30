"""Nullable nutrition conversion; unknown is distinct from a measured zero."""

import math

NUTRITION_FIELDS = {
    "calories": "energy_kcal",
    "protein_g": "protein_g",
    "fat_g": "fat_g",
    "carbs_g": "carbs_g",
}


def nutrition_value(value):
    """Read CSV blanks, None and NaN as missing, preserving numeric zero."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    number = float(value)
    return None if math.isnan(number) else number


def scale_nutrition(value, factor, digits=2):
    """Scale only available values, including when the factor is zero."""
    number = nutrition_value(value)
    return None if number is None else round(number * factor, digits)


def restore_missing_nutrition(rows, masters):
    """Restore master nulls only; keep matching, weights and known values intact."""
    result = []
    for row in rows:
        restored = dict(row)
        master = masters.get(str(row.get("master_ingredient_code", "")))
        if master is not None:
            for field, source in NUTRITION_FIELDS.items():
                if nutrition_value(master.get(source)) is None:
                    restored[field] = None
        result.append(restored)
    return result
