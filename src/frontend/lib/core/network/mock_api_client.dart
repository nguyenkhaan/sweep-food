import 'dart:async';
import 'dart:convert';

import 'package:flutter/services.dart' show rootBundle;
import 'package:sweepfood/core/config/app_constants.dart';
import 'package:sweepfood/core/error/app_exception.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/core/utils/logger.dart';

/// [ApiClient] that serves canned JSON from `assets/mock/*.json` with a small
/// artificial delay. Used when `AppConfig.backend == Backend.mock`.
///
/// - **GET** → returns the mapped fixture.
/// - **POST/PUT/PATCH** → echoes the request body back, adding an `id` if absent
///   (enough for optimistic-UI round trips in the mock).
/// - **DELETE** → returns `null`.
/// - Unmapped GET paths throw [MockFixtureException].
///
/// Fixture files are fleshed out per milestone (M1+). Add new mappings to
/// [_fixtures] as endpoints come online.
class MockApiClient implements ApiClient {
  MockApiClient({Duration? latency})
      : _latency = latency ?? AppConstants.mockLatency;

  final Duration _latency;
  final _cache = <String, dynamic>{};
  var _autoId = 1000;

  /// Path prefix → fixture asset (without `assets/mock/` or `.json`).
  ///
  /// NOTE: `/auth/*` and `/users/*` are intentionally absent — auth now runs
  /// against the real backend only. Use `config/live.json` (`BACKEND=live`)
  /// to exercise the sign-in flow.
  static final Map<String, String> _fixtures = {
    ApiPaths.ingredients: 'ingredients',
    ApiPaths.inventoryBatches: 'inventory_batches',
    ApiPaths.recommendations: 'recommendations',
    ApiPaths.suggestions: 'recommendations',
    '/recipes/': 'recipe',
    ApiPaths.notifications: 'notifications',
    ApiPaths.subscription: 'subscription',
    ApiPaths.reportsWasteReduction: 'waste_reduction_report',
    ApiPaths.favoriteRecipes: 'favorite_recipes',
    ApiPaths.favoriteMenus: 'favorite_menus',
    // M4 multimodal ingestion / Section G Extractions — `postMultipart` returns these canned ScanJobs.
    ApiPaths.extractionOcrLabel: 'scan_label',
    ApiPaths.extractionOcrInvoice: 'scan_receipt',
    ApiPaths.extractionAsr: 'scan_voice',
    ApiPaths.scanLabel: 'scan_label',
    ApiPaths.scanReceipt: 'scan_receipt',
    ApiPaths.scanVoice: 'scan_voice',
  };

  /// Read-shaped POST endpoints that return a canned fixture instead of echoing
  /// the request body (dish scoring). Matched exact-or-prefix.
  static final Map<String, String> _postFixtures = {
    ApiPaths.recommendations: 'recommendations',
    ApiPaths.suggestions: 'recommendations',
  };

  String? _postFixtureKey(String path) {
    for (final e in _postFixtures.entries) {
      if (path == e.key || path.startsWith(e.key)) return e.value;
    }
    return null;
  }

  Future<dynamic> _load(String path) {
    final entry = _fixtures.entries.firstWhere(
      (e) => path == e.key || path.startsWith(e.key),
      orElse: () => throw MockFixtureException('Không có fixture cho "$path"'),
    );
    return _loadKey(entry.value);
  }

  Future<dynamic> _loadKey(String key) async {
    if (_cache.containsKey(key)) return _cache[key];
    try {
      final raw = _fillDates(await rootBundle.loadString('assets/mock/$key.json'));
      final decoded = jsonDecode(raw);
      _cache[key] = decoded;
      return decoded;
    } catch (e) {
      throw MockFixtureException('Fixture "assets/mock/$key.json" lỗi: $e');
    }
  }

  dynamic _clone(dynamic v) => jsonDecode(jsonEncode(v));

