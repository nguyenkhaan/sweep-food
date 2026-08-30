import 'package:frontend/features/cooking/data/repositories/cooking_repository_impl.dart';
import 'package:frontend/features/cooking/domain/entities/cooked_food.dart';
import 'package:frontend/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'leftover_controller.g.dart';

/// D-06 — saves leftover portions as a new "Ăn liền" batch and refreshes the
/// pantry list. Kept alive: the saving sheet only `read`s this.
@Riverpod(keepAlive: true)
class LeftoverController extends _$LeftoverController {
  @override
  FutureOr<void> build() {}

  Future<void> save(CookedFood food) async {
    final pantry = ref.read(pantryListControllerProvider.notifier);
    state = const AsyncLoading();
    final res = await ref.read(cookingRepositoryProvider).saveLeftover(food);
    res.fold(
      (f) {
        state = AsyncError(f, StackTrace.current);
        throw f;
      },
      (item) {
        pantry.addExisting(item);
        state = const AsyncData(null);
      },
    );
  }
}
