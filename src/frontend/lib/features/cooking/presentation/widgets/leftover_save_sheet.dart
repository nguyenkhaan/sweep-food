import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooked_food.dart';
import 'package:sweepfood/features/cooking/presentation/controllers/leftover_controller.dart';

/// D-06 — "Còn dư món ăn?" (Concept B · Format 1 Crisp Sheet).
class LeftoverSaveSheet extends ConsumerStatefulWidget {
  const LeftoverSaveSheet({
    required this.sessionId,
    required this.dishName,
    required this.initialServings,
    super.key,
  });

  final String sessionId;
  final String dishName;
  final int initialServings;

  static Future<void> show(
    BuildContext context, {
    required String sessionId,
    required String dishName,
    required int initialServings,
  }) => showAppBottomSheet(
    context,
    builder: (_) => LeftoverSaveSheet(
      sessionId: sessionId,
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
              sessionId: widget.sessionId,
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
    final cs = context.colors;
    final sweep = context.sweep;

    return SheetBody(
      icon: AppIcons.packagePlus,
      warmIcon: true,
      title: l10n.leftoverTitle,
      subtitle: l10n.leftoverSubtitle,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SheetGroupCard(
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: Gap.md,
                    vertical: Gap.sm + 4,
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: Text(
                          l10n.leftoverServingsLabel,
                          style: context.text.titleSmall?.copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 4,
                          vertical: 3,
                        ),
                        decoration: BoxDecoration(
                          color: sweep.subtleFill,
                          borderRadius: BorderRadius.circular(Radii.pill),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            _RoundStepBtn(
                              icon: AppIcons.minus,
                              onTap: !_busy && _servings > 1
                                  ? () => setState(() => _servings--)
                                  : null,
                            ),
                            Padding(
                              padding: const EdgeInsets.symmetric(
                                horizontal: Gap.sm,
                              ),
                              child: Text(
                                l10n.servingsCount(_servings),
                                style: AppTypography.tabular(
                                  context.text.labelLarge?.copyWith(
                                    fontWeight: FontWeight.w800,
                                  ),
                                ),
                              ),
                            ),
                            _RoundStepBtn(
                              icon: AppIcons.add,
                              onTap: !_busy && _servings < 12
                                  ? () => setState(() => _servings++)
                                  : null,
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                Divider(height: 1, color: sweep.hairline),
                Padding(
                  padding: const EdgeInsets.all(Gap.md),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        l10n.leftoverReminderLabel,
                        style: context.text.titleSmall?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: Gap.sm),
                      Row(
                        children: [
                          for (final d in const [1, 2, 3]) ...[
                            if (d > 1) const SizedBox(width: Gap.xs),
                            Expanded(
                              child: GestureDetector(
                                onTap: _busy
                                    ? null
                                    : () {
                                        AppHaptics.selection();
                                        setState(() => _reminderDays = d);
                                      },
                                child: AnimatedContainer(
                                  duration: AppMotion.resolve(
                                    context,
                                    context.motion.fast,
                                  ),
                                  padding: const EdgeInsets.symmetric(
                                    vertical: 9,
                                  ),
                                  alignment: Alignment.center,
                                  decoration: BoxDecoration(
                                    color: _reminderDays == d
                                        ? cs.primary
                                        : sweep.subtleFill,
                                    borderRadius: BorderRadius.circular(
                                      Radii.pill,
                                    ),
                                  ),
                                  child: Text(
                                    l10n.leftoverReminderInDays(d),
                                    style: context.text.labelMedium?.copyWith(
                                      color: _reminderDays == d
                                          ? cs.onPrimary
                                          : sweep.textSecondary,
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          Gap.gapSm,
          Container(
            padding: const EdgeInsets.all(Gap.sm + 4),
            decoration: BoxDecoration(
              color: sweep.expired.bg,
              borderRadius: Radii.brLg,
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.only(top: 1),
                  child: Icon(
                    AppIcons.info,
                    size: 16,
                    color: sweep.expired.fg,
                  ),
                ),
                const SizedBox(width: Gap.xs + 2),
                Expanded(
                  child: Text(
                    l10n.leftoverSafetyNote,
                    style: context.text.bodySmall?.copyWith(
                      color: sweep.expired.fg,
                      fontWeight: FontWeight.w600,
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
                flex: 4,
                child: SheetCancelButton(
                  label: l10n.commonSkip,
                  onPressed: _busy ? null : () => Navigator.of(context).pop(),
                ),
              ),
              const SizedBox(width: Gap.sm),
              Expanded(
                flex: 6,
                child: SheetWarmButton(
                  label: l10n.leftoverSaveCta,
                  icon: AppIcons.check,
                  loading: _busy,
                  onPressed: _busy ? null : _save,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _RoundStepBtn extends StatelessWidget {
  const _RoundStepBtn({required this.icon, this.onTap});

  final IconData icon;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    return Material(
      color: cs.surfaceContainerLowest,
      shape: const CircleBorder(),
      child: InkWell(
        customBorder: const CircleBorder(),
        onTap: onTap == null
            ? null
            : () {
                AppHaptics.selection();
                onTap!();
              },
        child: SizedBox(
          width: 30,
          height: 30,
          child: Icon(
            icon,
            size: 15,
            color: onTap != null ? cs.primary : context.sweep.textTertiary,
          ),
        ),
      ),
    );
  }
}
