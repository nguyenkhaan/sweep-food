// lib/features/ingest/presentation/screens/receipt_review_screen.dart
// I-05 Kiểm tra danh sách từ hóa đơn
// Design: ReceiptReview.dc.html

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_colors.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/utils/extensions/date_time_x.dart';
import 'package:frontend/core/widgets/app_snackbar.dart';
import 'package:frontend/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:frontend/features/ingest/domain/entities/scan_job.dart';
import 'package:frontend/features/ingest/presentation/controllers/receipt_review_controller.dart';
import 'package:frontend/features/ingest/presentation/widgets/parsed_item_row.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';
import 'package:frontend/shared/domain/storage_tier.dart';
import 'package:go_router/go_router.dart';

/// I-05 — Kiểm tra & chọn lưu danh sách nguyên liệu từ hóa đơn.
class ReceiptReviewScreen extends ConsumerWidget {
  const ReceiptReviewScreen({required this.job, super.key});

  final ScanJob job;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
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
        title: Text('Hóa đơn — ${state.items.length} mục'),
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
                      'Chụp lại',
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
                      text: ' / ${state.items.length} mục được chọn',
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
                  allSelected ? 'Bỏ chọn tất cả' : 'Chọn tất cả',
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
                        'Đã thêm $count nguyên liệu vào kho!',
                      );
                      context.go(Routes.pantry);
                    } on Object catch (e) {
                      if (!context.mounted) return;
                      AppSnack.show(context, 'Lỗi lưu nguyên liệu: $e');
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
                  ? 'Thêm ${state.selectedCount} mục vào kho'
                  : 'Chọn ít nhất 1 mục',
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
    final nameController = TextEditingController(text: item.name);
    final qtyController = TextEditingController(
      text: item.quantity == 0 ? '' : item.quantity.toString(),
    );
    var selectedUnit = item.unit;
    var selectedTier = item.storageTier;
    var selectedCategory = item.category.isEmpty ? 'Khác' : item.category;

    const categories = [
      'Rau củ',
      'Thịt & Hải sản',
      'Gia vị',
      'Trứng & Sữa',
      'Đồ khô',
      'Khác',
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
                'Chỉnh sửa nguyên liệu',
                style: context.text.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              Gap.gapMd,
              TextField(
                controller: nameController,
                decoration: const InputDecoration(
                  labelText: 'Tên nguyên liệu',
                  border: OutlineInputBorder(),
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
                      decoration: const InputDecoration(
                        labelText: 'Số lượng',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                  const SizedBox(width: Gap.sm),
                  Expanded(
                    flex: 3,
                    child: DropdownButtonFormField<MeasurementUnit>(
                      initialValue: selectedUnit,
                      decoration: const InputDecoration(
                        labelText: 'Đơn vị',
                        border: OutlineInputBorder(),
                      ),
                      items: MeasurementUnit.values
                          .map((u) => DropdownMenuItem(
                                value: u,
                                child: Text(u.label),
                              ))
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
                decoration: const InputDecoration(
                  labelText: 'Danh mục',
                  border: OutlineInputBorder(),
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
                decoration: const InputDecoration(
                  labelText: 'Tầng bảo quản',
                  border: OutlineInputBorder(),
                ),
                items: StorageTier.values
                    .map((t) => DropdownMenuItem(
                          value: t,
                          child: Text(t.label),
                        ))
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
                      child: const Text('Xóa mục này'),
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
                      child: const Text('Lưu'),
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