  /// Replaces `{{today}}` / `{{today+N}}` / `{{today-N}}` — optionally with a
  /// `THH:MM` suffix (`{{today-1T19:00}}`) — with an ISO datetime so fixtures
  /// stay demo-stable regardless of run date.
  static final _dateToken =
      RegExp(r'\{\{today([+-]\d+)?(?:T(\d{2}):(\d{2}))?\}\}');
  String _fillDates(String raw) {
    final today = DateTime.now();
    return raw.replaceAllMapped(_dateToken, (m) {
      final offset = int.tryParse(m.group(1) ?? '0') ?? 0;
      final hh = int.tryParse(m.group(2) ?? '0') ?? 0;
      final mm = int.tryParse(m.group(3) ?? '0') ?? 0;
      final d = DateTime(today.year, today.month, today.day + offset, hh, mm);
      return d.toIso8601String();
    });
  }

  dynamic _echo(Object? body) {
    if (body is Map) {
      final m = Map<String, dynamic>.from(body);
      m.putIfAbsent('id', () => 'mock-${_autoId++}');
      return m;
    }
    return body;
  }

  // --- Inventory batch emulation -------------------------------------------
  //
  // `/inventory/batches` mutations (create/adjust/consume/move/patch/delete)
  // need to keep returning a full batch shape (PantryItemDto has several
  // required fields), not a plain echo of the request body. This mirrors just
  // enough of the real quantity/status bookkeeping for the mock to stay usable
  // for browsing/demoing the pantry without a backend.

  static const _inventoryBatchesPath = ApiPaths.inventoryBatches;

  Future<List<Map<String, dynamic>>> _inventoryItems() async {
    final doc = await _loadKey('inventory_batches') as Map<String, dynamic>;
    return (doc['items'] as List).cast<Map<String, dynamic>>();
  }

  Future<Map<String, dynamic>> _inventoryBatchById(String id) async {
    final items = await _inventoryItems();
    return _clone(
      items.firstWhere(
        (i) => i['id'] == id,
        orElse: () =>
            throw MockFixtureException('Không có inventory batch "$id"'),
      ),
    ) as Map<String, dynamic>;
  }

  /// Applies [apply] to the cached batch and writes it back so later GETs see it.
  Future<Map<String, dynamic>> _mutateInventoryBatch(
    String id,
    Map<String, dynamic> Function(Map<String, dynamic> batch) apply,
  ) async {
    final items = await _inventoryItems();
    final idx = items.indexWhere((i) => i['id'] == id);
    if (idx < 0) {
      throw MockFixtureException('Không có inventory batch "$id"');
    }
    final updated = apply(Map<String, dynamic>.from(items[idx]));
    updated['updated_at'] = DateTime.now().toIso8601String();
    items[idx] = updated;
    return _clone(updated) as Map<String, dynamic>;
  }

  Map<String, dynamic> _createInventoryBatch(Map<String, dynamic> body) {
    final now = DateTime.now().toIso8601String();
    final quantity = body['quantity'];
    return {
      'id': 'mock-${_autoId++}',
      'master_ingredient_id': body['master_ingredient_id'],
      'custom_name': body['custom_name'],
      'ingredient_name': body['custom_name'] ?? 'Nguyên liệu',
      'batch_type': 'RAW_INGREDIENT',
      'initial_quantity': quantity,
      'current_quantity': quantity,
      'unit': body['unit'],
      'storage_mode': body['storage_mode'],
      'status': 'ACTIVE',
      'purchased_at': body['purchased_at'],
      'packaged_at': body['packaged_at'],
      'stored_at': body['stored_at'],
      'expires_at': body['expires_at'],
      'expiration_source': body['expires_at'] != null ? 'MANUFACTURER' : 'UNKNOWN',
      'unit_cost': body['unit_cost'],
      'note': body['note'],
      'media_url': body['media_url'],
      'source': 'MANUAL',
      'source_cooking_session_id': null,
      'created_at': now,
      'updated_at': now,
      'archived_at': null,
    };
  }

  /// `/inventory/batches/{id}[/action]` → the `{id}` segment, or null when the
  /// path is the bare collection.
  String? _inventoryBatchIdFromPath(String path) {
    if (!path.startsWith('$_inventoryBatchesPath/')) return null;
    final rest = path.substring('$_inventoryBatchesPath/'.length);
    return rest.split('/').first;
  }

  // --- Meal plan emulation --------------------------------------------------
  //
  // The backend has no "current week" / seed-data concept — plans and items
  // are plain CRUD, same as a fresh backend user would see. Kept as an
  // in-memory list for the mock session (starts empty, not persisted).

