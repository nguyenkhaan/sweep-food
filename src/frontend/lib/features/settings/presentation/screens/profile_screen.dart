import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/features/auth/presentation/controllers/session_controller.dart';
import 'package:sweepfood/features/settings/presentation/widgets/settings_group.dart';

/// P-01a Hồ sơ & mật khẩu (Concept B Split Hero + 100% Lucide icons).
class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;
    final user = ref.watch(sessionControllerProvider).asData?.value?.user;

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
            SliverToBoxAdapter(
              child: DecoratedBox(
                decoration: BoxDecoration(color: sweep.heroSurface),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    SafeArea(
                      bottom: false,
                      child: Padding(
                        padding: const EdgeInsets.fromLTRB(
                          Gap.lg,
                          Gap.sm,
                          Gap.lg,
                          Gap.lg,
                        ),
                        child: Column(
                          children: [
                            Row(
                              children: [
                                Material(
                                  color: sweep.heroSurfaceElevated,
                                  shape: RoundedRectangleBorder(
                                    borderRadius: Radii.brMd,
                                    side: BorderSide(
                                      color: sweep.onHeroSurface.withValues(
                                        alpha: 0.14,
                                      ),
                                    ),
                                  ),
                                  child: InkWell(
                                    borderRadius: Radii.brMd,
                                    onTap: () => context.pop(),
                                    child: SizedBox(
                                      width: 40,
                                      height: 40,
                                      child: Icon(
                                        AppIcons.arrowLeft,
                                        size: 19,
                                        color: sweep.onHeroSurface,
                                      ),
                                    ),
                                  ),
                                ),
                                const SizedBox(width: Gap.sm + 2),
                                Expanded(
                                  child: Text(
                                    l10n.settingsProfilePassword,
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                    style: context.text.titleLarge?.copyWith(
                                      color: sweep.onHeroSurface,
                                      fontWeight: FontWeight.w800,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            Gap.gapMd,
                            Container(
                              width: 72,
                              height: 72,
                              alignment: Alignment.center,
                              decoration: BoxDecoration(
                                color: sweep.heroSurfaceElevated,
                                shape: BoxShape.circle,
                                border: Border.all(
                                  color: sweep.onHeroSurface.withValues(
                                    alpha: 0.28,
                                  ),
                                  width: 2,
                                ),
                              ),
                              child: Text(
                                user?.initials ?? '?',
                                style: context.text.headlineMedium?.copyWith(
                                  color: sweep.onHeroSurface,
                                  fontWeight: FontWeight.w800,
                                ),
                              ),
                            ),
                            const SizedBox(height: Gap.sm),
                            Text(
                              user?.name ?? '—',
                              style: context.text.titleMedium?.copyWith(
                                color: sweep.onHeroSurface,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            if ((user?.email ?? '').trim().isNotEmpty) ...[
                              const SizedBox(height: 2),
                              Text(
                                user!.email!,
                                style: context.text.bodySmall?.copyWith(
                                  color: sweep.onHeroMuted,
                                ),
                              ),
                            ],
                          ],
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
              ),
            ),
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(
                Gap.lg,
                Gap.xs,
                Gap.lg,
                Gap.xxl,
              ),
              sliver: SliverList.list(
                children: [
                  SettingsGroup(
                    label: l10n.profileGroupInfo,
                    rows: [
                      SettingsRow(
                        icon: AppIcons.profile,
                        label: l10n.authFullName,
                        trailing: user?.name ?? '—',
                        onTap: () => context.push(Routes.settingsEditProfile),
                      ),
                      SettingsRow(
                        icon: AppIcons.mail,
                        label: l10n.authEmail,
                        trailing: user?.email ?? '—',
                        onTap: () => context.push(Routes.settingsChangeEmail),
                      ),
                      SettingsRow(
                        icon: AppIcons.phone,
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
                        icon: AppIcons.lock,
                        label: l10n.profileChangePassword,
                        onTap: () =>
                            context.push(Routes.settingsChangePassword),
                      ),
                      SettingsRow(
                        icon: AppIcons.smartphone,
                        label: 'Thiết bị và phiên đăng nhập',
                        onTap: () => context.push(Routes.settingsSessions),
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
}
