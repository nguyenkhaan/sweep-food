import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_confirmation.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooking_history.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

part 'cooking_history_dto.freezed.dart';
part 'cooking_history_dto.g.dart';

/// Tolerates decimals that arrive as JSON strings (pydantic `Decimal`).
double _asDouble(Object? v) {
  if (v == null) return 0;
  if (v is num) return v.toDouble();
  return double.tryParse(v.toString()) ?? 0;
}

/// `GET /cooking/history` row. See `docs/api-contract.md` §6.
@freezed
abstract class CookingHistorySummaryDto with _$CookingHistorySummaryDto {
  const CookingHistorySummaryDto._();

  const factory CookingHistorySummaryDto({
    @JsonKey(name: 'session_id') required String sessionId,
    @JsonKey(name: 'recipe_id') required String recipeId,
    @JsonKey(name: 'recipe_name') @Default('') String recipeName,
    @JsonKey(fromJson: _asDouble) @Default(0) double servings,
    @Default('COMPLETED') String status,
    @JsonKey(name: 'completed_at') DateTime? completedAt,
  }) = _CookingHistorySummaryDto;

  factory CookingHistorySummaryDto.fromJson(Map<String, dynamic> json) =>
      _$CookingHistorySummaryDtoFromJson(json);

  CookingHistoryEntry toEntity() => CookingHistoryEntry(
        sessionId: sessionId,
        recipeId: recipeId,
        recipeName: recipeName,
        servings: servings,
        status: CookingSessionStatus.fromWire(status),
        completedAt: completedAt,
      );
}

@freezed
abstract class CookingHistoryListDto with _$CookingHistoryListDto {
  const factory CookingHistoryListDto({
    @Default(<CookingHistorySummaryDto>[]) List<CookingHistorySummaryDto> items,
  }) = _CookingHistoryListDto;

  factory CookingHistoryListDto.fromJson(Map<String, dynamic> json) =>
      _$CookingHistoryListDtoFromJson(json);
}

@freezed
abstract class CookingConsumptionDto with _$CookingConsumptionDto {
  const CookingConsumptionDto._();

  const factory CookingConsumptionDto({
    @JsonKey(name: 'recipe_ingredient_id') String? recipeIngredientId,
    @JsonKey(name: 'inventory_batch_id') required String inventoryBatchId,
    @JsonKey(fromJson: _asDouble) @Default(0) double quantity,
    @Default('GRAM') String unit,
  }) = _CookingConsumptionDto;

  factory CookingConsumptionDto.fromJson(Map<String, dynamic> json) =>
      _$CookingConsumptionDtoFromJson(json);

  CookingConsumption toEntity() => CookingConsumption(
        recipeIngredientId: recipeIngredientId,
        inventoryBatchId: inventoryBatchId,
        quantity: quantity,
        unit: MeasurementUnit.fromWire(unit),
      );
}

@freezed
abstract class CookingSessionDto with _$CookingSessionDto {
  const factory CookingSessionDto({
    required String id,
    @JsonKey(name: 'recipe_id') required String recipeId,
    @JsonKey(name: 'meal_plan_item_id') String? mealPlanItemId,
    @JsonKey(fromJson: _asDouble) @Default(0) double servings,
    @Default('COMPLETED') String status,
    @JsonKey(name: 'consumption_mode') String? consumptionMode,
    @JsonKey(name: 'completed_at') DateTime? completedAt,
  }) = _CookingSessionDto;

  factory CookingSessionDto.fromJson(Map<String, dynamic> json) =>
      _$CookingSessionDtoFromJson(json);
}

/// `GET /cooking/history/{session_id}`.
@freezed
abstract class CookingHistoryDetailDto with _$CookingHistoryDetailDto {
  const CookingHistoryDetailDto._();

  const factory CookingHistoryDetailDto({
    required CookingSessionDto session,
    @JsonKey(name: 'recipe_id') required String recipeId,
    @JsonKey(name: 'recipe_name') @Default('') String recipeName,
    @Default(<CookingConsumptionDto>[]) List<CookingConsumptionDto> consumptions,
    @JsonKey(name: 'leftover_batch_id') String? leftoverBatchId,
    @JsonKey(name: 'completed_at') DateTime? completedAt,
  }) = _CookingHistoryDetailDto;

  factory CookingHistoryDetailDto.fromJson(Map<String, dynamic> json) =>
      _$CookingHistoryDetailDtoFromJson(json);

  CookingHistoryDetail toEntity() => CookingHistoryDetail(
        sessionId: session.id,
        recipeId: recipeId,
        recipeName: recipeName,
        servings: session.servings,
        status: CookingSessionStatus.fromWire(session.status),
        consumptionMode: CookMode.fromWire(session.consumptionMode),
        completedAt: completedAt ?? session.completedAt,
        leftoverBatchId: leftoverBatchId,
        consumptions: [for (final c in consumptions) c.toEntity()],
      );
}
