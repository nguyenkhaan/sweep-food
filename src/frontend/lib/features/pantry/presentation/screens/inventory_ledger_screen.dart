import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/formatters/quantity_format.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/features/pantry/domain/entities/inventory_ledger.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/inventory_ledger_controller.dart';
import 'package:sweepfood/shared/domain/paginated.dart';

final _dateFmt = DateFormat('dd/MM/yyyy · HH:mm');

/// K-04 Lịch sử biến động kho. [batchId] `null` = toàn kho; [batchName] chỉ để
/// hiển thị tiêu đề khi xem 1 lô.
class InventoryLedgerScreen extends ConsumerStatefulWidget {
  const InventoryLedgerScreen({this.batchId, this.batchName, super.key});

  final String? batchId;
  final String? batchName;

  @override
  ConsumerState<InventoryLedgerScreen> createState() =>
      _InventoryLedgerScreenState();
}

class _InventoryLedgerScreenState
    extends ConsumerState<InventoryLedgerScreen> {
  final _scroll = ScrollController();

  @override
  void initState() {
    super.initState();
    _scroll.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scroll.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scroll.position.pixels >=
        _scroll.position.maxScrollExtent - 400) {
      ref
          .read(inventoryLedgerControllerProvider(widget.batchId).notifier)
          .loadMore();
    }
  }

  @override
  Widget build(BuildContext context) {
    final async =
        ref.watch(inventoryLedgerControllerProvider(widget.batchId));

    return Scaffold(
      appBar: AppBar(
        title: Text(
          widget.batchName != null
              ? 'Lịch sử: ${widget.batchName}'
              : 'Lịch sử biến động kho',
        ),
      ),
      body: RefreshIndicator(
        onRefresh: () => ref
            .read(inventoryLedgerControllerProvider(widget.batchId).notifier)
            .refresh(),
        child: AsyncValueWidget<Paginated<InventoryLedgerEntry>>(
          value: async,
          onRetry: () => ref.invalidate(
            inventoryLedgerControllerProvider(widget.batchId),
          ),
          data: (page) {
            if (page.items.isEmpty) {
              return ListView(
                children: const [
                  SizedBox(height: 100),
                  EmptyState(
                    title: 'Chưa có biến động nào',
                    message:
                        'Các thao tác thêm, dùng, chuyển ngăn, nấu ăn… sẽ được ghi lại ở đây.',
                    icon: Icons.receipt_long_rounded,
                  ),
                ],
              );
            }
            return ListView.separated(
              controller: _scroll,
              padding:
                  const EdgeInsets.fromLTRB(Gap.md, Gap.md, Gap.md, Gap.xxl),
              itemCount: page.items.length + (page.hasMore ? 1 : 0),
              separatorBuilder: (_, __) => const SizedBox(height: Gap.sm),
              itemBuilder: (context, i) {
                if (i >= page.items.length) {
                  return const Padding(
                    padding: EdgeInsets.all(Gap.md),
                    child: Center(
                      child: SizedBox(
                        width: 22,
                        height: 22,
                        child: CircularProgressIndicator(strokeWidth: 2.4),
                      ),
                    ),
                  );
                }
                return _LedgerTile(entry: page.items[i]);
              },
            );
          },
        ),
      ),
    );
  }
}

class _LedgerTile extends StatelessWidget {
  const _LedgerTile({required this.entry});

  final InventoryLedgerEntry entry;

  @override
  Widget build(BuildContext context) {
    final up = entry.isIncrease;
    final (icon, tint) = switch (entry.eventType) {
      LedgerEventType.initialStock ||
      LedgerEventType.leftoverCreated =>
        (Icons.add_rounded, context.colors.primary),
      LedgerEventType.cookingConsumption ||
      LedgerEventType.manualConsumption =>
        (Icons.restaurant_rounded, context.sweep.textSecondary),
      LedgerEventType.discarded => (Icons.delete_outline_rounded, context.colors.error),
      LedgerEventType.moved => (Icons.swap_horiz_rounded, context.sweep.textSecondary),
      LedgerEventType.metadataUpdated => (Icons.edit_outlined, context.sweep.textSecondary),
      LedgerEventType.archived => (Icons.archive_outlined, context.sweep.textSecondary),
      _ => (Icons.tune_rounded, context.sweep.textSecondary),
    };

    return Container(
      padding: const EdgeInsets.all(Gap.md),
      decoration: BoxDecoration(
        color: context.colors.surfaceContainerLowest,
        borderRadius: Radii.brMd,
        border: Border.all(color: context.sweep.hairline),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 38,
            height: 38,
            decoration: BoxDecoration(
              color: context.sweep.subtleFill,
              borderRadius: Radii.brSm,
            ),
            child: Icon(icon, size: 19, color: tint),
          ),
          Gap.gapSm,
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(entry.eventType.label, style: context.text.titleSmall),
                const SizedBox(height: 2),
                Text(
                  _dateFmt.format(entry.createdAt.toLocal()),
                  style: context.text.bodySmall?.copyWith(
                    color: context.sweep.textTertiary,
                  ),
                ),
                if (entry.reason != null && entry.reason!.isNotEmpty) ...[
                  const SizedBox(height: 2),
                  Text(
                    entry.reason!,
                    style: context.text.bodySmall?.copyWith(
                      color: context.sweep.textSecondary,
                    ),
                  ),
                ],
              ],
            ),
          ),
          Gap.gapSm,
          if (entry.eventType.affectsQuantity)
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '${up ? '+' : '−'}${formatQuantity(entry.quantityDelta.abs(), entry.unit)}',
                  style: context.text.titleSmall?.copyWith(
                    fontWeight: FontWeight.w700,
                    color: up ? context.colors.primary : context.sweep.textSecondary,
                  ),
                ),
                Text(
                  '${formatQuantity(entry.quantityBefore, entry.unit)} → ${formatQuantity(entry.quantityAfter, entry.unit)}',
                  style: context.text.labelSmall?.copyWith(
                    color: context.sweep.textTertiary,
                  ),
                ),
              ],
            ),
        ],
      ),
    );
  }
}
