// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'push_registrar.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Owns the FCM-token ↔ backend `/users/me/devices` lifecycle: obtain a token
/// once the user is signed in, register it, keep it fresh, route notification
/// taps, and unregister on sign-out.
///
/// Entirely best-effort — when FCM is disabled or unavailable every method is a
/// quiet no-op, so callers (SessionController) never branch on it.

@ProviderFor(pushRegistrar)
final pushRegistrarProvider = PushRegistrarProvider._();

/// Owns the FCM-token ↔ backend `/users/me/devices` lifecycle: obtain a token
/// once the user is signed in, register it, keep it fresh, route notification
/// taps, and unregister on sign-out.
///
/// Entirely best-effort — when FCM is disabled or unavailable every method is a
/// quiet no-op, so callers (SessionController) never branch on it.

final class PushRegistrarProvider
    extends $FunctionalProvider<PushRegistrar, PushRegistrar, PushRegistrar>
    with $Provider<PushRegistrar> {
  /// Owns the FCM-token ↔ backend `/users/me/devices` lifecycle: obtain a token
  /// once the user is signed in, register it, keep it fresh, route notification
  /// taps, and unregister on sign-out.
  ///
  /// Entirely best-effort — when FCM is disabled or unavailable every method is a
  /// quiet no-op, so callers (SessionController) never branch on it.
  PushRegistrarProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'pushRegistrarProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$pushRegistrarHash();

  @$internal
  @override
  $ProviderElement<PushRegistrar> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  PushRegistrar create(Ref ref) {
    return pushRegistrar(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(PushRegistrar value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<PushRegistrar>(value),
    );
  }
}

String _$pushRegistrarHash() => r'42f123ad946663e42676a6191039e15cbbeb8ffd';
