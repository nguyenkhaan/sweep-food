import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';

/// Low-emphasis inline action — "Xem tất cả", "Bỏ qua", footer links.
class AppTextButton extends StatelessWidget {
  const AppTextButton({
    required this.label,
    required this.onPressed,
    this.trailingChevron = false,
    super.key,
  });

  final String label;
  final VoidCallback? onPressed;
  final bool trailingChevron;

  @override
  Widget build(BuildContext context) {
    return TextButton(
      onPressed: onPressed == null
          ? null
          : () {
              AppHaptics.selection();
              onPressed!();
            },
      style: TextButton.styleFrom(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        minimumSize: Size.zero,
        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Flexible(child: Text(label, textAlign: TextAlign.center)),
          if (trailingChevron) ...[
            const SizedBox(width: 2),
            const Icon(AppIcons.chevronRight, size: 15),
          ],
        ],
      ),
    );
  }
}
