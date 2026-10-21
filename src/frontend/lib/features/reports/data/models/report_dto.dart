import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/reports/domain/entities/waste_reduction_summary.dart';

part 'report_dto.freezed.dart';
part 'report_dto.g.dart';

@freezed
abstract class WasteBarDto with _$WasteBarDto {
  const factory WasteBarDto({required String label, required int value}) =
      _WasteBarDto;

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
      _$WasteReductionSummaryDtoFromJson(_normalizedJson(json));

  static Map<String, dynamic> _normalizedJson(Map<String, dynamic> json) {
    if (json.containsKey('total_saved_kg')) {
      final periodStr = json['period']?.toString() ?? 'month';
      final periodLabel = periodStr == 'week'
          ? 'Tuần này'
          : (periodStr == 'year' ? 'Năm này' : 'Tháng này');
      final wasteKg =
          double.tryParse(json['total_saved_kg']?.toString() ?? '0') ?? 0.0;

      final topSaved = (json['top_saved_ingredients'] as List<dynamic>?) ?? [];
      final byCategory = <Map<String, dynamic>>[];
      for (final item in topSaved) {
        if (item is Map) {
          final name = item['name']?.toString() ?? '';
          final savedKg =
              double.tryParse(item['saved_kg']?.toString() ?? '0') ?? 0.0;
          byCategory.add({
            'category': name,
            'count': (savedKg * 10).round().clamp(1, 999),
          });
        }
      }

      final weeklySeries = (json['weekly_series'] as List<dynamic>?) ?? [];
      final weeklyLabels = (json['weekly_labels'] as List<dynamic>?) ?? [];
      final weeklyBars = <Map<String, dynamic>>[];
      for (var i = 0; i < weeklySeries.length; i++) {
        final val = double.tryParse(weeklySeries[i]?.toString() ?? '0') ?? 0.0;
        final label = i < weeklyLabels.length
            ? weeklyLabels[i].toString()
            : 'T${i + 1}';
        weeklyBars.add({
          'label': label.length > 5 ? label.substring(label.length - 5) : label,
          'value': (val * 10).round(),
        });
      }

      return {
        'period': periodStr,
        'period_label': periodLabel,
        'items_used_before_expiry': topSaved.length,
        'waste_avoided_kg': wasteKg,
        'dishes_cooked': topSaved.length,
        'weekly_bars': weeklyBars,
        'by_category': byCategory,
      };
    }
    return json;
  }

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
