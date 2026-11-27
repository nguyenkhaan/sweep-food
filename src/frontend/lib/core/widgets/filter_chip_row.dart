import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// One selectable option in a [FilterChipRow].
typedef ChipOption<T> = ({T value, String label});

/// Horizontal, scrollable row of single-select chips with haptic feedback and
/// smooth state transitions.
class FilterChipRow<T> extends StatelessWidget {
  const FilterChipRow({
    required this.options,
    required this.selected,
    required this.onSelected,
    this.padding = const EdgeInsets.symmetric(horizontal: Gap.lg),
    super.key,
  });

  final List<ChipOption<T>> options;
  final T selected;
  final ValueChanged<T> onSelected;
  final EdgeInsetsGeometry padding;

  @override
  Widget build(BuildContext context) {
    final duration = AppMotion.resolve(context, context.motion.fast);
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: padding,
      child: Row(
        children: [
          for (final o in options) ...[
            AnimatedContainer(
              duration: duration,
              curve: context.motion.enterCurve,
              decoration: BoxDecoration(
                color: o.value == selected
                    ? context.colors.primary
                    : context.colors.surfaceContainerLowest,
                borderRadius: BorderRadius.circular(Radii.pill),
                border: Border.all(
                  color: o.value == selected
                      ? context.colors.primary
                      : context.sweep.hairline,
                ),
              ),
              child: Material(
                color: Colors.transparent,
                child: InkWell(
                  onTap: () {
                    AppHaptics.selection();
                    onSelected(o.value);
                  },
                  borderRadius: BorderRadius.circular(Radii.pill),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: Gap.md - 2,
                      vertical: Gap.xs,
                    ),
                    child: Text(
                      o.label,
                      style: context.text.labelMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                        color: o.value == selected
                            ? context.colors.onPrimary
                            : context.sweep.textSecondary,
                      ),
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(width: Gap.xs),
          ],
        ],
      ),
    );
  }
}
