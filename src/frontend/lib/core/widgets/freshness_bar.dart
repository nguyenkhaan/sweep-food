import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/shared/domain/expiry_status.dart';

/// Slim visual freshness life-bar paired with [ExpiryBadge] on pantry cards.
///
/// Never communicates state by color alone — always accompanies explicit text
/// badges and exposes an accessible fraction via `Semantics`.
class FreshnessBar extends StatelessWidget {
  const FreshnessBar({
    required this.daysUntilExpiry,
    this.referenceDays,
    this.height = 3.5,
    super.key,
  });

  final int? daysUntilExpiry;
  final int? referenceDays;
  final double height;

  @override
  Widget build(BuildContext context) {
    final days = daysUntilExpiry;
    if (days == null) return const SizedBox.shrink();

    final level = Expiry.levelFromDays(days);
    final color = switch (level) {
      ExpiryLevel.expired => context.sweep.expired.fg,
      ExpiryLevel.critical => context.sweep.critical.fg,
      ExpiryLevel.soon => context.sweep.soon.fg,
      ExpiryLevel.ok => context.colors.primary,
    };

    final maxWindow = (referenceDays ?? 14).clamp(5, 30);
    final fraction = days <= 0 ? 0.08 : (days / maxWindow).clamp(0.14, 1.0);
    final duration = AppMotion.resolve(context, context.motion.medium);

    return ExcludeSemantics(
      child: ClipRRect(
        borderRadius: BorderRadius.circular(Radii.pill),
        child: SizedBox(
          height: height,
          width: double.infinity,
          child: ColoredBox(
            color: context.sweep.subtleFill,
            child: Align(
              alignment: AlignmentDirectional.centerStart,
              child: AnimatedFractionallySizedBox(
                duration: duration,
                curve: context.motion.enterCurve,
                widthFactor: fraction,
                heightFactor: 1,
                child: ColoredBox(color: color),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
