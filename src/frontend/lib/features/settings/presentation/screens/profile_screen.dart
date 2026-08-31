import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
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
                onTap: () => AppSnack.show(context, l10n.profileEditSoon),
              ),
              SettingsRow(
                icon: Icons.mail_outline_rounded,
                label: l10n.authEmail,
                trailing: user?.email ?? '—',
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
                onTap: () =>
                    AppSnack.show(context, l10n.profileChangePasswordSoon),
              ),
            ],
          ),
          Gap.gapMd,
          SettingsGroup(
            rows: [
              SettingsRow(
                icon: Icons.delete_outline_rounded,
                label: l10n.profileDeleteAccount,
                danger: true,
                onTap: () => _confirmDelete(context, ref),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Future<void> _confirmDelete(BuildContext context, WidgetRef ref) async {
    final l10n = context.l10n;
    final ok = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(l10n.profileDeleteConfirmTitle),
        content: Text(l10n.profileDeleteConfirmBody),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(l10n.commonCancel),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
            onPressed: () => Navigator.pop(context, true),
            child: Text(l10n.commonDelete),
          ),
        ],
      ),
    );
    if ((ok ?? false) && context.mounted) {
      AppSnack.show(context, l10n.profileDeleteRequested);
      await ref.read(sessionControllerProvider.notifier).logOut();
    }
  }
}
