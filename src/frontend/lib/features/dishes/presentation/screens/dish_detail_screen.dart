import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/recipe_image.dart';
import 'package:sweepfood/core/widgets/section_header.dart';
import 'package:sweepfood/features/cooking/presentation/controllers/cooking_controller.dart';
import 'package:sweepfood/features/cooking/presentation/widgets/post_cook_confirm_sheet.dart';
import 'package:sweepfood/features/cooking/presentation/widgets/post_cook_missing_sheet.dart';
import 'package:sweepfood/features/dishes/domain/entities/dish.dart';
import 'package:sweepfood/features/dishes/presentation/controllers/dish_detail_controller.dart';
import 'package:sweepfood/features/dishes/presentation/widgets/cooking_steps_view.dart';
import 'package:sweepfood/features/dishes/presentation/widgets/ingredient_checklist.dart';
import 'package:sweepfood/features/favorites/presentation/controllers/favorite_recipes_controller.dart';
import 'package:sweepfood/features/favorites/presentation/widgets/add_to_menu_sheet.dart';
import 'package:sweepfood/features/nutrition/presentation/widgets/macro_breakdown.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';

/// D-01 — Chi tiết món. Reached from S-01 (`/suggestions/dish/:id`), optionally
/// carrying its [DishSuggestion] via `extra` for the score badge.
class DishDetailScreen extends ConsumerWidget {
  const DishDetailScreen({required this.dishId, this.suggestion, super.key});

  final String dishId;
  final DishSuggestion? suggestion;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(dishByIdProvider(dishId));
    final isFav = ref.watch(isRecipeFavoriteProvider(dishId));

