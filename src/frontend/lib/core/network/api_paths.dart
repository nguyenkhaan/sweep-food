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

  // Pantry
  static const pantryItems = '/pantry/items';
  static const pantryItemsBatch = '/pantry/items:batch';
  static String pantryItem(String id) => '/pantry/items/$id';
  static String pantryItemConsume(String id) => '/pantry/items/$id/consume';
  static const pantrySummary = '/pantry/summary';
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

  // Meal plan
  static const mealPlans = '/meal-plans';
  static String mealPlan(String weekStart) => '/meal-plans/$weekStart';

  // Shopping list
  static const shoppingLists = '/shopping-lists';
  static const shoppingListsGenerate = '/shopping-lists/generate';
  static String shoppingList(String id) => '/shopping-lists/$id';
  static String shoppingListItem(String listId, String itemId) =>
      '/shopping-lists/$listId/items/$itemId';

  // Devices / notifications
  static const devices = '/devices';
  static String device(String token) => '/devices/$token';
  static const notifications = '/notifications';
  static String notificationRead(String id) => '/notifications/$id/read';

  // Subscription
  static const subscription = '/subscription';
  static const premiumInterest = '/subscription/premium-interest';

  // Reports
  static const reportsWasteReduction = '/reports/waste-reduction';
}
