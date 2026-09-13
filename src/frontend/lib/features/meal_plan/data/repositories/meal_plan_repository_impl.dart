import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/network/api_result.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/meal_plan/data/datasources/meal_plan_remote_data_source.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan_entry.dart';
import 'package:sweepfood/features/meal_plan/domain/repositories/meal_plan_repository.dart';

part 'meal_plan_repository_impl.g.dart';

@Riverpod(keepAlive: true)
MealPlanRepository mealPlanRepository(Ref ref) => MealPlanRepositoryImpl(
      MealPlanRemoteDataSource(ref.watch(apiClientProvider)),
    );

/// The backend has no "current week" concept — a plan is just an id with a
/// date range. This repository resolves each Monday-anchored week to a plan
/// id (scanning `GET /meal-plans/` for a `starts_on` match, creating one if
/// none exists) and caches the mapping in memory for the app session.
///
/// Known limitation: the scan only looks at the first 100 plans (most
/// recent-first, per backend default ordering) — a long-time user with more
/// plans than that could get a duplicate plan created for an old week. Not
/// persisted across app restarts either; every session re-resolves from
/// scratch. Acceptable for MVP — see IMPLEMENTATION_PLAN.md.
class MealPlanRepositoryImpl implements MealPlanRepository {
  MealPlanRepositoryImpl(this._remote);

  final MealPlanRemoteDataSource _remote;
  final Map<DateTime, String> _planIdByWeek = {};

  static DateTime _dateOnly(DateTime d) => DateTime(d.year, d.month, d.day);
  static bool _sameDate(DateTime a, DateTime b) =>
      a.year == b.year && a.month == b.month && a.day == b.day;

  Future<String> _resolvePlanId(DateTime weekStart) async {
    final key = _dateOnly(weekStart);
    final cached = _planIdByWeek[key];
    if (cached != null) return cached;

    final plans = await _remote.listPlans();
    for (final p in plans) {
      if (_sameDate(p.startsOn, key)) {
        _planIdByWeek[key] = p.id;
        return p.id;
      }
    }
    final created = await _remote.createPlan(
      startsOn: key,
      endsOn: key.add(const Duration(days: 6)),
    );
    _planIdByWeek[key] = created.id;
    return created.id;
  }

  @override
  Future<Result<MealPlan>> forWeek(DateTime weekStart) => runGuarded(() async {
        final key = _dateOnly(weekStart);
        final id = await _resolvePlanId(key);
        final dto = await _remote.getPlan(id);
        return MealPlan(
          id: dto.id,
          weekStart: key,
          entries: [for (final item in dto.items) item.toEntity()],
        );
      });

  @override
  Future<Result<MealPlanEntry>> addEntry({
    required DateTime weekStart,
    required DateTime date,
    required MealSlot slot,
    required String dishId,
    required double servings,
    String? dishName,
    String? dishImageUrl,
  }) =>
      runGuarded(() async {
        final planId = await _resolvePlanId(weekStart);
        final dto = await _remote.addItem(
          planId,
          recipeId: dishId,
          plannedFor: date,
          slot: slot,
          servings: servings,
        );
        return dto.toEntity(dishName: dishName, dishImageUrl: dishImageUrl);
      });

  @override
  Future<Result<MealPlanEntry>> updateEntry({
    required DateTime weekStart,
    required String itemId,
    required String dishId,
    required double servings,
    String? dishName,
    String? dishImageUrl,
  }) =>
      runGuarded(() async {
        final planId = await _resolvePlanId(weekStart);
        final dto = await _remote.updateItem(
          planId,
          itemId,
          recipeId: dishId,
          servings: servings,
        );
        return dto.toEntity(dishName: dishName, dishImageUrl: dishImageUrl);
      });

  @override
  Future<Result<void>> removeEntry({
    required DateTime weekStart,
    required String itemId,
  }) =>
      guardVoid(() async {
        final planId = await _resolvePlanId(weekStart);
        await _remote.deleteItem(planId, itemId);
      });
}
