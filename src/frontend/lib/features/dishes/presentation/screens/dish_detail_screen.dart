import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/recipe_image.dart';
import 'package:sweepfood/features/cooking/presentation/controllers/cooking_controller.dart';
import 'package:sweepfood/features/cooking/presentation/widgets/post_cook_confirm_sheet.dart';
import 'package:sweepfood/features/cooking/presentation/widgets/post_cook_missing_sheet.dart';
import 'package:sweepfood/features/dishes/domain/entities/dish.dart';
import 'package:sweepfood/features/dishes/presentation/controllers/dish_detail_controller.dart';
import 'package:sweepfood/features/dishes/presentation/widgets/cooking_steps_view.dart';
import 'package:sweepfood/features/dishes/presentation/widgets/guided_cook_sheet.dart';
import 'package:sweepfood/features/dishes/presentation/widgets/ingredient_checklist.dart';
import 'package:sweepfood/features/favorites/presentation/controllers/favorite_recipes_controller.dart';
import 'package:sweepfood/features/favorites/presentation/widgets/add_to_menu_sheet.dart';
import 'package:sweepfood/features/nutrition/presentation/widgets/macro_breakdown.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';

/// D-01 — Chi tiết món (Concept B · Format 1: Full-Bleed Photo Hero + Rising
/// Crisp Sheet + Inline Servings Stepper inside Ingredients Card).
class DishDetailScreen extends ConsumerWidget {
  const DishDetailScreen({required this.dishId, this.suggestion, super.key});

  final String dishId;
  final DishSuggestion? suggestion;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(dishByIdProvider(dishId));
    final isFav = ref.watch(isRecipeFavoriteProvider(dishId));
    final cs = context.colors;

    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.light,
        statusBarBrightness: Brightness.dark,
        systemNavigationBarColor: cs.surfaceContainerLowest,
        systemNavigationBarIconBrightness:
            Theme.of(context).brightness == Brightness.dark
            ? Brightness.light
            : Brightness.dark,
      ),
      child: Scaffold(
        backgroundColor: cs.surface,
        body: AsyncValueWidget<Dish>(
          value: async,
          onRetry: () => ref.invalidate(dishByIdProvider(dishId)),
          data: (_) => _DishDetailBody(
            dishId: dishId,
            score: suggestion?.score,
            suggestion: suggestion,
            isFav: isFav,
          ),
        ),
      ),
    );
  }
}

class _DishDetailBody extends ConsumerWidget {
  const _DishDetailBody({
    required this.dishId,
    required this.isFav,
    this.score,
    this.suggestion,
  });

  final String dishId;
  final bool isFav;
  final int? score;
  final DishSuggestion? suggestion;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;
    final fetchedDish = ref.watch(scaledDishProvider(dishId));
    if (fetchedDish == null) return const SizedBox.shrink();
    final dish = _withRecommendationContext(fetchedDish, suggestion);
    final servings = ref.watch(dishServingsProvider(dishId)) ?? dish.servings;