    return Scaffold(
      appBar: AppBar(
        title: Text(context.l10n.dishDetailTitle),
        actions: [
          IconButton(
            icon: Icon(
              isFav ? Icons.favorite_rounded : Icons.favorite_border_rounded,
              color: isFav ? Colors.red : null,
            ),
            tooltip: isFav ? 'Bỏ thích' : 'Yêu thích',
            onPressed: () {
              ref
                  .read(favoriteRecipesControllerProvider.notifier)
                  .toggleFavorite(dishId);
            },
          ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.more_vert_rounded),
            onSelected: (value) {
              if (value == 'add_to_menu') {
                final dish = async.value;
                AddToMenuSheet.show(
                  context,
                  recipeId: dishId,
                  recipeName: dish?.name ?? '',
                );
              }
            },
            itemBuilder: (context) => [
              PopupMenuItem(
                value: 'add_to_menu',
                child: Row(
                  children: [
                    const Icon(Icons.playlist_add_rounded),
                    const SizedBox(width: 8),
                    Text(context.l10n.favAddToMenuTitle),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: AsyncValueWidget<Dish>(
        value: async,
        onRetry: () => ref.invalidate(dishByIdProvider(dishId)),
        data: (_) => _Body(
          dishId: dishId,
          score: suggestion?.score,
          suggestion: suggestion,
        ),
      ),
    );
  }
}

class _Body extends ConsumerWidget {
  const _Body({required this.dishId, this.score, this.suggestion});

  final String dishId;
  final int? score;
  final DishSuggestion? suggestion;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final fetchedDish = ref.watch(scaledDishProvider(dishId));
    if (fetchedDish == null) return const SizedBox.shrink();
    final dish = _withRecommendationContext(fetchedDish, suggestion);

    final servings = ref.watch(dishServingsProvider(dishId)) ?? dish.servings;

    return Column(
      children: [
        Expanded(
          child: ListView(
            padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.md, Gap.lg, Gap.xxl),
            children: [
              _Hero(imageUrl: dish.imageUrl, score: score),
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

Dish _withRecommendationContext(Dish dish, DishSuggestion? suggestion) {
  if (suggestion == null) return dish;

  String key(String value) => value
      .toLowerCase()
      .replaceAll(RegExp(r'[^a-z0-9\u00c0-\u024f\u1e00-\u1eff ]'), '')
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim();

  final matched = {
    for (final item in suggestion.matchedIngredients) key(item.name),
  };
  final missing = {
    for (final item in suggestion.missingIngredients) key(item.name),
  };
  final nearExpiry = {
    for (final name in suggestion.nearExpiryIngredients) key(name),
  };
  final recommendationSaysEverythingIsAvailable =
      suggestion.toBuyCount == 0 && suggestion.availabilityRatio >= 0.995;

  bool containsName(Set<String> values, String name) {
    final normalized = key(name);
    return values.any(
      (value) =>
          value == normalized ||
          value.contains(normalized) ||
          normalized.contains(value),
    );
  }

  return dish.copyWith(
    prepTimeMin: dish.totalTimeMin == 0
        ? suggestion.dish.prepTimeMin
        : dish.prepTimeMin,
    cookTimeMin: dish.totalTimeMin == 0
        ? suggestion.dish.cookTimeMin
        : dish.cookTimeMin,
    ingredients: [
      for (final ingredient in dish.ingredients)
        if (ingredient.isSeasoning)
          ingredient
        else if (containsName(matched, ingredient.name))
          ingredient.copyWith(
            availableInPantry: true,
            missingQty: 0,
            nearExpiry: containsName(nearExpiry, ingredient.name),
          )
        else if (containsName(missing, ingredient.name))
          ingredient.copyWith(
            availableInPantry: false,
            missingQty: ingredient.quantity,
          )
        else if (recommendationSaysEverythingIsAvailable)
          ingredient.copyWith(availableInPantry: true, missingQty: 0)
        else
          ingredient,
    ],
  );
}

class _Hero extends StatelessWidget {
  const _Hero({this.imageUrl, this.score});

  final String? imageUrl;
  final int? score;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 168,
      decoration: BoxDecoration(
        color: context.sweep.subtleFill,
        borderRadius: Radii.brLg,
      ),
      clipBehavior: Clip.antiAlias,
      child: Stack(
        children: [
          Positioned.fill(
            child: RecipeImage(
              imageUrl: imageUrl,
              fit: BoxFit.cover,
              iconSize: 44,
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
            tooltip: 'Giảm khẩu phần',
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
            tooltip: 'Tăng khẩu phần',
            onPressed: servings < 12 ? () => onChanged(servings + 1) : null,
            icon: const Icon(Icons.add_rounded, size: 18),
            visualDensity: VisualDensity.compact,
          ),
        ],
      ),
    );
  }
}

class _CookBar extends ConsumerStatefulWidget {
  const _CookBar({required this.dish});

  final Dish dish;

  @override
  ConsumerState<_CookBar> createState() => _CookBarState();
}

class _CookBarState extends ConsumerState<_CookBar> {
  bool _busy = false;

  Future<void> _handleCook() async {
    if (_busy) return;
    setState(() => _busy = true);
    try {
      final controller = ref.read(cookingControllerProvider.notifier);
      final servings =
          (ref.read(dishServingsProvider(widget.dish.id)) ??
                  widget.dish.servings)
              .toDouble();
      final preview = await controller.previewForDish(
        dishId: widget.dish.id,
        servings: servings,
      );
      if (preview.hasMissingIngredients) {
        if (mounted) {
          await PostCookMissingSheet.show(
            context,
            dishName: widget.dish.name,
            servings: servings,
            missingIngredients: preview.missingIngredients,
            onReduceServings: servings > 1
                ? () {
                    final newServings = servings == 4 ? 2 : 1;
                    ref
                        .read(dishServingsProvider(widget.dish.id).notifier)
                        .set(newServings);
                  }
                : null,
          );
        }
        return;
      }
      if (mounted) {
        await PostCookConfirmSheet.show(
          context,
          preview: preview,
          dishName: widget.dish.name,
        );
      }
    } catch (e) {
      if (mounted) {
        AppSnack.show(context, 'Có lỗi khi cập nhật kho: $e');
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      minimum: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.sm),
      child: SizedBox(
        width: double.infinity,
        child: FilledButton.icon(
          onPressed: _busy ? null : _handleCook,
          icon: _busy
              ? const SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Icon(Icons.restaurant_menu_rounded, size: 18),
          label: Text(_busy ? 'Đang tải...' : context.l10n.dishCookedThis),
        ),
      ),
    );
  }
}
