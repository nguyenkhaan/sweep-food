import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/error/failure.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_dialog.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/features/auth/domain/entities/active_session.dart';
import 'package:sweepfood/features/auth/presentation/controllers/active_sessions_controller.dart';

final _dateFmt = DateFormat('dd/MM/yyyy · HH:mm');

/// P-01c — Thiết bị & phiên đăng nhập (Concept B · Format 1).
class ActiveSessionsScreen extends ConsumerWidget {
  const ActiveSessionsScreen({super.key});

  Future<void> _revoke(
    BuildContext context,
    WidgetRef ref,
    ActiveSession session,
  ) async {
    final ok = await showAppConfirmDialog(
      context,
      title: 'Thu hồi phiên này?',
      message:
          'Thiết bị "${session.deviceLabel}" sẽ bị đăng xuất trong lần yêu cầu '
          'tiếp theo. Nếu đây là thiết bị bạn đang dùng, bạn sẽ phải đăng nhập lại.',
      cancelLabel: 'Hủy',
      confirmLabel: 'Thu hồi',
      destructive: true,
    );
    if (ok != true || !context.mounted) return;

    try {
      await ref
          .read(activeSessionsControllerProvider.notifier)
          .revoke(session.id);
      if (context.mounted) AppSnack.show(context, 'Đã thu hồi phiên đăng nhập');
    } on Failure catch (f) {
      if (context.mounted) AppSnack.show(context, f.message);
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(activeSessionsControllerProvider);
    final cs = context.colors;

    return EmeraldSystemOverlay(
      child: Scaffold(
        backgroundColor: cs.surface,
        body: Column(
          children: [
            const EmeraldSplitHeader(
              title: 'Thiết bị và phiên đăng nhập',
              subtitle: 'Thu hồi một phiên sẽ đăng xuất thiết bị đó',
            ),
            Expanded(
              child: RefreshIndicator(
                onRefresh: () =>
                    ref.read(activeSessionsControllerProvider.notifier).refresh(),
                child: AsyncValueWidget<List<ActiveSession>>(
                  value: async,
                  onRetry: () =>
                      ref.invalidate(activeSessionsControllerProvider),
                  data: (sessions) {
                    if (sessions.isEmpty) {
                      return ListView(
                        padding: const EdgeInsets.fromLTRB(
                          Gap.lg,
                          Gap.xl,
                          Gap.lg,
                          Gap.xxl,
                        ),
                        children: const [
                          EmptyState(
                            title: 'Không có phiên nào',
                            message:
                                'Tài khoản của bạn hiện không có phiên đăng nhập '
                                'nào đang hoạt động.',
                            icon: AppIcons.smartphone,
                          ),
                        ],
                      );
                    }

                    return ListView(
                      padding: EdgeInsets.fromLTRB(
                        Gap.lg,
                        Gap.xs,
                        Gap.lg,
                        MediaQuery.paddingOf(context).bottom + Gap.xxl,
                      ),
                      children: [
                        Container(
                          decoration: BoxDecoration(
                            color: cs.surfaceContainerLowest,
                            borderRadius: Radii.brXl,
                            border: Border.all(color: context.sweep.hairline),
                            boxShadow: Shadows.e1,
                          ),
                          clipBehavior: Clip.antiAlias,
                          child: Column(
                            children: [
                              for (var i = 0; i < sessions.length; i++) ...[
                                _SessionTile(
                                  session: sessions[i],
                                  onRevoke: () =>
                                      _revoke(context, ref, sessions[i]),
                                ),
                                if (i < sessions.length - 1)
                                  Divider(
                                    height: 1,
                                    indent: 68,
                                    color: context.sweep.hairline,
                                  ),
                              ],
                            ],
                          ),
                        ),
                      ],
                    );
                  },
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SessionTile extends StatelessWidget {
  const _SessionTile({required this.session, required this.onRevoke});

  final ActiveSession session;
  final VoidCallback onRevoke;

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    final sweep = context.sweep;
    final lines = <String>[
      if (session.ipAddress?.trim().isNotEmpty ?? false)
        'IP: ${session.ipAddress!.trim()}',
      'Đăng nhập: ${_dateFmt.format(session.createdAt.toLocal())}',
      if (session.lastUsedAt != null)
        'Hoạt động gần nhất: ${_relative(session.lastUsedAt!)}',
      'Hết hạn: ${_dateFmt.format(session.expiresAt.toLocal())}',
    ];

    return Padding(
      padding: const EdgeInsets.fromLTRB(Gap.md, Gap.sm + 4, Gap.sm, Gap.sm + 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: cs.primaryContainer,
              borderRadius: Radii.brMd,
            ),
            child: Icon(AppIcons.smartphone, size: 19, color: cs.primary),
          ),
          const SizedBox(width: Gap.sm + 2),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  session.deviceLabel,
                  style: context.text.titleSmall?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 2),
                for (final line in lines)
                  Text(
                    line,
                    style: context.text.bodySmall?.copyWith(
                      color: sweep.textSecondary,
                    ),
                  ),
              ],
            ),
          ),
          TextButton(
            onPressed: onRevoke,
            style: TextButton.styleFrom(foregroundColor: cs.error),
            child: const Text('Thu hồi'),
          ),
        ],
      ),
    );
  }

  String _relative(DateTime t) {
    final d = DateTime.now().difference(t.toLocal());
    if (d.inMinutes < 1) return 'vừa xong';
    if (d.inMinutes < 60) return '${d.inMinutes} phút trước';
    if (d.inHours < 24) return '${d.inHours} giờ trước';
    if (d.inDays < 30) return '${d.inDays} ngày trước';
    return _dateFmt.format(t.toLocal());
  }
}
