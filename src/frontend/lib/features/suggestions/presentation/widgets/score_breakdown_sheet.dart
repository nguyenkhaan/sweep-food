import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/features/suggestions/domain/entities/score_breakdown.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

/// S-02 — "Vì sao món này đạt N điểm?". Explains the `0.4E + 0.3A + 0.2P + 0.1U`
/// components with a short reason and a bar per term.
class ScoreBreakdownSheet extends StatelessWidget {
  const ScoreBreakdownSheet({required this.suggestion, super.key});

  final DishSuggestion suggestion;

  static Future<void> show(BuildContext context, DishSuggestion suggestion) =>
      showAppBottomSheet(
        context,
        builder: (_) => ScoreBreakdownSheet(suggestion: suggestion),
      );

  String _reason(String letter, AppL10n l10n) {
    final s = suggestion;
    return switch (letter) {
      'E' =>
        s.nearExpiryIngredients.isEmpty
            ? l10n.scoreReasonENone
            : l10n.scoreReasonE(
                s.nearExpiryCount,
                s.nearExpiryIngredients.join(', '),
              ),
      'A' => l10n.scoreReasonA(s.availabilityPercent),
      'P' => l10n.scoreReasonP(
        s.dish.servings,
        s.dish.nutritionPerServing.energyKcal.round(),
        s.dish.totalTimeMin,
      ),
      'U' =>
        s.toBuyCount == 0
            ? l10n.scoreReasonUNone
            : l10n.scoreReasonU(s.toBuyCount),
      _ => '',
    };
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return SheetBody(
      title: l10n.scoreSheetTitle(suggestion.dish.name, suggestion.score),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: Gap.sm,
              vertical: Gap.xs + 1,
            ),
            decoration: BoxDecoration(
              color: context.colors.primaryContainer,
              borderRadius: Radii.brMd,
            ),
            child: Text(
              l10n.scoreFormula,
              textAlign: TextAlign.center,
              style: context.text.labelMedium?.copyWith(
                letterSpacing: 0.2,
                color: context.colors.onPrimaryContainer,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          Gap.gapMd,
          for (final c in suggestion.breakdown.components(l10n))
            Padding(
              padding: const EdgeInsets.only(bottom: Gap.md),
              child: _ComponentRow(
                component: c,
                reason: _reason(c.letter, l10n),
              ),
            ),
        ],
      ),
    );
  }
}

class _ComponentRow extends StatelessWidget {
  const _ComponentRow({required this.component, required this.reason});

  final ScoreComponent component;
  final String reason;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 28,
          height: 28,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: context.sweep.subtleFill,
            borderRadius: Radii.brSm,
          ),
          child: Text(
            component.letter,
            style: context.text.labelLarge?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
        const SizedBox(width: Gap.sm),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                component.name,
                style: context.text.labelLarge?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                reason,
                style: context.text.labelSmall?.copyWith(
                  letterSpacing: 0,
                  color: context.sweep.textTertiary,
                ),
              ),
              const SizedBox(height: Gap.xs),
              ClipRRect(
                borderRadius: BorderRadius.circular(Radii.pill),
                child: LinearProgressIndicator(
                  value: component.value.clamp(0.0, 1.0),
                  minHeight: 6,
                  backgroundColor: context.sweep.subtleFill,
                  valueColor: AlwaysStoppedAnimation(context.colors.primary),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(width: Gap.xs),
        SizedBox(
          width: 36,
          child: Text(
            component.weightLabel,
            textAlign: TextAlign.right,
            style: context.text.labelSmall?.copyWith(
              letterSpacing: 0,
              color: context.sweep.textTertiary,
            ),
          ),
        ),
      ],
    );
  }
}