  final _mealPlans = <Map<String, dynamic>>[];
  static final _mealPlanItemPath = RegExp(r'^/meal-plans/([^/]+)/items/([^/]+)$');

  Map<String, dynamic> _findMealPlan(String id) => _mealPlans.firstWhere(
        (p) => p['id'] == id,
        orElse: () => throw MockFixtureException('Không có meal plan "$id"'),
      );

  Map<String, dynamic> _createMealPlan(Map<String, dynamic> body) {
    final plan = {
      'id': 'mock-plan-${_autoId++}',
      'name': body['name'],
      'starts_on': body['starts_on'],
      'ends_on': body['ends_on'],
      'items': <Map<String, dynamic>>[],
    };
    _mealPlans.add(plan);
    return plan;
  }

  Map<String, dynamic> _createMealPlanItem(
    String planId,
    Map<String, dynamic> body,
  ) {
    final item = {
      'id': 'mock-item-${_autoId++}',
      'recipe_id': body['recipe_id'],
      'recipe_name': null,
      'planned_for': body['planned_for'],
      'meal_slot': body['meal_slot'],
      'servings': body['servings'],
      'status': 'PLANNED',
    };
    (_findMealPlan(planId)['items'] as List).add(item);
    return item;
  }

  Map<String, dynamic> _updateMealPlanItem(
    String planId,
    String itemId,
    Map<String, dynamic> body,
  ) {
    final items = (_findMealPlan(planId)['items'] as List)
        .cast<Map<String, dynamic>>();
    final idx = items.indexWhere((i) => i['id'] == itemId);
    if (idx < 0) {
      throw MockFixtureException('Không có meal-plan item "$itemId"');
    }
    final updated = {...items[idx], ...body};
    items[idx] = updated;
    return updated;
  }

  void _deleteMealPlanItem(String planId, String itemId) {
    (_findMealPlan(planId)['items'] as List)
        .removeWhere((i) => (i as Map)['id'] == itemId);
  }

  // --- Shopping list emulation -----------------------------------------------
  //
  // The backend has no "list all" / "active list" endpoint — only
  // generate-from-plan and read-by-id. `generate` seeds a fresh list from a
  // canned item set (the mock has no real recipe-ingredient data to compute
  // quantities from the actual plan); reads/writes after that operate on the
  // in-memory copy so check/add/delete persist for the session.

  final _shoppingLists = <Map<String, dynamic>>[];
  static final _shoppingListItemPath =
      RegExp(r'^/shopping-lists/([^/]+)/items/([^/]+)$');

  Map<String, dynamic> _findShoppingList(String id) => _shoppingLists.firstWhere(
        (l) => l['id'] == id,
        orElse: () =>
            throw MockFixtureException('Không có shopping list "$id"'),
      );

  Future<Map<String, dynamic>> _generateShoppingList(
    Map<String, dynamic>? body,
  ) async {
    final seed = await _loadKey('shopping_list') as Map<String, dynamic>;
    final items = (seed['items'] as List)
        .map((e) => {...e as Map<String, dynamic>, 'id': 'mock-sli-${_autoId++}'})
        .toList();
    final list = {
      'id': 'mock-list-${_autoId++}',
      'meal_plan_id': body?['meal_plan_id'],
      'status': 'ACTIVE',
      'generated_at': DateTime.now().toIso8601String(),
      'items': items,
    };
    _shoppingLists.add(list);
    return list;
  }

  Map<String, dynamic> _createShoppingListItem(
    String listId,
    Map<String, dynamic> body,
  ) {
    final quantity = body['quantity'];
    final item = {
      'id': 'mock-sli-${_autoId++}',
      'master_ingredient_id': body['master_ingredient_id'],
      'custom_name': body['custom_name'],
      'name': body['custom_name'] ?? 'Món mới',
      'required_quantity': quantity,
      'available_quantity': 0,
      'missing_quantity': quantity,
      'unit': body['unit'],
      'estimated_cost': body['estimated_cost'],
      'is_checked': false,
      'is_generated': false,
      'source_recipe_ids': <String>[],
      'inventory_batch_id': null,
    };
    (_findShoppingList(listId)['items'] as List).add(item);
    return item;
  }

