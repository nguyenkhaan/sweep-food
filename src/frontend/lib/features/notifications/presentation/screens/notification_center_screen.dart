import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/analytics/analytics_events.dart';
import 'package:sweepfood/core/analytics/analytics_provider.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/extensions/date_time_x.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/features/notifications/domain/entities/app_notification.dart';
import 'package:sweepfood/features/notifications/presentation/controllers/notifications_controller.dart';
import 'package:sweepfood/features/notifications/presentation/widgets/near_expiry_detail_sheet.dart';
import 'package:sweepfood/features/notifications/presentation/widgets/notification_tile.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

/// T-01 Trung tâm thông báo — alerts grouped by day, unread dots, "đánh dấu đã
/// đọc", tap → deep link.
class NotificationCenterScreen extends ConsumerWidget {
  const NotificationCenterScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final async = ref.watch(notificationsControllerProvider);
    final hasUnread = ref.watch(unreadNotificationCountProvider) > 0;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.notifTitle),
        actions: [
          if (hasUnread)
            TextButton(
              onPressed: () => ref
                  .read(notificationsControllerProvider.notifier)
                  .markAllRead(),
              child: Text(l10n.notifMarkAllRead),
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
                children: [
                  const SizedBox(height: 80),
                  EmptyState(
                    title: l10n.notifEmptyTitle,
                    message: l10n.notifEmptyBody,
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
                      _dayLabel(g.day, l10n),
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

  static String _dayLabel(DateTime day, AppL10n l10n) {
    final today = DateTime.now().dateOnly;
    final diff = today.difference(day).inDays;
    return switch (diff) {
      0 => l10n.dayToday,
      1 => l10n.dayYesterday,
      _ => day.ddMM,
    };
  }

  void _open(BuildContext context, WidgetRef ref, AppNotification n) {
    ref.read(notificationsControllerProvider.notifier).markRead(n.id);
    ref.read(analyticsProvider).log(AnalyticsEvents.notificationOpened, {
      AnalyticsParams.source: n.type.wire,
    });
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
