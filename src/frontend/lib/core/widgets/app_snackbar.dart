import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// Snackbar helpers with optional "Hoàn tác" (Undo) action and screen-reader-safe
/// auto-dismiss duration (`ui-states-and-feedback`).
abstract final class AppSnack {
  static void show(BuildContext context, String message) {
    final messenger = ScaffoldMessenger.of(context);
    final duration = MediaQuery.accessibleNavigationOf(context)
        ? const Duration(seconds: 20)
        : const Duration(seconds: 4);
    messenger
      ..clearSnackBars()
      ..showSnackBar(SnackBar(content: Text(message), duration: duration));
  }

  static void undoable(
    BuildContext context,
    String message, {
    required VoidCallback onUndo,
  }) {
    final messenger = ScaffoldMessenger.of(context);
    final duration = MediaQuery.accessibleNavigationOf(context)
        ? const Duration(seconds: 30)
        : const Duration(seconds: 5);
    messenger
      ..clearSnackBars()
      ..showSnackBar(
        SnackBar(
          content: Text(message),
          duration: duration,
          action: SnackBarAction(
            label: context.l10n.commonUndo,
            onPressed: () {
              AppHaptics.light();
              onUndo();
            },
          ),
        ),
      );
  }
}
