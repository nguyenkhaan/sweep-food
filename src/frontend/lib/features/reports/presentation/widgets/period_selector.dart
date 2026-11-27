import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/features/reports/domain/entities/waste_reduction_summary.dart';

/// R-01 top-bar period toggle — Tuần này / Tháng này.
class PeriodSelector extends StatelessWidget {
  const PeriodSelector({
    required this.value,
    required this.onChanged,
    this.foregroundColor,
    super.key,
  });

  final ReportPeriod value;
  final ValueChanged<ReportPeriod> onChanged;
  final Color? foregroundColor;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final fg = foregroundColor ?? context.colors.onSurface;
    return PopupMenuButton<ReportPeriod>(
      initialValue: value,
      onSelected: onChanged,
      itemBuilder: (context) => [
        for (final p in ReportPeriod.values)
          PopupMenuItem(value: p, child: Text(p.label(l10n))),
      ],
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              value.label(l10n),
              style: context.text.labelLarge?.copyWith(
                color: fg,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(width: 4),
            Icon(AppIcons.chevronDown, size: 16, color: fg),
          ],
        ),
      ),
    );
  }
}
