import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/app_bottom_sheet.dart';

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

/// Bottom sheet with a title and a short list of tappable actions
/// (D-03 "Bạn đã nấu…", T-02 helpers, etc.).
class QuickActionSheet extends StatelessWidget {
  const QuickActionSheet({
    required this.title,
    required this.actions,
    this.subtitle,
    super.key,
  });

  final String title;
  final String? subtitle;
  final List<QuickAction> actions;

  @override
  Widget build(BuildContext context) {
    return SheetBody(
      title: title,
      subtitle: subtitle,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          for (final a in actions)
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: a.icon != null
                  ? Container(
                      width: 34,
                      height: 34,
                      decoration: BoxDecoration(
                        color: context.colors.primaryContainer,
                        borderRadius: Radii.brSm,
                      ),
                      child: Icon(a.icon, size: 17, color: context.colors.primary),
                    )
                  : null,
              title: Row(
                children: [
                  Flexible(child: Text(a.label, style: context.text.titleSmall)),
                  if (a.recommended) ...[
                    const SizedBox(width: 6),
                    _RecommendedTag(),
                  ],
                ],
              ),
              subtitle: a.subtitle != null ? Text(a.subtitle!) : null,
              trailing: const Icon(Icons.chevron_right_rounded),
              onTap: () {
                Navigator.of(context).pop();
                a.onTap();
              },
            ),
        ],
      ),
    );
  }
}

class _RecommendedTag extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
      decoration: BoxDecoration(
        color: context.colors.primaryContainer,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        'Gợi ý',
        style: context.text.labelSmall?.copyWith(
          letterSpacing: 0,
          color: context.colors.primary,
        ),
      ),
    );
  }
}
