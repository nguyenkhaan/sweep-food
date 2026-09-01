import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

part 'waste_reduction_summary.freezed.dart';

enum ReportPeriod {
  week('week'),
  month('month');

  const ReportPeriod(this.wire);
  final String wire;

  String label(AppL10n l10n) => switch (this) {
    ReportPeriod.week => l10n.reportPeriodWeek,
    ReportPeriod.month => l10n.reportPeriodMonth,
  };

  static ReportPeriod fromWire(String? v) => ReportPeriod.values.firstWhere(
    (p) => p.wire == v,
    orElse: () => ReportPeriod.month,
  );
}

/// One bar in the weekly chart (R-01).
@freezed
abstract class WasteReductionBar with _$WasteReductionBar {
  const factory WasteReductionBar({required String label, required int value}) =
      _WasteReductionBar;
}

/// One row of the "theo nhóm thực phẩm" breakdown.
@freezed
abstract class WasteReductionCategory with _$WasteReductionCategory {
  const factory WasteReductionCategory({
    required String category,
    required int count,
    required int colorValue,
  }) = _WasteReductionCategory;
}

/// R-01 "Chống lãng phí". Counts of ingredients used before expiry + kg avoided
/// + dishes cooked. **No money** — price data isn't reliable (spec R-02 deferred).
@freezed
abstract class WasteReductionSummary with _$WasteReductionSummary {
  const WasteReductionSummary._();

  const factory WasteReductionSummary({
    required ReportPeriod period,
    required String periodLabel,
    required int itemsUsedBeforeExpiry,
    required double wasteAvoidedKg,
    required int dishesCooked,
    @Default(<WasteReductionBar>[]) List<WasteReductionBar> weeklyBars,
    @Default(<WasteReductionCategory>[])
    List<WasteReductionCategory> byCategory,
  }) = _WasteReductionSummary;

  bool get isEmpty => itemsUsedBeforeExpiry == 0 && dishesCooked == 0;

  String get wasteAvoidedLabel =>
      '${wasteAvoidedKg.toStringAsFixed(1).replaceAll('.', ',')} kg';

  int get maxBar => weeklyBars.fold(1, (m, b) => b.value > m ? b.value : m);
}
