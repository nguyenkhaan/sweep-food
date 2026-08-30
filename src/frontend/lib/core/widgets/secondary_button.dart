import 'package:flutter/material.dart';

/// Tonal / lower-emphasis action. Outlined in the design; use next to a
/// [PrimaryButton] (e.g. "Hủy" / "Xong").
class SecondaryButton extends StatelessWidget {
  const SecondaryButton({
    required this.label,
    required this.onPressed,
    this.icon,
    this.expand = true,
    super.key,
  });

  final String label;
  final VoidCallback? onPressed;
  final IconData? icon;
  final bool expand;

  @override
  Widget build(BuildContext context) {
    final button = icon != null
        ? OutlinedButton.icon(
            onPressed: onPressed,
            icon: Icon(icon, size: 18),
            label: Text(label),
          )
        : OutlinedButton(onPressed: onPressed, child: Text(label));
    return expand ? SizedBox(width: double.infinity, child: button) : button;
  }
}
