import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/error/failure.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/features/auth/domain/entities/active_session.dart';
import 'package:sweepfood/features/auth/presentation/controllers/active_sessions_controller.dart';

final _dateFmt = DateFormat('dd/MM/yyyy · HH:mm');

/// P-01c — Thiết bị & phiên đăng nhập. Lists the account's active login
/// sessions and lets the user revoke them one by one.
class ActiveSessionsScreen extends ConsumerWidget {
  const ActiveSessionsScreen({super.key});

  Future<void> _revoke(
    BuildContext context,
    WidgetRef ref,
    ActiveSession session,
  ) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Thu hồi phiên này?'),
        content: Text(
          'Thiết bị "${session.deviceLabel}" sẽ bị đăng xuất trong lần yêu cầu '
          'tiếp theo. Nếu đây là thiết bị bạn đang dùng, bạn sẽ phải đăng nhập lại.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Hủy'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(ctx).colorScheme.error,
            ),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Thu hồi'),
          ),
        ],
      ),
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

    return Scaffold(
      appBar: AppBar(title: const Text('Thiết bị & phiên đăng nhập')),
      body: RefreshIndicator(
        onRefresh: () =>
            ref.read(activeSessionsControllerProvider.notifier).refresh(),
        child: AsyncValueWidget<List<ActiveSession>>(
          value: async,
          onRetry: () => ref.invalidate(activeSessionsControllerProvider),
          data: (sessions) {
            if (sessions.isEmpty) {
              return ListView(
                children: const [
                  SizedBox(height: 100),
                  EmptyState(
                    title: 'Không có phiên nào',
                    message: 'Tài khoản của bạn hiện không có phiên đăng nhập '
                        'nào đang hoạt động.',
                    icon: Icons.devices_rounded,
                  ),
                ],
              );
            }

            return ListView.separated(
              padding: const EdgeInsets.fromLTRB(Gap.md, Gap.md, Gap.md, Gap.xxl),
              itemCount: sessions.length + 1,
              separatorBuilder: (_, __) => const SizedBox(height: Gap.sm),
              itemBuilder: (context, i) {
                if (i == 0) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: Gap.xs),
                    child: Text(
                      'Đây là các thiết bị đang đăng nhập vào tài khoản của bạn. '
                      'Thu hồi một phiên sẽ đăng xuất thiết bị đó.',
                      style: context.text.bodySmall?.copyWith(
                        color: context.sweep.textSecondary,
                      ),
                    ),
                  );
                }
                return _SessionTile(
                  session: sessions[i - 1],
                  onRevoke: () => _revoke(context, ref, sessions[i - 1]),
                );
              },
            );
          },
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
    final lines = <String>[
      if (session.ipAddress?.trim().isNotEmpty ?? false)
        'IP: ${session.ipAddress!.trim()}',
      'Đăng nhập: ${_dateFmt.format(session.createdAt.toLocal())}',
      if (session.lastUsedAt != null)
        'Hoạt động gần nhất: ${_relative(session.lastUsedAt!)}',
      'Hết hạn: ${_dateFmt.format(session.expiresAt.toLocal())}',
    ];

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: Radii.brMd,
        side: BorderSide(color: context.sweep.hairline),
      ),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(Gap.md, Gap.sm, Gap.sm, Gap.sm),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: context.sweep.subtleFill,
                borderRadius: Radii.brMd,
              ),
              child: Icon(
                Icons.devices_rounded,
                color: context.sweep.textSecondary,
              ),
            ),
            const SizedBox(width: Gap.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(session.deviceLabel, style: context.text.titleSmall),
                  const SizedBox(height: 2),
                  for (final line in lines)
                    Text(
                      line,
                      style: context.text.bodySmall?.copyWith(
                        color: context.sweep.textSecondary,
                      ),
                    ),
                ],
              ),
            ),
            TextButton(
              onPressed: onRevoke,
              style: TextButton.styleFrom(
                foregroundColor: Theme.of(context).colorScheme.error,
              ),
              child: const Text('Thu hồi'),
            ),
          ],
        ),
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
