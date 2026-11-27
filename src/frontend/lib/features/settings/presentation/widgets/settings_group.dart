import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// A labelled card of [SettingsRow]s — the building block of the Cài đặt screens.
class SettingsGroup extends StatelessWidget {
  const SettingsGroup({required this.rows, this.label, super.key});

  final String? label;
  final List<SettingsRow> rows;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final cs = context.colors;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (label != null) ...[
          Padding(
            padding: const EdgeInsets.only(left: 2, bottom: Gap.xs + 2),
            child: Text(
              label!.toUpperCase(),
              style: context.text.labelSmall?.copyWith(
                letterSpacing: 0.7,
                fontWeight: FontWeight.w800,
                color: sweep.textTertiary,
              ),
            ),
          ),
        ],
        Material(
          color: cs.surfaceContainerLowest,
          shape: RoundedRectangleBorder(
            borderRadius: Radii.brXl,
            side: BorderSide(color: sweep.hairline),
          ),
          clipBehavior: Clip.antiAlias,
          child: Column(
            children: [
              for (var i = 0; i < rows.length; i++) ...[
                if (i > 0)
                  Divider(height: 1, color: sweep.hairline, indent: 56),
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

  /// Right-aligned muted value text (e.g. "Tiếng Việt").
  final String? trailing;

  /// A pill (e.g. "2 bộ lọc").
  final String? badge;
  final bool danger;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    final sweep = context.sweep;
    final textFg = danger ? cs.error : cs.onSurface;
    final iconBg = danger ? cs.errorContainer : cs.primaryContainer;
    final iconFg = danger ? cs.error : cs.primary;

    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: Gap.md,
          vertical: Gap.sm + 3,
        ),
        child: LayoutBuilder(
          builder: (context, constraints) {
            final maxTrailing = constraints.maxWidth * 0.44;
            return Row(
              children: [
                Container(
                  width: 32,
                  height: 32,
                  decoration: BoxDecoration(
                    color: iconBg,
                    borderRadius: Radii.brSm,
                  ),
                  child: Icon(icon, size: 16, color: iconFg),
                ),
                const SizedBox(width: Gap.sm + 2),
                Expanded(
                  child: Text(
                    label,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: context.text.bodyMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                      color: textFg,
                    ),
                  ),
                ),
                if (trailing != null) ...[
                  const SizedBox(width: Gap.xs),
                  ConstrainedBox(
                    constraints: BoxConstraints(maxWidth: maxTrailing),
                    child: Text(
                      trailing!,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.end,
                      style: context.text.bodySmall?.copyWith(
                        color: sweep.textTertiary,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
                if (badge != null) ...[
                  const SizedBox(width: Gap.xs),
                  ConstrainedBox(
                    constraints: BoxConstraints(maxWidth: maxTrailing),
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: cs.primaryContainer,
                        borderRadius: BorderRadius.circular(Radii.pill),
                      ),
                      child: Text(
                        badge!,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: context.text.labelSmall?.copyWith(
                          color: cs.onPrimaryContainer,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ),
                ],
                if (onTap != null && !danger) ...[
                  const SizedBox(width: Gap.xs),
                  Icon(
                    AppIcons.chevronRight,
                    size: 16,
                    color: sweep.textTertiary,
                  ),
                ],
              ],
            );
          },
        ),
      ),
    );
  }
}
