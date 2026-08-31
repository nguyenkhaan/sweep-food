import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/app_snackbar.dart';
import 'package:frontend/core/widgets/async_value_widget.dart';
import 'package:frontend/core/widgets/section_header.dart';
import 'package:frontend/features/cooking/presentation/widgets/post_cook_confirm_sheet.dart';
import 'package:frontend/features/dishes/domain/entities/dish.dart';
import 'package:frontend/features/dishes/presentation/controllers/dish_detail_controller.dart';
import 'package:frontend/features/dishes/presentation/widgets/cooking_steps_view.dart';
import 'package:frontend/features/dishes/presentation/widgets/ingredient_checklist.dart';
import 'package:frontend/features/nutrition/presentation/widgets/macro_breakdown.dart';
import 'package:frontend/features/shopping_list/presentation/controllers/shopping_list_controller.dart';
import 'package:frontend/features/suggestions/domain/entities/dish_suggestion.dart';

/// D-01 — Chi tiết món. Reached from S-01 (`/suggestions/dish/:id`), optionally
/// carrying its [DishSuggestion] via `extra` for the score badge.
class DishDetailScreen extends ConsumerWidget {
  const DishDetailScreen({required this.dishId, this.suggestion, super.key});

  final String dishId;
  final DishSuggestion? suggestion;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(dishByIdProvider(dishId));

    return Scaffold(
      appBar: AppBar(title: Text(context.l10n.dishDetailTitle)),
      body: AsyncValueWidget<Dish>(
        value: async,
        onRetry: () => ref.invalidate(dishByIdProvider(dishId)),
        data: (_) => _Body(dishId: dishId, score: suggestion?.score),
      ),
    );
  }
}

class _Body extends ConsumerWidget {
  const _Body({required this.dishId, this.score});

  final String dishId;
  final int? score;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final dish = ref.watch(scaledDishProvider(dishId));
    if (dish == null) return const SizedBox.shrink();

    final servings = ref.watch(dishServingsProvider(dishId)) ?? dish.servings;

    return Column(
      children: [
        Expanded(
          child: ListView(
            padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.md, Gap.lg, Gap.xxl),
            children: [
              _Hero(score: score),
              Gap.gapMd,
              Text(dish.name, style: context.text.headlineSmall),
              const SizedBox(height: 4),
              Text(
                dish.metaLine(l10n),
                style: context.text.bodyMedium?.copyWith(
                  color: context.sweep.textTertiary,
                ),
              ),
              Gap.gapLg,
              _ServingsRow(
                servings: servings,
                onChanged: (v) =>
                    ref.read(dishServingsProvider(dishId).notifier).set(v),
              ),
              Gap.gapLg,
              MacroBreakdown(nutrition: dish.nutritionPerServing),
              Gap.gapLg,
              SectionHeader(title: l10n.dishIngredientsWithServings(servings)),
              Gap.gapXs,
              IngredientChecklist(ingredients: dish.mainIngredients),
              if (dish.seasonings.isNotEmpty) ...[
                Gap.gapLg,
                SectionHeader(title: l10n.dishSeasonings),
                Gap.gapXs,
                Wrap(
                  spacing: Gap.xs,
                  runSpacing: Gap.xs,
                  children: [
                    for (final s in dish.seasonings)
                      Chip(
                        label: Text(s.name),
                        visualDensity: VisualDensity.compact,
                      ),
                  ],
                ),
              ],
              if (dish.missingCount > 0) ...[
                Gap.gapMd,
                OutlinedButton.icon(
                  onPressed: () async {
                    final added = await ref
                        .read(shoppingListControllerProvider.notifier)
                        .addMissingFromDish(dish, l10n);
                    if (!context.mounted) return;
                    AppSnack.show(
                      context,
                      added > 0
                          ? context.l10n.dishAddedToShopping(added)
                          : context.l10n.dishShoppingNotReady,
                    );
                  },
                  icon: const Icon(Icons.add_shopping_cart_rounded, size: 18),
                  label: Text(l10n.dishAddMissing(dish.missingCount)),
                ),
              ],
              if (dish.steps.isNotEmpty) ...[
                Gap.gapLg,
                SectionHeader(title: l10n.dishHowTo),
                Gap.gapXs,
                CookingStepsView(steps: dish.steps),
              ],
            ],
          ),
        ),
        _CookBar(dish: dish),
      ],
    );
  }
}

class _Hero extends StatelessWidget {
  const _Hero({this.score});

  final int? score;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 168,
      decoration: BoxDecoration(
        color: context.sweep.subtleFill,
        borderRadius: Radii.brLg,
      ),
      child: Stack(
        children: [
          Center(
            child: Icon(
              Icons.restaurant_rounded,
              size: 44,
              color: context.sweep.textTertiary,
            ),
          ),
          if (score != null)
            Positioned(
              right: 12,
              bottom: 12,
              child: Container(
                width: 52,
                height: 52,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: context.colors.primary,
                  shape: BoxShape.circle,
                  boxShadow: Shadows.e2,
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      '$score',
                      style: context.text.titleMedium?.copyWith(
                        color: context.colors.onPrimary,
                        height: 1,
                      ),
                    ),
                    Text(
                      context.l10n.scoreBadgeLabel,
                      style: TextStyle(
                        color: context.colors.onPrimary.withValues(alpha: 0.85),
                        fontSize: 7,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 0.4,
                      ),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _ServingsRow extends StatelessWidget {
  const _ServingsRow({required this.servings, required this.onChanged});

  final int servings;
  final ValueChanged<int> onChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: Gap.sm, vertical: Gap.xs),
      decoration: BoxDecoration(
        color: context.colors.surfaceContainerLowest,
        borderRadius: Radii.brMd,
        border: Border.all(color: context.sweep.hairline),
      ),
      child: Row(
        children: [
          Text(context.l10n.dishServingsLabel, style: context.text.titleSmall),
          const Spacer(),
          IconButton.filledTonal(
            onPressed: servings > 1 ? () => onChanged(servings - 1) : null,
            icon: const Icon(Icons.remove_rounded, size: 18),
            visualDensity: VisualDensity.compact,
          ),
          const SizedBox(width: Gap.sm),
          Text(
            context.l10n.servingsCount(servings),
            style: context.text.titleMedium,
          ),
          const SizedBox(width: Gap.sm),
          IconButton.filledTonal(
            onPressed: servings < 12 ? () => onChanged(servings + 1) : null,
            icon: const Icon(Icons.add_rounded, size: 18),
            visualDensity: VisualDensity.compact,
          ),
        ],
      ),
    );
  }
}

class _CookBar extends StatelessWidget {
  const _CookBar({required this.dish});

  final Dish dish;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      minimum: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.sm),
      child: SizedBox(
        width: double.infinity,
        child: FilledButton.icon(
          onPressed: () => PostCookConfirmSheet.show(context, dish: dish),
          icon: const Icon(Icons.restaurant_menu_rounded, size: 18),
          label: Text(context.l10n.dishCookedThis),
        ),
      ),
    );
  }
}
