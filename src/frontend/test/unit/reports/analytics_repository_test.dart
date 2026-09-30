import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/features/reports/data/datasources/report_remote_data_source.dart';
import 'package:sweepfood/features/reports/data/repositories/report_repository_impl.dart';
import 'package:sweepfood/features/reports/domain/entities/efficiency_evaluation.dart';
import 'package:sweepfood/features/reports/domain/entities/food_usage_history.dart';
import 'package:sweepfood/features/reports/domain/entities/waste_reduction_summary.dart';

class _MockApiClient extends Mock implements ApiClient {}

void main() {
  late _MockApiClient mockApi;
  late ReportRepositoryImpl repo;

  setUp(() {
    mockApi = _MockApiClient();
    repo = ReportRepositoryImpl(ReportRemoteDataSource(mockApi));
  });

  group('Analytics & Reports Repository Tests', () {
    test('usageHistory maps JSON payload correctly', () async {
      when(() => mockApi.get('/reports/usage-history', query: {'period': 'month'}))
          .thenAnswer((_) async => {
                'period': 'month',
                'total_used_count': 2,
                'total_used_kg': 1.5,
                'items': [
                  {
                    'id': 'u1',
                    'ingredient_name': 'Thịt bò',
                    'quantity': 500.0,
                    'unit': 'GRAM',
                    'recipe_name': 'Bò kho',
                    'usage_type': 'COOKING',
                    'used_before_expiry': true,
                    'used_at': '2026-09-29T10:00:00Z',
                  },
                  {
                    'id': 'u2',
                    'ingredient_name': 'Sữa chua',
                    'quantity': 100.0,
                    'unit': 'GRAM',
                    'recipe_name': null,
                    'usage_type': 'MANUAL',
                    'used_before_expiry': false,
                    'used_at': '2026-09-28T09:00:00Z',
                  },
                ],
              });

      final res = await repo.usageHistory(ReportPeriod.month);

      expect(res.isRight(), isTrue);
      final history = res.fold((f) => throw f, (s) => s);
      expect(history.totalUsedCount, 2);
      expect(history.totalUsedKg, 1.5);
      expect(history.items.length, 2);
      expect(history.items[0].ingredientName, 'Thịt bò');
      expect(history.items[0].usageType, FoodUsageType.cooking);
      expect(history.items[0].usedBeforeExpiry, isTrue);
      expect(history.items[1].usageType, FoodUsageType.manual);
      expect(history.items[1].usedBeforeExpiry, isFalse);
    });

    test('wasteStatistics maps categories and reasons correctly', () async {
      when(() => mockApi.get('/reports/waste-statistics', query: {'period': 'month'}))
          .thenAnswer((_) async => {
                'period': 'month',
                'total_wasted_kg': 0.8,
                'wasted_items_count': 1,
                'by_category': [
                  {'category_name': 'Rau củ', 'wasted_kg': 0.8, 'percentage': 100.0}
                ],
                'waste_reasons': [
                  {'reason': 'EXPIRED', 'count': 1, 'percentage': 100.0}
                ],
                'wasted_batches': [
                  {
                    'batch_id': 'b1',
                    'ingredient_name': 'Rau bina',
                    'quantity': 800.0,
                    'unit': 'GRAM',
                    'expired_at': '2026-09-27T00:00:00Z',
                    'discarded_at': '2026-09-28T00:00:00Z',
                    'reason': 'EXPIRED',
                  }
                ],
              });

      final res = await repo.wasteStatistics(ReportPeriod.month);

      expect(res.isRight(), isTrue);
      final stats = res.fold((f) => throw f, (s) => s);
      expect(stats.totalWastedKg, 0.8);
      expect(stats.wastedItemsCount, 1);
      expect(stats.byCategory.first.categoryName, 'Rau củ');
      expect(stats.wasteReasons.first.reason, 'EXPIRED');
      expect(stats.wastedBatches.first.ingredientName, 'Rau bina');
    });

    test('efficiencyEvaluation maps score and insights correctly', () async {
      when(() => mockApi.get('/reports/efficiency', query: {'period': 'month'}))
          .thenAnswer((_) async => {
                'period': 'month',
                'efficiency_score': 88,
                'rating_level': 'EXCELLENT',
                'utilization_rate': 92.0,
                'waste_rate': 8.0,
                'trend_vs_previous_period': {
                  'score_delta': 3.5,
                  'waste_kg_delta': -0.2,
                },
                'insights': [
                  {
                    'type': 'POSITIVE',
                    'title': 'Bảo quản tốt',
                    'message': 'Rất ít thực phẩm bị hỏng.',
                  }
                ],
              });

      final res = await repo.efficiencyEvaluation(ReportPeriod.month);

      expect(res.isRight(), isTrue);
      final eval = res.fold((f) => throw f, (s) => s);
      expect(eval.efficiencyScore, 88);
      expect(eval.ratingLevel, EfficiencyRatingLevel.excellent);
      expect(eval.utilizationRate, 92.0);
      expect(eval.trend.isPositive, isTrue);
      expect(eval.insights.length, 1);
      expect(eval.insights.first.type, InsightType.positive);
    });
  });
}
