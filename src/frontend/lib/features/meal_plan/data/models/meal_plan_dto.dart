import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan_entry.dart';

part 'meal_plan_dto.freezed.dart';
part 'meal_plan_dto.g.dart';

/// One `meal-plans/{id}/items/{item_id}` row. See `docs/api-contract.md` §7.
@freezed
abstract class MealPlanItemDto with _$MealPlanItemDto {
  const MealPlanItemDto._();

  const factory MealPlanItemDto({
    required String id,
    @JsonKey(name: 'recipe_id') required String recipeId,
    @JsonKey(name: 'recipe_name') String? recipeName,
    @JsonKey(name: 'planned_for') required DateTime plannedFor,
    @JsonKey(name: 'meal_slot') required String mealSlot,
    required double servings,
    @Default('PLANNED') String status,
  }) = _MealPlanItemDto;

  factory MealPlanItemDto.fromJson(Map<String, dynamic> json) =>
      _$MealPlanItemDtoFromJson(json);

  /// [dishName]/[dishImageUrl] are only used when the backend's own
  /// `recipe_name` is missing — the backend has no image field at all, so
  /// [dishImageUrl] only ever comes from the caller's local knowledge.
  MealPlanEntry toEntity({String? dishName, String? dishImageUrl}) =>
      MealPlanEntry(
        id: id,
        date: DateTime(plannedFor.year, plannedFor.month, plannedFor.day),
        slot: MealSlot.fromWire(mealSlot),
        dishId: recipeId,
        servings: servings,
        status: MealPlanItemStatus.fromWire(status),
        dishName: recipeName ?? dishName,
        dishImageUrl: dishImageUrl,
      );
}

/// `POST /meal-plans` / `GET /meal-plans/` (no `items`) / `GET
/// /meal-plans/{id}` (with `items`) all return this shape.
@freezed
abstract class MealPlanDto with _$MealPlanDto {
  const MealPlanDto._();

  const factory MealPlanDto({
    required String id,
    String? name,
    @JsonKey(name: 'starts_on') required DateTime startsOn,
    @JsonKey(name: 'ends_on') required DateTime endsOn,
    @Default(<MealPlanItemDto>[]) List<MealPlanItemDto> items,
  }) = _MealPlanDto;

  factory MealPlanDto.fromJson(Map<String, dynamic> json) =>
      _$MealPlanDtoFromJson(json);
}
