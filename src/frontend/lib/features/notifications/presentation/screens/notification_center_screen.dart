import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/analytics/analytics_events.dart';
import 'package:sweepfood/core/analytics/analytics_provider.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/extensions/date_time_x.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/features/notifications/domain/entities/app_notification.dart';
import 'package:sweepfood/features/notifications/presentation/controllers/notifications_controller.dart';
import 'package:sweepfood/features/notifications/presentation/widgets/near_expiry_detail_sheet.dart';
import 'package:sweepfood/features/notifications/presentation/widgets/notification_tile.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

/// T-01 Trung tâm thông báo (Concept B · Format 1: Emerald Header + Day-Grouped
/// Hairline Cards).
class NotificationCenterScreen extends ConsumerWidget {
  const NotificationCenterScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final cs = context.colors;
    final async = ref.watch(notificationsControllerProvider);
    final unreadCount = ref.watch(unreadNotificationCountProvider);

    return EmeraldSystemOverlay(
      child: Scaffold(
        backgroundColor: cs.surface,
        body: Column(
          children: [
            EmeraldSplitHeader(
              title: l10n.notifTitle,
              trailing: unreadCount > 0
                  ? EmeraldHeaderPill(
                      label: l10n.notifMarkAllRead,
                      onTap: () => ref
                          .read(notificationsControllerProvider.notifier)
                          .markAllRead(),
                    )
                  : null,
            ),
            Expanded(
              child: RefreshIndicator(
                onRefresh: () => ref
                    .read(notificationsControllerProvider.notifier)
                    .refresh(),
                child: AsyncValueWidget(
                  value: async,
                  onRetry: () =>
                      ref.invalidate(notificationsControllerProvider),
                  data: (_) {
                    final groups = ref.watch(groupedNotificationsProvider);
                    if (groups.isEmpty) {
                      return ListView(
                        padding: const EdgeInsets.fromLTRB(
                          Gap.lg,
                          Gap.xl,
                          Gap.lg,
                          Gap.xxl,
                        ),
                        children: [
                          EmptyState(
                            illustrationAsset:
                                'assets/illustrations/empty_notifications.svg',
                            title: l10n.notifEmptyTitle,
                            message: l10n.notifEmptyBody,
                            icon: AppIcons.bellOff,
                          ),
                        ],
                      );
                    }
                    return ListView(
                      padding: EdgeInsets.fromLTRB(
                        Gap.lg,
                        Gap.xs,
                        Gap.lg,
                        MediaQuery.paddingOf(context).bottom + Gap.xxl,
                      ),
                      children: [
                        for (final g in groups) ...[
                          Padding(
                            padding: const EdgeInsets.fromLTRB(
                              4,
                              Gap.md,
                              4,
                              Gap.xs + 2,
                            ),
                            child: Text(
                              _dayLabel(g.day, l10n).toUpperCase(),
                              style: context.text.labelSmall?.copyWith(
                                letterSpacing: 0.7,
                                fontWeight: FontWeight.w800,
                                color: context.sweep.textTertiary,
                              ),
                            ),
                          ),
                          Container(
                            decoration: BoxDecoration(
                              color: cs.surfaceContainerLowest,
                              borderRadius: Radii.brXl,
                              border: Border.all(color: context.sweep.hairline),
                              boxShadow: Shadows.e1,
                            ),
                            clipBehavior: Clip.antiAlias,
                            child: Column(
                              children: [
                                for (var i = 0; i < g.items.length; i++) ...[
                                  NotificationTile(
                                    notification: g.items[i],
                                    onTap: () => _open(context, ref, g.items[i]),
                                  ),
                                  if (i < g.items.length - 1)
                                    Divider(
                                      height: 1,
                                      indent: 66,
                                      color: context.sweep.hairline,
                                    ),
                                ],
                              ],
                            ),
                          ),
                        ],
                      ],
                    );
                  },
                ),
              ),
            ),
          ],
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
