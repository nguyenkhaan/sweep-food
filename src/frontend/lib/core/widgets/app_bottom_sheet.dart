import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// Opens a Concept B Format 1 modal bottom sheet (transparent route barrier so
/// [SheetBody] draws the crisp 28px surface, drag pill, and safe-area padding).
Future<T?> showAppBottomSheet<T>(
  BuildContext context, {
  required WidgetBuilder builder,
  bool isScrollControlled = true,
  bool useRootNavigator = true,
}) {
  return showModalBottomSheet<T>(
    context: context,
    barrierLabel: 'Đóng bảng thao tác',
    isScrollControlled: isScrollControlled,
    useRootNavigator: useRootNavigator,
    useSafeArea: true,
    showDragHandle: false,
    backgroundColor: Colors.transparent,
    builder: (ctx) => Padding(
      padding: EdgeInsets.only(bottom: MediaQuery.viewInsetsOf(ctx).bottom),
      child: builder(ctx),
    ),
  );
}

/// Concept B · Format 1 Bottom Sheet shell:
/// Crisp rounded top surface + centered drag pill + optional icon-badged header
/// with circular close button + 1px hairline divider + padded body.
class SheetBody extends StatelessWidget {
  const SheetBody({
    required this.child,
    this.title,
    this.subtitle,
    this.icon,
    this.iconBg,
    this.iconFg,
    this.warmIcon = false,
    this.trailing,
    this.showCloseButton = true,
    this.headerDivider = true,
    this.expandChild = false,
    super.key,
  });

  final Widget child;
  final String? title;
  final String? subtitle;
  final IconData? icon;
  final Color? iconBg;
  final Color? iconFg;
  final bool warmIcon;
  final Widget? trailing;
  final bool showCloseButton;
  final bool headerDivider;

  /// Set `true` when [child] needs to fill the remaining height of a bounded
  /// container (e.g. a `FractionallySizedBox` wrapping a scrollable form).
  final bool expandChild;

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    final sweep = context.sweep;
    final hasHeader =
        title != null || subtitle != null || icon != null || trailing != null;

    final resolvedIconBg =
        iconBg ?? (warmIcon ? sweep.culinaryAccentBg : cs.primaryContainer);
    final resolvedIconFg =
        iconFg ?? (warmIcon ? sweep.ctaWarm : cs.primary);

