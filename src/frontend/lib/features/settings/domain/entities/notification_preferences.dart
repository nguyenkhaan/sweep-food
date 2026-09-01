import 'package:flutter/foundation.dart';

/// Per-type notification toggles + timing (P-04). Persisted locally as JSON;
/// `core/notifications/local_notifications.dart` reads it when scheduling the
/// near-expiry reminders (there's no server push in the MVP).
@immutable
class NotificationPreferences {
  const NotificationPreferences({
    this.nearExpiry = true,
    this.dailySuggestions = true,
    this.weeklyReport = true,
    this.postCookReminder = true,
    this.promosAndTips = false,
    this.nearExpiryHour = 8,
    this.dndStartHour = 22,
    this.dndEndHour = 7,
  });

  final bool nearExpiry;
  final bool dailySuggestions;
  final bool weeklyReport;
  final bool postCookReminder;
  final bool promosAndTips;

  /// Hour of day (0–23) the near-expiry digest fires.
  final int nearExpiryHour;

  /// "Không làm phiền" window — inclusive start, exclusive end, wraps midnight.
  final int dndStartHour;
  final int dndEndHour;

  String get nearExpiryTimeLabel =>
      '${nearExpiryHour.toString().padLeft(2, '0')}:00';

  String get dndWindowLabel =>
      '${dndStartHour.toString().padLeft(2, '0')}:00 – '
      '${dndEndHour.toString().padLeft(2, '0')}:00';

  NotificationPreferences copyWith({
    bool? nearExpiry,
    bool? dailySuggestions,
    bool? weeklyReport,
    bool? postCookReminder,
    bool? promosAndTips,
    int? nearExpiryHour,
    int? dndStartHour,
    int? dndEndHour,
  }) {
    return NotificationPreferences(
      nearExpiry: nearExpiry ?? this.nearExpiry,
      dailySuggestions: dailySuggestions ?? this.dailySuggestions,
      weeklyReport: weeklyReport ?? this.weeklyReport,
      postCookReminder: postCookReminder ?? this.postCookReminder,
      promosAndTips: promosAndTips ?? this.promosAndTips,
      nearExpiryHour: nearExpiryHour ?? this.nearExpiryHour,
      dndStartHour: dndStartHour ?? this.dndStartHour,
      dndEndHour: dndEndHour ?? this.dndEndHour,
    );
  }

  Map<String, Object?> toJson() => {
        'near_expiry': nearExpiry,
        'daily_suggestions': dailySuggestions,
        'weekly_report': weeklyReport,
        'post_cook_reminder': postCookReminder,
        'promos_and_tips': promosAndTips,
        'near_expiry_hour': nearExpiryHour,
        'dnd_start_hour': dndStartHour,
        'dnd_end_hour': dndEndHour,
      };

  factory NotificationPreferences.fromJson(Map<String, Object?> json) {
    bool b(String k, bool d) => json[k] as bool? ?? d;
    int i(String k, int d) => (json[k] as num?)?.toInt() ?? d;
    return NotificationPreferences(
      nearExpiry: b('near_expiry', true),
      dailySuggestions: b('daily_suggestions', true),
      weeklyReport: b('weekly_report', true),
      postCookReminder: b('post_cook_reminder', true),
      promosAndTips: b('promos_and_tips', false),
      nearExpiryHour: i('near_expiry_hour', 8),
      dndStartHour: i('dnd_start_hour', 22),
      dndEndHour: i('dnd_end_hour', 7),
    );
  }
}
