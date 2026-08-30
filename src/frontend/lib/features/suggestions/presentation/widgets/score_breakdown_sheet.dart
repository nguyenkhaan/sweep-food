import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/app_bottom_sheet.dart';
import 'package:frontend/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:frontend/features/suggestions/domain/entities/score_breakdown.dart';

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

  String _reason(String letter) {
    final s = suggestion;
    return switch (letter) {
      'E' => s.nearExpiryIngredients.isEmpty
          ? 'Không dùng nguyên liệu cận hạn nào'
          : 'Dùng ${s.nearExpiryCount} nguyên liệu cận hạn: '
              '${s.nearExpiryIngredients.join(", ")}',
      'A' => '${s.availabilityPercent}% nguyên liệu đã có trong tủ bếp',
      'P' => '${s.dish.servings} khẩu phần · '
          '${s.dish.nutritionPerServing.energyKcal.round()} kcal · '
          '${s.dish.totalTimeMin} phút',
      'U' => s.toBuyCount == 0
          ? 'Không phải mua thêm nguyên liệu nào'
          : 'Chỉ cần mua thêm ${s.toBuyCount} nguyên liệu',
      _ => '',
    };
  }

  @override
  Widget build(BuildContext context) {
    return SheetBody(
      title: 'Vì sao “${suggestion.dish.name}” đạt ${suggestion.score} điểm?',
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
              'Điểm = 0.4·E + 0.3·A + 0.2·P + 0.1·U',
              textAlign: TextAlign.center,
              style: context.text.labelMedium?.copyWith(
                letterSpacing: 0.2,
                color: context.colors.onPrimaryContainer,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          Gap.gapMd,
          for (final c in suggestion.breakdown.components)
            Padding(
              padding: const EdgeInsets.only(bottom: Gap.md),
              child: _ComponentRow(component: c, reason: _reason(c.letter)),
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
