import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/notifications/data/repositories/notification_repository_impl.dart';
import 'package:sweepfood/features/notifications/domain/entities/app_notification.dart';

part 'notifications_controller.g.dart';

/// T-01 Trung tâm thông báo. Loads the list; `markRead` / `markAllRead` update
/// optimistically and roll back on failure.
@riverpod
class NotificationsController extends _$NotificationsController {
  @override
  Future<List<AppNotification>> build() async {
    final res = await ref.watch(notificationRepositoryProvider).list();
    return res.fold((f) => throw f, (list) => list);
  }

  Future<void> refresh() => ref.refresh(notificationsControllerProvider.future);

  Future<void> markRead(String id) async {
    final current = state.asData?.value;
    if (current == null) return;
    state = AsyncData([
      for (final n in current) n.id == id ? n.copyWith(read: true) : n,
    ]);
    final res =
        await ref.read(notificationRepositoryProvider).markRead(id);
    res.fold((_) => ref.invalidateSelf(), (_) {});
  }

  Future<void> markAllRead() async {
    final current = state.asData?.value;
    if (current == null || current.every((n) => n.read)) return;
    final unreadIds = [for (final n in current) if (!n.read) n.id];
    state = AsyncData([for (final n in current) n.copyWith(read: true)]);
    final res = await ref
        .read(notificationRepositoryProvider)
        .markAllRead(unreadIds);
    res.fold((_) => ref.invalidateSelf(), (_) {});
  }
}

/// Unread badge count for the Home bell.
@riverpod
int unreadNotificationCount(Ref ref) {
  final list = ref.watch(notificationsControllerProvider).asData?.value;
  return list == null ? 0 : list.where((n) => !n.read).length;
}

/// Notifications bucketed by calendar day, newest bucket first — the T-01 layout
/// ("Hôm nay" / "Hôm qua" / "dd/MM").
typedef NotificationDay = ({DateTime day, List<AppNotification> items});

@riverpod
List<NotificationDay> groupedNotifications(Ref ref) {
  final list = ref.watch(notificationsControllerProvider).asData?.value ?? [];
  final byDay = <DateTime, List<AppNotification>>{};
  for (final n in list) {
    final d = DateTime(n.createdAt.year, n.createdAt.month, n.createdAt.day);
    byDay.putIfAbsent(d, () => []).add(n);
  }
  final days = byDay.keys.toList()..sort((a, b) => b.compareTo(a));
  return [for (final d in days) (day: d, items: byDay[d]!)];
}
