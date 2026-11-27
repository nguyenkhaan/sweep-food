import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/formatters/quantity_format.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/features/pantry/domain/entities/inventory_ledger.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/inventory_ledger_controller.dart';
import 'package:sweepfood/shared/domain/paginated.dart';

final _dateFmt = DateFormat('dd/MM/yyyy · HH:mm');

/// K-04 Lịch sử biến động kho (Concept B · Format 1: Emerald Header + Grouped Card).
class InventoryLedgerScreen extends ConsumerStatefulWidget {
  const InventoryLedgerScreen({this.batchId, this.batchName, super.key});

  final String? batchId;
  final String? batchName;

  @override
  ConsumerState<InventoryLedgerScreen> createState() =>
      _InventoryLedgerScreenState();
}

class _InventoryLedgerScreenState extends ConsumerState<InventoryLedgerScreen> {
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
    if (_scroll.position.pixels >= _scroll.position.maxScrollExtent - 400) {
      ref
          .read(inventoryLedgerControllerProvider(widget.batchId).notifier)
          .loadMore();
    }
  }

  @override
  Widget build(BuildContext context) {
    final async = ref.watch(inventoryLedgerControllerProvider(widget.batchId));
    final cs = context.colors;

    return EmeraldSystemOverlay(
      child: Scaffold(
        backgroundColor: cs.surface,
        body: Column(
          children: [
            EmeraldSplitHeader(
              title: widget.batchName != null
                  ? 'Lịch sử kho'
                  : 'Lịch sử biến động kho',
              subtitle: widget.batchName,
            ),
            Expanded(
              child: RefreshIndicator(
                onRefresh: () => ref
                    .read(
                      inventoryLedgerControllerProvider(
                        widget.batchId,
                      ).notifier,
                    )
                    .refresh(),
                child: AsyncValueWidget<Paginated<InventoryLedgerEntry>>(
                  value: async,
                  onRetry: () => ref.invalidate(
                    inventoryLedgerControllerProvider(widget.batchId),
                  ),
                  data: (page) {
                    if (page.items.isEmpty) {
                      return ListView(
                        padding: const EdgeInsets.fromLTRB(
                          Gap.lg,
                          Gap.xl,
                          Gap.lg,
                          Gap.xxl,
                        ),
                        children: const [
                          EmptyState(
                            illustrationAsset:
                                'assets/illustrations/empty_ledger.svg',
                            title: 'Chưa có biến động nào',
                            message:
                                'Các thao tác thêm, dùng, chuyển ngăn, nấu ăn… sẽ được ghi lại ở đây.',
                            icon: AppIcons.receipt,
                          ),
                        ],
                      );
                    }
                    return ListView(
                      controller: _scroll,
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
                              for (var i = 0; i < page.items.length; i++) ...[
                                _LedgerTile(entry: page.items[i]),
                                if (i < page.items.length - 1)
                                  Divider(
                                    height: 1,
                                    indent: 66,
                                    color: context.sweep.hairline,
                                  ),
                              ],
                            ],
                          ),
                        ),
                        if (page.hasMore)
                          const Padding(
                            padding: EdgeInsets.all(Gap.md),
                            child: Center(
                              child: SizedBox(
                                width: 22,
                                height: 22,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2.4,
                                ),
                              ),
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

class _LedgerTile extends StatelessWidget {
  const _LedgerTile({required this.entry});

  final InventoryLedgerEntry entry;

  @override
  Widget build(BuildContext context) {
    final up = entry.isIncrease;
    final cs = context.colors;
    final sweep = context.sweep;
    final (icon, fg, bg) = switch (entry.eventType) {
      LedgerEventType.initialStock || LedgerEventType.leftoverCreated => (
        AppIcons.add,
        cs.primary,
        cs.primaryContainer,
      ),
      LedgerEventType.cookingConsumption || LedgerEventType.manualConsumption =>
        (AppIcons.utensils, sweep.ctaWarm, sweep.culinaryAccentBg),
      LedgerEventType.discarded => (
        AppIcons.trash,
        sweep.expired.fg,
        sweep.expired.bg,
      ),
      LedgerEventType.moved => (
        AppIcons.arrowLeftRight,
        sweep.textSecondary,
        sweep.subtleFill,
      ),
      LedgerEventType.metadataUpdated => (
        AppIcons.edit,
        sweep.textSecondary,
        sweep.subtleFill,
      ),
      LedgerEventType.archived => (
        AppIcons.archive,
        sweep.textSecondary,
        sweep.subtleFill,
      ),
      _ => (AppIcons.filter, sweep.textSecondary, sweep.subtleFill),
    };

    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: Gap.md,
        vertical: Gap.sm + 4,
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 38,
            height: 38,
            decoration: BoxDecoration(color: bg, borderRadius: Radii.brMd),
            child: Icon(icon, size: 18, color: fg),
          ),
          const SizedBox(width: Gap.sm + 2),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  entry.eventType.label,
                  style: context.text.titleSmall?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  _dateFmt.format(entry.createdAt.toLocal()),
                  style: context.text.bodySmall?.copyWith(
                    color: sweep.textTertiary,
                  ),
                ),
                if (entry.reason != null && entry.reason!.isNotEmpty) ...[
                  const SizedBox(height: 2),
                  Text(
                    _localizeReason(context, entry.reason!),
                    style: context.text.bodySmall?.copyWith(
                      color: sweep.textSecondary,
                    ),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(width: Gap.sm),
          if (entry.eventType.affectsQuantity)
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '${up ? '+' : '−'}${formatQuantity(entry.quantityDelta.abs(), entry.unit)}',
                  style: AppTypography.tabular(
                    context.text.titleSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: up ? cs.primary : sweep.textSecondary,
                    ),
                  ),
                ),
                Text(
                  '${formatQuantity(entry.quantityBefore, entry.unit)} → ${formatQuantity(entry.quantityAfter, entry.unit)}',
                  style: context.text.labelSmall?.copyWith(
                    color: sweep.textTertiary,
                  ),
                ),
              ],
            ),
        ],
      ),
    );
  }

  static String _localizeReason(BuildContext context, String raw) {
    final isVi = Localizations.localeOf(context).languageCode == 'vi';
    if (!isVi) return raw;
    return switch (raw.trim().toLowerCase()) {
      'freshcheck assessment' => 'Đánh giá độ tươi FreshCheck',
      'manual batch creation' => 'Thêm thủ công vào kho',
      'user deleted from inventory' => 'Người dùng xóa khỏi kho',
      'manual consumption' => 'Người dùng ghi nhận đã dùng',
      _ => raw,
    };
  }
}
