import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_colors.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list_item.dart';

/// One checkable line on the shopping list (B-01).
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
    final row = InkWell(
      onTap: onToggle,
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: Gap.lg,
          vertical: Gap.sm,
        ),
        child: Row(
          children: [
            _Checkbox(checked: item.checked),
            Gap.gapSm,
            Expanded(
              child: Text(
                item.name,
                style: context.text.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                  decoration: item.checked ? TextDecoration.lineThrough : null,
                  color: item.checked ? context.sweep.textTertiary : null,
                ),
              ),
            ),
            Gap.gapSm,
            Text(
              item.quantityLabel,
              style: context.text.bodySmall?.copyWith(
                color: context.sweep.textTertiary,
              ),
            ),
            if (item.alreadyInPantry) ...[Gap.gapSm, _HavePill()],
          ],
        ),
      ),
    );

    if (onDismissed == null) return row;
    return Dismissible(
      key: ValueKey('shop-${item.id}'),
      direction: DismissDirection.endToStart,
      onDismissed: (_) => onDismissed!(),
      background: Container(
        alignment: Alignment.centerRight,
        color: context.colors.errorContainer,
        padding: const EdgeInsets.only(right: Gap.lg),
        child: Icon(Icons.delete_outline_rounded, color: context.colors.error),
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
    return Container(
      width: 22,
      height: 22,
      decoration: BoxDecoration(
        color: checked ? context.colors.primary : Colors.transparent,
        borderRadius: Radii.brSm,
        border: Border.all(
          color: checked ? context.colors.primary : context.sweep.hairline,
          width: 1.5,
        ),
      ),
      child: checked
          ? const Icon(Icons.check_rounded, size: 15, color: Colors.white)
          : null,
    );
  }
}

class _HavePill extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
      decoration: BoxDecoration(
        color: BrandPalette.green100,
        borderRadius: BorderRadius.circular(Radii.pill),
      ),
      child: Text(
        context.l10n.shoppingHavePill,
        style: const TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w700,
          color: BrandPalette.green700,
        ),
      ),
    );
  }
}
