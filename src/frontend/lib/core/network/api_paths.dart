/// REST paths, relative to `AppConfig.apiBaseUrl` (which ends in `/api`).
/// Keep the whole app pointed at these constants — see `docs/api-contract.md`.
///
/// NOTE: only `/auth/*` and `/users/*` are reconciled with the real backend
/// (see `docs/api-contract.md` §1). The rest is still the frontend's assumed
/// contract and served by `MockApiClient`.
abstract final class ApiPaths {
  // Auth — phone (E.164) + password + OTP. See api-contract.md §1.
  static const register = '/auth/register';
  static const registerResendOtp = '/auth/register/resend-otp';
  static const verifyRegister = '/auth/verify/register';
  static const login = '/auth/login';
  static const tokenRefresh = '/auth/token/refresh';
  static const logout = '/auth/logout';
  static const sessions = '/auth/sessions';
  static const passwordReset = '/auth/password/reset';
  static const passwordChange = '/auth/password/change';
  static const verifyChangePassword = '/auth/verify/change-password';

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
  static String inventoryBatchMove(String id) =>
      '/inventory/batches/$id/move';
  static String inventoryBatchLedger(String id) =>
      '/inventory/batches/$id/ledger';

  // TODO(Group D — Cooking): replace with the real leftover-creation endpoint
  // (`POST /cooking/sessions/{id}/leftovers`) once cooking is wired.
  static const cookedFood = '/pantry/cooked-food';

  // Scan / ingest
  static const scanLabel = '/scan/label';
  static const scanReceipt = '/scan/receipt';
  static const scanVoice = '/scan/voice';
  static String scanJob(String id) => '/scan/jobs/$id';
  static String scanJobConfirm(String id) => '/scan/jobs/$id/confirm';

  // Recipes (real backend) — the Dish detail screen reads from here.
  static String recipe(String id) => '/recipes/$id';

  // Suggestions / dishes (still frontend-assumed / mock)
  static const suggestions = '/suggestions/dishes';
  static String dish(String id) => '/dishes/$id';
  static String cookDish(String id) => '/dishes/$id/cook';

  // Meal plans (real backend) — no "current week" concept; FE creates/finds a
  // plan per viewed week and manages items individually. See api-contract.md §7.
  static const mealPlans = '/meal-plans'; // POST create (no trailing slash)
  static const mealPlansList = '/meal-plans/'; // GET list (trailing slash)
  static String mealPlan(String id) => '/meal-plans/$id';
  static String mealPlanItems(String planId) => '/meal-plans/$planId/items';
  static String mealPlanItem(String planId, String itemId) =>
      '/meal-plans/$planId/items/$itemId';

  // Shopping lists (real backend) — no "list all" / "active list" endpoint;
  // FE remembers the last generated list id locally. See api-contract.md §8.
  static const shoppingListsGenerate = '/shopping-lists/generate';
  static String shoppingList(String id) => '/shopping-lists/$id';
  static String shoppingListItems(String listId) =>
      '/shopping-lists/$listId/items';
  static String shoppingListItem(String listId, String itemId) =>
      '/shopping-lists/$listId/items/$itemId';

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
}
