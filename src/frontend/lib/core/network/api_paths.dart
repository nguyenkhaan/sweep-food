/// REST paths, relative to `AppConfig.apiBaseUrl` (which already ends in
/// `/api/v1`). Keep the whole app pointed at these constants — see plan.md §9.
///
/// NOTE: endpoint naming still needs reconciling with the backend team
/// (they stubbed `/ingestion/ocr/*`, `/recipes/recommend`). This file is the
/// frontend's assumed contract; `docs/api-contract.md` (M6) makes it shared.
abstract final class ApiPaths {
  // Auth
  static const register = '/auth/register';
  static const login = '/auth/login';
  static const refresh = '/auth/refresh';
  static const logout = '/auth/logout';
  static const me = '/auth/me';

  /// A-04. Frontend-assumed; not in the backend stub yet (see file header note).
  static const forgotPassword = '/auth/forgot-password';

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

  // Suggestions / dishes
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
