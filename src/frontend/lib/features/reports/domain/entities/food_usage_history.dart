import 'package:sweepfood/features/reports/domain/entities/waste_reduction_summary.dart';

enum FoodUsageType {
  cooking('COOKING'),
  manual('MANUAL');

  const FoodUsageType(this.wire);
  final String wire;

  static FoodUsageType fromWire(String? wire) {
    return switch (wire) {
      'COOKING' => FoodUsageType.cooking,
      'MANUAL' => FoodUsageType.manual,
      _ => FoodUsageType.cooking,
    };
  }

  String get label => switch (this) {
        FoodUsageType.cooking => 'Nấu ăn',
        FoodUsageType.manual => 'Dùng trực tiếp',
      };
}

class FoodUsageEntry {
  const FoodUsageEntry({
    required this.id,
    required this.ingredientName,
    required this.quantity,
    required this.unit,
    required this.recipeName,
    required this.usageType,
    required this.usedBeforeExpiry,
    required this.usedAt,
  });

  final String id;
  final String ingredientName;
  final double quantity;
  final String unit;
  final String? recipeName;
  final FoodUsageType usageType;
  final bool usedBeforeExpiry;
  final DateTime usedAt;

  String get quantityLabel {
    final qtyStr = quantity == quantity.roundToDouble()
        ? quantity.round().toString()
        : quantity.toStringAsFixed(1);
    return '$qtyStr $unit';
  }

  String get contextTitle {
    if (recipeName != null && recipeName!.isNotEmpty) {
      return 'Nấu: $recipeName';
    }
    return usageType.label;
  }
}

class FoodUsageHistory {
  const FoodUsageHistory({
    required this.period,
    required this.totalUsedCount,
    required this.totalUsedKg,
    required this.items,
  });

  final ReportPeriod period;
  final int totalUsedCount;
  final double totalUsedKg;
  final List<FoodUsageEntry> items;

  bool get isEmpty => items.isEmpty;

  String get totalUsedKgLabel =>
      '${totalUsedKg.toStringAsFixed(1).replaceAll('.', ',')} kg';
}
