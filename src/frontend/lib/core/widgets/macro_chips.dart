import 'package:flutter/material.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/shared/domain/nutrition_info.dart';

/// Row of "Đạm 28g · Tinh bột 30g · Chất béo 14g" chips with colour dots that
/// match [MacroRing].
class MacroChips extends StatelessWidget {
  const MacroChips({required this.nutrition, this.showKcal = true, super.key});

  final NutritionInfo nutrition;
  final bool showKcal;

  @override
  Widget build(BuildContext context) {
    String g(double v) => '${v.round()}g';
    final rows = <(String, String, Color)>[
      if (showKcal)
        ('Năng lượng', '${nutrition.energyKcal.round()} kcal', context.colors.onSurface),
      ('Đạm', g(nutrition.proteinG), context.colors.primary),
      ('Tinh bột', g(nutrition.carbG), context.sweep.soon.fg),
      ('Chất béo', g(nutrition.lipidG), context.sweep.expired.fg),
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
