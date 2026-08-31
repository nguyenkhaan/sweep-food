// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'session_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// App-wide auth state. `AsyncData(null)` = signed out, `AsyncData(session)` =
/// signed in, `AsyncLoading` = still reviving a persisted session (Splash).
///
/// The router watches this (via `route_guards.dart`) to gate every route. The
/// form controllers (`login`/`register`) call in here and rethrow failures for
/// the form to display — this notifier only ever moves to a resolved state.

@ProviderFor(SessionController)
final sessionControllerProvider = SessionControllerProvider._();

/// App-wide auth state. `AsyncData(null)` = signed out, `AsyncData(session)` =
/// signed in, `AsyncLoading` = still reviving a persisted session (Splash).
///
/// The router watches this (via `route_guards.dart`) to gate every route. The
/// form controllers (`login`/`register`) call in here and rethrow failures for
/// the form to display — this notifier only ever moves to a resolved state.
final class SessionControllerProvider
    extends $AsyncNotifierProvider<SessionController, Session?> {
  /// App-wide auth state. `AsyncData(null)` = signed out, `AsyncData(session)` =
  /// signed in, `AsyncLoading` = still reviving a persisted session (Splash).
  ///
  /// The router watches this (via `route_guards.dart`) to gate every route. The
  /// form controllers (`login`/`register`) call in here and rethrow failures for
  /// the form to display — this notifier only ever moves to a resolved state.
  SessionControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'sessionControllerProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$sessionControllerHash();

  @$internal
  @override
  SessionController create() => SessionController();
}

String _$sessionControllerHash() => r'f9fa9d79c6f34300e2e8ef3387889966fefbe43f';

/// App-wide auth state. `AsyncData(null)` = signed out, `AsyncData(session)` =
/// signed in, `AsyncLoading` = still reviving a persisted session (Splash).
///
/// The router watches this (via `route_guards.dart`) to gate every route. The
/// form controllers (`login`/`register`) call in here and rethrow failures for
/// the form to display — this notifier only ever moves to a resolved state.

abstract class _$SessionController extends $AsyncNotifier<Session?> {
  FutureOr<Session?> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<Session?>, Session?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<Session?>, Session?>,
              AsyncValue<Session?>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
