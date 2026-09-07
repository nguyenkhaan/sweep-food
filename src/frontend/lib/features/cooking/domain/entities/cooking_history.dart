import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_confirmation.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

part 'cooking_history.freezed.dart';

/// Backend `CookingSessionStatus`. History only ever lists `COMPLETED` /
/// `CANCELLED` sessions, but the enum carries all three for round-tripping.
enum CookingSessionStatus {
  planned('PLANNED'),
  completed('COMPLETED'),
  cancelled('CANCELLED');

  const CookingSessionStatus(this.wire);
  final String wire;

  static CookingSessionStatus fromWire(String? v) =>
      CookingSessionStatus.values.firstWhere(
        (s) => s.wire == v,
        orElse: () => CookingSessionStatus.completed,
      );

  String get label => switch (this) {
        CookingSessionStatus.planned => 'Đã lên kế hoạch',
        CookingSessionStatus.completed => 'Đã nấu',
        CookingSessionStatus.cancelled => 'Đã huỷ',
      };
}

/// One row in the cooking-history list (`GET /cooking/history`).
@freezed
abstract class CookingHistoryEntry with _$CookingHistoryEntry {
  const factory CookingHistoryEntry({
    required String sessionId,
    required String recipeId,
    required String recipeName,
    required double servings,
    required CookingSessionStatus status,
    DateTime? completedAt,
  }) = _CookingHistoryEntry;
}

/// One persisted deduction inside a completed session.
@freezed
abstract class CookingConsumption with _$CookingConsumption {
  const factory CookingConsumption({
    String? recipeIngredientId,
    required String inventoryBatchId,
    required double quantity,
    required MeasurementUnit unit,
  }) = _CookingConsumption;
}

/// Full detail of one completed session (`GET /cooking/history/{id}`).
@freezed
abstract class CookingHistoryDetail with _$CookingHistoryDetail {
  const factory CookingHistoryDetail({
    required String sessionId,
    required String recipeId,
    required String recipeName,
    required double servings,
    required CookingSessionStatus status,

    /// Which consumption mode was used at completion (`EXACT`/`HALF`/…).
    CookMode? consumptionMode,
    DateTime? completedAt,
    String? leftoverBatchId,
    @Default(<CookingConsumption>[]) List<CookingConsumption> consumptions,
  }) = _CookingHistoryDetail;
}
