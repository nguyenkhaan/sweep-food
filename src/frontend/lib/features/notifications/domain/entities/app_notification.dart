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

  static AppNotificationType fromWire(String? v) => AppNotificationType.values
      .firstWhere((t) => t.wire == v, orElse: () => AppNotificationType.system);
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

    /// Deep-link targets (set by type). `pantryItemId` for near-expiry,
    /// `dishIds` for "xem món gợi ý".
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
