import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooked_food.dart';
import 'package:sweepfood/features/cooking/presentation/controllers/leftover_controller.dart';

/// D-06 — "Còn dư món ăn?". Saves leftover portions as an "Ăn liền" batch with
/// a use-by reminder.
class LeftoverSaveSheet extends ConsumerStatefulWidget {
  const LeftoverSaveSheet({
    required this.dishId,
    required this.dishName,
    required this.initialServings,
    super.key,
  });

  final String dishId;
  final String dishName;
  final int initialServings;

  static Future<void> show(
    BuildContext context, {
    required String dishId,
    required String dishName,
    required int initialServings,
  }) => showAppBottomSheet(
    context,
    builder: (_) => LeftoverSaveSheet(
      dishId: dishId,
      dishName: dishName,
      initialServings: initialServings < 1 ? 1 : initialServings,
    ),
  );

  @override
  ConsumerState<LeftoverSaveSheet> createState() => _State();
}

class _State extends ConsumerState<LeftoverSaveSheet> {
  late int _servings = widget.initialServings;
  int _reminderDays = 2;
  bool _busy = false;

  Future<void> _save() async {
    setState(() => _busy = true);
    try {
      await ref
          .read(leftoverControllerProvider.notifier)
          .save(
            CookedFood(
              dishId: widget.dishId,
              dishName: widget.dishName,
              servings: _servings,
              reminderInDays: _reminderDays,
            ),
          );
      if (!mounted) return;
      Navigator.of(context).pop();
      AppSnack.show(context, context.l10n.leftoverSaved);
    } catch (_) {
      if (!mounted) return;
      setState(() => _busy = false);
      AppSnack.show(context, context.l10n.leftoverSaveFailed);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return SheetBody(
      title: l10n.leftoverTitle,
      subtitle: l10n.leftoverSubtitle,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _Row(
            label: l10n.leftoverServingsLabel,
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                IconButton.filledTonal(
                  visualDensity: VisualDensity.compact,
                  onPressed: _servings > 1
                      ? () => setState(() => _servings--)
                      : null,
                  icon: const Icon(Icons.remove_rounded, size: 18),
                ),
                const SizedBox(width: Gap.sm),
                Text(
                  l10n.servingsCount(_servings),
                  style: context.text.titleSmall,
                ),
                const SizedBox(width: Gap.sm),
                IconButton.filledTonal(
                  visualDensity: VisualDensity.compact,
                  onPressed: _servings < 12
                      ? () => setState(() => _servings++)
                      : null,
                  icon: const Icon(Icons.add_rounded, size: 18),
                ),
              ],
            ),
          ),
          Gap.gapSm,
          _Row(
            label: l10n.leftoverReminderLabel,
            child: DropdownButton<int>(
              value: _reminderDays,
              underline: const SizedBox.shrink(),
              onChanged: _busy
                  ? null
                  : (v) => setState(() => _reminderDays = v ?? 2),
              items: [
                for (final d in const [1, 2, 3])
                  DropdownMenuItem(
                    value: d,
                    child: Text(l10n.leftoverReminderInDays(d)),
                  ),
              ],
            ),
          ),
          Gap.gapSm,
          Container(
            padding: const EdgeInsets.all(Gap.sm),
            decoration: BoxDecoration(
              color: context.sweep.expired.bg,
              borderRadius: Radii.brMd,
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  Icons.info_outline_rounded,
                  size: 15,
                  color: context.sweep.expired.fg,
                ),
                const SizedBox(width: Gap.xs),
                Expanded(
                  child: Text(
                    l10n.leftoverSafetyNote,
                    style: context.text.labelMedium?.copyWith(
                      color: context.sweep.expired.fg,
                      height: 1.4,
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
                child: OutlinedButton(
                  onPressed: _busy ? null : () => Navigator.of(context).pop(),
                  child: Text(l10n.commonSkip),
                ),
              ),
              const SizedBox(width: Gap.sm),
              Expanded(
                child: FilledButton(
                  onPressed: _busy ? null : _save,
                  child: _busy
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.4,
                            color: Colors.white,
                          ),
                        )
                      : Text(l10n.leftoverSaveCta),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _Row extends StatelessWidget {
  const _Row({required this.label, required this.child});

  final String label;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: Gap.sm, vertical: Gap.xs),
      decoration: BoxDecoration(
        borderRadius: Radii.brMd,
        border: Border.all(color: context.sweep.hairline),
      ),
      child: Row(
        children: [
          Expanded(child: Text(label, style: context.text.titleSmall)),
          child,
        ],
      ),
    );
  }
}
