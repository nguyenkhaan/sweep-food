import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_logo.dart';
import 'package:sweepfood/features/notifications/domain/entities/app_notification.dart';
import 'package:sweepfood/shared/domain/expiry_status.dart';

/// One row in Trung tâm thông báo (T-01 · Concept B Format 1): Lucide icon badge,
/// title + body, relative time, and flat warm-orange unread dot.
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
        icon: AppIcons.flame,
        fg: sweep.expiry(ExpiryLevel.critical).fg,
        bg: sweep.expiry(ExpiryLevel.critical).bg,
      ),
      AppNotificationType.wasteWin => (
        icon: AppIcons.trendingUp,
        fg: sweep.successFg,
        bg: sweep.successBg,
      ),
      AppNotificationType.mealPlanReady => (
        icon: AppIcons.calendar,
        fg: context.colors.primary,
        bg: context.colors.primaryContainer,
      ),
      AppNotificationType.system => (
        icon: AppIcons.info,
        fg: sweep.textSecondary,
        bg: sweep.subtleFill,
      ),
    };
  }

  @override
  Widget build(BuildContext context) {
    final v = _visual(context);
    final unread = !notification.read;
    final isVi = Localizations.localeOf(context).languageCode == 'vi';
    final displayTitle = _localizeText(notification.title, isVi: isVi);
    final displayBody = _localizeText(notification.body, isVi: isVi);

    return ColoredBox(
      color: unread
          ? context.colors.primaryContainer.withValues(alpha: 0.22)
          : Colors.transparent,
      child: InkWell(
        onTap: () {
          AppHaptics.selection();
          onTap();
        },
        child: Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: Gap.md,
            vertical: Gap.sm + 4,
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (notification.type == AppNotificationType.system)
                const SizedBox(
                  width: 38,
                  height: 38,
                  child: Center(child: AppLogo(size: 32)),
                )
              else
                Container(
                  width: 38,
                  height: 38,
                  decoration: BoxDecoration(
                    color: v.bg,
                    borderRadius: Radii.brMd,
                  ),
                  child: Icon(v.icon, size: 18, color: v.fg),
                ),
              const SizedBox(width: Gap.sm + 2),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      displayTitle,
                      style: context.text.bodyMedium?.copyWith(
                        fontWeight: unread ? FontWeight.w700 : FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      displayBody,
                      style: context.text.bodySmall?.copyWith(
                        color: context.sweep.textSecondary,
                        height: 1.35,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: Gap.sm),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    notification.timeLabel,
                    style: context.text.labelSmall?.copyWith(
                      letterSpacing: 0,
                      color: context.sweep.textTertiary,
                    ),
                  ),
                  const SizedBox(height: 8),
                  if (unread)
                    Container(
                      width: 8,
                      height: 8,
                      decoration: BoxDecoration(
                        color: context.sweep.ctaWarm,
                        shape: BoxShape.circle,
                      ),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  static String _localizeText(String raw, {required bool isVi}) {
    if (!isVi) return raw;
    final trimmed = raw.trim();
    final lower = trimmed.toLowerCase();
    if (lower == 'food expired') return 'Thực phẩm đã quá hạn';
    if (lower == 'food expires today') return 'Thực phẩm hết hạn hôm nay';
    if (lower == 'food expires soon') return 'Thực phẩm sắp hết hạn';
    if (lower == 'food batch has expired.' ||
        lower == 'food batch has expired') {
      return 'Một lô thực phẩm trong kho đã quá hạn sử dụng.';
    }
    if (lower == 'food batch expires today.' ||
        lower == 'food batch expires today') {
      return 'Một lô thực phẩm trong kho sẽ hết hạn trong hôm nay.';
    }
    final inDays = RegExp(
      r'^food batch expires in (\d+) day\(s\)\.?$',
      caseSensitive: false,
    ).firstMatch(trimmed);
    if (inDays != null) {
      return 'Một lô thực phẩm trong kho sẽ hết hạn sau ${inDays.group(1)} ngày.';
    }
    return raw;
  }
}
