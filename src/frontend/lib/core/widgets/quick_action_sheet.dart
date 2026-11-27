import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';

/// One row in a [QuickActionSheet].
class QuickAction {
  const QuickAction({
    required this.label,
    required this.onTap,
    this.icon,
    this.subtitle,
    this.recommended = false,
  });

  final String label;
  final String? subtitle;
  final IconData? icon;
  final bool recommended;
  final VoidCallback onTap;
}

/// Bottom sheet with a Format 1 header and grouped tactile action rows.
class QuickActionSheet extends StatelessWidget {
  const QuickActionSheet({
    required this.title,
    required this.actions,
    this.subtitle,
    this.icon,
    super.key,
  });

  final String title;
  final String? subtitle;
  final IconData? icon;
  final List<QuickAction> actions;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    return SheetBody(
      icon: icon,
      title: title,
      subtitle: subtitle,
      child: SheetGroupCard(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            for (var i = 0; i < actions.length; i++) ...[
              if (i > 0) Divider(height: 1, color: sweep.hairline),
              _QuickActionRow(action: actions[i]),
            ],
          ],
        ),
      ),
    );
  }
}

class _QuickActionRow extends StatelessWidget {
  const _QuickActionRow({required this.action});

  final QuickAction action;

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    final sweep = context.sweep;
    final bg = action.recommended
        ? Color.alphaBlend(
            cs.primaryContainer.withValues(alpha: 0.3),
            cs.surfaceContainerLowest,
          )
        : Colors.transparent;

    return Material(
      color: bg,
      child: InkWell(
        onTap: () {
          AppHaptics.selection();
          Navigator.of(context).pop();
          action.onTap();
        },
        child: Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: Gap.md,
            vertical: Gap.sm + 4,
          ),
          child: Row(
            children: [
              if (action.icon != null) ...[
                Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(
                    color: cs.primaryContainer,
                    borderRadius: Radii.brMd,
                  ),
                  child: Icon(action.icon, size: 18, color: cs.primary),
                ),
                const SizedBox(width: Gap.sm + 2),
              ],
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Flexible(
                          child: Text(
                            action.label,
                            style: context.text.titleSmall?.copyWith(
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                        if (action.recommended) ...[
                          const SizedBox(width: 6),
                          const _RecommendedTag(),
                        ],
                      ],
                    ),
                    if (action.subtitle != null) ...[
                      const SizedBox(height: 2),
                      Text(
                        action.subtitle!,
                        style: context.text.bodySmall?.copyWith(
                          color: sweep.textSecondary,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(width: Gap.xs),
              Icon(
                AppIcons.chevronRight,
                size: 17,
                color: sweep.textTertiary,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _RecommendedTag extends StatelessWidget {
  const _RecommendedTag();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: context.colors.primaryContainer,
        borderRadius: BorderRadius.circular(Radii.pill),
      ),
      child: Text(
        context.l10n.commonRecommended,
        style: context.text.labelSmall?.copyWith(
          letterSpacing: 0,
          color: context.colors.primary,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }
}
