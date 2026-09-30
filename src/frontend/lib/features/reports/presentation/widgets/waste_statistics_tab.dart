import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:sweepfood/app/theme/app_colors.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/features/reports/domain/entities/waste_statistics.dart';
import 'package:sweepfood/features/reports/presentation/controllers/reports_controller.dart';

final _dateFmt = DateFormat('dd/MM/yyyy');

class WasteStatisticsTab extends ConsumerWidget {
  const WasteStatisticsTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(wasteStatisticsProvider);

    return RefreshIndicator(
      onRefresh: () => ref.refresh(wasteStatisticsProvider.future),
      child: AsyncValueWidget<WasteStatistics>(
        value: async,
        onRetry: () => ref.invalidate(wasteStatisticsProvider),
        data: (stats) {
          if (stats.isEmpty) {
            return ListView(
              children: const [
                SizedBox(height: 72),
                EmptyState(
                  title: 'Tuyệt vời! Không có thực phẩm lãng phí',
                  message:
                      'Bạn chưa có thực phẩm nào bị hỏng hoặc bỏ phí trong kỳ này.',
                  icon: Icons.check_circle_outline_rounded,
                ),
              ],
            );
          }

          return ListView(
            padding: const EdgeInsets.fromLTRB(Gap.md, Gap.md, Gap.md, Gap.xxl),
            children: [
              _HeroWasteCard(stats: stats),
              Gap.gapMd,
              _SectionCard(
                title: 'PHÂN BỐ THEO NHÓM THỰC PHẨM',
                child: Column(
                  children: [
                    for (final cat in stats.byCategory) ...[
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: Gap.xs),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  cat.categoryName,
                                  style: context.text.bodyMedium?.copyWith(
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                                Text(
                                  '${cat.percentage.toStringAsFixed(1)}% (${cat.wastedKgLabel})',
                                  style: context.text.bodySmall?.copyWith(
                                    color: context.sweep.textSecondary,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 6),
                            ClipRRect(
                              borderRadius: BorderRadius.circular(4),
                              child: LinearProgressIndicator(
                                value: (cat.percentage / 100).clamp(0.0, 1.0),
                                minHeight: 8,
                                backgroundColor: context.sweep.subtleFill,
                                valueColor: AlwaysStoppedAnimation<Color>(
                                  Color(cat.colorValue),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              Gap.gapMd,
              _SectionCard(
                title: 'NGUYÊN NHÂN LÃNG PHÍ',
                child: Wrap(
                  spacing: Gap.sm,
                  runSpacing: Gap.xs,
                  children: [
                    for (final r in stats.wasteReasons)
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: Gap.sm,
                          vertical: Gap.xs,
                        ),
                        decoration: BoxDecoration(
                          color: context.colors.surfaceContainerLow,
                          borderRadius: Radii.brSm,
                          border: Border.all(color: context.sweep.hairline),
                        ),
                        child: Text(
                          '${r.label}: ${r.count} món (${r.percentage.toStringAsFixed(0)}%)',
                          style: context.text.bodySmall?.copyWith(
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                  ],
                ),
              ),
              if (stats.wastedBatches.isNotEmpty) ...[
                Gap.gapMd,
                _SectionCard(
                  title: 'DANH SÁCH THỰC PHẨM ĐÃ BỎ PHÍ',
                  child: Column(
                    children: [
                      for (final item in stats.wastedBatches)
                        Padding(
                          padding: const EdgeInsets.symmetric(vertical: Gap.xs),
                          child: Row(
                            children: [
                              Container(
                                width: 8,
                                height: 8,
                                decoration: const BoxDecoration(
                                  color: BrandPalette.brick500,
                                  shape: BoxShape.circle,
                                ),
                              ),
                              const SizedBox(width: Gap.sm),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      item.ingredientName,
                                      style: context.text.bodyMedium?.copyWith(
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                    if (item.expiredAt != null)
                                      Text(
                                        'Hết hạn: ${_dateFmt.format(item.expiredAt!)}',
                                        style: context.text.labelSmall?.copyWith(
                                          color: context.sweep.textTertiary,
                                        ),
                                      ),
                                  ],
                                ),
                              ),
                              Text(
                                item.quantityLabel,
                                style: context.text.bodyMedium?.copyWith(
                                  fontWeight: FontWeight.w700,
                                  color: BrandPalette.brick500,
                                ),
                              ),
                            ],
                          ),
                        ),
                    ],
                  ),
                ),
              ],
            ],
          );
        },
      ),
    );
  }
}

class _HeroWasteCard extends StatelessWidget {
  const _HeroWasteCard({required this.stats});

  final WasteStatistics stats;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(Gap.lg),
      decoration: BoxDecoration(
        color: BrandPalette.brick100,
        borderRadius: Radii.brLg,
        border: Border.all(color: BrandPalette.brick500.withValues(alpha: 0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(
                Icons.delete_outline_rounded,
                size: 20,
                color: BrandPalette.brick500,
              ),
              const SizedBox(width: Gap.xs),
              Text(
                'Lượng thực phẩm lãng phí trong kỳ',
                style: context.text.labelMedium?.copyWith(
                  color: BrandPalette.brick500,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            stats.totalWastedKgLabel,
            style: context.text.headlineMedium?.copyWith(
              fontWeight: FontWeight.w800,
              color: BrandPalette.brick500,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            'Khoảng ${stats.wastedItemsCount} nguyên liệu đã không được dùng kịp thời.',
            style: context.text.bodySmall?.copyWith(
              color: BrandPalette.brick500.withValues(alpha: 0.9),
            ),
          ),
        ],
      ),
    );
  }
}

class _SectionCard extends StatelessWidget {
  const _SectionCard({required this.title, required this.child});

  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(Gap.md),
      decoration: BoxDecoration(
        color: context.colors.surfaceContainerLowest,
        borderRadius: Radii.brLg,
        border: Border.all(color: context.sweep.hairline),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: context.text.labelSmall?.copyWith(
              color: context.sweep.textSecondary,
              letterSpacing: 0.5,
            ),
          ),
          Gap.gapSm,
          child,
        ],
      ),
    );
  }
}
