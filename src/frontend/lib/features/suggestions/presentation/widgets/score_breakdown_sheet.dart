import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/extensions/date_time_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/shared/widgets/nutrition_disclaimer_banner.dart';

/// S-02 — "Vì sao món này đạt N điểm?" (Concept B · Format 1 Crisp Sheet).
class ScoreBreakdownSheet extends StatelessWidget {
  const ScoreBreakdownSheet({required this.suggestion, super.key});

  final DishSuggestion suggestion;

  static Future<void> show(BuildContext context, DishSuggestion suggestion) =>
      showAppBottomSheet(
        context,
        builder: (_) => ScoreBreakdownSheet(suggestion: suggestion),
      );

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final cs = context.colors;
    final explanationText = _localizedExplanation(
      context,
      suggestion.explanation,
    );
    final rescued = suggestion.rescuedIngredients.isNotEmpty
        ? suggestion.rescuedIngredients.map(_rescuedLabel).toList()
        : suggestion.nearExpiryIngredients;

    return SheetBody(
      icon: AppIcons.chefHat,
      title: '#${suggestion.rank} ${suggestion.dish.name}',
      subtitle: suggestion.statusLabel,
      trailing: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        decoration: BoxDecoration(
          color: sweep.heroSurface,
          borderRadius: BorderRadius.circular(Radii.pill),
        ),
        child: Text(
          '${suggestion.score} ${context.l10n.scoreBadgeLabel}',
          style: AppTypography.tabular(
            context.text.labelSmall?.copyWith(
              letterSpacing: 0,
              color: sweep.onHeroSurface,
              fontWeight: FontWeight.w800,
            ),
          ),
        ),
      ),
      child: ConstrainedBox(
        constraints: BoxConstraints(
          maxHeight: MediaQuery.sizeOf(context).height * 0.72,
        ),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 1. Compact ingredient readiness + rescued highlight
              SheetGroupCard(
                padding: const EdgeInsets.all(Gap.md),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        _MiniCountPill(
                          label: '${suggestion.matchedIngredients.length} có sẵn',
                          bg: cs.primaryContainer,
                          fg: cs.primary,
                        ),
                        const SizedBox(width: Gap.xs),
                        _MiniCountPill(
                          label: '${suggestion.missingIngredients.length} cần mua',
                          bg: suggestion.missingIngredients.isEmpty
                              ? sweep.subtleFill
                              : sweep.expired.bg,
                          fg: suggestion.missingIngredients.isEmpty
                              ? sweep.textSecondary
                              : sweep.expired.fg,
                        ),
                        if (suggestion.optionalIngredients.isNotEmpty) ...[
                          const SizedBox(width: Gap.xs),
                          _MiniCountPill(
                            label:
                                '${suggestion.optionalIngredients.length} tùy chọn',
                            bg: sweep.subtleFill,
                            fg: sweep.textSecondary,
                          ),
                        ],
                      ],
                    ),
                    if (rescued.isNotEmpty) ...[
                      const SizedBox(height: Gap.sm),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: Gap.sm + 2,
                          vertical: Gap.xs + 3,
                        ),
                        decoration: BoxDecoration(
                          color: sweep.culinaryAccentBg,
                          borderRadius: Radii.brMd,
                        ),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Padding(
                              padding: const EdgeInsets.only(top: 1),
                              child: Icon(
                                AppIcons.flame,
                                size: 15,
                                color: sweep.ctaWarm,
                              ),
                            ),
                            const SizedBox(width: 6),
                            Expanded(
                              child: Text(
                                'Giải cứu: ${rescued.join(', ')}',
                                style: context.text.bodySmall?.copyWith(
                                  color: sweep.ctaWarm,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              ),

              if (suggestion.fitReasons.isNotEmpty) ...[
                Gap.gapSm,
                _FitReasonsSection(reasons: suggestion.fitReasons),
              ],

              // 2. Score formula breakdown card
              Gap.gapMd,
              _SectionKicker(
                label: context.l10n.scoreFormula,
                uppercase: false,
              ),
              const SizedBox(height: Gap.xs),
              SheetGroupCard(
                padding: const EdgeInsets.fromLTRB(
                  Gap.md,
                  Gap.md,
                  Gap.md,
                  Gap.xs,
                ),
                child: Column(
                  children: [
                    for (final component in suggestion.breakdown.components(
                      context.l10n,
                    ))
                      _FeatureBar(
                        label: component.name,
                        value: component.value,
                        detail:
                            '${component.weightLabel} · ${(component.value * 100).round()}%',
                      ),
                  ],
                ),
              ),

              if (explanationText != null && explanationText.isNotEmpty) ...[
                Gap.gapSm,
                Container(
                  padding: const EdgeInsets.all(Gap.sm + 4),
                  decoration: BoxDecoration(
                    color: sweep.subtleFill,
                    borderRadius: Radii.brLg,
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(AppIcons.lightbulb, size: 16, color: cs.primary),
                      const SizedBox(width: Gap.xs + 2),
                      Expanded(
                        child: Text(
                          explanationText,
                          style: context.text.bodySmall?.copyWith(
                            color: sweep.textSecondary,
                            height: 1.4,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],

              // 3. Detailed AI ranking metrics & ingredients
              Gap.gapMd,
              const _SectionKicker(label: 'CHỈ SỐ XẾP HẠNG CHI TIẾT'),
              const SizedBox(height: Gap.xs),
              _AiFeatureList(suggestion: suggestion),

              Gap.gapMd,
              const NutritionDisclaimerBanner(compact: true),
            ],
          ),
        ),
      ),
    );
  }

  static String? _localizedExplanation(BuildContext context, String? raw) {
    if (raw == null || raw.trim().isEmpty) return null;
    final trimmed = raw.trim();
    final isVi = Localizations.localeOf(context).languageCode == 'vi';
    if (!isVi) return trimmed;
    if (trimmed.toLowerCase().contains(
      'ai-ranked from pantry availability, expiry',
    )) {
      return 'Được xếp hạng bằng SweepFood AI dựa trên nguyên liệu sẵn có, hạn dùng và số nguyên liệu cần mua thêm.';
    }
    return trimmed;
  }
}

class _SectionKicker extends StatelessWidget {
  const _SectionKicker({required this.label, this.uppercase = true});
  final String label;
  final bool uppercase;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(left: 2),
      child: Text(
        uppercase ? label.toUpperCase() : label,
        style: context.text.labelSmall?.copyWith(
          letterSpacing: uppercase ? 0.6 : 0,
          color: context.sweep.textTertiary,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }
}

class _MiniCountPill extends StatelessWidget {
  const _MiniCountPill({
    required this.label,
    required this.bg,
    required this.fg,
  });

