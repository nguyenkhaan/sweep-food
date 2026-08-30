import 'package:flutter/material.dart';

/// Filled primary action button. Sizing/shape come from the theme; adds a
/// loading spinner and an optional leading icon.
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
        ? const SizedBox(
            width: 20,
            height: 20,
            child: CircularProgressIndicator(strokeWidth: 2.4, color: Colors.white),
          )
        : Text(label);

    final button = icon != null && !loading
        ? FilledButton.icon(
            onPressed: loading ? null : onPressed,
            icon: Icon(icon, size: 18),
            label: child,
          )
        : FilledButton(onPressed: loading ? null : onPressed, child: child);

    return expand ? SizedBox(width: double.infinity, child: button) : button;
  }
}