  Map<String, dynamic> _updateShoppingListItem(
    String listId,
    String itemId,
    Map<String, dynamic> body,
  ) {
    final items = (_findShoppingList(listId)['items'] as List)
        .cast<Map<String, dynamic>>();
    final idx = items.indexWhere((i) => i['id'] == itemId);
    if (idx < 0) {
      throw MockFixtureException('Không có shopping-list item "$itemId"');
    }
    final updated = Map<String, dynamic>.from(items[idx]);
    if (body.containsKey('checked')) updated['is_checked'] = body['checked'];
    if (body.containsKey('quantity')) {
      updated['missing_quantity'] = body['quantity'];
    }
    if (body.containsKey('estimated_cost')) {
      updated['estimated_cost'] = body['estimated_cost'];
    }
    if (body['purchase'] != null) {
      updated['inventory_batch_id'] = 'mock-${_autoId++}';
    }
    items[idx] = updated;
    return updated;
  }

  void _deleteShoppingListItem(String listId, String itemId) {
    (_findShoppingList(listId)['items'] as List)
        .removeWhere((i) => (i as Map)['id'] == itemId);
  }

  // --- Favorites emulation --------------------------------------------------
  final _favoriteRecipeIds = <String>{'d1'};
  final _favoriteMenus = <Map<String, dynamic>>[
    {
      'id': 'mock-menu-1',
      'name': 'Bữa cơm gia đình',
      'description': 'Các món canh và mặn quen thuộc',
      'item_count': 1,
      'items': <Map<String, dynamic>>[
        {
          'id': 'mock-fav-item-1',
          'recipe_id': 'd1',
          'recipe_name': 'Canh chua cá lóc',
          'recipe_image_url': null,
          'created_at': '2026-03-01T08:00:00Z',
        },
      ],
      'created_at': '2026-03-01T08:00:00Z',
      'updated_at': '2026-03-01T08:00:00Z',
    },
  ];

  Map<String, dynamic> _findFavoriteMenu(String id) => _favoriteMenus.firstWhere(
        (m) => m['id'] == id,
        orElse: () => throw MockFixtureException('Không có favorite menu "$id"'),
      );

  Map<String, dynamic> _createFavoriteMenu(Map<String, dynamic> body) {
    final now = DateTime.now().toIso8601String();
    final menu = {
      'id': 'mock-fav-menu-${_autoId++}',
      'name': body['name'],
      'description': body['description'],
      'item_count': 0,
      'items': <Map<String, dynamic>>[],
      'created_at': now,
      'updated_at': now,
    };
    _favoriteMenus.add(menu);
    return menu;
  }

  Map<String, dynamic> _updateFavoriteMenu(String menuId, Map<String, dynamic> body) {
    final menu = _findFavoriteMenu(menuId);
    if (body.containsKey('name')) menu['name'] = body['name'];
    if (body.containsKey('description')) menu['description'] = body['description'];
    menu['updated_at'] = DateTime.now().toIso8601String();
    return menu;
  }

  void _deleteFavoriteMenu(String menuId) {
    _favoriteMenus.removeWhere((m) => m['id'] == menuId);
  }

  Map<String, dynamic> _addFavoriteMenuItem(String menuId, Map<String, dynamic> body) {
    final menu = _findFavoriteMenu(menuId);
    final recipeId = body['recipe_id'] as String;
    final item = {
      'id': 'mock-fav-item-${_autoId++}',
      'recipe_id': recipeId,
      'recipe_name': recipeId == 'd1' ? 'Canh chua cá lóc' : 'Món ngon #$recipeId',
      'recipe_image_url': null,
      'created_at': DateTime.now().toIso8601String(),
    };
    (menu['items'] as List).add(item);
    menu['item_count'] = (menu['items'] as List).length;
    return item;
  }

  void _deleteFavoriteMenuItem(String menuId, String itemId) {
    final menu = _findFavoriteMenu(menuId);
    (menu['items'] as List).removeWhere((i) => (i as Map)['id'] == itemId);
    menu['item_count'] = (menu['items'] as List).length;
  }


  // --- Cooking emulation -------------------------------------------------
  //
  // The backend's 3-step flow always goes through a meal-plan item. The mock
  // resolves the item's recipe against the single canned `recipe.json`
  // fixture and matches its ingredients against the cached inventory batches
  // by name (best-effort — no real catalog to join master_ingredient_id
  // against here).

