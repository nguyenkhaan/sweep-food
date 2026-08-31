import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/cooking/data/repositories/cooking_repository_impl.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_confirmation.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_result.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';

part 'cooking_controller.g.dart';

/// Drives the post-cook flow: confirm → deduct stock → expose the [CookResult]
/// for the D-05 / D-07 screen. Applying the result also refreshes the pantry
/// list + summary, so the Home waste count picks it up.
///
/// Kept alive: the confirming widget (a bottom sheet) only `read`s this, so an
/// auto-dispose provider would be torn down mid-request.
@Riverpod(keepAlive: true)
class CookingController extends _$CookingController {
  @override
  CookResult? build() => null;

  Future<CookResult> confirm(
    CookConfirmation confirmation, {
    String? dishName,
  }) async {
    final pantry = ref.read(pantryListControllerProvider.notifier);
    final res = await ref.read(cookingRepositoryProvider).cook(confirmation);
    return res.fold(
      (f) => throw f,
      (raw) {
        final result = raw.copyWith(
          dishId: raw.dishId.isEmpty ? confirmation.dishId : raw.dishId,
          dishName: raw.dishName.isEmpty ? (dishName ?? '') : raw.dishName,
        );
        pantry.applyCookChanges(
          updated: result.updatedPantryItems,
          depletedIds: result.depletedItemIds,
        );
        state = result;
        return result;
      },
    );
  }
}
