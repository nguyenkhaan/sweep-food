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
    final ranking = suggestion.rankingFeatures;
    return SheetBody(
      title: ranking == null
          ? l10n.scoreSheetTitle(suggestion.dish.name, suggestion.score)
          : l10n.rankingSheetTitle(suggestion.dish.name, suggestion.rank),
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
              ranking == null
                  ? l10n.scoreFormula
                  : l10n.rankingRawScore(
                      (suggestion.rankScore ?? 0).toStringAsFixed(3),
                    ),
              textAlign: TextAlign.center,
              style: context.text.labelMedium?.copyWith(
                letterSpacing: 0.2,
                color: context.colors.onPrimaryContainer,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          Gap.gapMd,
          if (suggestion.isMock) ...[
            Container(
              padding: const EdgeInsets.all(Gap.sm),
              decoration: BoxDecoration(
                color: context.sweep.soon.bg,
                borderRadius: Radii.brMd,
                border: Border.all(
                  color: context.sweep.soon.fg.withValues(alpha: 0.3),
                ),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(
                    Icons.info_outline_rounded,
                    size: 16,
                    color: context.sweep.soon.fg,
                  ),
                  const SizedBox(width: Gap.xs),
                  Expanded(
                    child: Text(
                      'Kết quả thử nghiệm (Mock AI) — Điểm số mẫu đang được cung cấp trong giai đoạn tích hợp mô hình AI thực tế.',
                      style: context.text.labelSmall?.copyWith(
                        color: context.sweep.soon.fg,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            Gap.gapSm,
          ],
          if (suggestion.explanation != null &&
              suggestion.explanation!.isNotEmpty) ...[
            Container(
              padding: const EdgeInsets.all(Gap.sm),
              decoration: BoxDecoration(
                color: context.sweep.subtleFill,
                borderRadius: Radii.brMd,
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(
                    Icons.auto_awesome_rounded,
                    size: 16,
                    color: context.colors.primary,
                  ),
                  const SizedBox(width: Gap.xs),
                  Expanded(
                    child: Text(
                      suggestion.explanation!,
                      style: context.text.bodySmall?.copyWith(
                        color: context.sweep.textSecondary,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            Gap.gapSm,
          ],
          if (ranking != null)
            _RankingFeaturesView(features: ranking)
          else
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

class _RankingFeaturesView extends StatelessWidget {
  const _RankingFeaturesView({required this.features});

  final RankingFeatures features;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final normalized = <({String letter, String name, double value})>[
      (
        letter: 'C',
        name: l10n.rankingCoreCoverage,
        value: features.coreCoverage,
      ),
      (
        letter: 'S',
        name: l10n.rankingSecondaryCoverage,
        value: features.secondaryCoverage,
      ),
      (
        letter: 'N',
        name: l10n.rankingNutritionConfidence,
        value: features.nutritionConfidence,
      ),
    ];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (final metric in normalized)
          Padding(
            padding: const EdgeInsets.only(bottom: Gap.md),
            child: _ComponentRow(
              component: ScoreComponent(
                letter: metric.letter,
                name: metric.name,
                weightLabel: '${(metric.value * 100).round()}%',
                value: metric.value,
              ),
              reason: '',
            ),
          ),
        Wrap(
          spacing: Gap.xs,
          runSpacing: Gap.xs,
          children: [
            _MetricChip(
              label: l10n.rankingCoreMissing(features.coreMissingCount.round()),
            ),
            _MetricChip(
              label: l10n.rankingShoppingGap(features.shoppingGapItems.round()),
            ),
            _MetricChip(
              label: l10n.rankingRescueWeight(features.rescueWeightG.round()),
            ),
            _MetricChip(
              label: l10n.rankingNutrition(
                features.kcalPerServing.round(),
                features.proteinPerServing.round(),
              ),
            ),
            _MetricChip(
              label: l10n.rankingPrepComplexity(
                features.prepComplexity.toStringAsFixed(1),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _MetricChip extends StatelessWidget {
  const _MetricChip({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: Gap.sm, vertical: Gap.xs),
    decoration: BoxDecoration(
      color: context.sweep.subtleFill,
      borderRadius: Radii.brSm,
    ),
    child: Text(label, style: context.text.labelSmall),
  );
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