    return Column(
      children: [
        Expanded(
          child: CustomScrollView(
            slivers: [
              // Full-bleed Photo Hero with floating translucent emerald actions
              SliverAppBar(
                pinned: true,
                automaticallyImplyLeading: false,
                expandedHeight: 248,
                backgroundColor: sweep.heroSurface,
                surfaceTintColor: Colors.transparent,
                elevation: 0,
                scrolledUnderElevation: 0,
                toolbarHeight: 58,
                titleSpacing: Gap.lg,
                title: Row(
                  children: [
                    _FloatingHeroButton(
                      icon: AppIcons.arrowLeft,
                      tooltip: 'Quay lại',
                      onPressed: () => context.pop(),
                    ),
                  ],
                ),
                actions: [
                  _FloatingHeroButton(
                    icon: AppIcons.heart,
                    iconColor: isFav ? sweep.ctaWarm : sweep.onHeroSurface,
                    active: isFav,
                    bounceOnTap: true,
                    tooltip: isFav ? 'Bỏ thích' : 'Yêu thích',
                    onPressed: () {
                      AppHaptics.light();
                      ref
                          .read(favoriteRecipesControllerProvider.notifier)
                          .toggleFavorite(dishId);
                    },
                  ),
                  const SizedBox(width: Gap.xs),
                  Padding(
                    padding: const EdgeInsets.only(right: Gap.lg),
                    child: _FloatingHeroButton(
                      icon: AppIcons.bookmark,
                      bounceOnTap: true,
                      tooltip: l10n.favAddToMenuTitle,
                      onPressed: () {
                        AppHaptics.selection();
                        AddToMenuSheet.show(
                          context,
                          recipeId: dishId,
                          recipeName: dish.name,
                        );
                      },
                    ),
                  ),
                ],
                flexibleSpace: FlexibleSpaceBar(
                  collapseMode: CollapseMode.parallax,
                  background: Stack(
                    fit: StackFit.expand,
                    children: [
                      RecipeImage(
                        imageUrl: dish.imageUrl,
                        heroTag: 'dish-$dishId',
                        fit: BoxFit.cover,
                        iconSize: 48,
                      ),
                      // Subtle top & bottom gradient scrims for icon contrast (no glow)
                      IgnorePointer(
                        child: DecoratedBox(
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              begin: Alignment.topCenter,
                              end: Alignment.bottomCenter,
                              colors: [
                                Colors.black.withValues(alpha: 0.42),
                                Colors.transparent,
                                Colors.black.withValues(alpha: 0.28),
                              ],
                              stops: const [0.0, 0.48, 1.0],
                            ),
                          ),
                        ),
                      ),
                      // Curved bottom sheet cap transitioning photo into surface
                      Positioned(
                        left: 0,
                        right: 0,
                        bottom: -1,
                        child: Container(
                          height: 24,
                          decoration: BoxDecoration(
                            color: cs.surface,
                            borderRadius: const BorderRadius.vertical(
                              top: Radius.circular(28),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              // Rising Crisp Sheet Body
              SliverPadding(
                padding: const EdgeInsets.fromLTRB(
                  Gap.lg,
                  Gap.xs,
                  Gap.lg,
                  Gap.xxl,
                ),
                sliver: SliverList.list(
                  children: [
                    Text(
                      dish.name,
                      style: context.text.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w800,
                        height: 1.2,
                      ),
                    ),
                    const SizedBox(height: Gap.sm),
                    // Compact metric pill strip
                    Wrap(
                      spacing: Gap.xs,
                      runSpacing: Gap.xs,
                      children: [
                        if (score != null)
                          _MetaPill(
                            label: '$score ${l10n.scoreBadgeLabel}',
                            emphasized: true,
                          ),
                        if (dish.totalTimeMin > 0)
                          _MetaPill(
                            icon: AppIcons.clock,
                            label: '${dish.totalTimeMin} phút',
                          ),
                        _MetaPill(
                          icon: AppIcons.flame,
                          label:
                              '${dish.nutritionPerServing.energyKcal.round()} kcal / phần',
                        ),
                      ],
                    ),
                    Gap.gapMd,

                    // Nutrition breakdown card
                    MacroBreakdown(nutrition: dish.nutritionPerServing),
                    Gap.gapMd,

                    // Unified Ingredients + Inline Servings Stepper Card
                    _IngredientsCard(
                      dish: dish,
                      servings: servings,
                      onServingsChanged: (v) {
                        AppHaptics.selection();
                        ref.read(dishServingsProvider(dishId).notifier).set(v);
                      },
                    ),

                    // Unified Cooking Steps Card
                    if (dish.steps.isNotEmpty) ...[
                      Gap.gapMd,
                      _StepsCard(dish: dish),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ),
        _CookBar(
          dish: dish,
          onGuidedCook: dish.steps.isEmpty
              ? null
              : () => GuidedCookSheet.show(
                  context,
                  dishName: dish.name,
                  steps: dish.steps,
                  onFinishCooking: () => _previewCookDish(context, ref, dish),
                ),
        ),
      ],
    );
  }
}

class _FloatingHeroButton extends StatefulWidget {
  const _FloatingHeroButton({
    required this.icon,
    required this.tooltip,
    required this.onPressed,
    this.iconColor,
    this.active = false,
    this.bounceOnTap = false,
  });

  final IconData icon;
  final String tooltip;
  final VoidCallback onPressed;
  final Color? iconColor;
  final bool active;
  final bool bounceOnTap;

  @override
  State<_FloatingHeroButton> createState() => _FloatingHeroButtonState();
}

class _FloatingHeroButtonState extends State<_FloatingHeroButton>
    with SingleTickerProviderStateMixin {
  late final AnimationController _bounceCtrl;
  late final Animation<double> _scaleAnim;

  @override
  void initState() {
    super.initState();
    _bounceCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 340),
    );
    _scaleAnim = TweenSequence<double>([
      TweenSequenceItem(
        tween: Tween(begin: 1.0, end: 0.82)
            .chain(CurveTween(curve: Curves.easeOut)),
        weight: 22,
      ),
      TweenSequenceItem(
        tween: Tween(begin: 0.82, end: 1.24)
            .chain(CurveTween(curve: Curves.easeOutBack)),
        weight: 43,
      ),
      TweenSequenceItem(
        tween: Tween(begin: 1.24, end: 1.0)
            .chain(CurveTween(curve: Curves.easeInOut)),
        weight: 35,
      ),
    ]).animate(_bounceCtrl);
  }

  @override
  void dispose() {
    _bounceCtrl.dispose();
    super.dispose();
  }

  void _handleTap() {
    if (widget.bounceOnTap && !MediaQuery.disableAnimationsOf(context)) {
      _bounceCtrl.forward(from: 0);
    }
    widget.onPressed();
  }

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    return Tooltip(
      message: widget.tooltip,
      child: Material(
        color: sweep.heroSurface.withValues(alpha: 0.8),
        shape: RoundedRectangleBorder(
          borderRadius: Radii.brMd,
          side: BorderSide(
            color: widget.active
                ? sweep.ctaWarm.withValues(alpha: 0.65)
                : sweep.onHeroSurface.withValues(alpha: 0.18),
          ),
        ),
        child: InkWell(
          borderRadius: Radii.brMd,
          onTap: _handleTap,
          child: SizedBox(
            width: 40,
            height: 40,
            child: AnimatedBuilder(
              animation: _scaleAnim,
              builder: (context, child) => Transform.scale(
                scale: _bounceCtrl.isAnimating ? _scaleAnim.value : 1.0,
                child: child,
              ),
              child: Icon(
                widget.icon,
                size: 19,
                color: widget.iconColor ?? sweep.onHeroSurface,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _MetaPill extends StatelessWidget {
  const _MetaPill({required this.label, this.icon, this.emphasized = false});

  final String label;
  final IconData? icon;
  final bool emphasized;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final cs = context.colors;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: emphasized ? sweep.heroSurface : cs.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(Radii.pill),
        border: Border.all(
          color: emphasized ? sweep.heroSurface : sweep.hairline,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(
              icon,
              size: 13.5,
              color: emphasized ? sweep.onHeroMuted : cs.primary,
            ),
            const SizedBox(width: 5),
          ],
          Text(
            label,
            style: AppTypography.tabular(
              context.text.labelSmall?.copyWith(
                letterSpacing: 0,
                color: emphasized ? sweep.onHeroSurface : sweep.textSecondary,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _IngredientsCard extends StatelessWidget {
  const _IngredientsCard({
    required this.dish,
    required this.servings,
    required this.onServingsChanged,
  });

  final Dish dish;
  final int servings;
  final ValueChanged<int> onServingsChanged;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;

    return Container(
      decoration: BoxDecoration(
        color: cs.surfaceContainerLowest,
        borderRadius: Radii.brXl,
        border: Border.all(color: sweep.hairline),
        boxShadow: Shadows.e1,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with inline servings stepper
          Padding(
            padding: const EdgeInsets.fromLTRB(
              Gap.md,
              Gap.sm + 2,
              Gap.sm + 2,
              Gap.sm + 2,
            ),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    'Nguyên liệu',
                    style: context.text.titleSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 4,
                    vertical: 3,
                  ),
                  decoration: BoxDecoration(
                    color: sweep.subtleFill,
                    borderRadius: BorderRadius.circular(Radii.pill),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      _StepperCircle(
                        icon: AppIcons.minus,
                        tooltip: 'Giảm khẩu phần',
                        onTap: servings > 1
                            ? () => onServingsChanged(servings - 1)
                            : null,
                      ),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: Gap.sm),
                        child: Text(
                          l10n.servingsCount(servings),
                          style: AppTypography.tabular(
                            context.text.labelMedium?.copyWith(
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ),
                      _StepperCircle(
                        icon: AppIcons.add,
                        tooltip: 'Tăng khẩu phần',
                        onTap: servings < 12
                            ? () => onServingsChanged(servings + 1)
                            : null,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          Divider(height: 1, color: sweep.hairline),
          Padding(
            padding: const EdgeInsets.all(Gap.md),
            child: IngredientChecklist(ingredients: dish.mainIngredients),
          ),
          if (dish.seasonings.isNotEmpty) ...[
            Divider(height: 1, color: sweep.hairline),
            Padding(
              padding: const EdgeInsets.fromLTRB(
                Gap.md,
                Gap.sm,
                Gap.md,
                Gap.md,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    l10n.dishSeasonings,
                    style: context.text.labelSmall?.copyWith(
                      letterSpacing: 0.5,
                      color: sweep.textTertiary,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: Gap.xs),
                  Wrap(
                    spacing: Gap.xs,
                    runSpacing: Gap.xs,
                    children: [
                      for (final s in dish.seasonings)
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 5,
                          ),
                          decoration: BoxDecoration(
                            color: sweep.subtleFill,
                            borderRadius: BorderRadius.circular(Radii.pill),
                          ),
                          child: Text(
                            s.name,
                            style: context.text.labelSmall?.copyWith(
                              letterSpacing: 0,
                              color: sweep.textSecondary,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _StepperCircle extends StatelessWidget {
  const _StepperCircle({required this.icon, required this.tooltip, this.onTap});

  final IconData icon;
  final String tooltip;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    final enabled = onTap != null;
    return Tooltip(
      message: tooltip,
      child: Material(
        color: cs.surfaceContainerLowest,
        shape: const CircleBorder(),
        child: InkWell(
          customBorder: const CircleBorder(),
          onTap: onTap,
          child: SizedBox(
            width: 28,
            height: 28,
            child: Icon(
              icon,
              size: 14,
              color: enabled ? cs.primary : context.sweep.textTertiary,
            ),
          ),
        ),
      ),
    );
  }
}

class _StepsCard extends StatelessWidget {
  const _StepsCard({required this.dish});

  final Dish dish;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;

    return Container(
      decoration: BoxDecoration(
        color: cs.surfaceContainerLowest,
        borderRadius: Radii.brXl,
        border: Border.all(color: sweep.hairline),
        boxShadow: Shadows.e1,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: Gap.md,
              vertical: Gap.sm + 4,
            ),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    l10n.dishHowTo,
                    style: context.text.titleSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                Text(
                  '${dish.steps.length} bước',
                  style: context.text.labelSmall?.copyWith(
                    letterSpacing: 0,
                    color: sweep.textTertiary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
          Divider(height: 1, color: sweep.hairline),
          Padding(
            padding: const EdgeInsets.all(Gap.md),
            child: CookingStepsView(steps: dish.steps),
          ),
        ],
      ),
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

Future<void> _previewCookDish(
  BuildContext context,
  WidgetRef ref,
  Dish dish,
) async {
  try {
    final controller = ref.read(cookingControllerProvider.notifier);
    final servings = (ref.read(dishServingsProvider(dish.id)) ?? dish.servings)
        .toDouble();
    final preview = await controller.previewForDish(
      dishId: dish.id,
      servings: servings,
    );
    if (!context.mounted) return;
    if (preview.hasMissingIngredients) {
      await PostCookMissingSheet.show(
        context,
        dishName: dish.name,
        servings: servings,
        missingIngredients: preview.missingIngredients,
        onReduceServings: servings > 1
            ? () {
                final newServings = servings == 4 ? 2 : 1;
                ref
                    .read(dishServingsProvider(dish.id).notifier)
                    .set(newServings);
              }
            : null,
      );
      return;
    }
    await PostCookConfirmSheet.show(
      context,
      preview: preview,
      dishName: dish.name,
    );
  } catch (e) {
    if (context.mounted) {
      AppSnack.show(context, 'Có lỗi khi cập nhật kho: $e');
    }
  }
}

class _CookBar extends ConsumerStatefulWidget {
  const _CookBar({required this.dish, this.onGuidedCook});

  final Dish dish;
  final VoidCallback? onGuidedCook;

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
    final sweep = context.sweep;
    final cs = context.colors;
    return DecoratedBox(
      decoration: BoxDecoration(
        color: cs.surfaceContainerLowest,
        border: Border(top: BorderSide(color: sweep.hairline)),
      ),
      child: SafeArea(
        top: false,
        minimum: const EdgeInsets.fromLTRB(Gap.lg, Gap.sm, Gap.lg, Gap.sm),
        child: Row(
          children: [
            if (widget.onGuidedCook != null) ...[
              Expanded(
                flex: 42,
                child: SizedBox(
                  height: 48,
                  child: OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      foregroundColor: cs.primary,
                      side: BorderSide(color: sweep.hairline),
                      padding: const EdgeInsets.symmetric(horizontal: Gap.sm),
                      shape: const RoundedRectangleBorder(
                        borderRadius: Radii.brLg,
                      ),
                    ),
                    onPressed: _busy ? null : widget.onGuidedCook,
                    icon: const Icon(AppIcons.timer, size: 17),
                    label: const Text(
                      'Từng bước',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: Gap.sm),
            ],
            Expanded(
              flex: 58,
              child: SizedBox(
                height: 48,
                child: FilledButton.icon(
                  style: FilledButton.styleFrom(
                    backgroundColor: sweep.ctaWarm,
                    foregroundColor: sweep.onCtaWarm,
                    elevation: 0,
                    shadowColor: Colors.transparent,
                    shape: const RoundedRectangleBorder(
                      borderRadius: Radii.brLg,
                    ),
                  ),
                  onPressed: _busy ? null : _handleCook,
                  icon: _busy
                      ? SizedBox(
                          width: 17,
                          height: 17,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: sweep.onCtaWarm,
                          ),
                        )
                      : const Icon(AppIcons.cook, size: 18),
                  label: Text(
                    _busy ? 'Đang tải...' : context.l10n.dishCookedThis,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
