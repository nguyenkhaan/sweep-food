import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/formatters/quantity_format.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooking_history.dart';
import 'package:sweepfood/features/cooking/presentation/controllers/cooking_history_controller.dart';

final _dateFmt = DateFormat('dd/MM/yyyy · HH:mm');

/// D-09 Chi tiết một phiên nấu đã hoàn tất (Concept B · Format 1).
class CookingHistoryDetailScreen extends ConsumerWidget {
  const CookingHistoryDetailScreen({required this.sessionId, super.key});

  final String sessionId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final cs = context.colors;
    final sweep = context.sweep;
    final async = ref.watch(cookingHistoryDetailProvider(sessionId));
    final detail = async.asData?.value;

    return EmeraldSystemOverlay(
      child: Scaffold(
        backgroundColor: cs.surface,
        body: Column(
          children: [
            EmeraldSplitHeader(
              title: detail != null && detail.recipeName.isNotEmpty
                  ? detail.recipeName
                  : l10n.cookingHistoryDetailTitle,
              subtitle: detail?.status.label,
            ),
            Expanded(
              child: AsyncValueWidget<CookingHistoryDetail>(
                value: async,
                onRetry: () =>
                    ref.invalidate(cookingHistoryDetailProvider(sessionId)),
                data: (d) => ListView(
                  padding: EdgeInsets.fromLTRB(
                    Gap.lg,
                    Gap.xs,
                    Gap.lg,
                    MediaQuery.paddingOf(context).bottom + Gap.xxl,
                  ),
                  children: [
                    _InfoCard(
                      rows: [
                        (l10n.cookingHistoryServingsCount, _num(d.servings)),
                        if (d.completedAt != null)
                          (
                            l10n.cookingHistoryCompletedAt,
                            _dateFmt.format(d.completedAt!.toLocal()),
                          ),
                        if (d.consumptionMode != null)
                          (
                            l10n.cookingHistoryDeductionMode,
                            d.consumptionMode!.label(l10n),
                          ),
                        (
                          l10n.cookingHistoryLeftoverSaved,
                          d.leftoverBatchId != null
                              ? l10n.commonYes
                              : l10n.commonNo,
                        ),
                      ],
                    ),
                    Gap.gapLg,
                    Padding(
                      padding: const EdgeInsets.only(left: 4, bottom: Gap.xs + 2),
                      child: Text(
                        l10n.cookingHistoryDeductedIngredients.toUpperCase(),
                        style: context.text.labelSmall?.copyWith(
                          letterSpacing: 0.7,
                          fontWeight: FontWeight.w800,
                          color: sweep.textTertiary,
                        ),
                      ),
                    ),
                    if (d.consumptions.isEmpty)
                      Container(
                        padding: const EdgeInsets.all(Gap.md),
                        decoration: BoxDecoration(
                          color: cs.surfaceContainerLowest,
                          borderRadius: Radii.brXl,
                          border: Border.all(color: sweep.hairline),
                        ),
                        child: Text(
                          l10n.cookingHistoryNoDeductions,
                          style: context.text.bodySmall?.copyWith(
                            color: sweep.textSecondary,
                          ),
                        ),
                      )
                    else
                      Container(
                        decoration: BoxDecoration(
                          color: cs.surfaceContainerLowest,
                          borderRadius: Radii.brXl,
                          border: Border.all(color: sweep.hairline),
                          boxShadow: Shadows.e1,
                        ),
                        child: Column(
                          children: [
                            for (final (i, c) in d.consumptions.indexed)
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: Gap.md,
                                  vertical: Gap.sm + 4,
                                ),
                                decoration: BoxDecoration(
                                  border: i == d.consumptions.length - 1
                                      ? null
                                      : Border(
                                          bottom: BorderSide(
                                            color: sweep.hairline,
                                          ),
                                        ),
                                ),
                                child: Row(
                                  children: [
                                    Expanded(
                                      child: Text(
                                        l10n.cookingHistoryBatchPrefix(
                                          _shortId(c.inventoryBatchId),
                                        ),
                                        style: context.text.bodyMedium,
                                      ),
                                    ),
                                    Text(
                                      '− ${formatQuantity(c.quantity, c.unit)}',
                                      style: AppTypography.tabular(
                                        context.text.bodyMedium?.copyWith(
                                          fontWeight: FontWeight.w700,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  static String _num(double v) =>
      v == v.roundToDouble() ? v.round().toString() : v.toStringAsFixed(1);

  static String _shortId(String id) =>
      id.length <= 8 ? id : '…${id.substring(id.length - 6)}';
}

class _InfoCard extends StatelessWidget {
  const _InfoCard({required this.rows});

  final List<(String, String)> rows;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: Gap.md, vertical: Gap.xs),
      decoration: BoxDecoration(
        color: context.colors.surfaceContainerLowest,
        borderRadius: Radii.brXl,
        border: Border.all(color: sweep.hairline),
        boxShadow: Shadows.e1,
      ),
      child: Column(
        children: [
          for (var i = 0; i < rows.length; i++) ...[
            Padding(
              padding: const EdgeInsets.symmetric(vertical: Gap.sm + 2),
              child: Row(
                children: [
                  Expanded(
                    flex: 5,
                    child: Text(
                      rows[i].$1,
                      style: context.text.bodyMedium?.copyWith(
                        color: sweep.textSecondary,
                      ),
                    ),
                  ),
                  Expanded(
                    flex: 4,
                    child: Text(
                      rows[i].$2,
                      textAlign: TextAlign.right,
                      style: context.text.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            if (i < rows.length - 1) Divider(height: 1, color: sweep.hairline),
          ],
        ],
      ),
    );
  }
}
