import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

enum AppDialogTone { neutral, primary, warm, danger }

/// Clean centered SweepFood Dialog inspired by minimal editorial split-action
/// modals: top centered icon badge + bold title + clean body/form + edge-to-edge
/// 1px hairline divider splitting equal action cells at the bottom.
class AppDialog extends StatelessWidget {
  const AppDialog({
    required this.title,
    this.message,
    this.content,
    this.icon,
    this.tone = AppDialogTone.neutral,
    this.cancelLabel,
    this.confirmLabel,
    this.onCancel,
    this.onConfirm,
    this.loading = false,
    this.confirmAccentColor,
    super.key,
  });

  final String title;
  final String? message;
  final Widget? content;
  final IconData? icon;
  final AppDialogTone tone;
  final String? cancelLabel;
  final String? confirmLabel;
  final VoidCallback? onCancel;
  final VoidCallback? onConfirm;
  final bool loading;
  final Color? confirmAccentColor;

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    final sweep = context.sweep;

    final (Color badgeBg, Color badgeFg, Color defaultAccent) = switch (tone) {
      AppDialogTone.neutral => (
        sweep.subtleFill,
        sweep.textSecondary,
        sweep.ctaWarm,
      ),
      AppDialogTone.primary => (
        cs.primaryContainer,
        cs.primary,
        cs.primary,
      ),
      AppDialogTone.warm => (
        sweep.culinaryAccentBg,
        sweep.ctaWarm,
        sweep.ctaWarm,
      ),
      AppDialogTone.danger => (
        sweep.expired.bg,
        sweep.expired.fg,
        sweep.ctaWarm,
      ),
    };

    final accentColor = confirmAccentColor ?? defaultAccent;
    final hasCancel = cancelLabel != null;
    final hasConfirm = confirmLabel != null;

    return Dialog(
      backgroundColor: cs.surfaceContainerLowest,
      surfaceTintColor: Colors.transparent,
      elevation: 0,
      insetPadding: const EdgeInsets.symmetric(horizontal: 32, vertical: 24),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(18),
        side: BorderSide(color: sweep.hairline),
      ),
      clipBehavior: Clip.antiAlias,
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 340),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Flexible(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(
                  Gap.lg,
                  Gap.lg + 4,
                  Gap.lg,
                  Gap.lg,
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    if (icon != null) ...[
                      Center(
                        child: Container(
                          width: 48,
                          height: 48,
                          decoration: BoxDecoration(
                            color: badgeBg,
                            shape: BoxShape.circle,
                          ),
                          child: Icon(icon, size: 22, color: badgeFg),
                        ),
                      ),
                      const SizedBox(height: Gap.md),
                    ],
                    Text(
                      title,
                      textAlign: TextAlign.center,
                      style: context.text.titleMedium?.copyWith(
                        fontWeight: FontWeight.w800,
                        letterSpacing: -0.1,
                      ),
                    ),
                    if (message != null) ...[
                      const SizedBox(height: Gap.xs + 2),
                      Text(
                        message!,
                        textAlign: TextAlign.center,
                        style: context.text.bodyMedium?.copyWith(
                          color: sweep.textSecondary,
                          height: 1.45,
                        ),
                      ),
                    ],
                    if (content != null) ...[
                      const SizedBox(height: Gap.md),
                      content!,
                    ],
                  ],
                ),
              ),
            ),
            if (hasCancel || hasConfirm) ...[
              Divider(height: 1, thickness: 1, color: sweep.hairline),
              IntrinsicHeight(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    if (hasCancel)
                      Expanded(
                        child: _DialogActionCell(
                          label: cancelLabel!,
                          color: sweep.textSecondary,
                          fontWeight: FontWeight.w700,
                          onTap: loading
                              ? null
                              : (onCancel ?? () => Navigator.of(context).pop()),
                        ),
                      ),
                    if (hasCancel && hasConfirm)
                      VerticalDivider(
                        width: 1,
                        thickness: 1,
                        color: sweep.hairline,
                      ),
                    if (hasConfirm)
                      Expanded(
                        child: _DialogActionCell(
                          label: confirmLabel!,
                          color: accentColor,
                          fontWeight: FontWeight.w800,
                          loading: loading,
                          onTap: loading ? null : onConfirm,
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _DialogActionCell extends StatelessWidget {
  const _DialogActionCell({
    required this.label,
    required this.color,
    required this.fontWeight,
    this.onTap,
    this.loading = false,
  });

  final String label;
  final Color color;
  final FontWeight fontWeight;
  final VoidCallback? onTap;
  final bool loading;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap == null
          ? null
          : () {
              AppHaptics.selection();
              onTap!();
            },
      child: ConstrainedBox(
        constraints: const BoxConstraints(minHeight: 52),
        child: Center(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: Gap.sm),
            child: loading
                ? SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(
                      strokeWidth: 2.2,
                      color: color,
                    ),
                  )
                : Text(
                    label,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: context.text.labelLarge?.copyWith(
                      color: onTap == null
                          ? color.withValues(alpha: 0.45)
                          : color,
                      fontWeight: fontWeight,
                      letterSpacing: 0.2,
                    ),
                  ),
          ),
        ),
      ),
    );
  }
}

/// Convenience helper for yes/no confirmation dialogs using [AppDialog].
Future<bool?> showAppConfirmDialog(
  BuildContext context, {
  required String title,
  required String message,
  required String confirmLabel,
  String? cancelLabel,
  IconData? icon,
  AppDialogTone tone = AppDialogTone.danger,
  bool destructive = false,
}) {
  final l10n = context.l10n;
  return showDialog<bool>(
    context: context,
    builder: (ctx) => AppDialog(
      icon: icon,
      tone: tone,
      title: title,
      message: message,
      cancelLabel: cancelLabel ?? l10n.commonCancel,
      confirmLabel: confirmLabel,
      confirmAccentColor: destructive ? ctx.colors.error : ctx.colors.primary,
      onCancel: () => Navigator.of(ctx).pop(false),
      onConfirm: () => Navigator.of(ctx).pop(true),
    ),
  );
}
