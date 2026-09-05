import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_confirmation.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooked_food.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooking_preview.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';

abstract interface class CookingRepository {
  /// `POST /cooking/preview` — read-only, writes nothing.
  Future<Result<CookingPreview>> preview(String mealPlanItemId);

  /// `POST /cooking/sessions` — creates a `PLANNED` session.
  Future<Result<String>> createSession(String mealPlanItemId);

  /// `POST /cooking/sessions/{id}/complete` — deducts stock.
  Future<Result<void>> complete(
    String sessionId,
    CookMode mode, {
    List<ConsumptionLine>? consumptions,
  });

  /// Save leftover portions as a new `COOKED_FOOD` batch
  /// (`POST /cooking/sessions/{id}/leftovers`).
  Future<Result<PantryItem>> saveLeftover(CookedFood food);
}
