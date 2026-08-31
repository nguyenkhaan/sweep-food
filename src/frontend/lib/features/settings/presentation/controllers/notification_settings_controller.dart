import 'dart:convert';

import 'package:frontend/core/config/app_constants.dart';
import 'package:frontend/core/notifications/notification_providers.dart';
import 'package:frontend/core/storage/prefs.dart';
import 'package:frontend/features/settings/domain/entities/notification_preferences.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'notification_settings_controller.g.dart';

/// P-04 Cài đặt thông báo. Persisted as JSON in SharedPreferences; on every
/// change it re-schedules the local near-expiry reminders.
@Riverpod(keepAlive: true)
class NotificationSettingsController extends _$NotificationSettingsController {
  @override
  NotificationPreferences build() {
    final raw =
        ref.watch(sharedPreferencesProvider).getString(AppConstants.kNotificationPrefs);
    if (raw == null) return const NotificationPreferences();
    try {
      return NotificationPreferences.fromJson(
        jsonDecode(raw) as Map<String, Object?>,
      );
    } catch (_) {
      return const NotificationPreferences();
    }
  }

  Future<void> _persist(NotificationPreferences next) async {
    state = next;
    await ref
        .read(sharedPreferencesProvider)
        .setString(AppConstants.kNotificationPrefs, jsonEncode(next.toJson()));
    ref.read(localNotificationsProvider).syncFromPreferences(next);
  }

  Future<void> toggleNearExpiry(bool v) =>
      _persist(state.copyWith(nearExpiry: v));
  Future<void> toggleDailySuggestions(bool v) =>
      _persist(state.copyWith(dailySuggestions: v));
  Future<void> toggleWeeklyReport(bool v) =>
      _persist(state.copyWith(weeklyReport: v));
  Future<void> togglePostCookReminder(bool v) =>
      _persist(state.copyWith(postCookReminder: v));
  Future<void> togglePromosAndTips(bool v) =>
      _persist(state.copyWith(promosAndTips: v));

  Future<void> setNearExpiryHour(int hour) =>
      _persist(state.copyWith(nearExpiryHour: hour));

  Future<void> setDndWindow({required int start, required int end}) =>
      _persist(state.copyWith(dndStartHour: start, dndEndHour: end));
}
