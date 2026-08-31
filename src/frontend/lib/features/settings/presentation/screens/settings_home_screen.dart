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
    final user = ref.watch(sessionControllerProvider).asData?.value?.user;

    return Scaffold(
      appBar: AppBar(title: const Text('Cá nhân')),
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
            label: 'Tài khoản',
            rows: [
              SettingsRow(
                icon: Icons.person_outline_rounded,
                label: 'Hồ sơ & mật khẩu',
                onTap: () => context.push(Routes.settingsProfile),
              ),
              SettingsRow(
                icon: Icons.workspace_premium_outlined,
                label: 'Gói dịch vụ',
                trailing: 'Premium sắp có',
                onTap: () => context.push(Routes.settingsSubscription),
              ),
              SettingsRow(
                icon: Icons.group_outlined,
                label: 'Chia sẻ tủ bếp',
                badge: 'Sắp có',
                onTap: () => context.push(Routes.settingsPantrySharing),
              ),
            ],
          ),
          Gap.gapMd,
          SettingsGroup(
            label: 'Kế hoạch bữa ăn',
            rows: [
              SettingsRow(
                icon: Icons.calendar_month_rounded,
                label: 'Thực đơn tuần',
                onTap: () => context.push(Routes.mealPlan),
              ),
              SettingsRow(
                icon: Icons.insights_rounded,
                label: 'Báo cáo chống lãng phí',
                onTap: () => context.push(Routes.reports),
              ),
            ],
          ),
          Gap.gapMd,
          SettingsGroup(
            label: 'Ứng dụng',
            rows: [
              SettingsRow(
                icon: Icons.tune_rounded,
                label: 'Tùy chọn',
                onTap: () => context.push(Routes.settingsPreferences),
              ),
              SettingsRow(
                icon: Icons.notifications_none_rounded,
                label: 'Thông báo',
                onTap: () => context.push(Routes.settingsNotifications),
              ),
              const SettingsRow(
                icon: Icons.language_rounded,
                label: 'Ngôn ngữ',
                trailing: 'Tiếng Việt',
              ),
            ],
          ),
          Gap.gapMd,
          SettingsGroup(
            label: 'Khác',
            rows: [
              SettingsRow(
                icon: Icons.info_outline_rounded,
                label: 'Giới thiệu & nguồn dữ liệu',
                onTap: () => context.push(Routes.settingsAbout),
              ),
              SettingsRow(
                icon: Icons.logout_rounded,
                label: 'Đăng xuất',
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
    final ok = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Đăng xuất?'),
        content: const Text('Bạn sẽ cần đăng nhập lại để dùng SweepFood.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Hủy'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Đăng xuất'),
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
                    style: context.text.titleMedium
                        ?.copyWith(fontWeight: FontWeight.w700),
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
            Icon(Icons.chevron_right_rounded, color: context.sweep.textTertiary),
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
                      'Bản đầy đủ · miễn phí',
                      style: context.text.titleSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                        color: context.colors.onPrimaryContainer,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'Premium (đồng bộ, báo cáo nâng cao…) đang phát triển',
                      style: context.text.bodySmall?.copyWith(
                        color: context.colors.onPrimaryContainer
                            .withValues(alpha: 0.8),
                      ),
                    ),
                  ],
                ),
              ),
              Gap.gapSm,
              Text(
                'Quan tâm',
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