    return DecoratedBox(
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: Radii.brSheet,
        boxShadow: Shadows.e3,
      ),
      child: SafeArea(
        top: false,
        child: Column(
          mainAxisSize: expandChild ? MainAxisSize.max : MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Centered grab handle
            Padding(
              padding: const EdgeInsets.only(top: 10, bottom: 4),
              child: Center(
                child: Container(
                  width: 38,
                  height: 4,
                  decoration: BoxDecoration(
                    color: sweep.hairline,
                    borderRadius: BorderRadius.circular(Radii.pill),
                  ),
                ),
              ),
            ),

            if (hasHeader) ...[
              Padding(
                padding: const EdgeInsets.fromLTRB(
                  Gap.lg,
                  Gap.xs + 2,
                  Gap.lg,
                  Gap.sm + 4,
                ),
                child: Row(
                  children: [
                    if (icon != null) ...[
                      Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          color: resolvedIconBg,
                          borderRadius: Radii.brMd,
                        ),
                        child: Icon(icon, size: 19, color: resolvedIconFg),
                      ),
                      const SizedBox(width: Gap.sm + 2),
                    ],
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          if (title != null)
                            Text(
                              title!,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              style: context.text.titleMedium?.copyWith(
                                fontWeight: FontWeight.w800,
                                height: 1.2,
                              ),
                            ),
                          if (subtitle != null) ...[
                            const SizedBox(height: 2),
                            Text(
                              subtitle!,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              style: context.text.bodySmall?.copyWith(
                                color: sweep.textSecondary,
                                height: 1.35,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                    if (trailing != null) ...[
                      const SizedBox(width: Gap.xs),
                      trailing!,
                    ],
                    if (showCloseButton) ...[
                      const SizedBox(width: Gap.xs),
                      Tooltip(
                        message: 'Đóng',
                        child: Material(
                          color: cs.surfaceContainerLowest,
                          shape: RoundedRectangleBorder(
                            borderRadius: Radii.brSm,
                            side: BorderSide(color: sweep.hairline),
                          ),
                          child: InkWell(
                            borderRadius: Radii.brSm,
                            onTap: () {
                              AppHaptics.selection();
                              Navigator.of(context).maybePop();
                            },
                            child: SizedBox(
                              width: 34,
                              height: 34,
                              child: Icon(
                                AppIcons.close,
                                size: 16,
                                color: sweep.textSecondary,
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              if (headerDivider) Divider(height: 1, color: sweep.hairline),
            ],

            if (expandChild)
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(
                    Gap.lg,
                    Gap.md,
                    Gap.lg,
                    Gap.lg,
                  ),
                  child: child,
                ),
              )
            else
              Flexible(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(
                    Gap.lg,
                    Gap.md,
                    Gap.lg,
                    Gap.lg,
                  ),
                  child: child,
                ),
              ),
          ],
        ),
      ),
    );
  }
}

/// Elevated Concept B grouped card container used inside Format 1 sheets.
class SheetGroupCard extends StatelessWidget {
  const SheetGroupCard({
    required this.child,
    this.padding,
    super.key,
  });

  final Widget child;
  final EdgeInsetsGeometry? padding;

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    final sweep = context.sweep;
    return Material(
      color: cs.surfaceContainerLowest,
      shape: RoundedRectangleBorder(
        borderRadius: Radii.brXl,
        side: BorderSide(color: sweep.hairline),
      ),
      clipBehavior: Clip.antiAlias,
      child: padding != null ? Padding(padding: padding!, child: child) : child,
    );
  }
}

/// Clean 2-tab pill segmented selector for Format 1 sheets.
class SheetSegmentedControl<T> extends StatelessWidget {
  const SheetSegmentedControl({
    required this.options,
    required this.selected,
    required this.onChanged,
    super.key,
  });

  final List<({T value, String label, IconData? icon})> options;
  final T selected;
  final ValueChanged<T> onChanged;

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    final sweep = context.sweep;

    return Container(
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: sweep.subtleFill,
        borderRadius: Radii.brLg,
      ),
      child: Row(
        children: [
          for (final opt in options)
            Expanded(
              child: GestureDetector(
                behavior: HitTestBehavior.opaque,
                onTap: () {
                  if (opt.value == selected) return;
                  AppHaptics.selection();
                  onChanged(opt.value);
                },
                child: AnimatedContainer(
                  duration: AppMotion.resolve(context, context.motion.fast),
                  curve: AppMotion.resolveCurve(
                    context,
                    context.motion.enterCurve,
                  ),
                  padding: const EdgeInsets.symmetric(
                    horizontal: Gap.sm,
                    vertical: 9,
                  ),
                  decoration: BoxDecoration(
                    color: opt.value == selected
                        ? cs.surfaceContainerLowest
                        : Colors.transparent,
                    borderRadius: Radii.brMd,
                    boxShadow: opt.value == selected ? Shadows.e1 : null,
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      if (opt.icon != null) ...[
                        Icon(
                          opt.icon,
                          size: 15,
                          color: opt.value == selected
                              ? cs.primary
                              : sweep.textSecondary,
                        ),
                        const SizedBox(width: 6),
                      ],
                      Flexible(
                        child: Text(
                          opt.label,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: context.text.labelMedium?.copyWith(
                            color: opt.value == selected
                                ? cs.primary
                                : sweep.textSecondary,
                            fontWeight: opt.value == selected
                                ? FontWeight.w800
                                : FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

/// Flat warm-orange primary CTA button (Concept B, zero glow) for sheets.
class SheetWarmButton extends StatelessWidget {
  const SheetWarmButton({
    required this.label,
    required this.onPressed,
    this.icon,
    this.loading = false,
    super.key,
  });

  final String label;
  final VoidCallback? onPressed;
  final IconData? icon;
  final bool loading;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final style = FilledButton.styleFrom(
      backgroundColor: sweep.ctaWarm,
      foregroundColor: sweep.onCtaWarm,
      elevation: 0,
      shadowColor: Colors.transparent,
      minimumSize: const Size(0, 48),
      shape: const RoundedRectangleBorder(borderRadius: Radii.brLg),
    );

    final spinner = SizedBox(
      width: 18,
      height: 18,
      child: CircularProgressIndicator(
        strokeWidth: 2.2,
        color: sweep.onCtaWarm,
      ),
    );

    if (icon != null && !loading) {
      return SizedBox(
        height: 48,
        child: FilledButton.icon(
          style: style,
          onPressed: onPressed,
          icon: Icon(icon, size: 18),
          label: Text(
            label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(fontWeight: FontWeight.w700),
          ),
        ),
      );
    }

    return SizedBox(
      height: 48,
      child: FilledButton(
        style: style,
        onPressed: loading ? null : onPressed,
        child: loading
            ? spinner
            : Text(
                label,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontWeight: FontWeight.w700),
              ),
      ),
    );
  }
}

/// Crisp hairline-bordered secondary button matching [SheetWarmButton] height.
class SheetCancelButton extends StatelessWidget {
  const SheetCancelButton({
    required this.label,
    required this.onPressed,
    this.icon,
    super.key,
  });

  final String label;
  final VoidCallback? onPressed;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final cs = context.colors;
    final style = OutlinedButton.styleFrom(
      foregroundColor: cs.onSurface,
      backgroundColor: cs.surfaceContainerLowest,
      side: BorderSide(color: sweep.hairline),
      minimumSize: const Size(0, 48),
      shape: const RoundedRectangleBorder(borderRadius: Radii.brLg),
    );

    if (icon != null) {
      return SizedBox(
        height: 48,
        child: OutlinedButton.icon(
          style: style,
          onPressed: onPressed,
          icon: Icon(icon, size: 17),
          label: Text(
            label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(fontWeight: FontWeight.w700),
          ),
        ),
      );
    }

    return SizedBox(
      height: 48,
      child: OutlinedButton(
        style: style,
        onPressed: onPressed,
        child: Text(
          label,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(fontWeight: FontWeight.w700),
        ),
      ),
    );
  }
}
