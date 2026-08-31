import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/app_snackbar.dart';
import 'package:frontend/features/auth/presentation/controllers/session_controller.dart';
import 'package:frontend/features/settings/presentation/widgets/settings_group.dart';

/// P-01a Hồ sơ & mật khẩu.
class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(sessionControllerProvider).asData?.value?.user;

    return Scaffold(
      appBar: AppBar(title: const Text('Hồ sơ & mật khẩu')),
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
            label: 'Thông tin',
            rows: [
              SettingsRow(
                icon: Icons.badge_outlined,
                label: 'Họ và tên',
                trailing: user?.name ?? '—',
                onTap: () => AppSnack.show(context, 'Sửa hồ sơ sẽ có ở bản sau.'),
              ),
              SettingsRow(
                icon: Icons.mail_outline_rounded,
                label: 'Email',
                trailing: user?.email ?? '—',
              ),
            ],
          ),
          Gap.gapMd,
          SettingsGroup(
            label: 'Bảo mật',
            rows: [
              SettingsRow(
                icon: Icons.lock_outline_rounded,
                label: 'Đổi mật khẩu',
                onTap: () =>
                    AppSnack.show(context, 'Đổi mật khẩu sẽ có ở bản sau.'),
              ),
            ],
          ),
          Gap.gapMd,
          SettingsGroup(
            rows: [
              SettingsRow(
                icon: Icons.delete_outline_rounded,
                label: 'Xóa tài khoản',
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
    final ok = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Xóa tài khoản?'),
        content: const Text(
          'Toàn bộ dữ liệu tủ bếp sẽ bị xóa vĩnh viễn. Hành động này không thể '
          'hoàn tác.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Hủy'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Xóa'),
          ),
        ],
      ),
    );
    if ((ok ?? false) && context.mounted) {
      AppSnack.show(context, 'Yêu cầu xóa tài khoản đã được ghi nhận.');
      await ref.read(sessionControllerProvider.notifier).logOut();
    }
  }
}
