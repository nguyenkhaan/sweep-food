"""Sweep Food SQLAlchemy metadata and table model registrations."""

from src.model.auth_session_model import AuthSessionModel
from src.model.base import Base, CreatedAtUUIDModel, TimestampedUUIDModel, UUIDModel
from src.model.cooking_consumption_model import CookingConsumptionModel
from src.model.cooking_session_model import CookingSessionModel
from src.model.device_registration_model import DeviceRegistrationModel
from src.model.favorite_menu_item_model import FavoriteMenuItemModel
from src.model.favorite_menu_model import FavoriteMenuModel
from src.model.favorite_recipe_model import FavoriteRecipeModel
from src.model.ingredient_alias_model import IngredientAliasModel
from src.model.ingredient_category_model import IngredientCategoryModel
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.inventory_ledger_entry_model import InventoryLedgerEntryModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.meal_plan_item_model import MealPlanItemModel
from src.model.meal_plan_model import MealPlanModel
from src.model.notification_model import NotificationModel
from src.model.recipe_ingredient_model import RecipeIngredientModel
from src.model.recipe_model import RecipeModel
from src.model.recommendation_item_model import RecommendationItemModel
from src.model.recommendation_run_model import RecommendationRunModel
from src.model.shelf_life_rule_model import ShelfLifeRuleModel
from src.model.shopping_list_item_model import ShoppingListItemModel
from src.model.shopping_list_model import ShoppingListModel
from src.model.user_model import UserModel
from src.model.user_notification_preference_model import UserNotificationPreferenceModel

__all__ = [
    "AuthSessionModel",
    "Base",
    "CookingConsumptionModel",
    "CookingSessionModel",
    "CreatedAtUUIDModel",
    "DeviceRegistrationModel",
    "FavoriteMenuItemModel",
    "FavoriteMenuModel",
    "FavoriteRecipeModel",
    "IngredientAliasModel",
    "IngredientCategoryModel",
    "InventoryBatchModel",
    "InventoryLedgerEntryModel",
    "MasterIngredientModel",
    "MealPlanItemModel",
    "MealPlanModel",
    "NotificationModel",
    "RecipeIngredientModel",
    "RecipeModel",
    "RecommendationItemModel",
    "RecommendationRunModel",
    "ShelfLifeRuleModel",
    "ShoppingListItemModel",
    "ShoppingListModel",
    "TimestampedUUIDModel",
    "UUIDModel",
    "UserModel",
    "UserNotificationPreferenceModel",
]
