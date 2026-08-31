// lib/features/ingest/presentation/screens/receipt_review_screen.dart
// I-05 Kiểm tra danh sách từ hóa đơn
// Design: ReceiptReview.dc.html

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_colors.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/extensions/date_time_x.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_job.dart';
import 'package:sweepfood/features/ingest/presentation/controllers/receipt_review_controller.dart';
import 'package:sweepfood/features/ingest/presentation/widgets/parsed_item_row.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

/// I-05 — Kiểm tra & chọn lưu danh sách nguyên liệu từ hóa đơn.
class ReceiptReviewScreen extends ConsumerWidget {
  const ReceiptReviewScreen({required this.job, super.key});

  final ScanJob job;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final state = ref.watch(receiptReviewControllerProvider(job));
    final controller = ref.read(receiptReviewControllerProvider(job).notifier);
    final sweep = context.sweep;
    final allSelected =
        state.selectedCount == state.items.length && state.items.isNotEmpty;

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          onPressed: () => context.pop(),
          icon: const Icon(Icons.arrow_back_rounded),
        ),
        title: Text(l10n.reviewReceiptTitle(state.items.length)),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.xxl * 3),
        children: [
          Row(
            children: [
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  color: sweep.subtleFill,
                  borderRadius: Radii.brMd,
                  border: Border.all(color: sweep.hairline),
                ),
                child: const Icon(
                  Icons.receipt_long_outlined,
                  size: 22,
                  color: BrandPalette.green700,
                ),
              ),
              const SizedBox(width: Gap.md),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    state.purchaseDate != null
                        ? '${state.storeName} · ${state.purchaseDate!.ddMM}'
                        : state.storeName,
                    style: context.text.titleSmall?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 2),
                  GestureDetector(
                    onTap: () => context.pop(),
                    child: Text(
                      l10n.reviewRetake,
                      style: context.text.bodySmall?.copyWith(
                        color: BrandPalette.green700,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
          Gap.gapMd,
          Row(
            children: [
              Text.rich(
                TextSpan(
                  children: [
                    TextSpan(
                      text: '${state.selectedCount}',
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                    TextSpan(
                      text: l10n.reviewSelectedOf(state.items.length),
                      style: TextStyle(color: sweep.textTertiary),
                    ),
                  ],
                ),
                style: context.text.bodySmall,
              ),
              const Spacer(),
              GestureDetector(
                onTap: allSelected
                    ? controller.deselectAll
                    : controller.selectAll,
                child: Text(
                  allSelected ? l10n.reviewDeselectAll : l10n.reviewSelectAll,
                  style: context.text.bodySmall?.copyWith(
                    color: BrandPalette.green700,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          Gap.gapSm,
          for (var i = 0; i < state.items.length; i++) ...[
            ParsedItemRow(
              item: state.items[i],
              selected: state.isSelected(i),
              onToggle: () => controller.toggleItem(i),
              onEdit: () => _editItem(context, i, state.items[i], controller),
            ),
            const SizedBox(height: Gap.xs + 2),
          ],
        ],
      ),
      bottomNavigationBar: SafeArea(
        child: Container(
          padding: const EdgeInsets.all(Gap.md),
          decoration: BoxDecoration(
            color: context.colors.surface,
            border: Border(top: BorderSide(color: sweep.hairline)),
            boxShadow: Shadows.e2,
          ),
          child: ElevatedButton(
            onPressed: state.selectedCount == 0
                ? null
                : () async {
                    try {
                      final count = state.selectedCount;
                      await controller.saveSelectedToPantry();
                      if (!context.mounted) return;
                      AppSnack.show(
                        context,
                        context.l10n.scanAddedCountToPantry(count),
                      );
                      context.go(Routes.pantry);
                    } on Object catch (e) {
                      if (!context.mounted) return;
                      AppSnack.show(context, context.l10n.scanSaveError('$e'));
                    }
                  },
            style: ElevatedButton.styleFrom(
              backgroundColor: BrandPalette.green700,
              foregroundColor: Colors.white,
              disabledBackgroundColor: sweep.subtleFill,
              disabledForegroundColor: sweep.textTertiary,
              minimumSize: const Size.fromHeight(50),
              shape: const RoundedRectangleBorder(borderRadius: Radii.brMd),
            ),
            child: Text(
              state.selectedCount > 0
                  ? l10n.reviewAddCount(state.selectedCount)
                  : l10n.reviewPickAtLeastOne,
              style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _editItem(
    BuildContext context,
    int index,
    ParsedItemDraft item,
    ReceiptReviewController controller,
  ) async {
    final l10n = context.l10n;
    final nameController = TextEditingController(text: item.name);
    final qtyController = TextEditingController(
      text: item.quantity == 0 ? '' : item.quantity.toString(),
    );
    var selectedUnit = item.unit;
    var selectedTier = item.storageTier;
    var selectedCategory = item.category.isEmpty
        ? l10n.catOther
        : item.category;

    final categories = [
      l10n.catVegetables,
      l10n.catMeatSeafood,
      l10n.catSpices,
      l10n.catDairyEgg,
      l10n.catDryGoods,
      l10n.catOther,
    ];

    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setState) => Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.viewInsetsOf(ctx).bottom,
            left: Gap.lg,
            right: Gap.lg,
            top: Gap.lg,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                l10n.reviewEditItem,
                style: context.text.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              Gap.gapMd,
              TextField(
                controller: nameController,
                decoration: InputDecoration(
                  labelText: l10n.pantryFieldName,
                  border: const OutlineInputBorder(),
                ),
              ),
              Gap.gapSm,
              Row(
                children: [
                  Expanded(
                    flex: 2,
                    child: TextField(
                      controller: qtyController,
                      keyboardType: TextInputType.number,
                      decoration: InputDecoration(
                        labelText: l10n.pantryStatQuantity,
                        border: const OutlineInputBorder(),
                      ),
                    ),
                  ),
                  const SizedBox(width: Gap.sm),
                  Expanded(
                    flex: 3,
                    child: DropdownButtonFormField<MeasurementUnit>(
                      initialValue: selectedUnit,
                      decoration: InputDecoration(
                        labelText: l10n.reviewUnit,
                        border: const OutlineInputBorder(),
                      ),
                      items: MeasurementUnit.values
                          .map(
                            (u) => DropdownMenuItem(
                              value: u,
                              child: Text(u.label),
                            ),
                          )
                          .toList(),
                      onChanged: (u) {
                        if (u != null) setState(() => selectedUnit = u);
                      },
                    ),
                  ),
                ],
              ),
              Gap.gapSm,
              DropdownButtonFormField<String>(
                initialValue: selectedCategory,
                decoration: InputDecoration(
                  labelText: l10n.reviewCategory,
                  border: const OutlineInputBorder(),
                ),
                items: categories
                    .map((c) => DropdownMenuItem(value: c, child: Text(c)))
                    .toList(),
                onChanged: (c) {
                  if (c != null) setState(() => selectedCategory = c);
                },
              ),
              Gap.gapSm,
              DropdownButtonFormField<StorageTier>(
                initialValue: selectedTier,
                decoration: InputDecoration(
                  labelText: l10n.reviewStorageTier,
                  border: const OutlineInputBorder(),
                ),
                items: StorageTier.values
                    .map(
                      (t) => DropdownMenuItem(
                        value: t,
                        child: Text(t.label(l10n)),
                      ),
                    )
                    .toList(),
                onChanged: (t) {
                  if (t != null) setState(() => selectedTier = t);
                },
              ),
              Gap.gapLg,
              Row(
                children: [
                  Expanded(
                    child: TextButton(
                      onPressed: () {
                        controller.removeItem(index);
                        ctx.pop();
                      },
                      style: TextButton.styleFrom(
                        foregroundColor: BrandPalette.brick500,
                      ),
                      child: Text(l10n.reviewRemoveItem),
                    ),
                  ),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () {
                        final qty =
                            double.tryParse(qtyController.text.trim()) ??
                            item.quantity;
                        controller.updateItem(
                          index,
                          item.copyWith(
                            name: nameController.text.trim(),
                            quantity: qty,
                            unit: selectedUnit,
                            category: selectedCategory,
                            storageTier: selectedTier,
                            isExpiryWarn: false,
                          ),
                        );
                        ctx.pop();
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: BrandPalette.green700,
                        foregroundColor: Colors.white,
                      ),
                      child: Text(l10n.commonSave),
                    ),
                  ),
                ],
              ),
              Gap.gapMd,
            ],
          ),
        ),
      ),
    );
  }
}
