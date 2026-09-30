import 'package:sweepfood/features/reports/domain/entities/waste_reduction_summary.dart';

enum EfficiencyRatingLevel {
  excellent('EXCELLENT'),
  good('GOOD'),
  average('AVERAGE'),
  poor('POOR');

  const EfficiencyRatingLevel(this.wire);
  final String wire;

  static EfficiencyRatingLevel fromWire(String? wire) => switch (wire) {
        'EXCELLENT' => EfficiencyRatingLevel.excellent,
        'GOOD' => EfficiencyRatingLevel.good,
        'AVERAGE' => EfficiencyRatingLevel.average,
        'POOR' => EfficiencyRatingLevel.poor,
        _ => EfficiencyRatingLevel.good,
      };

  String get label => switch (this) {
        EfficiencyRatingLevel.excellent => 'Xuất sắc',
        EfficiencyRatingLevel.good => 'Tốt',
        EfficiencyRatingLevel.average => 'Trung bình',
        EfficiencyRatingLevel.poor => 'Cần cải thiện',
      };
}

enum InsightType {
  positive('POSITIVE'),
  recommendation('RECOMMENDATION'),
  warning('WARNING');

  const InsightType(this.wire);
  final String wire;

  static InsightType fromWire(String? wire) => switch (wire) {
        'POSITIVE' => InsightType.positive,
        'RECOMMENDATION' => InsightType.recommendation,
        'WARNING' => InsightType.warning,
        _ => InsightType.recommendation,
      };
}

class SmartInsight {
  const SmartInsight({
    required this.type,
    required this.title,
    required this.message,
  });

  final InsightType type;
  final String title;
  final String message;
}

class EfficiencyTrend {
  const EfficiencyTrend({
    required this.scoreDelta,
    required this.wasteKgDelta,
  });

  final double scoreDelta;
  final double wasteKgDelta;

  bool get isPositive => scoreDelta >= 0;
}

class EfficiencyEvaluation {
  const EfficiencyEvaluation({
    required this.period,
    required this.efficiencyScore,
    required this.ratingLevel,
    required this.utilizationRate,
    required this.wasteRate,
    required this.trend,
    required this.insights,
  });

  final ReportPeriod period;
  final int efficiencyScore;
  final EfficiencyRatingLevel ratingLevel;
  final double utilizationRate;
  final double wasteRate;
  final EfficiencyTrend trend;
  final List<SmartInsight> insights;

  String get scoreLabel => '$efficiencyScore / 100';

  String get utilizationRateLabel =>
      '${utilizationRate.toStringAsFixed(1).replaceAll('.', ',')}%';

  String get wasteRateLabel =>
      '${wasteRate.toStringAsFixed(1).replaceAll('.', ',')}%';
}
