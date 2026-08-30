import 'package:flutter/material.dart';
import 'package:frontend/core/config/app_constants.dart';
import 'package:frontend/core/storage/prefs.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'theme_mode_controller.g.dart';

/// App theme mode (system / light / dark), persisted to SharedPreferences.
/// Read by [MaterialApp.router] in `app.dart`; changed from Cài đặt → Tùy chọn.
@Riverpod(keepAlive: true)
class ThemeModeController extends _$ThemeModeController {
  @override
  ThemeMode build() {
    final raw = ref
        .watch(sharedPreferencesProvider)
        .getString(AppConstants.kThemeMode);
    return switch (raw) {
      'light' => ThemeMode.light,
      'dark' => ThemeMode.dark,
      _ => ThemeMode.system,
    };
  }

  Future<void> set(ThemeMode mode) async {
    state = mode;
    await ref
        .read(sharedPreferencesProvider)
        .setString(AppConstants.kThemeMode, mode.name);
  }
}
