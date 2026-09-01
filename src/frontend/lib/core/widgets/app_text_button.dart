import 'package:flutter/material.dart';

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
      onPressed: onPressed,
      style: TextButton.styleFrom(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        minimumSize: Size.zero,
        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(label),
          if (trailingChevron) const Icon(Icons.chevron_right_rounded, size: 16),
        ],
      ),
    );
  }
}
