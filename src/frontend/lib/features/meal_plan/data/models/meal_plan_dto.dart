import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:frontend/features/meal_plan/domain/entities/meal_plan.dart';
import 'package:frontend/features/meal_plan/domain/entities/meal_plan_entry.dart';

part 'meal_plan_dto.freezed.dart';
part 'meal_plan_dto.g.dart';

@freezed
abstract class MealPlanEntryDto with _$MealPlanEntryDto {
  const MealPlanEntryDto._();

  const factory MealPlanEntryDto({
    required DateTime date,
    required String slot,
    @JsonKey(name: 'dish_id') required String dishId,
    @JsonKey(name: 'dish_name') String? dishName,
    @JsonKey(name: 'dish_image_url') String? dishImageUrl,
  }) = _MealPlanEntryDto;

  factory MealPlanEntryDto.fromJson(Map<String, dynamic> json) =>
      _$MealPlanEntryDtoFromJson(json);

  factory MealPlanEntryDto.fromEntity(MealPlanEntry e) => MealPlanEntryDto(
        date: e.date,
        slot: e.slot.wire,
        dishId: e.dishId,
        dishName: e.dishName,
        dishImageUrl: e.dishImageUrl,
      );

  MealPlanEntry toEntity() => MealPlanEntry(
        date: date,
        slot: MealSlot.fromWire(slot),
        dishId: dishId,
        dishName: dishName,
        dishImageUrl: dishImageUrl,
      );
}

@freezed
abstract class MealPlanDto with _$MealPlanDto {
  const MealPlanDto._();

  const factory MealPlanDto({
    @JsonKey(name: 'week_start') required DateTime weekStart,
    @Default(<MealPlanEntryDto>[]) List<MealPlanEntryDto> entries,
  }) = _MealPlanDto;

  factory MealPlanDto.fromJson(Map<String, dynamic> json) =>
      _$MealPlanDtoFromJson(json);

  factory MealPlanDto.fromEntity(MealPlan p) => MealPlanDto(
        weekStart: p.weekStart,
        entries: [for (final e in p.entries) MealPlanEntryDto.fromEntity(e)],
      );

  MealPlan toEntity() => MealPlan(
        weekStart: DateTime(weekStart.year, weekStart.month, weekStart.day),
        entries: [for (final e in entries) e.toEntity()],
      );
}
