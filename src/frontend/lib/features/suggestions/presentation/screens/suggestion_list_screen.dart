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
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/features/suggestions/domain/entities/suggestion_request.dart';
import 'package:sweepfood/features/suggestions/presentation/controllers/suggestion_list_controller.dart';
import 'package:sweepfood/features/suggestions/presentation/widgets/score_breakdown_sheet.dart';
import 'package:sweepfood/features/suggestions/presentation/widgets/suggestion_card_chips.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';

/// S-01 — Gợi ý món. 3–5 scored dishes for the current pantry + quick filters.
class SuggestionListScreen extends ConsumerWidget {
  const SuggestionListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(suggestionListControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(context.l10n.suggestionsTitle),
        actions: [
          IconButton(
            tooltip: 'Bộ lọc',
            style: IconButton.styleFrom(
              backgroundColor: context.sweep.subtleFill,
              shape: RoundedRectangleBorder(
                borderRadius: Radii.brMd,
                side: BorderSide(color: context.sweep.hairline),
              ),
            ),
            icon: Icon(
              Icons.filter_list_rounded,
              color: context.colors.onSurfaceVariant,
            ),
            onPressed: () {},
          ),
          const SizedBox(width: Gap.md),
        ],
      ),
      body: Column(
        children: [
          const _FilterBar(),
          Gap.gapXs,
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



class _FilterBar extends ConsumerWidget {
  const _FilterBar();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final filter = ref.watch(suggestionFilterControllerProvider);
    final notifier = ref.read(suggestionFilterControllerProvider.notifier);

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.symmetric(horizontal: Gap.lg),
      child: Row(
        children: [
          for (final meal in MealType.values) ...[
            _Chip(
              label: meal.label(l10n),
              selected: filter.mealType == meal,
              onTap: () => notifier.toggleMeal(meal),
            ),
            const SizedBox(width: Gap.xs),
          ],
          _Chip(
            label: l10n.suggestionsQuickCook,
            selected: filter.quickCookOnly,
            onTap: notifier.toggleQuickCook,
          ),
          const SizedBox(width: Gap.xs),
          _Chip(
            label: DietaryPreference.moreVeg.label(l10n),
            selected: filter.dietaryPreference == DietaryPreference.moreVeg,
            onTap: () => notifier.togglePreference(DietaryPreference.moreVeg),
          ),
        ],
      ),
    );
  }
}

class _Chip extends StatelessWidget {
  const _Chip({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return ChoiceChip(
      label: Text(label),
      selected: selected,
      onSelected: (_) => onTap(),
      showCheckmark: false,
      selectedColor: context.colors.primary,
      labelStyle: context.text.labelMedium?.copyWith(
        color: selected
            ? context.colors.onPrimary
            : context.sweep.textSecondary,
      ),
      side: BorderSide(
        color: selected ? context.colors.primary : context.sweep.hairline,
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
          meta: suggestion.dish.shortMeta(l10n),
          chips: suggestion.cardChips(l10n),
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
