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
class SuggestionListScreen extends ConsumerStatefulWidget {
  const SuggestionListScreen({super.key});

  @override
  ConsumerState<SuggestionListScreen> createState() =>
      _SuggestionListScreenState();
}

class _SuggestionListScreenState extends ConsumerState<SuggestionListScreen> {
  bool _showPrompt = false;

  @override
  Widget build(BuildContext context) {
    final async = ref.watch(suggestionListControllerProvider);
    final promptText = ref.watch(suggestionFilterControllerProvider).prompt;
    final isPromptActive = promptText.isNotEmpty || _showPrompt;

    return Scaffold(
      appBar: AppBar(
        title: Text(context.l10n.suggestionsTitle),
        actions: [
          IconButton(
            tooltip: 'AI Gợi ý prompt',
            style: IconButton.styleFrom(
              backgroundColor: isPromptActive
                  ? context.colors.primary.withValues(alpha: 0.15)
                  : context.sweep.subtleFill,
              shape: RoundedRectangleBorder(
                borderRadius: Radii.brMd,
                side: BorderSide(
                  color: isPromptActive
                      ? context.colors.primary
                      : context.sweep.hairline,
                ),
              ),
            ),
            icon: Icon(
              Icons.auto_awesome_rounded,
              color: isPromptActive
                  ? context.colors.primary
                  : context.colors.onSurfaceVariant,
            ),
            onPressed: () {
              setState(() {
                _showPrompt = !_showPrompt;
              });
            },
          ),
          const SizedBox(width: Gap.xs),
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
          if (isPromptActive) ...[
            const _RecipePromptBar(),
          ],
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

class _RecipePromptBar extends ConsumerStatefulWidget {
  const _RecipePromptBar();

  @override
  ConsumerState<_RecipePromptBar> createState() => _RecipePromptBarState();
}

class _RecipePromptBarState extends ConsumerState<_RecipePromptBar> {
  late final TextEditingController _controller;

  static const _quickPrompts = [
    'Thanh đạm',
    'Ít dầu mỡ',
    'Nhanh gọn',
    'Món canh',
    'Món xào',
  ];

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(
      text: ref.read(suggestionFilterControllerProvider).prompt,
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _submitPrompt(String val) {
    ref.read(suggestionFilterControllerProvider.notifier).setPrompt(val.trim());
  }

  @override
  Widget build(BuildContext context) {
    final currentPrompt = ref.watch(suggestionFilterControllerProvider).prompt;

    return Padding(
      padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.xs),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          TextField(
            controller: _controller,
            textInputAction: TextInputAction.search,
            onSubmitted: _submitPrompt,
            decoration: InputDecoration(
              hintText: 'Nhập gợi ý prompt (VD: canh chua, ít dầu, gà...)...',
              prefixIcon: const Icon(Icons.auto_awesome_rounded, size: 20),
              suffixIcon: _controller.text.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.clear_rounded, size: 18),
                      onPressed: () {
                        _controller.clear();
                        ref
                            .read(suggestionFilterControllerProvider.notifier)
                            .clearPrompt();
                        setState(() {});
                      },
                    )
                  : null,
              isDense: true,
              contentPadding: const EdgeInsets.symmetric(
                horizontal: Gap.md,
                vertical: Gap.sm,
              ),
              filled: true,
              fillColor: context.sweep.subtleFill,
              border: const OutlineInputBorder(
                borderRadius: Radii.brMd,
                borderSide: BorderSide.none,
              ),
            ),
            onChanged: (val) {
              setState(() {});
              _submitPrompt(val);
            },
          ),
          const SizedBox(height: 6),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                for (final p in _quickPrompts) ...[
                  InkWell(
                    onTap: () {
                      if (currentPrompt == p) {
                        _controller.clear();
                        ref
                            .read(suggestionFilterControllerProvider.notifier)
                            .clearPrompt();
                      } else {
                        _controller.text = p;
                        _submitPrompt(p);
                      }
                      setState(() {});
                    },
                    borderRadius: BorderRadius.circular(Radii.pill),
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: currentPrompt == p
                            ? context.colors.primary.withValues(alpha: 0.12)
                            : context.sweep.subtleFill,
                        borderRadius: BorderRadius.circular(Radii.pill),
                        border: Border.all(
                          color: currentPrompt == p
                              ? context.colors.primary
                              : context.sweep.hairline,
                        ),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.bolt_rounded,
                            size: 14,
                            color: currentPrompt == p
                                ? context.colors.primary
                                : context.sweep.textSecondary,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            p,
                            style: context.text.labelSmall?.copyWith(
                              color: currentPrompt == p
                                  ? context.colors.primary
                                  : context.sweep.textSecondary,
                              fontWeight: currentPrompt == p
                                  ? FontWeight.w600
                                  : FontWeight.normal,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(width: Gap.xs),
                ],
              ],
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
