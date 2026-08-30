// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Vietnamese (`vi`).
class AppL10nVi extends AppL10n {
  AppL10nVi([String locale = 'vi']) : super(locale);

  @override
  String get appName => 'SweepFood';

  @override
  String get navHome => 'Trang chủ';

  @override
  String get navPantry => 'Kho';

  @override
  String get navSuggestions => 'Gợi ý';

  @override
  String get navShopping => 'Mua sắm';

  @override
  String get navProfile => 'Cá nhân';
}
