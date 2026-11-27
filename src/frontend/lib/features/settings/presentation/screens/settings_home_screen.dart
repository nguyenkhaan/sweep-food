import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/locale_controller.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/theme_mode_controller.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_dialog.dart';
import 'package:sweepfood/core/widgets/tactile_card.dart';
import 'package:sweepfood/features/auth/presentation/controllers/session_controller.dart';
import 'package:sweepfood/features/settings/presentation/widgets/rating_dialog.dart';
import 'package:sweepfood/features/settings/presentation/widgets/settings_group.dart';

/// P-01 Cá nhân (Concept B · Format 1: Emerald Identity Hero + 2×2 Kitchen
/// Bento Shortcuts + Grouped Settings with 100% Lucide icons).
class SettingsHomeScreen extends ConsumerWidget {
  const SettingsHomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;
    final user = ref.watch(sessionControllerProvider).asData?.value?.user;
    final langCode = ref.watch(localeControllerProvider).languageCode;
    final themeMode = ref.watch(themeModeControllerProvider);

    final dietSummary = user == null
        ? ''
        : l10n.nutritionProfileRowSubtitle(
            user.nutritionProfile.householdSize,
            user.nutritionProfile.diet.label(l10n),
          );

    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.light,
        statusBarBrightness: Brightness.dark,
        systemNavigationBarColor: cs.surfaceContainerLowest,
        systemNavigationBarIconBrightness:
            Theme.of(context).brightness == Brightness.dark
            ? Brightness.light
            : Brightness.dark,
      ),
      child: Scaffold(
        backgroundColor: cs.surface,
        body: CustomScrollView(
          slivers: [
            SliverAppBar(
              pinned: true,
              elevation: 0,
              scrolledUnderElevation: 0,
              automaticallyImplyLeading: false,
              backgroundColor: sweep.heroSurface,
              surfaceTintColor: Colors.transparent,
              titleSpacing: Gap.lg,
              title: Text(
                l10n.navProfile,
                style: context.text.titleLarge?.copyWith(
                  color: sweep.onHeroSurface,
                  fontWeight: FontWeight.w800,
                ),
              ),
              actions: [
                Padding(
                  padding: const EdgeInsets.only(right: Gap.md),
                  child: Tooltip(
                    message: l10n.settingsProfilePassword,
                    child: Material(
                      color: sweep.heroSurfaceElevated,
                      shape: RoundedRectangleBorder(
                        borderRadius: Radii.brMd,
                        side: BorderSide(
                          color: sweep.onHeroSurface.withValues(alpha: 0.14),
                        ),
                      ),
                      child: InkWell(
                        borderRadius: Radii.brMd,
                        onTap: () {
                          AppHaptics.selection();
                          context.push(Routes.settingsProfile);
                        },
                        child: SizedBox(
                          width: 44,
                          height: 44,
                          child: Icon(
                            AppIcons.edit,
                            size: 18,
                            color: sweep.onHeroSurface,
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
            SliverToBoxAdapter(
              child: _ProfileEmeraldHero(
                name: user?.name ?? '—',
                subtitle: dietSummary.isNotEmpty
                    ? dietSummary
                    : (user?.email ?? ''),
                initials: user?.initials ?? '?',
                onEdit: () => context.push(Routes.settingsProfile),
              ),
            ),
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(Gap.lg, 0, Gap.lg, 96),
              sliver: SliverList.list(
                children: [
                  // 2×2 Quick Kitchen Bento Shortcuts
                  IntrinsicHeight(
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Expanded(
                          child: _KitchenBentoTile(
                            icon: AppIcons.calendar,
                            iconBg: cs.primaryContainer,
                            iconFg: cs.primary,
                            title: l10n.mealPlanTitle,
                            subtitle: 'Lên lịch bữa ăn',
                            onTap: () => context.push(Routes.mealPlan),
                          ),
                        ),
                        const SizedBox(width: Gap.sm),
                        Expanded(
                          child: _KitchenBentoTile(
                            icon: AppIcons.heart,
                            iconBg: sweep.expired.bg,
                            iconFg: sweep.expired.fg,
                            title: l10n.favoritesTitle,
                            subtitle: 'Món và thực đơn lưu',
                            onTap: () => context.push(Routes.favorites),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: Gap.sm),
                  IntrinsicHeight(
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Expanded(
                          child: _KitchenBentoTile(
                            icon: AppIcons.history,
                            iconBg: sweep.soon.bg,
                            iconFg: sweep.soon.fg,
                            title: l10n.cookingHistoryTitle,
                            subtitle: 'Các bữa đã nấu',
                            onTap: () => context.push(Routes.cookHistory),
                          ),
                        ),
                        const SizedBox(width: Gap.sm),
                        Expanded(
                          child: _KitchenBentoTile(
                            icon: AppIcons.leaf,
                            iconBg: sweep.culinaryAccentBg,
                            iconFg: sweep.culinaryAccent,
                            title: l10n.reportsTitle,
                            subtitle: 'Thống kê tiết kiệm',
                            onTap: () => context.push(Routes.reports),
                          ),
                        ),
                      ],
                    ),
                  ),
                  Gap.gapLg,
                  SettingsGroup(
                    label: l10n.settingsGroupAccount,
                    rows: [
                      SettingsRow(
                        icon: AppIcons.shield,
                        label: l10n.nutritionProfileTitle,
                        trailing:
                            user == null ||
                                user.nutritionProfile.activeConstraintCount > 0
                            ? null
                            : dietSummary,
                        badge:
                            user != null &&
                                user.nutritionProfile.activeConstraintCount > 0
                            ? l10n.nutritionProfileFilterBadge(
                                user.nutritionProfile.activeConstraintCount,
                              )
                            : null,
                        onTap: () =>
                            context.push(Routes.settingsNutritionProfile),
                      ),
                      SettingsRow(
                        icon: AppIcons.profile,
                        label: l10n.settingsProfilePassword,
                        onTap: () => context.push(Routes.settingsProfile),
                      ),
                      SettingsRow(
                        icon: AppIcons.award,
                        label: l10n.settingsPlan,
                        trailing: l10n.settingsPremiumSoon,
                        onTap: () => context.push(Routes.settingsSubscription),
                      ),
                    ],
                  ),
                  Gap.gapMd,
                  SettingsGroup(
                    label: l10n.settingsGroupApp,
                    rows: [
                      SettingsRow(
                        icon: AppIcons.bell,
                        label: l10n.notifTitle,
                        onTap: () => context.push(Routes.settingsNotifications),
                      ),
                      SettingsRow(
                        icon: AppIcons.filter,
                        label: l10n.prefsTitle,
                        onTap: () => context.push(Routes.settingsPreferences),
                      ),
                      SettingsRow(
                        icon: AppIcons.sun,
                        label: l10n.prefsTheme,
                        trailing: switch (themeMode) {
                          ThemeMode.light => l10n.themeLight,
                          ThemeMode.dark => l10n.themeDark,
                          ThemeMode.system => l10n.themeSystem,
                        },
                        onTap: () => context.push(Routes.settingsPreferences),
                      ),
                      SettingsRow(
                        icon: AppIcons.globe,
                        label: l10n.prefsLanguage,
                        trailing: langCode == 'en' ? l10n.langEn : l10n.langVi,
                        onTap: () => context.push(Routes.settingsPreferences),
                      ),
                    ],
                  ),
                  Gap.gapMd,
                  SettingsGroup(
                    label: l10n.settingsGroupOther,
                    rows: [
                      SettingsRow(
                        icon: AppIcons.info,
                        label: l10n.settingsAboutData,
                        onTap: () => context.push(Routes.settingsAbout),
                      ),
                      SettingsRow(
                        icon: AppIcons.star,
                        label: 'Đánh giá ứng dụng và Góp ý',
                        onTap: () => RatingDialog.show(context),
                      ),
                      SettingsRow(
                        icon: AppIcons.logOut,
                        label: l10n.settingsSignOut,
                        danger: true,
                        onTap: () => _confirmSignOut(context, ref),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _confirmSignOut(BuildContext context, WidgetRef ref) async {
    final l10n = context.l10n;
    final ok = await showAppConfirmDialog(
      context,
      title: l10n.signOutConfirmTitle,
      message: l10n.signOutConfirmBody,
      confirmLabel: l10n.settingsSignOut,
      cancelLabel: l10n.commonCancel,
      destructive: true,
    );
    if ((ok ?? false) && context.mounted) {
      await ref.read(sessionControllerProvider.notifier).logOut();
    }
  }
}

class _ProfileEmeraldHero extends StatelessWidget {
  const _ProfileEmeraldHero({
    required this.name,
    required this.subtitle,
    required this.initials,
    required this.onEdit,
  });

  final String name;
  final String subtitle;
  final String initials;
  final VoidCallback onEdit;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final cs = context.colors;

    return DecoratedBox(
      decoration: BoxDecoration(color: sweep.heroSurface),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: () {
                AppHaptics.selection();
                onEdit();
              },
              child: Padding(
                padding: const EdgeInsets.fromLTRB(
                  Gap.lg,
                  Gap.xs,
                  Gap.lg,
                  Gap.lg,
                ),
                child: Row(
                  children: [
                    Container(
                      width: 54,
                      height: 54,
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        color: sweep.heroSurfaceElevated,
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: sweep.onHeroSurface.withValues(alpha: 0.25),
                          width: 1.5,
                        ),
                      ),
                      child: Text(
                        initials,
                        style: context.text.titleLarge?.copyWith(
                          color: sweep.onHeroSurface,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                    const SizedBox(width: Gap.sm + 4),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            name,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: context.text.titleLarge?.copyWith(
                              color: sweep.onHeroSurface,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          if (subtitle.trim().isNotEmpty) ...[
                            const SizedBox(height: 2),
                            Text(
                              subtitle,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: context.text.bodySmall?.copyWith(
                                color: sweep.onHeroMuted,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          Container(
            height: 20,
            decoration: BoxDecoration(
              color: cs.surface,
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(26),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _KitchenBentoTile extends StatelessWidget {
  const _KitchenBentoTile({
    required this.icon,
    required this.iconBg,
    required this.iconFg,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final Color iconBg;
  final Color iconFg;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return TactileCard(
      color: context.colors.surfaceContainerLowest,
      borderColor: context.sweep.hairline,
      boxShadow: Shadows.e1,
      padding: const EdgeInsets.all(Gap.md - 2),
      onTap: onTap,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: iconBg,
                  borderRadius: Radii.brMd,
                ),
                child: Icon(icon, size: 18, color: iconFg),
              ),
              const Spacer(),
              Icon(
                AppIcons.chevronRight,
                size: 15,
                color: context.sweep.textTertiary,
              ),
            ],
          ),
          const SizedBox(height: Gap.sm + 2),
          Text(
            title,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: context.text.titleSmall?.copyWith(
              fontWeight: FontWeight.w700,
              height: 1.2,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            subtitle,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: context.text.bodySmall?.copyWith(
              color: context.sweep.textTertiary,
            ),
          ),
        ],
      ),
    );
  }
}
