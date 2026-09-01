import 'package:flutter/material.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/config/app_constants.dart';
import 'package:sweepfood/core/storage/prefs.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

part 'locale_controller.g.dart';

/// App UI language, persisted to SharedPreferences. Read by [MaterialApp.router]
/// in `app.dart`; changed from Cài đặt → Tùy chọn → Ngôn ngữ.
///
/// Defaults to Vietnamese (the MVP language). English is opt-in and some
/// data-layer strings still fall back to `vi` (see IMPLEMENTATION_PLAN.md M6.1).
@Riverpod(keepAlive: true)
class LocaleController extends _$LocaleController {
  @override
  Locale build() {
    final raw = ref.watch(sharedPreferencesProvider).getString(AppConstants.kLocale);
    return _fromCode(raw) ?? const Locale('vi');
  }

  Future<void> set(Locale locale) async {
    state = locale;
    await ref
        .read(sharedPreferencesProvider)
        .setString(AppConstants.kLocale, locale.languageCode);
  }

  static Locale? _fromCode(String? code) {
    if (code == null) return null;
    for (final l in AppL10n.supportedLocales) {
      if (l.languageCode == code) return l;
    }
    return null;
  }
}
