import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/network/api_result.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/cooking/data/datasources/cooking_remote_data_source.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_confirmation.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooked_food.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooking_preview.dart';
import 'package:sweepfood/features/cooking/domain/repositories/cooking_repository.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';

part 'cooking_repository_impl.g.dart';

@Riverpod(keepAlive: true)
CookingRepository cookingRepository(Ref ref) => CookingRepositoryImpl(
      CookingRemoteDataSource(ref.watch(apiClientProvider)),
    );

class CookingRepositoryImpl implements CookingRepository {
  CookingRepositoryImpl(this._remote);

  final CookingRemoteDataSource _remote;

  @override
  Future<Result<CookingPreview>> preview(String mealPlanItemId) =>
      runGuarded(() async =>
          (await _remote.preview(mealPlanItemId)).toEntity(mealPlanItemId));

  @override
  Future<Result<String>> createSession(String mealPlanItemId) =>
      runGuarded(() => _remote.createSession(mealPlanItemId));

  @override
  Future<Result<void>> complete(
    String sessionId,
    CookMode mode, {
    List<ConsumptionLine>? consumptions,
  }) =>
      guardVoid(() => _remote.completeSession(sessionId, mode, consumptions));

  @override
  Future<Result<PantryItem>> saveLeftover(CookedFood food) => runGuarded(
        () async => (await _remote.saveLeftover(food)).toEntity(),
      );
}
