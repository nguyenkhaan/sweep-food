import 'package:flutter/material.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/features/reports/domain/entities/waste_reduction_summary.dart';

/// R-01 top-bar period toggle — Tuần này / Tháng này.
class PeriodSelector extends StatelessWidget {
  const PeriodSelector({
    required this.value,
    required this.onChanged,
    super.key,
  });

  final ReportPeriod value;
  final ValueChanged<ReportPeriod> onChanged;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return PopupMenuButton<ReportPeriod>(
      initialValue: value,
      onSelected: onChanged,
      itemBuilder: (context) => [
        for (final p in ReportPeriod.values)
          PopupMenuItem(value: p, child: Text(p.label(l10n))),
      ],
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(value.label(l10n)),
            const Icon(Icons.arrow_drop_down_rounded),
          ],
        ),
      ),
    );
  }
}
