import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/formatters/quantity_format.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooking_history.dart';
import 'package:sweepfood/features/cooking/presentation/controllers/cooking_history_controller.dart';

final _dateFmt = DateFormat('dd/MM/yyyy · HH:mm');

/// D-09 Chi tiết một phiên nấu đã hoàn tất.
class CookingHistoryDetailScreen extends ConsumerWidget {
  const CookingHistoryDetailScreen({required this.sessionId, super.key});

  final String sessionId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final async = ref.watch(cookingHistoryDetailProvider(sessionId));

    return Scaffold(
      appBar: AppBar(title: Text(l10n.cookingHistoryDetailTitle)),
      body: AsyncValueWidget<CookingHistoryDetail>(
        value: async,
        onRetry: () => ref.invalidate(cookingHistoryDetailProvider(sessionId)),
        data: (d) => ListView(
          padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.md, Gap.lg, Gap.xxl),
          children: [
            Text(
              d.recipeName.isEmpty ? 'Món ăn' : d.recipeName,
              style: context.text.headlineSmall,
            ),
            const SizedBox(height: 4),
            Text(
              d.status.label,
              style: context.text.bodyMedium?.copyWith(
                color: context.sweep.textSecondary,
              ),
            ),
            Gap.gapLg,
            _InfoCard(
              rows: [
                (l10n.cookingHistoryServingsCount, _num(d.servings)),
                if (d.completedAt != null)
                  (l10n.cookingHistoryCompletedAt, _dateFmt.format(d.completedAt!.toLocal())),
                if (d.consumptionMode != null)
                  (l10n.cookingHistoryDeductionMode, d.consumptionMode!.label(l10n)),
                (l10n.cookingHistoryLeftoverSaved, d.leftoverBatchId != null ? l10n.commonYes : l10n.commonNo),
              ],
            ),
            Gap.gapLg,
            Text(
              l10n.cookingHistoryDeductedIngredients,
              style: context.text.labelSmall?.copyWith(
                color: context.sweep.textTertiary,
              ),
            ),
            Gap.gapXs,
            if (d.consumptions.isEmpty)
              Text(
                l10n.cookingHistoryNoDeductions,
                style: context.text.bodySmall?.copyWith(
                  color: context.sweep.textSecondary,
                ),
              )
            else
              Container(
                decoration: BoxDecoration(
                  color: context.colors.surfaceContainerLowest,
                  borderRadius: Radii.brLg,
                  border: Border.all(color: context.sweep.hairline),
                ),
                child: Column(
                  children: [
                    for (final (i, c) in d.consumptions.indexed)
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: Gap.md,
                          vertical: Gap.sm,
                        ),
                        decoration: BoxDecoration(
                          border: i == d.consumptions.length - 1
                              ? null
                              : Border(
                                  bottom: BorderSide(
                                    color: context.sweep.hairline,
                                  ),
                                ),
                        ),
                        child: Row(
                          children: [
                            Expanded(
                              child: Text(
                                l10n.cookingHistoryBatchPrefix(_shortId(c.inventoryBatchId)),
                                style: context.text.bodyMedium,
                              ),
                            ),
                            Text(
                              '− ${formatQuantity(c.quantity, c.unit)}',
                              style: context.text.bodyMedium?.copyWith(
                                fontWeight: FontWeight.w700,
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
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: Gap.md, vertical: Gap.xs),
      decoration: BoxDecoration(
        color: context.colors.surfaceContainerLowest,
        borderRadius: Radii.brLg,
        border: Border.all(color: context.sweep.hairline),
      ),
      child: Column(
        children: [
          for (final (label, value) in rows)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: Gap.sm),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      label,
                      style: context.text.bodyMedium?.copyWith(
                        color: context.sweep.textSecondary,
                      ),
                    ),
                  ),
                  Text(
                    value,
                    style: context.text.bodyMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}
