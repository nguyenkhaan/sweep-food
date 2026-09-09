import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooking_history.dart';
import 'package:sweepfood/features/cooking/presentation/controllers/cooking_history_controller.dart';

final _dateFmt = DateFormat('dd/MM/yyyy · HH:mm');

/// D-08 Lịch sử nấu ăn — danh sách các phiên nấu đã hoàn tất.
class CookingHistoryScreen extends ConsumerWidget {
  const CookingHistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final async = ref.watch(cookingHistoryControllerProvider);

    return Scaffold(
      appBar: AppBar(title: Text(l10n.cookingHistoryTitle)),
      body: RefreshIndicator(
        onRefresh: () =>
            ref.read(cookingHistoryControllerProvider.notifier).refresh(),
        child: AsyncValueWidget<List<CookingHistoryEntry>>(
          value: async,
          onRetry: () => ref.invalidate(cookingHistoryControllerProvider),
          data: (entries) {
            if (entries.isEmpty) {
              return ListView(
                children: [
                  const SizedBox(height: 100),
                  EmptyState(
                    title: l10n.cookingHistoryEmptyTitle,
                    message: l10n.cookingHistoryEmptyMessage,
                    icon: Icons.restaurant_menu_rounded,
                    actionLabel: l10n.cookingHistoryExploreSuggestions,
                    onAction: () => context.go(Routes.suggestions),
                  ),
                ],
              );
            }

            return ListView.separated(
              padding: const EdgeInsets.fromLTRB(Gap.md, Gap.md, Gap.md, Gap.xxl),
              itemCount: entries.length,
              separatorBuilder: (_, __) => const SizedBox(height: Gap.sm),
              itemBuilder: (context, i) => _HistoryTile(entry: entries[i]),
            );
          },
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
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: Radii.brMd,
        side: BorderSide(color: context.sweep.hairline),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(
          horizontal: Gap.md,
          vertical: Gap.xs,
        ),
        leading: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: done
                ? context.colors.primaryContainer
                : context.sweep.subtleFill,
            borderRadius: Radii.brMd,
          ),
          child: Icon(
            done ? Icons.check_rounded : Icons.close_rounded,
            color: done
                ? context.colors.onPrimaryContainer
                : context.sweep.textTertiary,
          ),
        ),
        title: Text(
          entry.recipeName.isEmpty ? 'Món ăn' : entry.recipeName,
          style: context.text.titleSmall,
        ),
        subtitle: Text(
          [
            context.l10n.cookingHistoryServings(_servingsLabel(entry.servings)),
            if (entry.completedAt != null)
              _dateFmt.format(entry.completedAt!.toLocal())
            else
              entry.status.label,
          ].join(' · '),
          style: context.text.bodySmall?.copyWith(
            color: context.sweep.textSecondary,
          ),
        ),
        trailing: const Icon(Icons.chevron_right_rounded),
        onTap: () => context.push('${Routes.cookHistory}/${entry.sessionId}'),
      ),
    );
  }

  String _servingsLabel(double v) =>
      v == v.roundToDouble() ? v.round().toString() : v.toStringAsFixed(1);
}
