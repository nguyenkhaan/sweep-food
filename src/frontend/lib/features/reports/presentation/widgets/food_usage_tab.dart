import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:sweepfood/app/theme/app_colors.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/features/reports/domain/entities/food_usage_history.dart';
import 'package:sweepfood/features/reports/presentation/controllers/reports_controller.dart';

final _dateTimeFmt = DateFormat('dd/MM/yyyy · HH:mm');

class FoodUsageTab extends ConsumerWidget {
  const FoodUsageTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(foodUsageHistoryProvider);

    return RefreshIndicator(
      onRefresh: () => ref.refresh(foodUsageHistoryProvider.future),
      child: AsyncValueWidget<FoodUsageHistory>(
        value: async,
        onRetry: () => ref.invalidate(foodUsageHistoryProvider),
        data: (history) {
          if (history.isEmpty) {
            return ListView(
              children: const [
                SizedBox(height: 72),
                EmptyState(
                  title: 'Chưa có lịch sử sử dụng',
                  message: 'Các lượt nấu ăn và tiêu thụ thực phẩm sẽ hiển thị tại đây.',
                  icon: Icons.history_toggle_off_rounded,
                ),
              ],
            );
          }

          return ListView(
            padding: const EdgeInsets.fromLTRB(Gap.md, Gap.md, Gap.md, Gap.xxl),
            children: [
              _UsageHeroCard(history: history),
              Gap.gapMd,
              Text(
                'LỊCH SỬ TIÊU THỤ NGUYÊN LIỆU',
                style: context.text.labelSmall?.copyWith(
                  color: context.sweep.textSecondary,
                  letterSpacing: 0.5,
                ),
              ),
              Gap.gapSm,
              for (final entry in history.items) ...[
                _UsageEntryCard(entry: entry),
                const SizedBox(height: Gap.sm),
              ],
            ],
          );
        },
      ),
    );
  }
}

class _UsageHeroCard extends StatelessWidget {
  const _UsageHeroCard({required this.history});

  final FoodUsageHistory history;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(Gap.lg),
      decoration: BoxDecoration(
        color: context.colors.primaryContainer,
        borderRadius: Radii.brLg,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Tổng nguyên liệu đã sử dụng',
            style: context.text.labelMedium?.copyWith(
              color: context.colors.onPrimaryContainer.withValues(alpha: 0.8),
            ),
          ),
          const SizedBox(height: 4),
          Row(
            crossAxisAlignment: CrossAxisAlignment.baseline,
            textBaseline: TextBaseline.alphabetic,
            children: [
              Text(
                history.totalUsedKgLabel,
                style: context.text.headlineMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: context.colors.onPrimaryContainer,
                ),
              ),
              const SizedBox(width: Gap.sm),
              Text(
                '(${history.totalUsedCount} lượt sử dụng)',
                style: context.text.bodyMedium?.copyWith(
                  color: context.colors.onPrimaryContainer.withValues(alpha: 0.9),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _UsageEntryCard extends StatelessWidget {
  const _UsageEntryCard({required this.entry});

  final FoodUsageEntry entry;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(Gap.md),
      decoration: BoxDecoration(
        color: context.colors.surfaceContainerLowest,
        borderRadius: Radii.brMd,
        border: Border.all(color: context.sweep.hairline),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: entry.usedBeforeExpiry
                  ? BrandPalette.green100
                  : BrandPalette.brick100,
              borderRadius: Radii.brSm,
            ),
            child: Icon(
              entry.usageType == FoodUsageType.cooking
                  ? Icons.soup_kitchen_outlined
                  : Icons.restaurant_outlined,
              size: 20,
              color: entry.usedBeforeExpiry
                  ? BrandPalette.green700
                  : BrandPalette.brick500,
            ),
          ),
          const SizedBox(width: Gap.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        entry.ingredientName,
                        style: context.text.titleSmall?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                    Text(
                      entry.quantityLabel,
                      style: context.text.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                        color: context.colors.primary,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 2),
                Text(
                  entry.contextTitle,
                  style: context.text.bodySmall?.copyWith(
                    color: context.sweep.textSecondary,
                  ),
                ),
                const SizedBox(height: 6),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: Gap.xs + 2,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: entry.usedBeforeExpiry
                            ? BrandPalette.green100
                            : BrandPalette.brick100,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        entry.usedBeforeExpiry ? 'Dùng kịp thời' : 'Quá hạn',
                        style: context.text.labelSmall?.copyWith(
                          color: entry.usedBeforeExpiry
                              ? BrandPalette.green700
                              : BrandPalette.brick500,
                          fontWeight: FontWeight.w600,
                          fontSize: 11,
                        ),
                      ),
                    ),
                    Text(
                      _dateTimeFmt.format(entry.usedAt),
                      style: context.text.labelSmall?.copyWith(
                        color: context.sweep.textTertiary,
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
