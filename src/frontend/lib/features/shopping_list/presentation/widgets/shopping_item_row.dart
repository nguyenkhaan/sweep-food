import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list_item.dart';

/// One checkable line inside a grouped shopping category card (B-01).
class ShoppingItemRow extends StatelessWidget {
  const ShoppingItemRow({
    required this.item,
    required this.onToggle,
    this.onDismissed,
    super.key,
  });

  final ShoppingListItem item;
  final VoidCallback onToggle;
  final VoidCallback? onDismissed;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final catColors = sweep.categoryForLabel(
      item.category,
      fallbackName: item.name,
    );

    final row = InkWell(
      onTap: () {
        AppHaptics.selection();
        onToggle();
      },
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: Gap.md,
          vertical: Gap.sm + 3,
        ),
        child: Row(
          children: [
            _Checkbox(checked: item.checked),
            const SizedBox(width: Gap.sm),
            AnimatedOpacity(
              duration: AppMotion.resolve(context, context.motion.fast),
              opacity: item.checked ? 0.52 : 1.0,
              child: Container(
                width: 34,
                height: 34,
                decoration: BoxDecoration(
                  color: catColors.bg,
                  borderRadius: Radii.brSm,
                ),
                child: Icon(
                  AppIcons.forCategory(item.category, fallbackName: item.name),
                  size: 16,
                  color: catColors.fg,
                ),
              ),
            ),
            const SizedBox(width: Gap.sm),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  _AnimatedStrikeText(
                    text: item.name,
                    struck: item.checked,
                    baseStyle: context.text.titleSmall?.copyWith(
                      fontWeight: FontWeight.w600,
                      color: context.colors.onSurface,
                    ),
                    struckColor: sweep.textTertiary,
                  ),
                  if (item.alreadyInPantry) ...[
                    const SizedBox(height: 3),
                    const _HavePill(),
                  ],
                ],
              ),
            ),
            const SizedBox(width: Gap.sm),
            AnimatedOpacity(
              duration: AppMotion.resolve(context, context.motion.fast),
              opacity: item.checked ? 0.55 : 1.0,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
                decoration: BoxDecoration(
                  color: sweep.subtleFill,
                  borderRadius: BorderRadius.circular(Radii.pill),
                ),
                child: Text(
                  item.quantityLabel,
                  style: AppTypography.tabular(
                    context.text.labelSmall?.copyWith(
                      letterSpacing: 0,
                      color: sweep.textSecondary,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );

    if (onDismissed == null) return row;
    return Dismissible(
      key: ValueKey('shop-${item.id}'),
      direction: DismissDirection.horizontal,
      onDismissed: (_) {
        AppHaptics.medium();
        onDismissed!();
      },
      background: Container(
        alignment: Alignment.centerLeft,
        color: context.colors.errorContainer,
        padding: const EdgeInsets.only(left: Gap.lg),
        child: Icon(AppIcons.trash, size: 18, color: context.colors.error),
      ),
      secondaryBackground: Container(
        alignment: Alignment.centerRight,
        color: context.colors.errorContainer,
        padding: const EdgeInsets.only(right: Gap.lg),
        child: Icon(AppIcons.trash, size: 18, color: context.colors.error),
      ),
      child: row,
    );
  }
}

class _Checkbox extends StatelessWidget {
  const _Checkbox({required this.checked});
  final bool checked;

  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      duration: AppMotion.resolve(context, context.motion.fast),
      curve: AppMotion.resolveCurve(context, context.motion.enterCurve),
      width: 24,
      height: 24,
      decoration: BoxDecoration(
        color: checked ? context.colors.primary : Colors.transparent,
        borderRadius: Radii.brSm,
        border: Border.all(
          color: checked ? context.colors.primary : context.sweep.hairline,
          width: 1.6,
        ),
      ),
      child: AnimatedScale(
        scale: checked ? 1.0 : 0.0,
        duration: AppMotion.resolve(context, context.motion.fast),
        curve: AppMotion.resolveCurve(context, context.motion.springCurve),
        child: Icon(AppIcons.check, size: 15, color: context.colors.onPrimary),
      ),
    );
  }
}

class _HavePill extends StatelessWidget {
  const _HavePill();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
      decoration: BoxDecoration(
        color: context.sweep.successBg,
        borderRadius: BorderRadius.circular(Radii.pill),
      ),
      child: Text(
        context.l10n.shoppingHavePill,
        style: context.text.labelSmall?.copyWith(
          letterSpacing: 0,
          fontSize: 10,
          color: context.sweep.successFg,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

/// Smooth left-to-right animated strike-through bar drawn over the text width
/// so checking a shopping item feels tactile without abrupt text reflow.
class _AnimatedStrikeText extends StatelessWidget {
  const _AnimatedStrikeText({
    required this.text,
    required this.struck,
    required this.baseStyle,
    required this.struckColor,
  });

  final String text;
  final bool struck;
  final TextStyle? baseStyle;
  final Color struckColor;

  @override
  Widget build(BuildContext context) {
    final duration = AppMotion.resolve(
      context,
      const Duration(milliseconds: 260),
    );
    final curve = AppMotion.resolveCurve(context, Curves.easeOutCubic);
    final effectiveStyle =
        (baseStyle ?? const TextStyle()).copyWith(
          color: struck ? struckColor : baseStyle?.color,
        );

    return TweenAnimationBuilder<double>(
      tween: Tween<double>(end: struck ? 1.0 : 0.0),
      duration: duration,
      curve: curve,
      builder: (context, progress, child) => CustomPaint(
        foregroundPainter: _StrikeThroughPainter(
          progress: progress,
          color: struckColor,
        ),
        child: child,
      ),
      child: AnimatedDefaultTextStyle(
        duration: duration,
        curve: curve,
        style: effectiveStyle,
        child: Text(
          text,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
      ),
    );
  }
}

class _StrikeThroughPainter extends CustomPainter {
  const _StrikeThroughPainter({required this.progress, required this.color});

  final double progress;
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    if (progress <= 0.01) return;
    final y = size.height * 0.54;
    final endX = size.width * progress.clamp(0.0, 1.0);
    canvas.drawLine(
      Offset(0, y),
      Offset(endX, y),
      Paint()
        ..color = color.withValues(alpha: 0.85)
        ..strokeWidth = 1.5
        ..strokeCap = StrokeCap.round,
    );
  }

  @override
  bool shouldRepaint(covariant _StrikeThroughPainter old) =>
      old.progress != progress || old.color != color;
}
