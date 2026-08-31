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
import 'package:frontend/features/ingest/presentation/controllers/receipt_review_controller.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';
import 'package:frontend/shared/domain/storage_tier.dart';
import 'package:go_router/go_router.dart';

/// I-05 — Màn hình kiểm tra & chọn lưu danh sách nguyên liệu từ hóa đơn.
class ReceiptReviewScreen extends ConsumerWidget {
  const ReceiptReviewScreen({this.imagePath, super.key});

  final String? imagePath;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(receiptReviewControllerProvider(imagePath: imagePath));
    final controller = ref.read(receiptReviewControllerProvider(imagePath: imagePath).notifier);
    final sweep = context.sweep;

    final allSelected = state.selectedCount == state.items.length && state.items.isNotEmpty;

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
          // ── Store & Photo summary ───────────────────────────────────────────
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
                    '${state.storeName} · ${state.purchaseDate.ddMM}',
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

          // ── Selection toolbar ───────────────────────────────────────────────
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
                onTap: () {
                  if (allSelected) {
                    controller.deselectAll();
                  } else {
                    controller.selectAll();
                  }
                },
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

          // ── Item list ───────────────────────────────────────────────────────
          for (var i = 0; i < state.items.length; i++) ...[
            _ReceiptItemTile(
              item: state.items[i],
              isSelected: state.isSelected(i),
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
                    } catch (e) {
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
    final qtyController = TextEditingController(text: item.quantity.toString());
    var selectedUnit = item.unit;
    var selectedTier = item.storageTier;
    var selectedCategory = item.category;

    const categories = ['Rau củ', 'Thịt & Hải sản', 'Gia vị', 'Trứng & Sữa', 'Đồ khô', 'Khác'];

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
                      items: MeasurementUnit.values.map((u) {
                        return DropdownMenuItem(value: u, child: Text(u.label));
                      }).toList(),
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
                items: categories.map((c) {
                  return DropdownMenuItem(value: c, child: Text(c));
                }).toList(),
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
                items: StorageTier.values.map((t) {
                  return DropdownMenuItem(value: t, child: Text(t.label));
                }).toList(),
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
                        final qty = double.tryParse(qtyController.text.trim()) ?? item.quantity;
                        final updated = item.copyWith(
                          name: nameController.text.trim(),
                          quantity: qty,
                          unit: selectedUnit,
                          category: selectedCategory,
                          storageTier: selectedTier,
                          isExpiryWarn: false,
                        );
                        controller.updateItem(index, updated);
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

// ─────────────────────────────────────────────────────────────────────────────
// Receipt Item Tile Component
// ─────────────────────────────────────────────────────────────────────────────

class _ReceiptItemTile extends StatelessWidget {
  const _ReceiptItemTile({
    required this.item,
    required this.isSelected,
    required this.onToggle,
    required this.onEdit,
  });

  final ParsedItemDraft item;
  final bool isSelected;
  final VoidCallback onToggle;
  final VoidCallback onEdit;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;

    final quantityFormatted = item.quantity == item.quantity.roundToDouble()
        ? item.quantity.round().toString()
        : item.quantity.toStringAsFixed(1);
    final subtitle = '$quantityFormatted ${item.unit.label} · ${item.category} · ${item.storageTier.label}';

    return Material(
      color: context.colors.surface,
      borderRadius: Radii.brMd,
      child: InkWell(
        onTap: onToggle,
        borderRadius: Radii.brMd,
        child: Container(
          padding: const EdgeInsets.all(Gap.sm),
          decoration: BoxDecoration(
            borderRadius: Radii.brMd,
            border: Border.all(
              color: isSelected ? BrandPalette.green700 : sweep.hairline,
              width: isSelected ? 1.5 : 1,
            ),
          ),
          child: Row(
            children: [
              // Checkbox icon
              Container(
                width: 22,
                height: 22,
                decoration: BoxDecoration(
                  color: isSelected ? BrandPalette.green700 : Colors.transparent,
                  borderRadius: BorderRadius.circular(6),
                  border: isSelected
                      ? null
                      : Border.all(color: sweep.hairline, width: 1.5),
                ),
                child: isSelected
                    ? const Icon(Icons.check_rounded, size: 16, color: Colors.white)
                    : null,
              ),
              const SizedBox(width: Gap.sm),

              // Item details
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.name,
                      style: context.text.titleSmall?.copyWith(
                        fontWeight: FontWeight.w600,
                        color: isSelected
                            ? context.colors.onSurface
                            : sweep.textTertiary,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 2),
                    Text(
                      subtitle,
                      style: context.text.bodySmall?.copyWith(
                        color: sweep.textTertiary,
                        fontSize: 11,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),

              // Flag / Edit action
              if (item.isExpiryWarn) ...[
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                  decoration: BoxDecoration(
                    color: BrandPalette.warnSoon.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: const Text(
                    'Kiểm tra',
                    style: TextStyle(
                      color: BrandPalette.warnSoon,
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
                const SizedBox(width: Gap.xs),
              ],
              IconButton(
                visualDensity: VisualDensity.compact,
                icon: Icon(
                  Icons.edit_outlined,
                  size: 18,
                  color: sweep.textTertiary,
                ),
                onPressed: onEdit,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
