import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_colors.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/core/error/failure.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

extension BuildContextX on BuildContext {
  ThemeData get theme => Theme.of(this);
  TextTheme get text => Theme.of(this).textTheme;
  ColorScheme get colors => Theme.of(this).colorScheme;

  /// Localized strings (`app_vi.arb` / `app_en.arb`).
  AppL10n get l10n => AppL10n.of(this);

  /// Semantic colours (expiry states, storage tiers, category tints).
  SweepColors get sweep => SweepColors.of(this);

  /// Semantic motion durations and curves.
  AppMotion get motion => AppMotion.of(this);

  MediaQueryData get mq => MediaQuery.of(this);
  bool get isDark => Theme.of(this).brightness == Brightness.dark;
  bool get reduceMotion => MediaQuery.disableAnimationsOf(this);

  /// Snack text for a failed save: "food not supported" when the backend
  /// rejected the food, otherwise the generic error carrying [error].
  String saveErrorMessage(Object error) => error is UnsupportedIngredientFailure
      ? l10n.failUnsupportedIngredient
      : l10n.scanSaveError('$error');

  void showSnack(String message, {SnackBarAction? action}) {
    ScaffoldMessenger.of(this)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(message), action: action));
  }
}
