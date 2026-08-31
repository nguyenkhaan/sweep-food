import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// One selectable option in a [FilterChipRow].
typedef ChipOption<T> = ({T value, String label});

/// Horizontal, scrollable row of single-select chips (bữa sáng/trưa/tối, sort…).
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
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: padding,
      child: Row(
        children: [
          for (final o in options) ...[
            ChoiceChip(
              label: Text(o.label),
              selected: o.value == selected,
              onSelected: (_) => onSelected(o.value),
              showCheckmark: false,
              selectedColor: context.colors.primary,
              labelStyle: context.text.labelMedium?.copyWith(
                color: o.value == selected
                    ? context.colors.onPrimary
                    : context.sweep.textSecondary,
              ),
              side: BorderSide(
                color: o.value == selected
                    ? context.colors.primary
                    : context.sweep.hairline,
              ),
            ),
            const SizedBox(width: Gap.xs),
          ],
        ],
      ),
    );
  }
}
