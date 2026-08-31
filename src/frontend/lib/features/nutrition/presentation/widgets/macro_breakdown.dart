import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/macro_chips.dart';
import 'package:frontend/core/widgets/macro_ring.dart';
import 'package:frontend/shared/domain/nutrition_info.dart';

/// Reusable nutrition card: [MacroRing] + [MacroChips] + an estimate note.
/// Used by dish detail (D-01) and later nutrition-goal screens.
class MacroBreakdown extends StatelessWidget {
  const MacroBreakdown({required this.nutrition, this.note, super.key});

  final NutritionInfo nutrition;

  /// Footer note; defaults to the localized "estimated per serving" line.
  final String? note;

  @override
  Widget build(BuildContext context) {
    final note = this.note ?? context.l10n.macroEstimateNote;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(Gap.md),
          decoration: BoxDecoration(
            color: context.colors.surfaceContainerLowest,
            borderRadius: Radii.brLg,
            border: Border.all(color: context.sweep.hairline),
          ),
          child: Row(
            children: [
              MacroRing(nutrition: nutrition, size: 64),
              const SizedBox(width: Gap.md),
              Expanded(child: MacroChips(nutrition: nutrition)),
            ],
          ),
        ),
        const SizedBox(height: Gap.xs),
        Text(
          note,
          style: context.text.labelSmall?.copyWith(
            letterSpacing: 0,
            color: context.sweep.textTertiary,
          ),
        ),
      ],
    );
  }
}
