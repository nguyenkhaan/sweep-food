import 'package:freezed_annotation/freezed_annotation.dart';

part 'app_notification.freezed.dart';

/// What a notification is about — drives its icon/tint and the deep link on tap.
enum AppNotificationType {
  nearExpiry('near_expiry'),
  wasteWin('waste_win'),
  mealPlanReady('meal_plan_ready'),
  system('system');

  const AppNotificationType(this.wire);
  final String wire;

  /// Backend `NotificationType` enum tokens (`docs/DATABASE.txt`). The backend
  /// only emits expiry-related notifications today, so they all collapse to
  /// [nearExpiry]; `waste_win` / `meal_plan_ready` come from the mock only.
  static const Map<String, AppNotificationType> _backendTokens = {
    'EXPIRING_SOON': AppNotificationType.nearExpiry,
    'EXPIRES_TODAY': AppNotificationType.nearExpiry,
    'EXPIRED': AppNotificationType.nearExpiry,
    'LEFTOVER_REMINDER': AppNotificationType.nearExpiry,
  };

  /// Accepts the frontend wire tokens (`near_expiry`, …) and the backend enum
  /// tokens (`EXPIRING_SOON`, …). Unknown values fall back to [system].
  static AppNotificationType fromWire(String? v) {
    if (v == null) return AppNotificationType.system;
    for (final t in AppNotificationType.values) {
      if (t.wire == v) return t;
    }
    return _backendTokens[v.toUpperCase()] ?? AppNotificationType.system;
  }
}

/// One entry in the Trung tâm thông báo (T-01).
@freezed
abstract class AppNotification with _$AppNotification {
  const AppNotification._();

  const factory AppNotification({
    required String id,
    required AppNotificationType type,
    required String title,
    required String body,
    required DateTime createdAt,
    @Default(false) bool read,

    /// Deep-link targets (set by type). `pantryItemId` for near-expiry (the
    /// backend sends it as `inventory_batch_id`), `dishIds` for "xem món gợi ý"
    /// (mock only — the backend has no dish links yet).
    String? pantryItemId,
    @Default([]) List<String> dishIds,
  }) = _AppNotification;

  /// "8:00" — the time shown at the trailing edge of the row.
  String get timeLabel {
    final h = createdAt.hour;
    final m = createdAt.minute.toString().padLeft(2, '0');
    return '$h:$m';
  }
}
