/// REST paths, relative to `AppConfig.apiBaseUrl` (which ends in `/api`).
/// Keep the whole app pointed at these constants — see `docs/api-contract.md`.
///
/// Every path in this file is backed by the current FastAPI OpenAPI document.
abstract final class ApiPaths {
  // Auth — phone (E.164) + password + OTP. See api-contract.md §1.
  static const register = '/auth/register';
  static const registerResendOtp = '/auth/register/resend-otp';
  static const verifyRegister = '/auth/verify/register';
  static const login = '/auth/login';
  static const tokenRefresh = '/auth/token/refresh';
  static const logout = '/auth/logout';
  static const sessions = '/auth/sessions';
  static String session(String id) => '/auth/sessions/$id';
  static const passwordReset = '/auth/password/reset';
  static const passwordChange = '/auth/password/change';
  static const verifyChangePassword = '/auth/verify/change-password';

  // Service readiness
  static const aiHealth = '/health/ai';

  // Current user
  static const me = '/users/me';
  static const profile = '/users/profile';
  static const meEmailRequest = '/users/me/email/request-verification';
  static const meEmailVerify = '/users/me/email/verify';
  static const mePhoneRequest = '/users/me/phone/request-change';
  static const mePhoneConfirm = '/users/me/phone/confirm-change';

  // Catalog
  static const ingredients = '/ingredients';
  static String ingredient(String id) => '/ingredients/$id';

  // Inventory (real backend) — pantry screen reads/writes here. See
  // api-contract.md §2.
  static const inventoryBatches = '/inventory/batches';
  static String inventoryBatch(String id) => '/inventory/batches/$id';
  static String inventoryBatchAdjustments(String id) =>
      '/inventory/batches/$id/adjustments';
  static String inventoryBatchConsume(String id) =>
      '/inventory/batches/$id/consume';
  static String inventoryBatchMove(String id) => '/inventory/batches/$id/move';
  // Immutable quantity-change history. Filter to one batch with `?batch_id=`.
  static const inventoryLedger = '/inventory/ledger';

  // Cooking (real backend) — the 3-step flow: preview -> session -> complete.
  // Always requires a meal_plan_item_id. See api-contract.md §6.
  static const cookingPreview = '/cooking/preview';
  static const cookingSessions = '/cooking/sessions';
  static String cookingSessionComplete(String id) =>
      '/cooking/sessions/$id/complete';
  static String cookingSessionLeftovers(String id) =>
      '/cooking/sessions/$id/leftovers';
  static const cookingHistory = '/cooking/history';
  static String cookingHistoryDetail(String id) => '/cooking/history/$id';

  // Extractions (real backend) — see api-contract.md §11
  static const extractionOcrLabel = '/extractions/ocr/label';
  static const extractionOcrInvoice = '/extractions/ocr/invoice';
  static const extractionAsr = '/extractions/asr';
  static const extractionText = '/extractions/text';
  static String extractionBarcode(String barcode) =>
      '/extractions/barcode?barcode=$barcode';

  // Recipes (real backend) — search & detail
  static const recipes = '/recipes';
  static String recipe(String id) => '/recipes/$id';
  static String recipeFavorite(String id) => '/recipes/$id/favorite';

  // Favorites (real backend) — see api-contract.md §9
  static const favoriteRecipes = '/favorite-recipes';
  static const favoriteMenus = '/favorite-menus';
  static String favoriteMenu(String id) => '/favorite-menus/$id';
  static String favoriteMenuItems(String menuId) =>
      '/favorite-menus/$menuId/items';
  static String favoriteMenuItem(String menuId, String itemId) =>
      '/favorite-menus/$menuId/items/$itemId';

  // AI recommendations (structured SweepFood AI v2 request/response)
  static const recommendations = '/recommendations';

  // Meal plans (real backend) — no "current week" concept; FE creates/finds a
  // plan per viewed week and manages items individually. See api-contract.md §7.
  static const mealPlans = '/meal-plans'; // POST create (no trailing slash)
  static const mealPlansList = '/meal-plans/'; // GET list (trailing slash)
  static String mealPlan(String id) => '/meal-plans/$id';
  static String mealPlanItems(String planId) => '/meal-plans/$planId/items';
  static String mealPlanItem(String planId, String itemId) =>
      '/meal-plans/$planId/items/$itemId';

  // Shopping lists (real backend)
  static const shoppingLists = '/shopping-lists';
  static const shoppingListsGenerate = '/shopping-lists/generate';
  static String shoppingList(String id) => '/shopping-lists/$id';
  static String shoppingListItems(String listId) =>
      '/shopping-lists/$listId/items';
  static String shoppingListItem(String listId, String itemId) =>
      '/shopping-lists/$listId/items/$itemId';

  // Freshness (FreshCheck sensory assessment)
  static const freshnessQuestions = '/freshness/questions';
  static String freshnessAssessment(String batchId) =>
      '/freshness/batches/$batchId/assessment';
  static const freshnessPreview = '/freshness/previews';

  // Rating & Feedback
  static const rating = '/rating';

  // Devices / notifications
  static const devices = '/users/me/devices';
  static String device(String deviceId) => '/users/me/devices/$deviceId';
  static const notifications = '/notifications';
  static String notification(String id) => '/notifications/$id';

  // Subscription
  static const subscription = '/subscription';
  static const premiumInterest = '/subscription/premium-interest';

  // Reports
  static const reportsWasteReduction = '/reports/waste-reduction';
  static const inventoryWaste = '/inventory/waste';
}
