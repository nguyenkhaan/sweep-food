import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// Square, bordered icon button used in top bars (filter, sort, share…).
class AppIconButton extends StatelessWidget {
  const AppIconButton({
    required this.icon,
    required this.onPressed,
    this.tooltip,
    this.badge = false,
    this.variant = AppIconButtonVariant.neutral,
    super.key,
  });

  final IconData icon;
  final VoidCallback? onPressed;
  final String? tooltip;
  final bool badge;
  final AppIconButtonVariant variant;

  @override
  Widget build(BuildContext context) {
    final (fg, bg, border) = switch (variant) {
      AppIconButtonVariant.neutral => (
          context.colors.onSurface,
          context.colors.surfaceContainerLowest,
          context.sweep.hairline,
        ),
      AppIconButtonVariant.brick => (
          context.sweep.expired.fg,
          context.sweep.expired.bg,
          Colors.transparent,
        ),
    };

    final button = Material(
      color: bg,
      shape: RoundedRectangleBorder(
        borderRadius: Radii.brMd,
        side: BorderSide(color: border),
      ),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onPressed,
        child: SizedBox(
          width: 38,
          height: 38,
          child: Icon(icon, size: 18, color: fg),
        ),
      ),
    );

    final withBadge = badge
        ? Badge(
            smallSize: 7,
            backgroundColor: context.sweep.critical.fg,
            child: button,
          )
        : button;

    return tooltip != null
        ? Tooltip(message: tooltip!, child: withBadge)
        : withBadge;
  }
}

enum AppIconButtonVariant { neutral, brick }
