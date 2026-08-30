import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/utils/extensions/date_time_x.dart';
import 'package:frontend/core/utils/formatters/currency_vnd.dart';
import 'package:frontend/core/utils/formatters/expiry_text.dart';
import 'package:frontend/core/widgets/app_snackbar.dart';
import 'package:frontend/core/widgets/empty_state.dart';
import 'package:frontend/core/widgets/expiry_badge.dart';
import 'package:frontend/core/widgets/primary_button.dart';
import 'package:frontend/core/widgets/secondary_button.dart';
import 'package:frontend/core/widgets/tier_chip.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item.dart';
import 'package:frontend/features/pantry/presentation/controllers/pantry_item_controller.dart';
import 'package:frontend/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:frontend/features/pantry/presentation/widgets/adjust_quantity_sheet.dart';
import 'package:go_router/go_router.dart';

/// K-02 — Chi tiết nguyên liệu.
class PantryItemDetailScreen extends ConsumerStatefulWidget {
  const PantryItemDetailScreen({required this.itemId, super.key});

  final String itemId;

  @override
  ConsumerState<PantryItemDetailScreen> createState() =>
      _PantryItemDetailScreenState();
}

class _PantryItemDetailScreenState
    extends ConsumerState<PantryItemDetailScreen> {
  bool _busy = false;

  Future<void> _consumeAll(PantryItem item) async {
    setState(() => _busy = true);
    try {
      await ref
          .read(pantryListControllerProvider.notifier)
          .consume(item.id, quantityUsed: item.quantity);
      if (!mounted) return;
      context.pop();
      AppSnack.show(context, 'Đã dùng hết ${item.name}');
    } catch (_) {
      if (!mounted) return;
      setState(() => _busy = false);
      AppSnack.show(context, 'Không cập nhật được. Thử lại.');
    }
  }

  Future<void> _delete(PantryItem item) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Xóa nguyên liệu?'),
        content: Text('“${item.name}” sẽ bị xóa khỏi kho.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Hủy'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Xóa'),
          ),
        ],
      ),
    );
    if (confirmed != true) return;
    setState(() => _busy = true);
    try {
      await ref.read(pantryListControllerProvider.notifier).delete(item.id);
      if (!mounted) return;
      context.pop();
      AppSnack.show(context, 'Đã xóa ${item.name}');
    } catch (_) {
      if (!mounted) return;
      setState(() => _busy = false);
      AppSnack.show(context, 'Không xóa được. Thử lại.');
    }
  }

  @override
  Widget build(BuildContext context) {
    final item = ref.watch(pantryItemByIdProvider(widget.itemId));

    if (item == null) {
      return Scaffold(
        appBar: AppBar(),
        body: const EmptyState(
          title: 'Không tìm thấy nguyên liệu',
          message: 'Có thể nó đã được dùng hết hoặc đã xóa khỏi kho.',
          icon: Icons.inventory_2_outlined,
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(item.name),
        actions: [
          IconButton(
            tooltip: 'Sửa',
            icon: const Icon(Icons.edit_outlined),
            onPressed: _busy
                ? null
                : () => context.push('${Routes.pantry}/add', extra: item.id),
          ),
          PopupMenuButton<String>(
            enabled: !_busy,
            onSelected: (v) {
              if (v == 'delete') _delete(item);
            },
            itemBuilder: (_) => const [
              PopupMenuItem(value: 'delete', child: Text('Xóa khỏi kho')),
            ],
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.md, Gap.lg, Gap.xxl),
        children: [
          Row(
            children: [
              TierChip(item.storageTier),
              Gap.gapXs,
              ExpiryBadge(daysUntilExpiry: item.daysUntilExpiry),
            ],
          ),
          Gap.gapSm,
          Text(item.name, style: context.text.headlineSmall),
          const SizedBox(height: 2),
          Text(
            item.category,
            style: context.text.bodyMedium?.copyWith(
              color: context.sweep.textSecondary,
            ),
          ),
          Gap.gapLg,
          Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Expanded(
                child: _StatTile(
                  icon: Icons.scale_outlined,
                  label: 'Số lượng',
                  value: item.quantityLabel,
                ),
              ),
              const SizedBox(width: Gap.sm),
              Expanded(
                child: _StatTile(
                  icon: Icons.event_outlined,
                  label: 'Hạn dùng',
                  value: item.expiryDate?.ddMM ?? '—',
                  sub: expiryText(item.daysUntilExpiry),
                ),
              ),
              const SizedBox(width: Gap.sm),
              Expanded(
                child: item.priceVnd != null
                    ? _StatTile(
                        icon: Icons.payments_outlined,
                        label: 'Giá',
                        value: formatVnd(item.priceVnd!),
                      )
                    : _StatTile(
                        icon: Icons.schedule_outlined,
                        label: 'Bảo quản',
                        value: item.referenceShelfLifeDays != null
                            ? '~${item.referenceShelfLifeDays} ngày'
                            : '—',
                      ),
              ),
            ],
          ),
          Gap.gapLg,
          _DetailCard(item: item),
          Gap.gapMd,
          SecondaryButton(
            label: 'Tìm món nấu từ nguyên liệu này',
            icon: Icons.restaurant_menu_rounded,
            onPressed: () =>
                AppSnack.show(context, 'Gợi ý món sẽ có ở bước kế tiếp.'),
          ),
        ],
      ),
      bottomNavigationBar: _ActionBar(
        busy: _busy,
        onAdjust: () => AdjustQuantitySheet.show(context, item),
        onConsumeAll: () => _consumeAll(item),
      ),
    );
  }
}

