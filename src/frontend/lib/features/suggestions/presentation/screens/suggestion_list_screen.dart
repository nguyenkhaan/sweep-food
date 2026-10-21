import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/core/widgets/suggestion_card.dart';
import 'package:sweepfood/features/ingest/presentation/screens/add_entry_chooser_sheet.dart';
import 'package:sweepfood/features/suggestions/data/datasources/suggestion_remote_data_source.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/features/suggestions/presentation/controllers/suggestion_list_controller.dart';
import 'package:sweepfood/features/suggestions/presentation/widgets/score_breakdown_sheet.dart';
import 'package:sweepfood/features/suggestions/presentation/widgets/suggestion_card_chips.dart';

/// S-01 — AI-ranked dishes for the current pantry.
class SuggestionListScreen extends ConsumerWidget {
  const SuggestionListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(suggestionListControllerProvider);
    final aiHealth = ref.watch(aiServiceHealthProvider);

    return Scaffold(
      appBar: AppBar(title: Text(context.l10n.suggestionsTitle)),
      body: Column(
        children: [
          _AiStatusBanner(health: aiHealth),
          Expanded(
            child: RefreshIndicator(
              onRefresh: () =>
                  ref.read(suggestionListControllerProvider.notifier).refresh(),
              child: AsyncValueWidget<List<DishSuggestion>>(
                value: async,
                onRetry: () => ref.invalidate(suggestionListControllerProvider),
                data: (items) => _List(items: items),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _List extends StatelessWidget {
  const _List({required this.items});

  final List<DishSuggestion> items;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    if (items.isEmpty) {
      return ListView(
        children: [
          const SizedBox(height: 80),
          EmptyState(
            title: l10n.suggestionsEmptyTitle,
            message: l10n.suggestionsEmptyBody,
            icon: Icons.restaurant_menu_rounded,
            actionLabel: l10n.pantryAddIngredient,
            onAction: () => showAddEntryChooser(context),
          ),
        ],
      );
    }

    return ListView(
      padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, 96),
      children: [
        Padding(
          padding: const EdgeInsets.only(bottom: Gap.sm),
          child: Text(
            l10n.suggestionsCaption(items.length),
            style: context.text.labelSmall?.copyWith(
              letterSpacing: 0,
              color: context.sweep.textTertiary,
            ),
          ),
        ),
        if (items.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: Gap.md),
            child: _ModelSummary(suggestion: items.first),
          ),
        for (final s in items)
          Padding(
            padding: const EdgeInsets.only(bottom: Gap.md),
            child: _SuggestionTile(suggestion: s),
          ),
      ],
    );
  }
}

class _SuggestionTile extends StatelessWidget {
  const _SuggestionTile({required this.suggestion});

  final DishSuggestion suggestion;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        SuggestionCard(
          title: suggestion.dish.name,
          score: suggestion.score,
          rank: suggestion.rank,
          meta: suggestion.dish.shortMeta(l10n),
          chips: suggestion.cardChips(l10n),
          imageUrl: suggestion.dish.imageUrl,
          onTap: () => context.push(
            '${Routes.suggestions}/dish/${suggestion.id}',
            extra: suggestion,
          ),
        ),
        Align(
          alignment: Alignment.centerRight,
          child: TextButton.icon(
            onPressed: () => ScoreBreakdownSheet.show(context, suggestion),
            icon: const Icon(Icons.help_outline_rounded, size: 16),
            label: Text(context.l10n.suggestionsWhyScore),
          ),
        ),
      ],
    );
  }
}

class _AiStatusBanner extends ConsumerWidget {
  const _AiStatusBanner({required this.health});

  final AsyncValue<AiServiceHealthDto> health;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final healthValue = health.asData?.value;
    final ready = healthValue?.isReady == true;
    final failed = health.hasError;
    final color = ready
        ? context.colors.primary
        : failed
        ? context.colors.error
        : context.sweep.textTertiary;
    final label = ready
        ? 'SweepFood AI đã sẵn sàng'
        : failed
        ? 'SweepFood AI chưa kết nối'
        : 'Đang kiểm tra SweepFood AI…';

    return Padding(
      padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.sm),
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: Gap.sm,
          vertical: Gap.xs,
        ),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.08),
          borderRadius: Radii.brMd,
          border: Border.all(color: color.withValues(alpha: 0.25)),
        ),
        child: Row(
          children: [
            Icon(
              ready ? Icons.auto_awesome_rounded : Icons.hub_outlined,
              size: 17,
              color: color,
            ),
            const SizedBox(width: Gap.xs),
            Expanded(
              child: Text(
                label,
                style: context.text.labelMedium?.copyWith(color: color),
              ),
            ),
            if (failed)
              IconButton(
                visualDensity: VisualDensity.compact,
                tooltip: 'Thử lại',
                onPressed: () => ref.invalidate(aiServiceHealthProvider),
                icon: const Icon(Icons.refresh_rounded, size: 17),
              ),
          ],
        ),
      ),
    );
  }
}

class _ModelSummary extends StatelessWidget {
  const _ModelSummary({required this.suggestion});

  final DishSuggestion suggestion;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(Gap.sm),
      decoration: BoxDecoration(
        color: context.colors.primaryContainer.withValues(alpha: 0.45),
        borderRadius: Radii.brMd,
        border: Border.all(
          color: context.colors.primary.withValues(alpha: 0.2),
        ),
      ),
      child: Row(
        children: [
          Icon(Icons.psychology_alt_rounded, color: context.colors.primary),
          const SizedBox(width: Gap.sm),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Gợi ý được cá nhân hóa bởi SweepFood AI',
                  style: context.text.labelMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                Text(
                  'Ưu tiên nguyên liệu sẵn có, hạn dùng, dinh dưỡng và phần cần mua.',
                  style: context.text.labelSmall?.copyWith(
                    color: context.sweep.textSecondary,
                    letterSpacing: 0,
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
