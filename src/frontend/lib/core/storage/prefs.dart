import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:shared_preferences/shared_preferences.dart';

part 'prefs.g.dart';

/// The [SharedPreferences] instance, loaded once in `bootstrap.dart` and
/// injected via `overrideWithValue`. Reading it before that override is a bug.
@Riverpod(keepAlive: true)
SharedPreferences sharedPreferences(Ref ref) => throw UnimplementedError(
      'sharedPreferencesProvider must be overridden in bootstrap()',
    );
