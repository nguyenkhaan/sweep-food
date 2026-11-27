import 'dart:async';
import 'dart:convert';

import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/config/app_constants.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/core/notifications/notification_providers.dart';
import 'package:sweepfood/core/storage/prefs.dart';
import 'package:sweepfood/features/settings/domain/entities/notification_preferences.dart';

part 'notification_settings_controller.g.dart';

/// P-04 Cài đặt thông báo. Hydrates immediately from local SharedPreferences,
/// then syncs bidirectionally with `GET`/`PATCH /api/notifications/preferences`
/// and re-schedules local near-expiry reminders on every change.
@Riverpod(keepAlive: true)
class NotificationSettingsController extends _$NotificationSettingsController {
  @override
  NotificationPreferences build() {
    final initial = _readLocal();
    unawaited(_syncFromServer());
    return initial;
  }

  NotificationPreferences _readLocal() {
    final raw = ref
        .watch(sharedPreferencesProvider)
        .getString(AppConstants.kNotificationPrefs);
    if (raw == null) return const NotificationPreferences();
    try {
      return NotificationPreferences.fromJson(
        jsonDecode(raw) as Map<String, Object?>,
      );
    } catch (_) {
      return const NotificationPreferences();
    }
  }

  Future<void> _syncFromServer() async {
    try {
      final json = await ref
          .read(apiClientProvider)
          .get(ApiPaths.notificationPreferences);
      if (json is! Map<String, dynamic>) return;
      final remote = NotificationPreferences.fromJson(
        Map<String, Object?>.from(json),
      );
      state = remote;
      await ref
          .read(sharedPreferencesProvider)
          .setString(
            AppConstants.kNotificationPrefs,
            jsonEncode(remote.toJson()),
          );
      ref.read(localNotificationsProvider).syncFromPreferences(remote);
    } catch (_) {
      // Offline, unauthenticated, or older backend — keep local cache intact.
    }
  }

  Future<void> _persist(NotificationPreferences next) async {
    state = next;
    await ref
        .read(sharedPreferencesProvider)
        .setString(AppConstants.kNotificationPrefs, jsonEncode(next.toJson()));
    ref.read(localNotificationsProvider).syncFromPreferences(next);
    try {
      await ref
          .read(apiClientProvider)
          .patch(ApiPaths.notificationPreferences, body: next.toJson());
    } catch (_) {
      // Optimistic local save already succeeded; server sync retries on next edit.
    }
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
