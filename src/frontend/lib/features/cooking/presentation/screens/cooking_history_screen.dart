import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooking_history.dart';
import 'package:sweepfood/features/cooking/presentation/controllers/cooking_history_controller.dart';

final _dateFmt = DateFormat('dd/MM/yyyy · HH:mm');

/// D-08 Lịch sử nấu ăn (Concept B · Format 1: Emerald Header + Grouped Card).
class CookingHistoryScreen extends ConsumerWidget {
  const CookingHistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final cs = context.colors;
    final async = ref.watch(cookingHistoryControllerProvider);
    final count = async.asData?.value.length;

    return EmeraldSystemOverlay(
      child: Scaffold(
        backgroundColor: cs.surface,
        body: Column(
          children: [
            EmeraldSplitHeader(
              title: l10n.cookingHistoryTitle,
              trailing: count != null && count > 0
                  ? EmeraldHeaderPill(label: '$count bữa')
                  : null,
            ),
            Expanded(
              child: RefreshIndicator(
                onRefresh: () =>
                    ref.read(cookingHistoryControllerProvider.notifier).refresh(),
                child: AsyncValueWidget<List<CookingHistoryEntry>>(
                  value: async,
                  onRetry: () =>
                      ref.invalidate(cookingHistoryControllerProvider),
                  data: (entries) {
                    if (entries.isEmpty) {
                      return ListView(
                        padding: const EdgeInsets.fromLTRB(
                          Gap.lg,
                          Gap.xl,
                          Gap.lg,
                          Gap.xxl,
                        ),
                        children: [
                          EmptyState(
                            illustrationAsset:
                                'assets/illustrations/empty_cooking_history.svg',
                            title: l10n.cookingHistoryEmptyTitle,
                            message: l10n.cookingHistoryEmptyMessage,
                            icon: AppIcons.utensils,
                            actionLabel: l10n.cookingHistoryExploreSuggestions,
                            onAction: () => context.go(Routes.suggestions),
                          ),
                        ],
                      );
                    }

                    return ListView(
                      padding: EdgeInsets.fromLTRB(
                        Gap.lg,
                        Gap.xs,
                        Gap.lg,
                        MediaQuery.paddingOf(context).bottom + Gap.xxl,
                      ),
                      children: [
                        Container(
                          decoration: BoxDecoration(
                            color: cs.surfaceContainerLowest,
                            borderRadius: Radii.brXl,
                            border: Border.all(color: context.sweep.hairline),
                            boxShadow: Shadows.e1,
                          ),
                          clipBehavior: Clip.antiAlias,
                          child: Column(
                            children: [
                              for (var i = 0; i < entries.length; i++) ...[
                                _HistoryTile(entry: entries[i]),
                                if (i < entries.length - 1)
                                  Divider(
                                    height: 1,
                                    indent: 68,
                                    color: context.sweep.hairline,
                                  ),
                              ],
                            ],
                          ),
                        ),
                      ],
                    );
                  },
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _HistoryTile extends StatelessWidget {
  const _HistoryTile({required this.entry});

  final CookingHistoryEntry entry;

  @override
  Widget build(BuildContext context) {
    final done = entry.status == CookingSessionStatus.completed;
    return InkWell(
      onTap: () {
        AppHaptics.selection();
        context.push('${Routes.cookHistory}/${entry.sessionId}');
      },
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: Gap.md,
          vertical: Gap.sm + 4,
        ),
        child: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: done
                    ? context.colors.primaryContainer
                    : context.sweep.subtleFill,
                borderRadius: Radii.brMd,
              ),
              child: Icon(
                done ? AppIcons.check : AppIcons.close,
                size: 18,
                color: done
                    ? context.colors.primary
                    : context.sweep.textTertiary,
              ),
            ),
            const SizedBox(width: Gap.sm + 2),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    entry.recipeName.isEmpty ? 'Món ăn' : entry.recipeName,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: context.text.titleSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    [
                      context.l10n.cookingHistoryServings(
                        _servingsLabel(entry.servings),
                      ),
                      if (entry.completedAt != null)
                        _dateFmt.format(entry.completedAt!.toLocal())
                      else
                        entry.status.label,
                    ].join(' · '),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: context.text.bodySmall?.copyWith(
                      color: context.sweep.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              AppIcons.chevronRight,
              size: 17,
              color: context.sweep.textTertiary,
            ),
          ],
        ),
      ),
    );
  }

  String _servingsLabel(double v) =>
      v == v.roundToDouble() ? v.round().toString() : v.toStringAsFixed(1);
}
