import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_colors.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/features/notifications/domain/entities/app_notification.dart';

/// One row in the Trung tâm thông báo (T-01): tinted icon, title + body, time,
/// and an unread dot.
class NotificationTile extends StatelessWidget {
  const NotificationTile({
    required this.notification,
    required this.onTap,
    super.key,
  });

  final AppNotification notification;
  final VoidCallback onTap;

  ({IconData icon, Color fg, Color bg}) _visual(BuildContext context) {
    final sweep = context.sweep;
    return switch (notification.type) {
      AppNotificationType.nearExpiry => (
          icon: Icons.schedule_rounded,
          fg: sweep.expiry(ExpiryLevel.critical).fg,
          bg: sweep.expiry(ExpiryLevel.critical).bg,
        ),
      AppNotificationType.wasteWin => (
          icon: Icons.trending_up_rounded,
          fg: BrandPalette.green700,
          bg: BrandPalette.green100,
        ),
      AppNotificationType.mealPlanReady => (
          icon: Icons.calendar_month_rounded,
          fg: sweep.textSecondary,
          bg: sweep.subtleFill,
        ),
      AppNotificationType.system => (
          icon: Icons.info_outline_rounded,
          fg: sweep.textSecondary,
          bg: sweep.subtleFill,
        ),
    };
  }

  @override
  Widget build(BuildContext context) {
    final v = _visual(context);
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: Gap.lg,
          vertical: Gap.sm,
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(color: v.bg, borderRadius: Radii.brMd),
              child: Icon(v.icon, size: 18, color: v.fg),
            ),
            Gap.gapSm,
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    notification.title,
                    style: context.text.bodyMedium?.copyWith(
                      fontWeight:
                          notification.read ? FontWeight.w500 : FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    notification.body,
                    style: context.text.bodySmall?.copyWith(
                      color: context.sweep.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            Gap.gapSm,
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  notification.timeLabel,
                  style: context.text.labelSmall?.copyWith(
                    color: context.sweep.textTertiary,
                  ),
                ),
                const SizedBox(height: 6),
                if (!notification.read)
                  Container(
                    width: 8,
                    height: 8,
                    decoration: const BoxDecoration(
                      color: BrandPalette.warnCritical,
                      shape: BoxShape.circle,
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
