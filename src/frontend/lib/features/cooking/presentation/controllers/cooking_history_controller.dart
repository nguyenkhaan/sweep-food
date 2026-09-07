import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/cooking/data/repositories/cooking_repository_impl.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooking_history.dart';

part 'cooking_history_controller.g.dart';

/// D-08 — the completed-cooking-session list (`GET /cooking/history`).
@riverpod
class CookingHistoryController extends _$CookingHistoryController {
  @override
  Future<List<CookingHistoryEntry>> build() async {
    final res = await ref.watch(cookingRepositoryProvider).history();
    return res.fold((f) => throw f, (list) => list);
  }

  Future<void> refresh() => ref.refresh(cookingHistoryControllerProvider.future);
}

/// One completed session in full (`GET /cooking/history/{id}`).
@riverpod
Future<CookingHistoryDetail> cookingHistoryDetail(Ref ref, String sessionId) async {
  final res = await ref.watch(cookingRepositoryProvider).historyDetail(sessionId);
  return res.fold((f) => throw f, (detail) => detail);
}
