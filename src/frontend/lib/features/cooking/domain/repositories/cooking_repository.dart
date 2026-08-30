import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/cooking/domain/entities/cook_confirmation.dart';
import 'package:frontend/features/cooking/domain/entities/cook_result.dart';
import 'package:frontend/features/cooking/domain/entities/cooked_food.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item.dart';

abstract interface class CookingRepository {
  /// Deduct stock for a cooked dish (`POST /dishes/{id}/cook`).
  Future<Result<CookResult>> cook(CookConfirmation confirmation);

  /// Save leftover portions as a new "Ăn liền" batch (`POST /pantry/cooked-food`).
  Future<Result<PantryItem>> saveLeftover(CookedFood food);
}
