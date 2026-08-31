import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/features/auth/presentation/controllers/session_controller.dart';
import 'package:frontend/features/settings/presentation/widgets/settings_group.dart';
import 'package:go_router/go_router.dart';

/// P-01 Cá nhân — profile header, plan bar, grouped settings, sign out.
class SettingsHomeScreen extends ConsumerWidget {
  const SettingsHomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final user = ref.watch(sessionControllerProvider).asData?.value?.user;

    return Scaffold(
      appBar: AppBar(title: Text(l10n.navProfile)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.md, Gap.lg, Gap.xxl),
        children: [
          _ProfileCard(
            name: user?.name ?? '—',
            email: user?.email ?? '',
            initials: user?.initials ?? '?',
            onTap: () => context.push(Routes.settingsProfile),
          ),
          Gap.gapMd,
          _PlanBar(onTap: () => context.push(Routes.paywall)),
          Gap.gapLg,
          SettingsGroup(
            label: l10n.settingsGroupAccount,
            rows: [
              SettingsRow(
                icon: Icons.person_outline_rounded,
                label: l10n.settingsProfilePassword,
                onTap: () => context.push(Routes.settingsProfile),
              ),
              SettingsRow(
                icon: Icons.workspace_premium_outlined,
                label: l10n.settingsPlan,
                trailing: l10n.settingsPremiumSoon,
                onTap: () => context.push(Routes.settingsSubscription),
              ),
              SettingsRow(
                icon: Icons.group_outlined,
                label: l10n.settingsPantrySharing,
                badge: l10n.commonComingSoon,
                onTap: () => context.push(Routes.settingsPantrySharing),
              ),
            ],
          ),
          Gap.gapMd,
          SettingsGroup(
            label: l10n.settingsGroupMealPlanning,
            rows: [
              SettingsRow(
                icon: Icons.calendar_month_rounded,
                label: l10n.mealPlanTitle,
                onTap: () => context.push(Routes.mealPlan),
              ),
              SettingsRow(
                icon: Icons.insights_rounded,
                label: l10n.settingsWasteReport,
                onTap: () => context.push(Routes.reports),
              ),
            ],
          ),
          Gap.gapMd,
          SettingsGroup(
            label: l10n.settingsGroupApp,
            rows: [
              SettingsRow(
                icon: Icons.tune_rounded,
                label: l10n.prefsTitle,
                onTap: () => context.push(Routes.settingsPreferences),
              ),
              SettingsRow(
                icon: Icons.notifications_none_rounded,
                label: l10n.notifTitle,
                onTap: () => context.push(Routes.settingsNotifications),
              ),
              SettingsRow(
                icon: Icons.language_rounded,
                label: l10n.prefsLanguage,
                trailing: l10n.prefsLanguageValue,
              ),
            ],
          ),
          Gap.gapMd,
          SettingsGroup(
            label: l10n.settingsGroupOther,
            rows: [
              SettingsRow(
                icon: Icons.info_outline_rounded,
                label: l10n.settingsAboutData,
                onTap: () => context.push(Routes.settingsAbout),
              ),
              SettingsRow(
                icon: Icons.logout_rounded,
                label: l10n.settingsSignOut,
                danger: true,
                onTap: () => _confirmSignOut(context, ref),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Future<void> _confirmSignOut(BuildContext context, WidgetRef ref) async {
    final l10n = context.l10n;
    final ok = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(l10n.signOutConfirmTitle),
        content: Text(l10n.signOutConfirmBody),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(l10n.commonCancel),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text(l10n.settingsSignOut),
          ),
        ],
      ),
    );
    if ((ok ?? false) && context.mounted) {
      await ref.read(sessionControllerProvider.notifier).logOut();
    }
  }
}

class _ProfileCard extends StatelessWidget {
  const _ProfileCard({
    required this.name,
    required this.email,
    required this.initials,
    required this.onTap,
  });

  final String name;
  final String email;
  final String initials;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: Radii.brLg,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: Gap.xs),
        child: Row(
          children: [
            CircleAvatar(
              radius: 26,
              backgroundColor: context.colors.primaryContainer,
              child: Text(
                initials,
                style: TextStyle(
                  color: context.colors.onPrimaryContainer,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
            Gap.gapMd,
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    name,
                    style: context.text.titleMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  Text(
                    email,
                    style: context.text.bodySmall?.copyWith(
                      color: context.sweep.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              Icons.chevron_right_rounded,
              color: context.sweep.textTertiary,
            ),
          ],
        ),
      ),
    );
  }
}

class _PlanBar extends StatelessWidget {
  const _PlanBar({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Material(
      color: context.colors.primaryContainer,
      borderRadius: Radii.brLg,
      child: InkWell(
        onTap: onTap,
        borderRadius: Radii.brLg,
        child: Padding(
          padding: const EdgeInsets.all(Gap.md),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      l10n.planFullFree,
                      style: context.text.titleSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                        color: context.colors.onPrimaryContainer,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      l10n.planPremiumDeveloping,
                      style: context.text.bodySmall?.copyWith(
                        color: context.colors.onPrimaryContainer.withValues(
                          alpha: 0.8,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              Gap.gapSm,
              Text(
                l10n.planInterested,
                style: context.text.labelLarge?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: context.colors.onPrimaryContainer,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
