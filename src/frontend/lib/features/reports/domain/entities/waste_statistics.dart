import 'package:sweepfood/features/reports/domain/entities/waste_reduction_summary.dart';

class WasteCategoryShare {
  const WasteCategoryShare({
    required this.categoryName,
    required this.wastedKg,
    required this.percentage,
    required this.colorValue,
  });

  final String categoryName;
  final double wastedKg;
  final double percentage;
  final int colorValue;

  String get wastedKgLabel =>
      '${wastedKg.toStringAsFixed(2).replaceAll('.', ',')} kg';
}

class WasteReasonShare {
  const WasteReasonShare({
    required this.reason,
    required this.count,
    required this.percentage,
  });

  final String reason;
  final int count;
  final double percentage;

  String get label => switch (reason) {
        'EXPIRED' => 'Hết hạn sử dụng',
        'SPOILED' => 'Bị hư hỏng / ẩm mốc',
        'DAMAGED' => 'Bị vỡ / biến chất',
        _ => 'Khác',
      };
}

class WastedBatchItem {
  const WastedBatchItem({
    required this.batchId,
    required this.ingredientName,
    required this.quantity,
    required this.unit,
    required this.expiredAt,
    required this.discardedAt,
    required this.reason,
  });

  final String batchId;
  final String ingredientName;
  final double quantity;
  final String unit;
  final DateTime? expiredAt;
  final DateTime? discardedAt;
  final String reason;

  String get quantityLabel {
    final qtyStr = quantity == quantity.roundToDouble()
        ? quantity.round().toString()
        : quantity.toStringAsFixed(1);
    return '$qtyStr $unit';
  }
}

class WasteStatistics {
  const WasteStatistics({
    required this.period,
    required this.totalWastedKg,
    required this.wastedItemsCount,
    required this.byCategory,
    required this.wasteReasons,
    required this.wastedBatches,
  });

  final ReportPeriod period;
  final double totalWastedKg;
  final int wastedItemsCount;
  final List<WasteCategoryShare> byCategory;
  final List<WasteReasonShare> wasteReasons;
  final List<WastedBatchItem> wastedBatches;

  bool get isEmpty => wastedItemsCount == 0 && totalWastedKg == 0;

  String get totalWastedKgLabel =>
      '${totalWastedKg.toStringAsFixed(2).replaceAll('.', ',')} kg';
}
