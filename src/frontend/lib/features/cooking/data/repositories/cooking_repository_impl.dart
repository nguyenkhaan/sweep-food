import 'package:frontend/core/network/api_result.dart';
import 'package:frontend/core/network/network_providers.dart';
import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/cooking/data/datasources/cooking_remote_data_source.dart';
import 'package:frontend/features/cooking/domain/entities/cook_confirmation.dart';
import 'package:frontend/features/cooking/domain/entities/cook_result.dart';
import 'package:frontend/features/cooking/domain/entities/cooked_food.dart';
import 'package:frontend/features/cooking/domain/repositories/cooking_repository.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';
import 'package:frontend/shared/domain/storage_tier.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'cooking_repository_impl.g.dart';

@Riverpod(keepAlive: true)
CookingRepository cookingRepository(Ref ref) => CookingRepositoryImpl(
      CookingRemoteDataSource(ref.watch(apiClientProvider)),
    );

class CookingRepositoryImpl implements CookingRepository {
  CookingRepositoryImpl(this._remote);

  final CookingRemoteDataSource _remote;

  @override
  Future<Result<CookResult>> cook(CookConfirmation confirmation) =>
      runGuarded(() async => (await _remote.cook(confirmation)).toEntity());

  @override
  Future<Result<PantryItem>> saveLeftover(CookedFood food) =>
      runGuarded(() async {
        final id = await _remote.saveLeftover(food);
        return PantryItem(
          id: id,
          name: '${food.dishName} (đã nấu)',
          category: 'Thức ăn đã nấu',
          quantity: food.servings.toDouble(),
          unit: MeasurementUnit.piece,
          storageTier: StorageTier.eatSoon,
          addedAt: DateTime.now(),
          source: PantrySource.cooked,
          status: PantryItemStatus.active,
          expiryDate: food.reminderAt,
        );
      });
}
