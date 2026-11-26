"""Shared schema, validation, and parsing for user nutrition preferences."""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_HOUSEHOLD_SIZE = 4
MIN_HOUSEHOLD_SIZE = 1
MAX_HOUSEHOLD_SIZE = 10
MAX_DISLIKED_INGREDIENTS = 50
MAX_DISLIKED_INGREDIENT_LENGTH = 100

DEFAULT_DIET = "balanced"
VEGETARIAN_DIET = "vegetarian"
VEGETARIAN_SCENARIO = "an_chay"

VALID_DIETS: frozenset[str] = frozenset(
    {
        "balanced",
        "high_protein",
        "low_calorie",
        "more_veg",
        "vegetarian",
    }
)

VALID_HEALTH_CONDITIONS: frozenset[str] = frozenset(
    {
        "nguoi_tieu_duong",
        "nguoi_cao_huyet_ap",
        "nguoi_benh_gout",
        "nguoi_dau_da_day",
        "an_kieng_keto_lowcarb",
    }
)

VALID_ALLERGIES: frozenset[str] = frozenset(
    {
        "shellfish",
        "fish",
        "peanut",
        "egg",
        "dairy",
        "soy",
        "gluten",
        "sesame",
    }
)


@dataclass(frozen=True, slots=True)
class UserNutritionProfile:
    """Typed nutrition profile extracted from `users.preferences` JSONB."""

    household_size: int = DEFAULT_HOUSEHOLD_SIZE
    diet: str = DEFAULT_DIET
    health_conditions: tuple[str, ...] = ()
    allergies: tuple[str, ...] = ()
    disliked_ingredients: tuple[str, ...] = ()

    def scenario_types(self) -> list[str]:
        """Return ordered hard-filter scenarios for the AI engine."""
        scenarios: list[str] = []
        if self.diet == VEGETARIAN_DIET:
            scenarios.append(VEGETARIAN_SCENARIO)
        for condition in self.health_conditions:
            if condition not in scenarios:
                scenarios.append(condition)
        return scenarios

    def primary_scenario_type(self) -> str:
        """Return single-scenario fallback for backwards compatibility."""
        scenarios = self.scenario_types()
        return scenarios[0] if scenarios else "custom"


def validate_preferences_patch(
    preferences: dict[str, object],
) -> dict[str, object]:
    """Validate and normalize known nutrition profile keys in a profile patch."""
    normalized: dict[str, object] = dict(preferences)

    if "household_size" in normalized:
        normalized["household_size"] = _validate_household_size(
            normalized["household_size"]
        )
    if "diet" in normalized:
        normalized["diet"] = _validate_diet(normalized["diet"])
    if "health_conditions" in normalized:
        normalized["health_conditions"] = _validate_enum_list(
            normalized["health_conditions"],
            VALID_HEALTH_CONDITIONS,
            field_name="health_conditions",
        )
    if "allergies" in normalized:
        normalized["allergies"] = _validate_enum_list(
            normalized["allergies"],
            VALID_ALLERGIES,
            field_name="allergies",
        )
    if "disliked_ingredients" in normalized:
        normalized["disliked_ingredients"] = _validate_disliked_ingredients(
            normalized["disliked_ingredients"]
        )

    return normalized


def parse_nutrition_profile(
    preferences: dict[str, object] | None,
) -> UserNutritionProfile:
    """Tolerantly read a typed nutrition profile from stored JSONB preferences."""
    if not isinstance(preferences, dict):
        return UserNutritionProfile()

    household_size = _parse_household_size(preferences.get("household_size"))
    diet = _parse_diet(preferences)
    health_conditions = _parse_enum_tuple(
        preferences.get("health_conditions"),
        VALID_HEALTH_CONDITIONS,
    )
    allergies = _parse_enum_tuple(
        preferences.get("allergies"),
        VALID_ALLERGIES,
    )
    disliked_ingredients = _parse_disliked_tuple(
        preferences.get("disliked_ingredients")
    )

    return UserNutritionProfile(
        household_size=household_size,
        diet=diet,
        health_conditions=health_conditions,
        allergies=allergies,
        disliked_ingredients=disliked_ingredients,
    )


def _validate_household_size(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("household_size must be an integer between 1 and 10")
    if value < MIN_HOUSEHOLD_SIZE or value > MAX_HOUSEHOLD_SIZE:
        raise ValueError("household_size must be an integer between 1 and 10")
    return value


def _validate_diet(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("diet must be a valid diet option")
    cleaned = value.strip().lower()
    if cleaned not in VALID_DIETS:
        raise ValueError(f"Unsupported diet value: {value}")
    return cleaned


def _validate_enum_list(
    value: object,
    allowed: frozenset[str],
    *,
    field_name: str,
) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list of strings")
    deduped: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{field_name} must contain only strings")
        cleaned = item.strip().lower()
        if cleaned not in allowed:
            raise ValueError(f"Unsupported {field_name} value: {item}")
        if cleaned not in seen:
            seen.add(cleaned)
            deduped.append(cleaned)
    return deduped


def _validate_disliked_ingredients(value: object) -> list[str]:
    if not isinstance(value, list):
        raise ValueError("disliked_ingredients must be a list of strings")
    deduped: list[str] = []
    seen_lower: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            raise ValueError("disliked_ingredients must contain only strings")
        cleaned = item.strip()
        if not cleaned:
            continue
        if len(cleaned) > MAX_DISLIKED_INGREDIENT_LENGTH:
            raise ValueError(
                f"disliked_ingredients item exceeds "
                f"{MAX_DISLIKED_INGREDIENT_LENGTH} characters"
            )
        key = cleaned.lower()
        if key not in seen_lower:
            seen_lower.add(key)
            deduped.append(cleaned)
    if len(deduped) > MAX_DISLIKED_INGREDIENTS:
        raise ValueError(
            f"disliked_ingredients cannot exceed {MAX_DISLIKED_INGREDIENTS} items"
        )
    return deduped


def _parse_household_size(value: object) -> int:
    if (
        not isinstance(value, bool)
        and isinstance(value, int)
        and MIN_HOUSEHOLD_SIZE <= value <= MAX_HOUSEHOLD_SIZE
    ):
        return value
    return DEFAULT_HOUSEHOLD_SIZE


def _parse_diet(preferences: dict[str, object]) -> str:
    raw = preferences.get("diet")
    if not isinstance(raw, str):
        raw = preferences.get("dietary_preference")
    if isinstance(raw, str):
        cleaned = raw.strip().lower()
        if cleaned in VALID_DIETS:
            return cleaned
    return DEFAULT_DIET


def _parse_enum_tuple(value: object, allowed: frozenset[str]) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    deduped: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            continue
        cleaned = item.strip().lower()
        if cleaned in allowed and cleaned not in seen:
            seen.add(cleaned)
            deduped.append(cleaned)
    return tuple(deduped)


def _parse_disliked_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    deduped: list[str] = []
    seen_lower: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            continue
        cleaned = item.strip()
        if not cleaned or len(cleaned) > MAX_DISLIKED_INGREDIENT_LENGTH:
            continue
        key = cleaned.lower()
        if key not in seen_lower:
            seen_lower.add(key)
            deduped.append(cleaned)
        if len(deduped) >= MAX_DISLIKED_INGREDIENTS:
            break
    return tuple(deduped)
