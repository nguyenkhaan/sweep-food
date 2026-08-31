import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/features/auth/presentation/controllers/session_controller.dart';
import 'package:frontend/features/settings/domain/entities/pantry_member.dart';
import 'package:go_router/go_router.dart';

/// P-05 Chia sẻ tủ bếp — **"Sắp có"** in the MVP: a preview of the member list
/// with a disabled invite and a nudge toward the paywall.
class PantrySharingScreen extends ConsumerWidget {
  const PantrySharingScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final me = ref.watch(sessionControllerProvider).asData?.value?.user;
    final members = [
      PantryMember(
        name: me?.name ?? l10n.commonYou,
        role: PantryMemberRole.owner,
      ),
      const PantryMember(name: 'Lê B', role: PantryMemberRole.editor),
      const PantryMember(
        name: 'Trần C',
        role: PantryMemberRole.editor,
        status: PantryMemberStatus.invited,
      ),
    ];

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.settingsPantrySharing),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: Gap.md),
            child: Chip(
              label: Text(l10n.commonComingSoon),
              visualDensity: VisualDensity.compact,
              backgroundColor: context.colors.primaryContainer,
              side: BorderSide.none,
            ),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.md, Gap.lg, Gap.xxl),
        children: [
          Text(
            l10n.pantrySharingIntro,
            style: context.text.bodyMedium?.copyWith(
              color: context.sweep.textSecondary,
            ),
          ),
          Gap.gapMd,
          Opacity(
            opacity: 0.6,
            child: Column(
              children: [for (final m in members) _MemberRow(member: m)],
            ),
          ),
          Gap.gapMd,
          DottedInviteButton(onTap: () => context.push(Routes.paywall)),
          Gap.gapMd,
          Text(
            l10n.pantrySharingFootnote,
            style: context.text.bodySmall?.copyWith(
              color: context.sweep.textTertiary,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }
}

class _MemberRow extends StatelessWidget {
  const _MemberRow({required this.member});

  final PantryMember member;

  @override
  Widget build(BuildContext context) {
    final pending = member.status == PantryMemberStatus.invited;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: Gap.xs),
      child: Row(
        children: [
          CircleAvatar(
            radius: 18,
            backgroundColor: context.colors.primaryContainer,
            child: Text(
              member.initials,
              style: TextStyle(
                color: context.colors.onPrimaryContainer,
                fontWeight: FontWeight.w700,
                fontSize: 13,
              ),
            ),
          ),
          Gap.gapSm,
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  member.name,
                  style: context.text.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  member.roleLabel(context.l10n),
                  style: context.text.bodySmall?.copyWith(
                    color: pending
                        ? context.colors.tertiary
                        : context.sweep.textTertiary,
                  ),
                ),
              ],
            ),
          ),
          if (member.role != PantryMemberRole.owner)
            Icon(
              Icons.close_rounded,
              size: 18,
              color: context.sweep.textTertiary,
            ),
        ],
      ),
    );
  }
}

/// Dashed "Mời thành viên" button — exported so tests/other screens can reuse it.
class DottedInviteButton extends StatelessWidget {
  const DottedInviteButton({required this.onTap, super.key});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: Radii.brLg,
      child: Container(
        padding: const EdgeInsets.all(Gap.md),
        decoration: BoxDecoration(
          borderRadius: Radii.brLg,
          border: Border.all(
            color: context.colors.primary,
            style: BorderStyle.solid,
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.add_rounded, size: 18, color: context.colors.primary),
            Gap.gapXs,
            Text(
              context.l10n.pantrySharingInvite,
              style: context.text.labelLarge?.copyWith(
                color: context.colors.primary,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
