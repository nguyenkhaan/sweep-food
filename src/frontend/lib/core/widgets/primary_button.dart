import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// Filled primary action button with tactile haptic feedback and theme-matched
/// loading spinner.
class PrimaryButton extends StatelessWidget {
  const PrimaryButton({
    required this.label,
    required this.onPressed,
    this.icon,
    this.loading = false,
    this.expand = true,
    super.key,
  });

  final String label;
  final VoidCallback? onPressed;
  final IconData? icon;
  final bool loading;
  final bool expand;

  @override
  Widget build(BuildContext context) {
    final child = loading
        ? SizedBox(
            width: 20,
            height: 20,
            child: CircularProgressIndicator(
              strokeWidth: 2.4,
              color: context.colors.onPrimary,
            ),
          )
        : Text(label);

    final handler = loading || onPressed == null
        ? null
        : () {
            AppHaptics.light();
            onPressed!();
          };

    final button = icon != null && !loading
        ? FilledButton.icon(
            onPressed: handler,
            icon: Icon(icon, size: 18),
            label: child,
          )
        : FilledButton(onPressed: handler, child: child);

    return expand ? SizedBox(width: double.infinity, child: button) : button;
  }
}
