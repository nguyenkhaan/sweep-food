import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/app_bottom_sheet.dart';
import 'package:frontend/core/widgets/app_snackbar.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item.dart';
import 'package:frontend/features/pantry/presentation/controllers/pantry_list_controller.dart';

enum _Mode { partial, all, exact }

/// K-04 — "Điều chỉnh số lượng". Reduces (consumes) an item's quantity.
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
    } catch (e) {
      if (mounted) {
        setState(() => _busy = false);
        AppSnack.show(context, context.l10n.pantryUpdateFailed);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final unit = widget.item.unit.label;
    final remaining = (_total - _effectiveUsed).clamp(0, _total);

    return SheetBody(
      title: l10n.adjustQtyTitle(widget.item.name),
      subtitle: l10n.adjustQtySubtitle(
        widget.item.quantityLabel,
        widget.item.storageTier.shortLabel(l10n),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SegmentedButton<_Mode>(
            segments: [
              ButtonSegment(
                value: _Mode.partial,
                label: Text(l10n.adjustQtyPartial),
              ),
              ButtonSegment(value: _Mode.all, label: Text(l10n.adjustQtyAll)),
            ],
            selected: {_mode == _Mode.exact ? _Mode.partial : _mode},
            onSelectionChanged: (s) => setState(() => _mode = s.first),
            showSelectedIcon: false,
          ),
          if (_mode == _Mode.partial) ...[
            Gap.gapMd,
            Slider(
              value: _used.clamp(0, _total),
              max: _total == 0 ? 1 : _total,
              divisions: _total >= 10 ? 20 : null,
              label: '${_used.round()} $unit',
              onChanged: (v) => setState(() => _used = v),
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '0 $unit',
                  style: context.text.labelSmall?.copyWith(letterSpacing: 0),
                ),
                Text(
                  '${_total.round()} $unit',
                  style: context.text.labelSmall?.copyWith(letterSpacing: 0),
                ),
              ],
            ),
          ],
          Gap.gapMd,
          Container(
            padding: const EdgeInsets.all(Gap.sm + 2),
            decoration: BoxDecoration(
              color: context.sweep.subtleFill,
              borderRadius: Radii.brMd,
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(l10n.adjustQtyRemaining),
                Text(
                  '${remaining.round()} $unit',
                  style: const TextStyle(fontWeight: FontWeight.w700),
                ),
              ],
            ),
          ),
          Gap.gapMd,
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: _busy ? null : () => Navigator.of(context).pop(),
                  child: Text(l10n.commonCancel),
                ),
              ),
              const SizedBox(width: Gap.sm),
              Expanded(
                child: FilledButton(
                  onPressed: _busy ? null : _submit,
                  child: _busy
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.4,
                            color: Colors.white,
                          ),
                        )
                      : Text(l10n.commonSave),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
