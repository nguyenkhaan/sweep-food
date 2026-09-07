// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'active_sessions_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// P-01c — the "devices signed into your account" list (`GET /auth/sessions`)
/// plus per-row revoke (`DELETE /auth/sessions/{id}`).

@ProviderFor(ActiveSessionsController)
final activeSessionsControllerProvider = ActiveSessionsControllerProvider._();

/// P-01c — the "devices signed into your account" list (`GET /auth/sessions`)
/// plus per-row revoke (`DELETE /auth/sessions/{id}`).
final class ActiveSessionsControllerProvider
    extends
        $AsyncNotifierProvider<ActiveSessionsController, List<ActiveSession>> {
  /// P-01c — the "devices signed into your account" list (`GET /auth/sessions`)
  /// plus per-row revoke (`DELETE /auth/sessions/{id}`).
  ActiveSessionsControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'activeSessionsControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$activeSessionsControllerHash();

  @$internal
  @override
  ActiveSessionsController create() => ActiveSessionsController();
}

String _$activeSessionsControllerHash() =>
    r'6a68136781a90c36f5cf91d486a59a9c63fdaea3';

/// P-01c — the "devices signed into your account" list (`GET /auth/sessions`)
/// plus per-row revoke (`DELETE /auth/sessions/{id}`).

abstract class _$ActiveSessionsController
    extends $AsyncNotifier<List<ActiveSession>> {
  FutureOr<List<ActiveSession>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<List<ActiveSession>>, List<ActiveSession>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<List<ActiveSession>>, List<ActiveSession>>,
              AsyncValue<List<ActiveSession>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
