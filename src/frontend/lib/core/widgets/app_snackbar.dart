import 'package:flutter/material.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// Snackbar helpers with an optional "Hoàn tác" action (spec G-07).
abstract final class AppSnack {
  static void show(BuildContext context, String message) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(message)));
  }

  static void undoable(
    BuildContext context,
    String message, {
    required VoidCallback onUndo,
  }) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(message),
          duration: const Duration(seconds: 4),
          action: SnackBarAction(
            label: context.l10n.commonUndo,
            onPressed: onUndo,
          ),
        ),
      );
  }
}