  final String label;
  final Color bg;
  final Color fg;

  @override
  Widget build(BuildContext context) {
    return Flexible(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
        decoration: BoxDecoration(
          color: bg,
          borderRadius: BorderRadius.circular(Radii.pill),
        ),
        child: Text(
          label,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: AppTypography.tabular(
            context.text.labelSmall?.copyWith(
              letterSpacing: 0,
              color: fg,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
      ),
    );
  }
}

class _FitReasonsSection extends StatelessWidget {
  const _FitReasonsSection({required this.reasons});

  final List<String> reasons;

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    return SheetGroupCard(
      padding: const EdgeInsets.all(Gap.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(AppIcons.badgeCheck, size: 16, color: cs.primary),
              const SizedBox(width: Gap.xs),
              Expanded(
                child: Text(
                  context.l10n.suggestionsFitReasonsTitle,
                  style: context.text.labelMedium?.copyWith(
                    color: cs.primary,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: Gap.xs + 2),
          for (var i = 0; i < reasons.length; i++) ...[
            if (i > 0) const SizedBox(height: 6),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.only(top: 3),
                  child: Icon(AppIcons.check, size: 14, color: cs.primary),
                ),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    reasons[i],
                    style: context.text.bodySmall?.copyWith(
                      color: cs.onSurface,
                      height: 1.38,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}

/// "400g đùi gà (hạn 22/10)" — grams this dish uses from soon-to-expire batches.
String _rescuedLabel(RescuedIngredient item) {
  final grams = item.rescuedG.round();
  final expiry = item.expiresAt;
  final label = '${grams}g ${item.name.toLowerCase()}';
  return expiry == null ? label : '$label (hạn ${expiry.ddMM})';
}

class _AiFeatureList extends StatelessWidget {
  const _AiFeatureList({required this.suggestion});

  final DishSuggestion suggestion;

  @override
  Widget build(BuildContext context) {
    final f = suggestion.rankingFeatures;
    final sweep = context.sweep;
    final cs = context.colors;
    final metrics = <(String, String)>[
      (
        'Khối lượng cận hạn được giải cứu',
        '${f.rescueWeightG.toStringAsFixed(0)} g',
      ),
      (
        'Khoảng trống mua sắm',
        '${f.shoppingGapItems.toStringAsFixed(0)} món',
      ),
      (
        'Dinh dưỡng mỗi khẩu phần',
        '${f.kcalPerServing.toStringAsFixed(0)} kcal · ${f.proteinPerServing.toStringAsFixed(1)} g đạm',
      ),
      ('Độ phức tạp chế biến', f.prepComplexity.toStringAsFixed(2)),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        SheetGroupCard(
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(
                  Gap.md,
                  Gap.md,
                  Gap.md,
                  Gap.xs,
                ),
                child: Column(
                  children: [
                    _FeatureBar(
                      label: 'Độ phủ nguyên liệu chính',
                      value: f.coreCoverage,
                      detail: '${(f.coreCoverage * 100).round()}%',
                    ),
                    _FeatureBar(
                      label: 'Độ phủ nguyên liệu phụ',
                      value: f.secondaryCoverage,
                      detail: '${(f.secondaryCoverage * 100).round()}%',
                    ),
                    _FeatureBar(
                      label: 'Độ tin cậy dinh dưỡng',
                      value: f.nutritionConfidence,
                      detail: '${(f.nutritionConfidence * 100).round()}%',
                    ),
                  ],
                ),
              ),
              for (final m in metrics) ...[
                Divider(height: 1, color: sweep.hairline),
                Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: Gap.md,
                    vertical: 11,
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: Text(
                          m.$1,
                          style: context.text.bodySmall?.copyWith(
                            color: sweep.textSecondary,
                          ),
                        ),
                      ),
                      const SizedBox(width: Gap.sm),
                      Text(
                        m.$2,
                        style: AppTypography.tabular(
                          context.text.labelMedium?.copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
        if (suggestion.matchedIngredients.isNotEmpty ||
            suggestion.missingIngredients.isNotEmpty ||
            suggestion.optionalIngredients.isNotEmpty) ...[
          Gap.gapMd,
          SheetGroupCard(
            padding: const EdgeInsets.all(Gap.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (suggestion.matchedIngredients.isNotEmpty)
                  _IngredientGroup(
                    title: 'Đã có trong kho',
                    icon: AppIcons.checkCircle,
                    pillBg: cs.primaryContainer,
                    pillFg: cs.primary,
                    items: suggestion.matchedIngredients,
                  ),
                if (suggestion.missingIngredients.isNotEmpty) ...[
                  if (suggestion.matchedIngredients.isNotEmpty) Gap.gapSm,
                  _IngredientGroup(
                    title: 'Cần mua thêm',
                    icon: AppIcons.shopping,
                    pillBg: sweep.expired.bg,
                    pillFg: sweep.expired.fg,
                    items: suggestion.missingIngredients,
                  ),
                ],
                if (suggestion.optionalIngredients.isNotEmpty) ...[
                  if (suggestion.matchedIngredients.isNotEmpty ||
                      suggestion.missingIngredients.isNotEmpty)
                    Gap.gapSm,
                  _IngredientGroup(
                    title: 'Ăn kèm tùy chọn',
                    icon: AppIcons.add,
                    pillBg: sweep.subtleFill,
                    pillFg: sweep.textSecondary,
                    items: suggestion.optionalIngredients,
                  ),
                ],
              ],
            ),
          ),
        ],
      ],
    );
  }
}

class _IngredientGroup extends StatelessWidget {
  const _IngredientGroup({
    required this.title,
    required this.icon,
    required this.pillBg,
    required this.pillFg,
    required this.items,
  });

  final String title;
  final IconData icon;
  final Color pillBg;
  final Color pillFg;
  final List<RecommendationIngredient> items;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 15, color: pillFg),
            const SizedBox(width: Gap.xs),
            Text(
              title,
              style: context.text.labelMedium?.copyWith(
                color: pillFg,
                fontWeight: FontWeight.w800,
              ),
            ),
          ],
        ),
        const SizedBox(height: Gap.xs),
        Wrap(
          spacing: Gap.xs,
          runSpacing: Gap.xs,
          children: [
            for (final item in items)
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 5,
                ),
                decoration: BoxDecoration(
                  color: pillBg,
                  borderRadius: BorderRadius.circular(Radii.pill),
                ),
                child: Text(
                  item.requiredG > 0
                      ? '${item.name} · ${item.requiredG.toStringAsFixed(0)} g'
                      : item.name,
                  style: context.text.labelSmall?.copyWith(
                    letterSpacing: 0,
                    color: pillFg,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
          ],
        ),
      ],
    );
  }
}

class _FeatureBar extends StatelessWidget {
  const _FeatureBar({
    required this.label,
    required this.value,
    required this.detail,
  });

  final String label;
  final double value;
  final String detail;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    return Padding(
      padding: const EdgeInsets.only(bottom: Gap.sm + 4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  label,
                  style: context.text.labelMedium?.copyWith(
                    color: sweep.textSecondary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              Text(
                detail,
                style: AppTypography.tabular(
                  context.text.labelMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          ClipRRect(
            borderRadius: BorderRadius.circular(Radii.pill),
            child: TweenAnimationBuilder<double>(
              tween: Tween(begin: 0, end: value.clamp(0.0, 1.0)),
              duration: AppMotion.resolve(context, context.motion.medium),
              curve: AppMotion.resolveCurve(context, context.motion.enterCurve),
              builder: (_, val, __) => LinearProgressIndicator(
                value: val,
                minHeight: 6,
                backgroundColor: sweep.subtleFill,
                valueColor: AlwaysStoppedAnimation(context.colors.primary),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
