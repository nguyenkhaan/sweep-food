"""Database enum values shared by all SQLAlchemy models."""

from enum import Enum


class AccountStatus(str, Enum):
    """Current account access state."""
    UNVERIFIED = "UNVERIFIED"
    ACTIVE = "ACTIVE"
    BANNED = "BANNED"


class UserRole(str, Enum):
    """Supported application roles."""

    USER = "USER"
    ADMIN = "ADMIN"


class OTPChannel(str, Enum):
    """Delivery channel for an OTP challenge."""

    SMS = "SMS"
    EMAIL = "EMAIL"


class OTPPurpose(str, Enum):
    """Operation authorized by a verified OTP grant."""

    REGISTER = "REGISTER"
    VERIFY_EMAIL = "VERIFY_EMAIL"
    CHANGE_PHONE = "CHANGE_PHONE"
    CHANGE_EMAIL = "CHANGE_EMAIL"
    RESET_PASSWORD = "RESET_PASSWORD"
    CHANGE_PASSWORD = "CHANGE_PASSWORD"
    STEP_UP_AUTH = "STEP_UP_AUTH"


class MeasurementUnit(str, Enum):
    """Canonical measurement units."""

    KG = "KG"
    GRAM = "GRAM"
    LITER = "LITER"
    ML = "ML"
    PIECE = "PIECE"
    PACK = "PACK"
    OTHER = "OTHER"


class StorageMode(str, Enum):
    """Supported ingredient storage modes."""

    ROOM_TEMPERATURE = "ROOM_TEMPERATURE"
    REFRIGERATED = "REFRIGERATED"
    FROZEN = "FROZEN"
    DRY_SHELF = "DRY_SHELF"


class ShelfLifeRuleScope(str, Enum):
    """Target type for shelf-life rules."""

    INGREDIENT = "INGREDIENT"
    CATEGORY = "CATEGORY"


class InventoryBatchType(str, Enum):
    """Inventory batch contents."""

    RAW_INGREDIENT = "RAW_INGREDIENT"
    COOKED_FOOD = "COOKED_FOOD"


class InventoryBatchStatus(str, Enum):
    """Inventory batch lifecycle state."""

    ACTIVE = "ACTIVE"
    DEPLETED = "DEPLETED"
    DISCARDED = "DISCARDED"
    ARCHIVED = "ARCHIVED"


class ExpirationSource(str, Enum):
    """Origin of a batch expiration timestamp."""

    MANUFACTURER = "MANUFACTURER"
    ESTIMATED = "ESTIMATED"
    USER_OVERRIDE = "USER_OVERRIDE"
    UNKNOWN = "UNKNOWN"


class InventorySource(str, Enum):
    """Origin of an inventory batch."""

    MANUAL = "MANUAL"
    LEFTOVER = "LEFTOVER"


class InventoryLedgerEventType(str, Enum):
    """Immutable inventory quantity mutation type."""

    INITIAL_STOCK = "INITIAL_STOCK"
    MANUAL_ADJUSTMENT = "MANUAL_ADJUSTMENT"
    MANUAL_CONSUMPTION = "MANUAL_CONSUMPTION"
    COOKING_CONSUMPTION = "COOKING_CONSUMPTION"
    DISCARDED = "DISCARDED"
    LEFTOVER_CREATED = "LEFTOVER_CREATED"
    CORRECTION = "CORRECTION"
    METADATA_UPDATED = "METADATA_UPDATED"
    MOVED = "MOVED"
    ARCHIVED = "ARCHIVED"


class RecommendationProviderType(str, Enum):
    """Recommendation provider implementation."""

    RULE_BASED_MVP = "RULE_BASED_MVP"
    XGBOOST = "XGBOOST"
    LIGHTGBM = "LIGHTGBM"


class MealSlot(str, Enum):
    """Meal-plan slot."""

    BREAKFAST = "BREAKFAST"
    LUNCH = "LUNCH"
    DINNER = "DINNER"
    SNACK = "SNACK"


class MealPlanItemStatus(str, Enum):
    """Meal-plan item lifecycle state."""

    PLANNED = "PLANNED"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"


class CookingSessionStatus(str, Enum):
    """Cooking-session lifecycle state."""

    PLANNED = "PLANNED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class CookingConsumptionMode(str, Enum):
    """Confirmed cooking-consumption mode."""

    EXACT = "EXACT"
    HALF = "HALF"
    USE_ALL_MATCHED = "USE_ALL_MATCHED"
    CUSTOM = "CUSTOM"


class ShoppingListStatus(str, Enum):
    """Shopping-list lifecycle state."""

    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class NotificationType(str, Enum):
    """Notification category."""

    EXPIRING_SOON = "EXPIRING_SOON"
    EXPIRES_TODAY = "EXPIRES_TODAY"
    EXPIRED = "EXPIRED"
    LEFTOVER_REMINDER = "LEFTOVER_REMINDER"


class NotificationStatus(str, Enum):
    """In-app notification read state."""

    UNREAD = "UNREAD"
    READ = "READ"
    DISMISSED = "DISMISSED"


class NotificationDeliveryStatus(str, Enum):
    """Push-delivery state."""

    PENDING = "PENDING"
    SENT = "SENT"
    RETRYING = "RETRYING"
    FAILED = "FAILED"


class DevicePlatform(str, Enum):
    """Registered device platform."""

    ANDROID = "ANDROID"
    IOS = "IOS"
    WEB = "WEB"
