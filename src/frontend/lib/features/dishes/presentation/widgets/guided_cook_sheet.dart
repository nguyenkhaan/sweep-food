import 'dart:async';

import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/features/dishes/domain/entities/cooking_step.dart';

/// Interactive step-by-step cook mode sheet with an optional per-step timer.
class GuidedCookSheet extends StatefulWidget {
  const GuidedCookSheet({
    required this.dishName,
    required this.steps,
    this.onFinishCooking,
    super.key,
  });

  final String dishName;
  final List<CookingStep> steps;
  final VoidCallback? onFinishCooking;

  static Future<void> show(
    BuildContext context, {
    required String dishName,
    required List<CookingStep> steps,
    VoidCallback? onFinishCooking,
  }) => showAppBottomSheet<void>(
    context,
    builder: (_) => GuidedCookSheet(
      dishName: dishName,
      steps: steps,
      onFinishCooking: onFinishCooking,
    ),
  );

  @override
  State<GuidedCookSheet> createState() => _GuidedCookSheetState();
}

class _GuidedCookSheetState extends State<GuidedCookSheet> {
  int _index = 0;
  Timer? _timer;
  int? _remainingSeconds;
  bool _running = false;

  CookingStep get _current => widget.steps[_index];

  @override
  void initState() {
    super.initState();
    _syncTimerToStep();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _syncTimerToStep() {
    _timer?.cancel();
    _running = false;
    final mins = _current.durationMin;
    _remainingSeconds = mins != null && mins > 0 ? mins * 60 : null;
  }

  void _toggleTimer() {
    if (_remainingSeconds == null) return;
    AppHaptics.selection();
    if (_running) {
      _timer?.cancel();
      setState(() => _running = false);
      return;
    }
    if (_remainingSeconds == 0) {
      _syncTimerToStep();
    }
    setState(() => _running = true);
    _timer = Timer.periodic(const Duration(seconds: 1), (t) {
      if (!mounted) {
        t.cancel();
        return;
      }
      if ((_remainingSeconds ?? 0) <= 1) {
        t.cancel();
        AppHaptics.success();
        setState(() {
          _remainingSeconds = 0;
          _running = false;
        });
      } else {
        setState(() => _remainingSeconds = _remainingSeconds! - 1);
      }
    });
  }

  void _goTo(int nextIndex) {
    AppHaptics.selection();
    setState(() {
      _index = nextIndex.clamp(0, widget.steps.length - 1);
      _syncTimerToStep();
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final total = widget.steps.length;
    final progress = total == 0 ? 1.0 : (_index + 1) / total;
    final isLast = _index >= total - 1;
    final mins = _current.durationMin;
    final rem = _remainingSeconds;

    return SheetBody(
      icon: AppIcons.cook,
      warmIcon: true,
      title: widget.dishName,
      subtitle: l10n.dishStepOf(_index + 1, total),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(Radii.pill),
            child: TweenAnimationBuilder<double>(
              tween: Tween(begin: 0, end: progress),
              duration: AppMotion.resolve(context, context.motion.medium),
              curve: AppMotion.resolveCurve(context, context.motion.enterCurve),
              builder: (_, val, __) => LinearProgressIndicator(
                value: val,
                minHeight: 6,
                backgroundColor: sweep.subtleFill,
                valueColor: AlwaysStoppedAnimation(context.colors.primary),
              ),
            ),
          ),
          Gap.gapMd,
          SheetGroupCard(
            padding: const EdgeInsets.all(Gap.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: Gap.sm + 2,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: sweep.heroSurface,
                    borderRadius: BorderRadius.circular(Radii.pill),
                  ),
                  child: Text(
                    l10n.dishStepOf(_index + 1, total),
                    style: context.text.labelSmall?.copyWith(
                      letterSpacing: 0,
                      color: sweep.onHeroSurface,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
                Gap.gapSm,
                Text(
                  _current.text,
                  style: context.text.bodyLarge?.copyWith(height: 1.5),
                ),
                if (mins != null && mins > 0 && rem != null) ...[
                  Gap.gapMd,
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: Gap.sm + 4,
                      vertical: Gap.sm,
                    ),
                    decoration: BoxDecoration(
                      color: rem == 0 ? sweep.successBg : sweep.subtleFill,
                      borderRadius: Radii.brLg,
                      border: Border.all(
                        color: rem == 0 ? sweep.successFg : sweep.hairline,
                      ),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          rem == 0 ? AppIcons.checkCircle : AppIcons.timer,
                          size: 18,
                          color: rem == 0
                              ? sweep.successFg
                              : sweep.ctaWarm,
                        ),
                        const SizedBox(width: Gap.xs + 2),
                        Expanded(
                          child: Text(
                            rem == 0 ? l10n.dishTimerDone : _formatClock(rem),
                            style: AppTypography.tabular(
                              context.text.titleMedium?.copyWith(
                                fontWeight: FontWeight.w800,
                                color: rem == 0
                                    ? sweep.successFg
                                    : context.colors.onSurface,
                              ),
                            ),
                          ),
                        ),
                        FilledButton.tonal(
                          onPressed: _toggleTimer,
                          style: FilledButton.styleFrom(
                            minimumSize: const Size(80, 38),
                            padding: const EdgeInsets.symmetric(
                              horizontal: Gap.md,
                            ),
                            shape: const RoundedRectangleBorder(
                              borderRadius: Radii.brMd,
                            ),
                          ),
                          child: Text(
                            _running
                                ? l10n.dishTimerPause
                                : (rem < mins * 60 && rem > 0
                                      ? l10n.dishTimerResume
                                      : l10n.dishTimerStart(mins)),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
          Gap.gapMd,
          Row(
            children: [
              Expanded(
                flex: 4,
                child: SheetCancelButton(
                  icon: AppIcons.chevronLeft,
                  label: l10n.dishPrevStep,
                  onPressed: _index > 0 ? () => _goTo(_index - 1) : null,
                ),
              ),
              const SizedBox(width: Gap.sm),
              Expanded(
                flex: 6,
                child: SheetWarmButton(
                  icon: isLast ? AppIcons.check : AppIcons.chevronRight,
                  label: isLast ? l10n.dishFinishCooking : l10n.dishNextStep,
                  onPressed: isLast
                      ? () {
                          AppHaptics.medium();
                          Navigator.of(context).pop();
                          widget.onFinishCooking?.call();
                        }
                      : () => _goTo(_index + 1),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  static String _formatClock(int totalSeconds) {
    final m = totalSeconds ~/ 60;
    final s = totalSeconds % 60;
    final mm = m.toString().padLeft(2, '0');
    final ss = s.toString().padLeft(2, '0');
    return '$mm:$ss';
  }
}