class _StatTile extends StatelessWidget {
  const _StatTile({
    required this.icon,
    required this.label,
    required this.value,
    this.sub,
  });

  final IconData icon;
  final String label;
  final String value;
  final String? sub;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(Gap.sm),
      decoration: BoxDecoration(
        color: context.sweep.subtleFill,
        borderRadius: Radii.brMd,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 16, color: context.sweep.textTertiary),
          Gap.gapXs,
          Text(
            label,
            style: context.text.labelSmall?.copyWith(letterSpacing: 0),
          ),
          const SizedBox(height: 2),
          Text(
            value,
            style: context.text.titleSmall,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          if (sub != null)
            Text(
              sub!,
              style: context.text.labelSmall?.copyWith(
                letterSpacing: 0,
                color: context.sweep.textTertiary,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
        ],
      ),
    );
  }
}

class _DetailCard extends StatelessWidget {
  const _DetailCard({required this.item});

  final PantryItem item;

  @override
  Widget build(BuildContext context) {
    final rows = <(String, String)>[
      ('Vị trí bảo quản', item.storageTier.label),
      ('Ngày thêm', item.addedAt.ddMMyyyy),
      if (item.packedDate != null)
        ('Ngày đóng gói / mua', item.packedDate!.ddMMyyyy),
      ('Nguồn nhập', item.source.label),
      if (item.referenceShelfLifeDays != null)
        ('Bảo quản tham khảo', '${item.referenceShelfLifeDays} ngày'),
    ];

    return Container(
      padding: const EdgeInsets.all(Gap.md),
      decoration: BoxDecoration(
        borderRadius: Radii.brLg,
        border: Border.all(color: context.sweep.hairline),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Chi tiết', style: context.text.titleSmall),
          Gap.gapXs,
          for (final (label, value) in rows)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 5),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SizedBox(
                    width: 132,
                    child: Text(
                      label,
                      style: context.text.bodyMedium?.copyWith(
                        color: context.sweep.textSecondary,
                      ),
                    ),
                  ),
                  Expanded(
                    child: Text(
                      value,
                      style: context.text.bodyMedium,
                      textAlign: TextAlign.right,
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

class _ActionBar extends StatelessWidget {
  const _ActionBar({
    required this.busy,
    required this.onAdjust,
    required this.onConsumeAll,
  });

  final bool busy;
  final VoidCallback onAdjust;
  final VoidCallback onConsumeAll;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      minimum: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.sm),
      child: Row(
        children: [
          Expanded(
            child: SecondaryButton(
              label: 'Điều chỉnh',
              icon: Icons.tune_rounded,
              onPressed: busy ? null : onAdjust,
            ),
          ),
          const SizedBox(width: Gap.sm),
          Expanded(
            child: PrimaryButton(
              label: 'Đã dùng hết',
              icon: Icons.check_rounded,
              loading: busy,
              onPressed: busy ? null : onConsumeAll,
            ),
          ),
        ],
      ),
    );
  }
}
