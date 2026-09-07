import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/auth/domain/entities/active_session.dart';

part 'active_sessions_controller.g.dart';

/// P-01c — the "devices signed into your account" list (`GET /auth/sessions`)
/// plus per-row revoke (`DELETE /auth/sessions/{id}`).
@riverpod
class ActiveSessionsController extends _$ActiveSessionsController {
  @override
  Future<List<ActiveSession>> build() async {
    final res = await ref.watch(authRepositoryProvider).activeSessions();
    return res.fold((f) => throw f, (list) => list);
  }

  Future<void> refresh() =>
      ref.refresh(activeSessionsControllerProvider.future);

  /// Revoke one session and drop it from the list. Rethrows the `Failure` so the
  /// screen can show a snackbar.
  Future<void> revoke(String id) async {
    final res = await ref.read(authRepositoryProvider).revokeSession(id);
    res.fold(
      (f) => throw f,
      (_) {
        final current = state.asData?.value ?? const [];
        state = AsyncData([
          for (final s in current)
            if (s.id != id) s,
        ]);
      },
    );
  }
}
