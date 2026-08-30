// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'session_expired.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// A one-way "the session just died" signal.
///
/// [AuthInterceptor] can't reach the auth feature (that would cycle:
/// session → repo → apiClient → dio → session). Instead, when a token refresh
/// fails it bumps this counter; [SessionController] listens and tears the
/// session down, which flips the router back to `/welcome`.

@ProviderFor(SessionExpired)
final sessionExpiredProvider = SessionExpiredProvider._();

/// A one-way "the session just died" signal.
///
/// [AuthInterceptor] can't reach the auth feature (that would cycle:
/// session → repo → apiClient → dio → session). Instead, when a token refresh
/// fails it bumps this counter; [SessionController] listens and tears the
/// session down, which flips the router back to `/welcome`.
final class SessionExpiredProvider
    extends $NotifierProvider<SessionExpired, int> {
  /// A one-way "the session just died" signal.
  ///
  /// [AuthInterceptor] can't reach the auth feature (that would cycle:
  /// session → repo → apiClient → dio → session). Instead, when a token refresh
  /// fails it bumps this counter; [SessionController] listens and tears the
  /// session down, which flips the router back to `/welcome`.
  SessionExpiredProvider._()
      : super(
          from: null,
          argument: null,
          retry: null,
          name: r'sessionExpiredProvider',
          isAutoDispose: false,
          dependencies: null,
          $allTransitiveDependencies: null,
        );

  @override
  String debugGetCreateSourceHash() => _$sessionExpiredHash();

  @$internal
  @override
  SessionExpired create() => SessionExpired();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(int value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<int>(value),
    );
  }
}

String _$sessionExpiredHash() => r'362cb896ee8750a00e88a0a8926e4447f64338cc';

/// A one-way "the session just died" signal.
///
/// [AuthInterceptor] can't reach the auth feature (that would cycle:
/// session → repo → apiClient → dio → session). Instead, when a token refresh
/// fails it bumps this counter; [SessionController] listens and tears the
/// session down, which flips the router back to `/welcome`.

abstract class _$SessionExpired extends $Notifier<int> {
  int build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<int, int>;
    final element = ref.element
        as $ClassProviderElement<AnyNotifier<int, int>, int, Object?, Object?>;
    element.handleCreate(ref, build);
  }
}
