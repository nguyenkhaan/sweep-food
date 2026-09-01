import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/network/api_result.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/meal_plan/data/datasources/meal_plan_remote_data_source.dart';
import 'package:sweepfood/features/meal_plan/data/models/meal_plan_dto.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan.dart';
import 'package:sweepfood/features/meal_plan/domain/repositories/meal_plan_repository.dart';

part 'meal_plan_repository_impl.g.dart';

@Riverpod(keepAlive: true)
MealPlanRepository mealPlanRepository(Ref ref) => MealPlanRepositoryImpl(
      MealPlanRemoteDataSource(ref.watch(apiClientProvider)),
    );

class MealPlanRepositoryImpl implements MealPlanRepository {
  MealPlanRepositoryImpl(this._remote);

  final MealPlanRemoteDataSource _remote;

  @override
  Future<Result<MealPlan>> forWeek(DateTime weekStart) => runGuarded(() async {
        final dto = await _remote.forWeek(weekStart);
        final base = dto.toEntity();
        // The mock fixture carries one representative week; re-anchor each entry
        // onto the requested week (by weekday) so the grid is stable while
        // navigating. A live backend returns per-week data directly.
        return MealPlan(
          weekStart: weekStart,
          entries: [
            for (final e in base.entries)
              e.copyWith(
                date: weekStart.add(Duration(days: e.date.weekday - 1)),
              ),
          ],
        );
      });

  @override
  Future<Result<MealPlan>> save(MealPlan plan) => runGuarded(() async {
        final dto = await _remote.save(MealPlanDto.fromEntity(plan));
        return dto.toEntity();
      });
}
