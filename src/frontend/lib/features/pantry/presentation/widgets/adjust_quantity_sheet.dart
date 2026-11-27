import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';

enum _Mode { partial, all, exact }

/// K-04 — "Điều chỉnh số lượng" (Concept B · Format 1 Crisp Sheet).
class AdjustQuantitySheet extends ConsumerStatefulWidget {
  const AdjustQuantitySheet({required this.item, super.key});
  final PantryItem item;

  static Future<void> show(BuildContext context, PantryItem item) =>
      showAppBottomSheet(
        context,
        builder: (_) => AdjustQuantitySheet(item: item),
      );

  @override
  ConsumerState<AdjustQuantitySheet> createState() => _State();
}

class _State extends ConsumerState<AdjustQuantitySheet> {
  _Mode _mode = _Mode.partial;
  late double _used = widget.item.quantity / 2;
  bool _busy = false;

  double get _total => widget.item.quantity;

  double get _effectiveUsed => switch (_mode) {
    _Mode.all => _total,
    _Mode.exact => _total,
    _Mode.partial => _used.clamp(0, _total),
  };

  Future<void> _submit() async {
    setState(() => _busy = true);
    try {
      await ref
          .read(pantryListControllerProvider.notifier)
          .consume(widget.item.id, quantityUsed: _effectiveUsed);
      if (mounted) {
        Navigator.of(context).pop();
        AppSnack.show(
          context,
          context.l10n.pantryItemUpdated(widget.item.name),
        );
      }
    } catch (_) {
      if (mounted) {
        setState(() => _busy = false);
        AppSnack.show(context, context.l10n.pantryUpdateFailed);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final cs = context.colors;
    final sweep = context.sweep;
    final unit = widget.item.unit.label;
    final remaining = (_total - _effectiveUsed).clamp(0, _total);

    return SheetBody(
      icon: AppIcons.filter,
      title: l10n.adjustQtyTitle(widget.item.name),
      subtitle: l10n.adjustQtySubtitle(
        widget.item.quantityLabel,
        widget.item.storageTier.shortLabel(l10n),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SheetSegmentedControl<_Mode>(
            selected: _mode == _Mode.exact ? _Mode.partial : _mode,
            options: [
              (value: _Mode.partial, label: l10n.adjustQtyPartial, icon: null),
              (value: _Mode.all, label: l10n.adjustQtyAll, icon: null),
            ],
            onChanged: (next) => setState(() => _mode = next),
          ),
          if (_mode == _Mode.partial) ...[
            Gap.gapMd,
            SheetGroupCard(
              padding: const EdgeInsets.fromLTRB(
                Gap.md,
                Gap.sm + 4,
                Gap.md,
                Gap.sm + 2,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    crossAxisAlignment: CrossAxisAlignment.baseline,
                    textBaseline: TextBaseline.alphabetic,
                    children: [
                      Text(
                        'Số lượng đã dùng',
                        style: context.text.labelMedium?.copyWith(
                          color: sweep.textSecondary,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      Text(
                        '${_used.round()} $unit',
                        style: AppTypography.tabular(
                          context.text.titleLarge?.copyWith(
                            color: cs.primary,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                    ],
                  ),
                  SliderTheme(
                    data: SliderTheme.of(context).copyWith(
                      activeTrackColor: cs.primary,
                      inactiveTrackColor: sweep.subtleFill,
                      thumbColor: cs.primary,
                      trackHeight: 5,
                    ),
                    child: Slider(
                      value: _used.clamp(0, _total),
                      max: _total == 0 ? 1 : _total,
                      divisions: _total >= 10 ? 20 : null,
                      label: '${_used.round()} $unit',
                      onChanged: (v) => setState(() => _used = v),
                    ),
                  ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        '0 $unit',
                        style: AppTypography.tabular(
                          context.text.labelSmall?.copyWith(
                            letterSpacing: 0,
                            color: sweep.textTertiary,
                          ),
                        ),
                      ),
                      Text(
                        '${_total.round()} $unit',
                        style: AppTypography.tabular(
                          context.text.labelSmall?.copyWith(
                            letterSpacing: 0,
                            color: sweep.textTertiary,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
          Gap.gapSm,
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: Gap.md,
              vertical: Gap.sm + 4,
            ),
            decoration: BoxDecoration(
              color: cs.primaryContainer,
              borderRadius: Radii.brLg,
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  l10n.adjustQtyRemaining,
                  style: context.text.labelLarge?.copyWith(
                    color: cs.onPrimaryContainer,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                Text(
                  '${remaining.round()} $unit',
                  style: AppTypography.tabular(
                    context.text.titleSmall?.copyWith(
                      color: cs.primary,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ),
          ),
          Gap.gapMd,
          Row(
            children: [
              Expanded(
                flex: 4,
                child: SheetCancelButton(
                  label: l10n.commonCancel,
                  onPressed: _busy ? null : () => Navigator.of(context).pop(),
                ),
              ),
              const SizedBox(width: Gap.sm),
              Expanded(
                flex: 6,
                child: SheetWarmButton(
                  label: l10n.commonSave,
                  icon: AppIcons.check,
                  loading: _busy,
                  onPressed: _busy ? null : _submit,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
