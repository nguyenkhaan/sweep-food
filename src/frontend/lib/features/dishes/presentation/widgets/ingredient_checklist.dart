import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/features/dishes/domain/entities/dish_ingredient.dart';

/// D-01 ingredient rows: ✓ có sẵn / + cần mua, with a "cận hạn" or "cần mua" tag.
class IngredientChecklist extends StatelessWidget {
  const IngredientChecklist({required this.ingredients, super.key});

  final List<DishIngredient> ingredients;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        for (final (i, ing) in ingredients.indexed)
          Padding(
            padding: EdgeInsets.only(
              top: i == 0 ? 0 : Gap.xs,
              bottom: i == ingredients.length - 1 ? 0 : Gap.xs,
            ),
            child: _Row(ing: ing),
          ),
      ],
    );
  }
}

class _Row extends StatelessWidget {
  const _Row({required this.ing});

  final DishIngredient ing;

  @override
  Widget build(BuildContext context) {
    final available = ing.availableInPantry;
    final (checkBg, checkFg) = available
        ? (context.colors.primaryContainer, context.colors.primary)
        : (context.sweep.subtleFill, context.sweep.textTertiary);

    final (tagLabel, tagBg, tagFg) = switch ((available, ing.nearExpiry)) {
      (true, true) => ('cận hạn', context.sweep.soon.bg, context.sweep.soon.fg),
      (false, _) => (
          'cần mua',
          context.sweep.subtleFill,
          context.sweep.textSecondary,
        ),
      _ => (null, Colors.transparent, Colors.transparent),
    };

    return Row(
      children: [
        Container(
          width: 22,
          height: 22,
          decoration: BoxDecoration(color: checkBg, shape: BoxShape.circle),
          child: Icon(
            available ? Icons.check_rounded : Icons.add_rounded,
            size: 13,
            color: checkFg,
          ),
        ),
        const SizedBox(width: Gap.sm),
        Expanded(child: Text(ing.name, style: context.text.bodyMedium)),
        const SizedBox(width: Gap.xs),
        Text(
          ing.quantityLabel,
          style: context.text.bodyMedium?.copyWith(
            color: context.sweep.textTertiary,
          ),
        ),
        if (tagLabel != null) ...[
          const SizedBox(width: Gap.xs),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: tagBg,
              borderRadius: BorderRadius.circular(Radii.pill),
            ),
            child: Text(
              tagLabel,
              style: context.text.labelSmall?.copyWith(
                letterSpacing: 0,
                color: tagFg,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ],
    );
  }
}
