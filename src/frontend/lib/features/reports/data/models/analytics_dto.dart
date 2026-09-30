import 'package:sweepfood/features/reports/domain/entities/efficiency_evaluation.dart';
import 'package:sweepfood/features/reports/domain/entities/food_usage_history.dart';
import 'package:sweepfood/features/reports/domain/entities/waste_reduction_summary.dart';
import 'package:sweepfood/features/reports/domain/entities/waste_statistics.dart';

class FoodUsageEntryDto {
  const FoodUsageEntryDto({
    required this.id,
    required this.ingredientName,
    required this.quantity,
    required this.unit,
    this.recipeName,
    required this.usageType,
    required this.usedBeforeExpiry,
    required this.usedAt,
  });

  final String id;
  final String ingredientName;
  final double quantity;
  final String unit;
  final String? recipeName;
  final String usageType;
  final bool usedBeforeExpiry;
  final String usedAt;

  factory FoodUsageEntryDto.fromJson(Map<String, dynamic> json) {
    return FoodUsageEntryDto(
      id: json['id']?.toString() ?? '',
      ingredientName: json['ingredient_name'] as String? ?? 'Nguyên liệu',
      quantity: (json['quantity'] as num?)?.toDouble() ?? 0.0,
      unit: json['unit'] as String? ?? 'g',
      recipeName: json['recipe_name'] as String?,
      usageType: json['usage_type'] as String? ?? 'COOKING',
      usedBeforeExpiry: json['used_before_expiry'] as bool? ?? true,
      usedAt: json['used_at'] as String? ?? '',
    );
  }

  FoodUsageEntry toEntity() {
    return FoodUsageEntry(
      id: id,
      ingredientName: ingredientName,
      quantity: quantity,
      unit: unit,
      recipeName: recipeName,
      usageType: FoodUsageType.fromWire(usageType),
      usedBeforeExpiry: usedBeforeExpiry,
      usedAt: DateTime.tryParse(usedAt)?.toLocal() ?? DateTime.now(),
    );
  }
}

class FoodUsageHistoryDto {
  const FoodUsageHistoryDto({
    required this.period,
    required this.totalUsedCount,
    required this.totalUsedKg,
    required this.items,
  });

  final String period;
  final int totalUsedCount;
  final double totalUsedKg;
  final List<FoodUsageEntryDto> items;

  factory FoodUsageHistoryDto.fromJson(Map<String, dynamic> json) {
    final rawItems = json['items'] as List<dynamic>? ?? [];
    return FoodUsageHistoryDto(
      period: json['period'] as String? ?? 'month',
      totalUsedCount: (json['total_used_count'] as num?)?.toInt() ?? rawItems.length,
      totalUsedKg: double.tryParse(json['total_used_kg']?.toString() ?? '0') ??
          (json['total_used_kg'] as num?)?.toDouble() ??
          0.0,
      items: rawItems
          .whereType<Map<String, dynamic>>()
          .map(FoodUsageEntryDto.fromJson)
          .toList(),
    );
  }

  FoodUsageHistory toEntity() {
    return FoodUsageHistory(
      period: ReportPeriod.fromWire(period),
      totalUsedCount: totalUsedCount,
      totalUsedKg: totalUsedKg,
      items: items.map((e) => e.toEntity()).toList(),
    );
  }
}

class WasteStatisticsDto {
  const WasteStatisticsDto({
    required this.period,
    required this.totalWastedKg,
    required this.wastedItemsCount,
    required this.byCategory,
    required this.wasteReasons,
    required this.wastedBatches,
  });

  final String period;
  final double totalWastedKg;
  final int wastedItemsCount;
  final List<Map<String, dynamic>> byCategory;
  final List<Map<String, dynamic>> wasteReasons;
  final List<Map<String, dynamic>> wastedBatches;

  factory WasteStatisticsDto.fromJson(Map<String, dynamic> json) {
    return WasteStatisticsDto(
      period: json['period'] as String? ?? 'month',
      totalWastedKg: double.tryParse(json['total_wasted_kg']?.toString() ?? '0') ??
          (json['total_wasted_kg'] as num?)?.toDouble() ??
          0.0,
      wastedItemsCount: (json['wasted_items_count'] as num?)?.toInt() ?? 0,
      byCategory: (json['by_category'] as List<dynamic>?)
              ?.whereType<Map<String, dynamic>>()
              .toList() ??
          [],
      wasteReasons: (json['waste_reasons'] as List<dynamic>?)
              ?.whereType<Map<String, dynamic>>()
              .toList() ??
          [],
      wastedBatches: (json['wasted_batches'] as List<dynamic>?)
              ?.whereType<Map<String, dynamic>>()
              .toList() ??
          [],
    );
  }

