import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/features/auth/presentation/controllers/session_controller.dart';
import 'package:sweepfood/features/settings/presentation/widgets/settings_group.dart';

/// P-01a Hồ sơ & mật khẩu.
class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final user = ref.watch(sessionControllerProvider).asData?.value?.user;

    return Scaffold(
      appBar: AppBar(title: Text(l10n.settingsProfilePassword)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.lg, Gap.lg, Gap.xxl),
        children: [
          Center(
            child: CircleAvatar(
              radius: 40,
              backgroundColor: context.colors.primaryContainer,
              child: Text(
                user?.initials ?? '?',
                style: context.text.headlineSmall?.copyWith(
                  color: context.colors.onPrimaryContainer,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ),
          Gap.gapLg,
          SettingsGroup(
            label: l10n.profileGroupInfo,
            rows: [
              SettingsRow(
                icon: Icons.badge_outlined,
                label: l10n.authFullName,
                trailing: user?.name ?? '—',
                onTap: () => context.push(Routes.settingsEditProfile),
              ),
              SettingsRow(
                icon: Icons.mail_outline_rounded,
                label: l10n.authEmail,
                trailing: user?.email ?? '—',
                onTap: () => context.push(Routes.settingsChangeEmail),
              ),
              SettingsRow(
                icon: Icons.phone_outlined,
                label: l10n.authPhone,
                trailing: user?.phone ?? '—',
                onTap: () => context.push(Routes.settingsChangePhone),
              ),
            ],
          ),
          Gap.gapMd,
          SettingsGroup(
            label: l10n.profileGroupSecurity,
            rows: [
              SettingsRow(
                icon: Icons.lock_outline_rounded,
                label: l10n.profileChangePassword,
                onTap: () => context.push(Routes.settingsChangePassword),
              ),
              SettingsRow(
                icon: Icons.devices_rounded,
                label: 'Thiết bị & phiên đăng nhập',
                onTap: () => context.push(Routes.settingsSessions),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
