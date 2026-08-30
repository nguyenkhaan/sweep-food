// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppL10nEn extends AppL10n {
  AppL10nEn([String locale = 'en']) : super(locale);

  @override
  String get appName => 'SweepFood';

  @override
  String get navHome => 'Home';

  @override
  String get navPantry => 'Pantry';

  @override
  String get navSuggestions => 'Suggestions';

  @override
  String get navShopping => 'Shopping';

  @override
  String get navProfile => 'Profile';
}