  final _cookingSessions = <Map<String, dynamic>>[];

  Map<String, dynamic>? _findMealPlanItem(String itemId) {
    for (final plan in _mealPlans) {
      for (final item in (plan['items'] as List).cast<Map<String, dynamic>>()) {
        if (item['id'] == itemId) return item;
      }
    }
    return null;
  }

  /// Matches `recipe.json`'s ingredients against the cached inventory batches
  /// by name. Shared by preview (read-only) and complete (which also applies
  /// the deduction), so a later re-fetch of the pantry stays consistent with
  /// what preview already showed the user.
  Future<({List<Map<String, dynamic>> proposed, List<Map<String, dynamic>> missing})>
      _matchIngredients(
    Map<String, dynamic> recipe,
    List<Map<String, dynamic>> batches,
  ) async {
    final proposed = <Map<String, dynamic>>[];
    final missing = <Map<String, dynamic>>[];
    for (final ing in (recipe['ingredients'] as List).cast<Map<String, dynamic>>()) {
      final ingName = (ing['name'] as String).toLowerCase();
      final match = batches.cast<Map<String, dynamic>?>().firstWhere(
            (b) =>
                (b!['ingredient_name'] as String?)?.toLowerCase() == ingName ||
                (b['custom_name'] as String?)?.toLowerCase() == ingName,
            orElse: () => null,
          );
      if (match != null) {
        proposed.add({
          'recipe_ingredient_id': ing['recipe_ingredient_id'],
          'master_ingredient_id': ing['master_ingredient_id'],
          'batch_id': match['id'],
          'quantity': ing['required_quantity'],
          'unit': ing['unit'],
        });
      } else if (ing['is_optional'] != true) {
        missing.add({
          'recipe_ingredient_id': ing['recipe_ingredient_id'],
          'ingredient_name': ing['name'],
          'missing_quantity': ing['required_quantity'],
          'unit': ing['unit'],
        });
      }
    }
    return (proposed: proposed, missing: missing);
  }

  Future<Map<String, dynamic>> _cookingPreview(Map<String, dynamic> body) async {
    final itemId = body['meal_plan_item_id'] as String;
    final item = _findMealPlanItem(itemId);
    if (item == null) {
      throw MockFixtureException('Không có meal-plan item "$itemId"');
    }
    final recipe = await _loadKey('recipe') as Map<String, dynamic>;
    final matched = await _matchIngredients(recipe, await _inventoryItems());
    return {
      'recipe_id': recipe['id'],
      'recipe_name': recipe['name'],
      'servings': item['servings'],
      'proposed_deductions': matched.proposed,
      'missing_ingredients': matched.missing,
    };
  }

  Map<String, dynamic> _createCookingSession(Map<String, dynamic> body) {
    final session = {
      'id': 'mock-session-${_autoId++}',
      'meal_plan_item_id': body['meal_plan_item_id'],
      'status': 'PLANNED',
    };
    _cookingSessions.add(session);
    return session;
  }

  /// Applies the same deduction the client already displayed (see
  /// `CookingController._buildResult`) to the cached inventory batches, so a
  /// later re-fetch of the pantry doesn't "snap back" to un-deducted
  /// quantities.
  Future<Map<String, dynamic>> _completeCookingSession(
    String sessionId,
    Map<String, dynamic> body,
  ) async {
    final session = _cookingSessions.firstWhere(
      (s) => s['id'] == sessionId,
      orElse: () =>
          throw MockFixtureException('Không có cooking session "$sessionId"'),
    );
    session['status'] = 'COMPLETED';

    final item = _findMealPlanItem(session['meal_plan_item_id'] as String);
    if (item == null) return session;
    final recipe = await _loadKey('recipe') as Map<String, dynamic>;
    final items = await _inventoryItems();
    final matched = await _matchIngredients(recipe, items);

    final mode = body['consumption_mode'] as String?;
    final consumptions =
        (body['consumptions'] as List?)?.cast<Map<String, dynamic>>();

    for (final d in matched.proposed) {
      final idx = items.indexWhere((b) => b['id'] == d['batch_id']);
      if (idx < 0) continue;
      final batch = items[idx];
      final current = (batch['current_quantity'] as num).toDouble();
      final proposedQty = (d['quantity'] as num).toDouble();
      final used = switch (mode) {
        'HALF' => proposedQty / 2,
        'USE_ALL_MATCHED' => current,
        'CUSTOM' => (consumptions
                    ?.firstWhere(
                      (c) =>
                          c['inventory_batch_id'] == d['batch_id'] &&
                          c['recipe_ingredient_id'] == d['recipe_ingredient_id'],
                      orElse: () => const {},
                    )['quantity'] as num?)
                ?.toDouble() ??
            proposedQty,
        _ => proposedQty, // EXACT
      };
      final next = (current - used).clamp(0, double.infinity);
      batch['current_quantity'] = next;
      batch['status'] = next <= 0 ? 'DEPLETED' : 'ACTIVE';
      batch['updated_at'] = DateTime.now().toIso8601String();
    }
    return session;
  }

