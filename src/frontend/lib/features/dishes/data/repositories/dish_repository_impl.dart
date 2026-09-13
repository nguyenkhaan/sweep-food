import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/network/api_result.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/dishes/data/datasources/dish_remote_data_source.dart';
import 'package:sweepfood/features/dishes/domain/entities/dish.dart';
import 'package:sweepfood/features/dishes/domain/repositories/dish_repository.dart';

part 'dish_repository_impl.g.dart';

@Riverpod(keepAlive: true)
DishRepository dishRepository(Ref ref) => DishRepositoryImpl(
      DishRemoteDataSource(ref.watch(apiClientProvider)),
    );

class DishRepositoryImpl implements DishRepository {
  DishRepositoryImpl(this._remote);

  final DishRemoteDataSource _remote;

  @override
  Future<Result<Dish>> getById(String id) =>
      runGuarded(() async => (await _remote.getById(id)).toEntity());
}
