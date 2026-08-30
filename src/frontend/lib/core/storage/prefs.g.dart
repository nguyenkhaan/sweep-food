// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'prefs.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// The [SharedPreferences] instance, loaded once in `bootstrap.dart` and
/// injected via `overrideWithValue`. Reading it before that override is a bug.

@ProviderFor(sharedPreferences)
final sharedPreferencesProvider = SharedPreferencesProvider._();

/// The [SharedPreferences] instance, loaded once in `bootstrap.dart` and
/// injected via `overrideWithValue`. Reading it before that override is a bug.

final class SharedPreferencesProvider extends $FunctionalProvider<
    SharedPreferences,
    SharedPreferences,
    SharedPreferences> with $Provider<SharedPreferences> {
  /// The [SharedPreferences] instance, loaded once in `bootstrap.dart` and
  /// injected via `overrideWithValue`. Reading it before that override is a bug.
  SharedPreferencesProvider._()
      : super(
          from: null,
          argument: null,
          retry: null,
          name: r'sharedPreferencesProvider',
          isAutoDispose: false,
          dependencies: null,
          $allTransitiveDependencies: null,
        );

  @override
  String debugGetCreateSourceHash() => _$sharedPreferencesHash();

  @$internal
  @override
  $ProviderElement<SharedPreferences> $createElement(
          $ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  SharedPreferences create(Ref ref) {
    return sharedPreferences(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(SharedPreferences value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<SharedPreferences>(value),
    );
  }
}

String _$sharedPreferencesHash() => r'e17acf9a132446d37cf576d80c59210fb3ac4ce0';
