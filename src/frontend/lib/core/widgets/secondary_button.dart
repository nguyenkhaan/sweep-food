import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_motion.dart';

/// Lower-emphasis outlined action paired next to a [PrimaryButton].
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
    final handler = onPressed == null
        ? null
        : () {
            AppHaptics.selection();
            onPressed!();
          };
    final button = icon != null
        ? OutlinedButton.icon(
            onPressed: handler,
            icon: Icon(icon, size: 18),
            label: Text(label),
          )
        : OutlinedButton(onPressed: handler, child: Text(label));
    return expand ? SizedBox(width: double.infinity, child: button) : button;
  }
}
