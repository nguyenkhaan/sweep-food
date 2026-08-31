import 'package:flutter/material.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/shared/domain/nutrition_info.dart';

/// Row of "Đạm 28g · Tinh bột 30g · Chất béo 14g" chips with colour dots that
/// match [MacroRing].
class MacroChips extends StatelessWidget {
  const MacroChips({required this.nutrition, this.showKcal = true, super.key});

  final NutritionInfo nutrition;
  final bool showKcal;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    String g(double v) => l10n.macroGrams(v.round());
    final rows = <(String, String, Color)>[
      if (showKcal)
        (
          l10n.macroEnergy,
          l10n.macroKcal(nutrition.energyKcal.round()),
          context.colors.onSurface,
        ),
      (l10n.macroProtein, g(nutrition.proteinG), context.colors.primary),
      (l10n.macroCarb, g(nutrition.carbG), context.sweep.soon.fg),
      (l10n.macroFat, g(nutrition.lipidG), context.sweep.expired.fg),
    ];
    return Wrap(
      spacing: 8,
      runSpacing: 6,
      children: [
        for (final (label, value, color) in rows)
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(color: color, shape: BoxShape.circle),
              ),
              const SizedBox(width: 6),
              Text.rich(
                TextSpan(
                  style: context.text.labelMedium,
                  children: [
                    TextSpan(text: '$label '),
                    TextSpan(
                      text: value,
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                  ],
                ),
              ),
            ],
          ),
      ],
    );
  }
}
