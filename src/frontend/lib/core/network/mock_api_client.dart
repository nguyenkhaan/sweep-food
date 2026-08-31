import 'dart:async';
import 'dart:convert';

import 'package:flutter/services.dart' show rootBundle;
import 'package:frontend/core/config/app_constants.dart';
import 'package:frontend/core/error/app_exception.dart';
import 'package:frontend/core/network/api_client.dart';
import 'package:frontend/core/network/api_paths.dart';
import 'package:frontend/core/utils/logger.dart';

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
  static final Map<String, String> _fixtures = {
    ApiPaths.me: 'auth_me',
    ApiPaths.ingredients: 'ingredients',
    ApiPaths.pantryItems: 'pantry_items',
    ApiPaths.pantrySummary: 'pantry_summary',
    ApiPaths.suggestions: 'suggestions',
    '/dishes/': 'dish',
    ApiPaths.mealPlans: 'meal_plan',
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
    ApiPaths.login: 'auth_session',
    ApiPaths.register: 'auth_session',
    ApiPaths.refresh: 'auth_tokens',
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
    if (_cache.containsKey(key)) return _clone(_cache[key]);
    try {
      final raw = _fillDates(await rootBundle.loadString('assets/mock/$key.json'));
      final decoded = jsonDecode(raw);
      _cache[key] = decoded;
      return _clone(decoded);
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

  @override
  Future<dynamic> get(String path, {Map<String, dynamic>? query}) async {
    await Future<void>.delayed(_latency);
    log.d('MOCK GET $path ${query ?? ''}');
    return _load(path);
  }

  @override
  Future<dynamic> post(
    String path, {
    Object? body,
    Map<String, dynamic>? query,
  }) async {
    await Future<void>.delayed(_latency);
    log.d('MOCK POST $path');
    final fixture = _postFixtureKey(path);
    if (fixture != null) return _loadKey(fixture);
    return _echo(body);
  }

  @override
  Future<dynamic> put(String path, {Object? body}) async {
    await Future<void>.delayed(_latency);
    log.d('MOCK PUT $path');
    return _echo(body);
  }

  @override
  Future<dynamic> patch(String path, {Object? body}) async {
    await Future<void>.delayed(_latency);
    log.d('MOCK PATCH $path');
    return _echo(body);
  }

  @override
  Future<dynamic> delete(String path, {Object? body}) async {
    await Future<void>.delayed(_latency);
    log.d('MOCK DELETE $path');
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
    return _load(path);
  }
}
