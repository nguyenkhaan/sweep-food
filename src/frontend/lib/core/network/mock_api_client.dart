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
    ApiPaths.suggestions: 'suggestions',
    '/recipes/': 'recipe',
    '/shopping-lists': 'shopping_list',
    ApiPaths.notifications: 'notifications',
    ApiPaths.subscription: 'subscription',
    ApiPaths.reportsWasteReduction: 'waste_reduction_report',
    // M4 multimodal ingestion — `postMultipart` returns these canned ScanJobs.
    ApiPaths.scanLabel: 'scan_label',
    ApiPaths.scanReceipt: 'scan_receipt',
    ApiPaths.scanVoice: 'scan_voice',
  };

  /// Read-shaped POST endpoints that return a canned fixture instead of echoing
  /// the request body (dish scoring, cook result). Matched exact-or-prefix; the
  /// `/cook` suffix covers `POST /dishes/{id}/cook`.
  static final Map<String, String> _postFixtures = {
    ApiPaths.suggestions: 'suggestions',
    ApiPaths.shoppingListsGenerate: 'shopping_list',
  };

  String? _postFixtureKey(String path) {
    if (path.endsWith('/cook')) return 'cook_result';
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
    final fixture = _postFixtureKey(path);
    if (fixture != null) return _clone(await _loadKey(fixture));
    return _echo(body);
  }

  @override
  Future<dynamic> put(String path, {Object? body}) async {
    await Future<void>.delayed(_latency);
    log.d('MOCK PUT $path');
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
