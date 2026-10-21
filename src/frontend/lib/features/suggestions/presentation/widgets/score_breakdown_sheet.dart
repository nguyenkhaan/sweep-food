import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/extensions/date_time_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';

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

  @override
  Widget build(BuildContext context) {
    return SheetBody(
      title: '#${suggestion.rank} ${suggestion.dish.name}',
      child: ConstrainedBox(
        constraints: BoxConstraints(
          maxHeight: MediaQuery.sizeOf(context).height * 0.68,
        ),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _AiResultHeader(suggestion: suggestion),
              Gap.gapMd,
              Text(
                context.l10n.scoreFormula,
                style: context.text.labelMedium?.copyWith(
                  color: context.sweep.textSecondary,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: Gap.sm),
              for (final component in suggestion.breakdown.components(
                context.l10n,
              ))
                _FeatureBar(
                  label: component.name,
                  value: component.value,
                  detail:
                      '${component.weightLabel} · ${(component.value * 100).round()}%',
                ),
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
              _AiFeatureList(suggestion: suggestion),
            ],
          ),
        ),
      ),
    );
  }
}

class _AiResultHeader extends StatelessWidget {
  const _AiResultHeader({required this.suggestion});

  final DishSuggestion suggestion;

  @override
  Widget build(BuildContext context) {
    final rescued = suggestion.rescuedIngredients.isNotEmpty
        ? suggestion.rescuedIngredients.map(_rescuedLabel).toList()
        : suggestion.nearExpiryIngredients;
    return Container(
      padding: const EdgeInsets.all(Gap.sm),
      decoration: BoxDecoration(
        color: context.colors.primaryContainer,
        borderRadius: Radii.brMd,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.auto_awesome_rounded, color: context.colors.primary),
              const SizedBox(width: Gap.xs),
              Expanded(
                child: Text(
                  suggestion.statusLabel,
                  style: context.text.labelLarge?.copyWith(
                    color: context.colors.onPrimaryContainer,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
              Text(
                'AI ${suggestion.rankScore.toStringAsFixed(3)}',
                style: context.text.labelSmall?.copyWith(
                  color: context.colors.onPrimaryContainer,
                ),
              ),
            ],
          ),
          if (rescued.isNotEmpty) ...[
            const SizedBox(height: Gap.xs),
            Text(
              '🔥 Giải cứu: ${rescued.join(', ')}',
              style: context.text.bodySmall?.copyWith(
                color: context.colors.onPrimaryContainer,
              ),
            ),
          ],
          const SizedBox(height: Gap.xs),
          Text(
            '${suggestion.matchedIngredients.length} nguyên liệu đã khớp · '
            '${suggestion.missingIngredients.length} cần mua · '
            '${suggestion.optionalIngredients.length} tùy chọn',
            style: context.text.labelSmall?.copyWith(
              color: context.colors.onPrimaryContainer.withValues(alpha: 0.85),
            ),
          ),
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
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
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
        _FeatureValue(
          label: 'Khối lượng cận hạn được giải cứu',
          value: '${f.rescueWeightG.toStringAsFixed(0)} g',
        ),
        _FeatureValue(
          label: 'Khoảng trống mua sắm',
          value: '${f.shoppingGapItems.toStringAsFixed(0)} món',
        ),
        _FeatureValue(
          label: 'Dinh dưỡng mỗi khẩu phần',
          value:
              '${f.kcalPerServing.toStringAsFixed(0)} kcal · ${f.proteinPerServing.toStringAsFixed(1)} g đạm',
        ),
        _FeatureValue(
          label: 'Độ phức tạp chế biến',
          value: f.prepComplexity.toStringAsFixed(2),
        ),
        if (suggestion.matchedIngredients.isNotEmpty)
          _IngredientGroup(
            title: 'Đã có trong kho',
            icon: Icons.check_circle_outline_rounded,
            color: context.colors.primary,
            items: suggestion.matchedIngredients,
          ),
        if (suggestion.missingIngredients.isNotEmpty)
          _IngredientGroup(
            title: 'Cần mua thêm',
            icon: Icons.shopping_cart_outlined,
            color: context.colors.error,
            items: suggestion.missingIngredients,
          ),
        if (suggestion.optionalIngredients.isNotEmpty)
          _IngredientGroup(
            title: 'Ăn kèm tùy chọn',
            icon: Icons.add_circle_outline_rounded,
            color: context.sweep.textSecondary,
            items: suggestion.optionalIngredients,
          ),
      ],
    );
  }
}

class _IngredientGroup extends StatelessWidget {
  const _IngredientGroup({
    required this.title,
    required this.icon,
    required this.color,
    required this.items,
  });

  final String title;
  final IconData icon;
  final Color color;
  final List<RecommendationIngredient> items;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: Gap.xs, bottom: Gap.sm),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 16, color: color),
              const SizedBox(width: Gap.xs),
              Text(
                title,
                style: context.text.labelMedium?.copyWith(
                  color: color,
                  fontWeight: FontWeight.w700,
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
                Chip(
                  visualDensity: VisualDensity.compact,
                  label: Text(
                    item.requiredG > 0
                        ? '${item.name} · ${item.requiredG.toStringAsFixed(0)} g'
                        : item.name,
                  ),
                ),
            ],
          ),
        ],
      ),
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
    return Padding(
      padding: const EdgeInsets.only(bottom: Gap.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(child: Text(label, style: context.text.labelMedium)),
              Text(detail, style: context.text.labelMedium),
            ],
          ),
          const SizedBox(height: Gap.xs),
          ClipRRect(
            borderRadius: BorderRadius.circular(Radii.pill),
            child: LinearProgressIndicator(
              value: value.clamp(0.0, 1.0),
              minHeight: 7,
              backgroundColor: context.sweep.subtleFill,
              valueColor: AlwaysStoppedAnimation(context.colors.primary),
            ),
          ),
        ],
      ),
    );
  }
}

class _FeatureValue extends StatelessWidget {
  const _FeatureValue({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: Gap.sm),
      child: Row(
        children: [
          Expanded(
            child: Text(
              label,
              style: context.text.bodySmall?.copyWith(
                color: context.sweep.textSecondary,
              ),
            ),
          ),
          Text(
            value,
            style: context.text.labelMedium?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}
