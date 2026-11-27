import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// Applies consistent light-icon status bar + themed navigation bar chrome
/// for every Concept B screen that opens with a deep emerald hero header.
class EmeraldSystemOverlay extends StatelessWidget {
  const EmeraldSystemOverlay({required this.child, super.key});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.light,
        statusBarBrightness: Brightness.dark,
        systemNavigationBarColor: cs.surfaceContainerLowest,
        systemNavigationBarIconBrightness:
            Theme.of(context).brightness == Brightness.dark
            ? Brightness.light
            : Brightness.dark,
      ),
      child: child,
    );
  }
}

/// Concept B shared deep-emerald split header with optional back button,
/// title + subtitle, trailing action pill/button, optional bottom slot
/// (segmented tabs or onboarding progress bar), and a rising 26dp rounded sheet.
class EmeraldSplitHeader extends StatelessWidget {
  const EmeraldSplitHeader({
    required this.title,
    this.subtitle,
    this.trailing,
    this.bottom,
    this.showBack = true,
    this.onBack,
    this.sheetColor,
    super.key,
  });

  final String title;
  final String? subtitle;
  final Widget? trailing;
  final Widget? bottom;
  final bool showBack;
  final VoidCallback? onBack;
  final Color? sheetColor;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final cs = context.colors;
    final canPop = showBack && Navigator.of(context).canPop();

    return DecoratedBox(
      decoration: BoxDecoration(color: sweep.heroSurface),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          SafeArea(
            bottom: false,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(
                Gap.lg,
                Gap.sm,
                Gap.lg,
                Gap.md,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    children: [
                      if (canPop) ...[
                        EmeraldHeaderIconButton(
                          icon: AppIcons.arrowLeft,
                          tooltip: MaterialLocalizations.of(
                            context,
                          ).backButtonTooltip,
                          onTap: onBack ?? () => Navigator.of(context).maybePop(),
                        ),
                        const SizedBox(width: Gap.sm + 2),
                      ],
                      Expanded(
                        child: Text(
                          title,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: context.text.titleLarge?.copyWith(
                            color: sweep.onHeroSurface,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                      if (trailing != null) ...[
                        const SizedBox(width: Gap.xs),
                        trailing!,
                      ],
                    ],
                  ),
                  if (subtitle != null && subtitle!.trim().isNotEmpty) ...[
                    const SizedBox(height: Gap.xs + 2),
                    Text(
                      subtitle!,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: context.text.bodySmall?.copyWith(
                        color: sweep.onHeroMuted,
                        height: 1.35,
                      ),
                    ),
                  ],
                  if (bottom != null) ...[
                    const SizedBox(height: Gap.sm + 2),
                    bottom!,
                  ],
                ],
              ),
            ),
          ),
          Container(
            height: 20,
            decoration: BoxDecoration(
              color: sheetColor ?? cs.surface,
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(26),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// 44dp rounded translucent icon button designed for [EmeraldSplitHeader].
class EmeraldHeaderIconButton extends StatelessWidget {
  const EmeraldHeaderIconButton({
    required this.icon,
    required this.onTap,
    this.tooltip,
    super.key,
  });

  final IconData icon;
  final VoidCallback onTap;
  final String? tooltip;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final btn = Material(
      color: sweep.heroSurfaceElevated,
      shape: RoundedRectangleBorder(
        borderRadius: Radii.brMd,
        side: BorderSide(color: sweep.onHeroSurface.withValues(alpha: 0.16)),
      ),
      child: InkWell(
        borderRadius: Radii.brMd,
        onTap: () {
          AppHaptics.selection();
          onTap();
        },
        child: SizedBox(
          width: 44,
          height: 44,
          child: Icon(icon, size: 19, color: sweep.onHeroSurface),
        ),
      ),
    );
    return tooltip != null ? Tooltip(message: tooltip, child: btn) : btn;
  }
}

/// High-contrast pill button/badge for [EmeraldSplitHeader.trailing].
class EmeraldHeaderPill extends StatelessWidget {
  const EmeraldHeaderPill({
    required this.label,
    this.icon,
    this.onTap,
    super.key,
  });

  final String label;
  final IconData? icon;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final content = Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 15, color: sweep.onHeroSurface),
            const SizedBox(width: 5),
          ],
          Text(
            label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: context.text.labelMedium?.copyWith(
              color: sweep.onHeroSurface,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );

    return Material(
      color: sweep.heroSurfaceElevated,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(Radii.pill),
        side: BorderSide(color: sweep.onHeroSurface.withValues(alpha: 0.18)),
      ),
      child: onTap != null
          ? InkWell(
              borderRadius: BorderRadius.circular(Radii.pill),
              onTap: () {
                AppHaptics.selection();
                onTap!();
              },
              child: content,
            )
          : content,
    );
  }
}
