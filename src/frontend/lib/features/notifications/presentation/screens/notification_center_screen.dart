import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/analytics/analytics_events.dart';
import 'package:frontend/core/analytics/analytics_provider.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/utils/extensions/date_time_x.dart';
import 'package:frontend/core/widgets/async_value_widget.dart';
import 'package:frontend/core/widgets/empty_state.dart';
import 'package:frontend/features/notifications/domain/entities/app_notification.dart';
import 'package:frontend/features/notifications/presentation/controllers/notifications_controller.dart';
import 'package:frontend/features/notifications/presentation/widgets/near_expiry_detail_sheet.dart';
import 'package:frontend/features/notifications/presentation/widgets/notification_tile.dart';
import 'package:go_router/go_router.dart';

/// T-01 Trung tâm thông báo — alerts grouped by day, unread dots, "đánh dấu đã
/// đọc", tap → deep link.
class NotificationCenterScreen extends ConsumerWidget {
  const NotificationCenterScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(notificationsControllerProvider);
    final hasUnread = ref.watch(unreadNotificationCountProvider) > 0;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Thông báo'),
        actions: [
          if (hasUnread)
            TextButton(
              onPressed: () =>
                  ref.read(notificationsControllerProvider.notifier).markAllRead(),
              child: const Text('Đánh dấu đã đọc'),
            ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () =>
            ref.read(notificationsControllerProvider.notifier).refresh(),
        child: AsyncValueWidget(
          value: async,
          onRetry: () => ref.invalidate(notificationsControllerProvider),
          data: (_) {
            final groups = ref.watch(groupedNotificationsProvider);
            if (groups.isEmpty) {
              return ListView(
                children: const [
                  SizedBox(height: 80),
                  EmptyState(
                    title: 'Chưa có thông báo',
                    message:
                        'Nhắc hạn sử dụng và tổng kết chống lãng phí sẽ xuất hiện ở đây.',
                    icon: Icons.notifications_none_rounded,
                  ),
                ],
              );
            }
            return ListView(
              padding: const EdgeInsets.only(bottom: Gap.xl),
              children: [
                for (final g in groups) ...[
                  Padding(
                    padding: const EdgeInsets.fromLTRB(
                      Gap.lg,
                      Gap.md,
                      Gap.lg,
                      Gap.xs,
                    ),
                    child: Text(
                      _dayLabel(g.day),
                      style: context.text.labelSmall,
                    ),
                  ),
                  for (final n in g.items)
                    NotificationTile(
                      notification: n,
                      onTap: () => _open(context, ref, n),
                    ),
                ],
              ],
            );
          },
        ),
      ),
    );
  }

  static String _dayLabel(DateTime day) {
    final today = DateTime.now().dateOnly;
    final diff = today.difference(day).inDays;
    return switch (diff) {
      0 => 'Hôm nay',
      1 => 'Hôm qua',
      _ => day.ddMM,
    };
  }

  void _open(BuildContext context, WidgetRef ref, AppNotification n) {
    ref.read(notificationsControllerProvider.notifier).markRead(n.id);
    ref.read(analyticsProvider).log(
      AnalyticsEvents.notificationOpened,
      {AnalyticsParams.source: n.type.wire},
    );
    switch (n.type) {
      case AppNotificationType.nearExpiry:
        if (n.pantryItemId != null) {
          NearExpiryDetailSheet.show(context, n.pantryItemId!);
        } else {
          context.go(Routes.pantry);
        }
      case AppNotificationType.mealPlanReady:
        context.push(Routes.mealPlan);
      case AppNotificationType.wasteWin:
        context.push(Routes.reports);
      case AppNotificationType.system:
        break;
    }
  }
}
