import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:frontend/features/reports/domain/entities/waste_reduction_summary.dart';

part 'report_dto.freezed.dart';
part 'report_dto.g.dart';

@freezed
abstract class WasteBarDto with _$WasteBarDto {
  const factory WasteBarDto({
    required String label,
    required int value,
  }) = _WasteBarDto;

  factory WasteBarDto.fromJson(Map<String, dynamic> json) =>
      _$WasteBarDtoFromJson(json);
}

@freezed
abstract class WasteCategoryDto with _$WasteCategoryDto {
  const factory WasteCategoryDto({
    required String category,
    required int count,
  }) = _WasteCategoryDto;

  factory WasteCategoryDto.fromJson(Map<String, dynamic> json) =>
      _$WasteCategoryDtoFromJson(json);
}

@freezed
abstract class WasteReductionSummaryDto with _$WasteReductionSummaryDto {
  const WasteReductionSummaryDto._();

  const factory WasteReductionSummaryDto({
    required String period,
    @JsonKey(name: 'period_label') required String periodLabel,
    @JsonKey(name: 'items_used_before_expiry')
    required int itemsUsedBeforeExpiry,
    @JsonKey(name: 'waste_avoided_kg') required double wasteAvoidedKg,
    @JsonKey(name: 'dishes_cooked') required int dishesCooked,
    @JsonKey(name: 'weekly_bars')
    @Default(<WasteBarDto>[])
    List<WasteBarDto> weeklyBars,
    @JsonKey(name: 'by_category')
    @Default(<WasteCategoryDto>[])
    List<WasteCategoryDto> byCategory,
  }) = _WasteReductionSummaryDto;

  factory WasteReductionSummaryDto.fromJson(Map<String, dynamic> json) =>
      _$WasteReductionSummaryDtoFromJson(json);

  WasteReductionSummary toEntity() => WasteReductionSummary(
        period: ReportPeriod.fromWire(period),
        periodLabel: periodLabel,
        itemsUsedBeforeExpiry: itemsUsedBeforeExpiry,
        wasteAvoidedKg: wasteAvoidedKg,
        dishesCooked: dishesCooked,
        weeklyBars: [
          for (final b in weeklyBars)
            WasteReductionBar(label: b.label, value: b.value),
        ],
        byCategory: [
          for (final c in byCategory)
            WasteReductionCategory(
              category: c.category,
              count: c.count,
              colorValue: _colorFor(c.category),
            ),
        ],
      );

  static int _colorFor(String category) {
    final c = category.toLowerCase();
    if (c.contains('rau')) return 0xFF40916C;
    if (c.contains('thịt') || c.contains('cá')) return 0xFF8D4D4E;
    return 0xFFB08422;
  }
}
