import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_colors.dart';

extension BuildContextX on BuildContext {
  ThemeData get theme => Theme.of(this);
  TextTheme get text => Theme.of(this).textTheme;
  ColorScheme get colors => Theme.of(this).colorScheme;

  /// Semantic colours (expiry states, storage-tier tints) from the theme extension.
  SweepColors get sweep => Theme.of(this).extension<SweepColors>()!;

  MediaQueryData get mq => MediaQuery.of(this);
  bool get isDark => Theme.of(this).brightness == Brightness.dark;

  void showSnack(String message, {SnackBarAction? action}) {
    ScaffoldMessenger.of(this)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(message), action: action));
  }
}
