import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';

/// A labelled card of [SettingsRow]s — the building block of the Cài đặt screens.
class SettingsGroup extends StatelessWidget {
  const SettingsGroup({required this.rows, this.label, super.key});

  final String? label;
  final List<SettingsRow> rows;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (label != null) ...[
          Padding(
            padding: const EdgeInsets.only(left: Gap.xxs, bottom: Gap.xs),
            child: Text(label!.toUpperCase(), style: context.text.labelSmall),
          ),
        ],
        Container(
          decoration: BoxDecoration(
            color: context.colors.surfaceContainerLowest,
            borderRadius: Radii.brLg,
            border: Border.all(color: context.sweep.hairline),
          ),
          child: Column(
            children: [
              for (var i = 0; i < rows.length; i++) ...[
                if (i > 0)
                  Divider(height: 1, color: context.sweep.hairline, indent: 52),
                rows[i],
              ],
            ],
          ),
        ),
      ],
    );
  }
}

/// One tappable row inside a [SettingsGroup].
class SettingsRow extends StatelessWidget {
  const SettingsRow({
    required this.icon,
    required this.label,
    this.trailing,
    this.badge,
    this.danger = false,
    this.onTap,
    super.key,
  });

  final IconData icon;
  final String label;

  /// Right-aligned grey value text (e.g. "Tiếng Việt").
  final String? trailing;

  /// A pill (e.g. "Sắp có").
  final String? badge;
  final bool danger;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final fg = danger ? context.colors.error : context.colors.onSurface;
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: Gap.md,
          vertical: Gap.sm + 1,
        ),
        child: Row(
          children: [
            Container(
              width: 30,
              height: 30,
              decoration: BoxDecoration(
                color: danger
                    ? context.colors.errorContainer
                    : context.sweep.subtleFill,
                borderRadius: Radii.brSm,
              ),
              child: Icon(icon, size: 17, color: fg),
            ),
            Gap.gapSm,
            Expanded(
              child: Text(
                label,
                style: context.text.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: fg,
                ),
              ),
            ),
            if (trailing != null)
              Text(
                trailing!,
                style: context.text.bodySmall?.copyWith(
                  color: context.sweep.textTertiary,
                ),
              ),
            if (badge != null)
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: context.colors.primaryContainer,
                  borderRadius: Radii.pill.toBorderRadius(),
                ),
                child: Text(
                  badge!,
                  style: context.text.labelSmall?.copyWith(
                    color: context.colors.onPrimaryContainer,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            if (onTap != null && !danger) ...[
              const SizedBox(width: Gap.xs),
              Icon(
                Icons.chevron_right_rounded,
                size: 18,
                color: context.sweep.textTertiary,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

extension on double {
  BorderRadius toBorderRadius() => BorderRadius.circular(this);
}