  WasteStatistics toEntity() {
    return WasteStatistics(
      period: ReportPeriod.fromWire(period),
      totalWastedKg: totalWastedKg,
      wastedItemsCount: wastedItemsCount,
      byCategory: byCategory.map((c) {
        final catName = c['category_name'] as String? ?? 'Khác';
        return WasteCategoryShare(
          categoryName: catName,
          wastedKg: double.tryParse(c['wasted_kg']?.toString() ?? '0') ??
              (c['wasted_kg'] as num?)?.toDouble() ??
              0.0,
          percentage: (c['percentage'] as num?)?.toDouble() ?? 0.0,
          colorValue: _colorFor(catName),
        );
      }).toList(),
      wasteReasons: wasteReasons.map((r) {
        return WasteReasonShare(
          reason: r['reason'] as String? ?? 'OTHER',
          count: (r['count'] as num?)?.toInt() ?? 0,
          percentage: (r['percentage'] as num?)?.toDouble() ?? 0.0,
        );
      }).toList(),
      wastedBatches: wastedBatches.map((b) {
        return WastedBatchItem(
          batchId: b['batch_id']?.toString() ?? '',
          ingredientName: b['ingredient_name'] as String? ?? 'Nguyên liệu',
          quantity: (b['quantity'] as num?)?.toDouble() ?? 0.0,
          unit: b['unit'] as String? ?? 'g',
          expiredAt: b['expired_at'] != null
              ? DateTime.tryParse(b['expired_at'].toString())
              : null,
          discardedAt: b['discarded_at'] != null
              ? DateTime.tryParse(b['discarded_at'].toString())
              : null,
          reason: b['reason'] as String? ?? 'EXPIRED',
        );
      }).toList(),
    );
  }

  static int _colorFor(String category) {
    final c = category.toLowerCase();
    if (c.contains('rau')) return 0xFF40916C;
    if (c.contains('thịt') || c.contains('cá')) return 0xFF8D4D4E;
    if (c.contains('sữa')) return 0xFFE09F3E;
    return 0xFF7D8597;
  }
}

class EfficiencyEvaluationDto {
  const EfficiencyEvaluationDto({
    required this.period,
    required this.efficiencyScore,
    required this.ratingLevel,
    required this.utilizationRate,
    required this.wasteRate,
    required this.trend,
    required this.insights,
  });

  final String period;
  final int efficiencyScore;
  final String ratingLevel;
  final double utilizationRate;
  final double wasteRate;
  final Map<String, dynamic> trend;
  final List<Map<String, dynamic>> insights;

  factory EfficiencyEvaluationDto.fromJson(Map<String, dynamic> json) {
    return EfficiencyEvaluationDto(
      period: json['period'] as String? ?? 'month',
      efficiencyScore: (json['efficiency_score'] as num?)?.toInt() ?? 75,
      ratingLevel: json['rating_level'] as String? ?? 'GOOD',
      utilizationRate: (json['utilization_rate'] as num?)?.toDouble() ?? 85.0,
      wasteRate: (json['waste_rate'] as num?)?.toDouble() ?? 15.0,
      trend: (json['trend_vs_previous_period'] as Map<String, dynamic>?) ?? {},
      insights: (json['insights'] as List<dynamic>?)
              ?.whereType<Map<String, dynamic>>()
              .toList() ??
          [],
    );
  }

  EfficiencyEvaluation toEntity() {
    return EfficiencyEvaluation(
      period: ReportPeriod.fromWire(period),
      efficiencyScore: efficiencyScore,
      ratingLevel: EfficiencyRatingLevel.fromWire(ratingLevel),
      utilizationRate: utilizationRate,
      wasteRate: wasteRate,
      trend: EfficiencyTrend(
        scoreDelta: (trend['score_delta'] as num?)?.toDouble() ?? 0.0,
        wasteKgDelta: double.tryParse(trend['waste_kg_delta']?.toString() ?? '0') ??
            (trend['waste_kg_delta'] as num?)?.toDouble() ??
            0.0,
      ),
      insights: insights.map((i) {
        return SmartInsight(
          type: InsightType.fromWire(i['type'] as String?),
          title: i['title'] as String? ?? '',
          message: i['message'] as String? ?? '',
        );
      }).toList(),
    );
  }
}