  /// Matches the real backend's narrower `CookedLeftoverResponseDTO` shape
  /// (not a general inventory batch — see `cooked_leftover_dto.dart`).
  Map<String, dynamic> _createLeftoverBatch(
    String sessionId,
    Map<String, dynamic> body,
  ) {
    final now = DateTime.now().toIso8601String();
    return {
      'batch_id': 'mock-${_autoId++}',
      'cooking_session_id': sessionId,
      'batch_type': 'COOKED_FOOD',
      'quantity': body['quantity'],
      'unit': body['unit'],
      'storage_mode': body['storage_mode'] ?? 'REFRIGERATED',
      'expires_at': body['expires_at'],
      'created_at': now,
    };
  }

  // ---------------------------------------------------------------------------

  @override
  Future<dynamic> get(String path, {Map<String, dynamic>? query}) async {
    await Future<void>.delayed(_latency);
    log.d('MOCK GET $path ${query ?? ''}');
    final batchId = _inventoryBatchIdFromPath(path);
    if (batchId != null) return _inventoryBatchById(batchId);
    if (path == ApiPaths.mealPlansList) {
      return {
        'items': _mealPlans,
        'total': _mealPlans.length,
        'limit': 200,
        'offset': 0,
      };
    }
    if (path.startsWith('${ApiPaths.mealPlans}/')) {
      return _clone(_findMealPlan(path.substring('${ApiPaths.mealPlans}/'.length)));
    }
    if (path.startsWith('/shopping-lists/') && !path.contains('/items')) {
      return _clone(_findShoppingList(path.substring('/shopping-lists/'.length)));
    }
    if (path == ApiPaths.favoriteRecipes) {
      final items = _favoriteRecipeIds.map((id) => {
        'recipe_id': id,
        'recipe_name': id == 'd1' ? 'Canh chua cá lóc' : 'Món ngon #$id',
        'recipe_image_url': null,
        'favorited_at': '2026-03-01T08:00:00Z',
      }).toList();
      return {
        'items': items,
        'total': items.length,
        'limit': 50,
        'offset': 0,
      };
    }
    if (path == ApiPaths.favoriteMenus) {
      final items = _favoriteMenus.map((m) => {
        'id': m['id'],
        'name': m['name'],
        'description': m['description'],
        'item_count': (m['items'] as List).length,
        'created_at': m['created_at'],
        'updated_at': m['updated_at'],
      }).toList();
      return {
        'items': items,
      };
    }
    if (path.startsWith('${ApiPaths.favoriteMenus}/')) {
      final menuId = path.substring('${ApiPaths.favoriteMenus}/'.length);
      return _clone(_findFavoriteMenu(menuId));
    }
    if (path.startsWith('/recipes/')) {
      final doc = await _loadKey('recipe') as Map<String, dynamic>;
      final recipeId = path.substring('/recipes/'.length);
      final recipe = Map<String, dynamic>.from(doc);
      recipe['id'] = recipeId;
      if (recipeId == 'd2') {
        recipe['name'] = 'Canh chua cá lóc';
      } else if (recipeId == 'd3') {
        recipe['name'] = 'Trứng chiên hành lá';
      } else if (recipeId == 'd4') {
        recipe['name'] = 'Thịt ba chỉ rang cháy cạnh';
      }
      return _clone(recipe);
    }
    return _clone(await _load(path));
  }

