// lib/features/ingest/presentation/widgets/parsed_item_row.dart
// One parsed-item row on the receipt / voice review lists (I-05 / I-07).

import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_colors.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/features/ingest/domain/entities/parsed_item_draft.dart';

/// Editable summary row for one [ParsedItemDraft].
///
/// * [onToggle] non-null → a leading checkbox (receipt multi-select).
/// * [selected] dims the row when `false`.
/// * [onEdit] / [onDelete] add trailing actions.
class ParsedItemRow extends StatelessWidget {
  const ParsedItemRow({
    required this.item,
    this.selected = true,
    this.onToggle,
    this.onEdit,
    this.onDelete,
    super.key,
  });

  final ParsedItemDraft item;
  final bool selected;
  final VoidCallback? onToggle;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final qty = item.quantity == item.quantity.roundToDouble()
        ? item.quantity.round().toString()
        : item.quantity.toStringAsFixed(1);
    final subtitle =
        '$qty ${item.unit.label} · ${item.category} · ${item.storageTier.shortLabel(context.l10n)}';

    return Material(
      color: context.colors.surface,
      borderRadius: Radii.brMd,
      child: InkWell(
        onTap: onToggle,
        borderRadius: Radii.brMd,
        child: Container(
          padding: const EdgeInsets.all(Gap.sm),
          decoration: BoxDecoration(
            borderRadius: Radii.brMd,
            border: Border.all(
              color: selected ? BrandPalette.green700 : sweep.hairline,
              width: selected ? 1.5 : 1,
            ),
          ),
          child: Row(
            children: [
              if (onToggle != null) ...[
                _Checkbox(selected: selected, hairline: sweep.hairline),
                const SizedBox(width: Gap.sm),
              ],
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.name.isEmpty ? context.l10n.scanNoName : item.name,
                      style: context.text.titleSmall?.copyWith(
                        fontWeight: FontWeight.w600,
                        color: selected
                            ? context.colors.onSurface
                            : sweep.textTertiary,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 2),
                    Text(
                      subtitle,
                      style: context.text.bodySmall?.copyWith(
                        color: sweep.textTertiary,
                        fontSize: 11,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              if (item.isExpiryWarn) ...[
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 7,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: BrandPalette.warnSoon.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    context.l10n.scanNeedsCheckShort,
                    style: const TextStyle(
                      color: BrandPalette.warnSoon,
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
                const SizedBox(width: Gap.xs),
              ],
              if (onEdit != null)
                IconButton(
                  visualDensity: VisualDensity.compact,
                  icon: Icon(
                    Icons.edit_outlined,
                    size: 18,
                    color: sweep.textTertiary,
                  ),
                  onPressed: onEdit,
                ),
              if (onDelete != null)
                IconButton(
                  visualDensity: VisualDensity.compact,
                  icon: Icon(
                    Icons.close_rounded,
                    size: 18,
                    color: sweep.textTertiary,
                  ),
                  onPressed: onDelete,
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Checkbox extends StatelessWidget {
  const _Checkbox({required this.selected, required this.hairline});

  final bool selected;
  final Color hairline;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 22,
      height: 22,
      decoration: BoxDecoration(
        color: selected ? BrandPalette.green700 : Colors.transparent,
        borderRadius: BorderRadius.circular(6),
        border: selected ? null : Border.all(color: hairline, width: 1.5),
      ),
      child: selected
          ? const Icon(Icons.check_rounded, size: 16, color: Colors.white)
          : null,
    );
  }
}
