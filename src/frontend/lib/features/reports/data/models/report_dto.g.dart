// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'report_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_WasteBarDto _$WasteBarDtoFromJson(Map<String, dynamic> json) => _WasteBarDto(
  label: json['label'] as String,
  value: (json['value'] as num).toInt(),
);

Map<String, dynamic> _$WasteBarDtoToJson(_WasteBarDto instance) =>
    <String, dynamic>{'label': instance.label, 'value': instance.value};

_WasteCategoryDto _$WasteCategoryDtoFromJson(Map<String, dynamic> json) =>
    _WasteCategoryDto(
      category: json['category'] as String,
      count: (json['count'] as num).toInt(),
    );

Map<String, dynamic> _$WasteCategoryDtoToJson(_WasteCategoryDto instance) =>
    <String, dynamic>{'category': instance.category, 'count': instance.count};

_WasteReductionSummaryDto _$WasteReductionSummaryDtoFromJson(
  Map<String, dynamic> json,
) => _WasteReductionSummaryDto(
  period: json['period'] as String,
  periodLabel: json['period_label'] as String,
  itemsUsedBeforeExpiry: (json['items_used_before_expiry'] as num).toInt(),
  wasteAvoidedKg: (json['waste_avoided_kg'] as num).toDouble(),
  dishesCooked: (json['dishes_cooked'] as num).toInt(),
  weeklyBars:
      (json['weekly_bars'] as List<dynamic>?)
          ?.map((e) => WasteBarDto.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <WasteBarDto>[],
  byCategory:
      (json['by_category'] as List<dynamic>?)
          ?.map((e) => WasteCategoryDto.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <WasteCategoryDto>[],
);

Map<String, dynamic> _$WasteReductionSummaryDtoToJson(
  _WasteReductionSummaryDto instance,
) => <String, dynamic>{
  'period': instance.period,
  'period_label': instance.periodLabel,
  'items_used_before_expiry': instance.itemsUsedBeforeExpiry,
  'waste_avoided_kg': instance.wasteAvoidedKg,
  'dishes_cooked': instance.dishesCooked,
  'weekly_bars': instance.weeklyBars,
  'by_category': instance.byCategory,
};
