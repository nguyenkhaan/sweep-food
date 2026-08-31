import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_colors.dart';
import 'package:frontend/l10n/app_localizations.dart';

extension BuildContextX on BuildContext {
  ThemeData get theme => Theme.of(this);
  TextTheme get text => Theme.of(this).textTheme;
  ColorScheme get colors => Theme.of(this).colorScheme;

  /// Localized strings (`app_vi.arb` / `app_en.arb`). MVP runs `vi` only.
  AppL10n get l10n => AppL10n.of(this);

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