  @override
  Future<dynamic> post(
    String path, {
    Object? body,
    Map<String, dynamic>? query,
    Map<String, String>? headers,
  }) async {
    await Future<void>.delayed(_latency);
    log.d('MOCK POST $path');
    if (path == _inventoryBatchesPath) {
      return _createInventoryBatch(body as Map<String, dynamic>);
    }
    if (path == ApiPaths.mealPlans) {
      return _createMealPlan(body as Map<String, dynamic>);
    }
    if (path.startsWith('${ApiPaths.mealPlans}/') && path.endsWith('/items')) {
      final planId = path.split('/')[2];
      return _createMealPlanItem(planId, body as Map<String, dynamic>);
    }
    if (path == ApiPaths.shoppingListsGenerate) {
      return _generateShoppingList(body as Map<String, dynamic>?);
    }
    if (path.startsWith('/shopping-lists/') && path.endsWith('/items')) {
      final listId = path.split('/')[2];
      return _createShoppingListItem(listId, body as Map<String, dynamic>);
    }
    if (path == ApiPaths.favoriteMenus) {
      return _createFavoriteMenu(body as Map<String, dynamic>);
    }
    if (path.startsWith('${ApiPaths.favoriteMenus}/') && path.endsWith('/items')) {
      final menuId = path.split('/')[2];
      return _addFavoriteMenuItem(menuId, body as Map<String, dynamic>);
    }
    if (path == ApiPaths.cookingPreview) {
      return _cookingPreview(body as Map<String, dynamic>);
    }
    if (path == ApiPaths.cookingSessions) {
      return _createCookingSession(body as Map<String, dynamic>);
    }
    if (path.startsWith('${ApiPaths.cookingSessions}/') && path.endsWith('/complete')) {
      final sessionId = path.split('/')[3];
      return _completeCookingSession(sessionId, body as Map<String, dynamic>);
    }
    if (path.startsWith('${ApiPaths.cookingSessions}/') && path.endsWith('/leftovers')) {
      final sessionId = path.split('/')[3];
      return _createLeftoverBatch(sessionId, body as Map<String, dynamic>);
    }
    final batchId = _inventoryBatchIdFromPath(path);
    if (batchId != null && path.endsWith('/adjustments')) {
      final b = body as Map<String, dynamic>;
      return _mutateInventoryBatch(batchId, (batch) {
        final delta = b['event_type'] == 'DISCARDED'
            ? -(batch['current_quantity'] as num)
            : (b['quantity_delta'] as num);
        final next = (batch['current_quantity'] as num) + delta;
        batch['current_quantity'] = next < 0 ? 0 : next;
        batch['status'] = next <= 0
            ? (b['event_type'] == 'DISCARDED' ? 'DISCARDED' : 'DEPLETED')
            : 'ACTIVE';
        return batch;
      });
    }
    if (batchId != null && path.endsWith('/consume')) {
      final b = body as Map<String, dynamic>;
      return _mutateInventoryBatch(batchId, (batch) {
        final next = (batch['current_quantity'] as num) - (b['quantity'] as num);
        batch['current_quantity'] = next < 0 ? 0 : next;
        batch['status'] = next <= 0 ? 'DEPLETED' : 'ACTIVE';
        return batch;
      });
    }
    if (batchId != null && path.endsWith('/move')) {
      final b = body as Map<String, dynamic>;
      return _mutateInventoryBatch(
        batchId,
        (batch) => batch..['storage_mode'] = b['storage_mode'],
      );
    }
    if (path.startsWith('/extractions/barcode')) {
      final uri = Uri.parse(path);
      final barcode = uri.queryParameters['barcode'] ?? '8934567890123';
      return {
        'request_id': 'req-barcode-mock',
        'status': 'SUCCEEDED',
        'provider': 'MOCK_BARCODE',
        'raw_text': 'Product found for barcode $barcode',
        'fields': {
          'barcode': barcode,
          'product_name': 'Sữa tươi tiệt trùng',
          'brand': 'Vinamilk',
          'category': 'Trứng & Sữa',
          'ingredient_name': 'Sữa tươi',
          'quantity': 1.0,
          'unit': 'LITER',
          'expires_at': null,
          'price': 35000.0,
          'currency': 'VND',
        },
        'confidence': {'product_name': 0.90},
        'warnings': <String>[],
        'persisted': false,
      };
    }
    final fixture = _postFixtureKey(path);
    if (fixture != null) return _clone(await _loadKey(fixture));
    return _echo(body);
  }

