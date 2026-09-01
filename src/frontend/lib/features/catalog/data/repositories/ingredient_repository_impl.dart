import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/network/api_result.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/catalog/data/datasources/ingredient_remote_data_source.dart';
import 'package:sweepfood/features/catalog/domain/entities/ingredient.dart';
import 'package:sweepfood/features/catalog/domain/repositories/ingredient_repository.dart';

part 'ingredient_repository_impl.g.dart';

@Riverpod(keepAlive: true)
IngredientRepository ingredientRepository(Ref ref) => IngredientRepositoryImpl(
      IngredientRemoteDataSource(ref.watch(apiClientProvider)),
    );

class IngredientRepositoryImpl implements IngredientRepository {
  IngredientRepositoryImpl(this._remote);

  final IngredientRemoteDataSource _remote;

  @override
  Future<Result<List<Ingredient>>> search(String query) => runGuarded(() async {
        final dtos = await _remote.search(query);
        return [for (final d in dtos) d.toEntity()];
      });

  @override
  Future<Result<Ingredient>> byId(String id) =>
      runGuarded(() async => (await _remote.byId(id)).toEntity());
}