  @override
  Future<dynamic> put(String path, {Object? body}) async {
    await Future<void>.delayed(_latency);
    log.d('MOCK PUT $path');
    if (path.startsWith('/recipes/') && path.endsWith('/favorite')) {
      final recipeId = path.split('/')[2];
      _favoriteRecipeIds.add(recipeId);
      return {'recipe_id': recipeId, 'is_favorite': true};
    }
    return _echo(body);
  }

  @override
  Future<dynamic> patch(
    String path, {
    Object? body,
    Map<String, String>? headers,
  }) async {
    await Future<void>.delayed(_latency);
    log.d('MOCK PATCH $path');
    if (path.startsWith('${ApiPaths.favoriteMenus}/')) {
      final menuId = path.substring('${ApiPaths.favoriteMenus}/'.length);
      return _updateFavoriteMenu(menuId, body! as Map<String, dynamic>);
    }
    final batchId = _inventoryBatchIdFromPath(path);
    if (batchId != null) {
      final b = Map<String, dynamic>.from(body! as Map)..remove('reason');
      return _mutateInventoryBatch(batchId, (batch) => batch..addAll(b));
    }
    final itemMatch = _mealPlanItemPath.firstMatch(path);
    if (itemMatch != null) {
      return _updateMealPlanItem(
        itemMatch.group(1)!,
        itemMatch.group(2)!,
        body! as Map<String, dynamic>,
      );
    }
    final shoppingItemMatch = _shoppingListItemPath.firstMatch(path);
    if (shoppingItemMatch != null) {
      return _updateShoppingListItem(
        shoppingItemMatch.group(1)!,
        shoppingItemMatch.group(2)!,
        body! as Map<String, dynamic>,
      );
    }
    return _echo(body);
  }

  @override
  Future<dynamic> delete(
    String path, {
    Object? body,
    Map<String, String>? headers,
  }) async {
    await Future<void>.delayed(_latency);
    log.d('MOCK DELETE $path');
    if (path.startsWith('/recipes/') && path.endsWith('/favorite')) {
      final recipeId = path.split('/')[2];
      _favoriteRecipeIds.remove(recipeId);
      return null;
    }
    if (path.startsWith('${ApiPaths.favoriteMenus}/') && path.contains('/items/')) {
      final parts = path.split('/');
      final menuId = parts[2];
      final itemId = parts[4];
      _deleteFavoriteMenuItem(menuId, itemId);
      return null;
    }
    if (path.startsWith('${ApiPaths.favoriteMenus}/')) {
      final menuId = path.substring('${ApiPaths.favoriteMenus}/'.length);
      _deleteFavoriteMenu(menuId);
      return null;
    }
    final batchId = _inventoryBatchIdFromPath(path);
    if (batchId != null) {
      await _mutateInventoryBatch(
        batchId,
        (batch) => batch
          ..['status'] = 'ARCHIVED'
          ..['archived_at'] = DateTime.now().toIso8601String(),
      );
      return null;
    }
    final itemMatch = _mealPlanItemPath.firstMatch(path);
    if (itemMatch != null) {
      _deleteMealPlanItem(itemMatch.group(1)!, itemMatch.group(2)!);
      return null;
    }
    final shoppingItemMatch = _shoppingListItemPath.firstMatch(path);
    if (shoppingItemMatch != null) {
      _deleteShoppingListItem(shoppingItemMatch.group(1)!, shoppingItemMatch.group(2)!);
    }
    return null;
  }

  @override
  Future<dynamic> postMultipart(
    String path, {
    Map<String, dynamic> fields = const {},
    List<UploadFile> files = const [],
  }) async {
    await Future<void>.delayed(_latency * 2);
    log.d('MOCK MULTIPART $path (${files.length} file)');
    // Scan endpoints return a canned ScanJob fixture in M4.
    return _clone(await _load(path));
  }
}
