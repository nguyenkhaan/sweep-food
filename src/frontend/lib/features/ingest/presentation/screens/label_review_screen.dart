// lib/features/ingest/presentation/screens/label_review_screen.dart
// I-03 Kiểm tra thông tin tem nhãn
// Design: LabelReview.dc.html

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_colors.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/utils/extensions/date_time_x.dart';
import 'package:frontend/core/utils/formatters/currency_vnd.dart';
import 'package:frontend/core/widgets/app_snackbar.dart';
import 'package:frontend/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:frontend/features/ingest/presentation/controllers/label_review_controller.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';
import 'package:frontend/shared/domain/storage_tier.dart';
import 'package:go_router/go_router.dart';

/// I-03 — Màn hình kiểm tra & chỉnh sửa thông tin bóc tách từ tem nhãn OCR.
class LabelReviewScreen extends ConsumerWidget {
  const LabelReviewScreen({this.imagePath, super.key});

  final String? imagePath;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final draft = ref.watch(labelReviewControllerProvider(imagePath: imagePath));
    final controller = ref.read(labelReviewControllerProvider(imagePath: imagePath).notifier);
    final sweep = context.sweep;

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          onPressed: () => context.pop(),
          icon: const Icon(Icons.arrow_back_rounded),
        ),
        title: const Text('Kiểm tra thông tin'),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.xxl * 3),
        children: [
          // ── Thumbnail shot ──────────────────────────────────────────────────
          Row(
            children: [
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  color: sweep.subtleFill,
                  borderRadius: Radii.brMd,
                  border: Border.all(color: sweep.hairline),
                ),
                child: const Icon(
                  Icons.receipt_long_outlined,
                  size: 24,
                  color: BrandPalette.green700,
                ),
              ),
              const SizedBox(width: Gap.md),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Ảnh tem nhãn',
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

          // ── Banner ──────────────────────────────────────────────────────────
          Container(
            padding: const EdgeInsets.symmetric(horizontal: Gap.md, vertical: Gap.sm),
            decoration: const BoxDecoration(
              color: BrandPalette.green100,
              borderRadius: Radii.brMd,
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(
                  Icons.check_circle_rounded,
                  size: 16,
                  color: BrandPalette.green800,
                ),
                const SizedBox(width: Gap.xs),
                Expanded(
                  child: Text(
                    'Đã đọc được 5 trường. Kiểm tra lại trường được đánh dấu trước khi lưu.',
                    style: context.text.bodySmall?.copyWith(
                      color: BrandPalette.green800,
                      height: 1.45,
                    ),
                  ),
                ),
              ],
            ),
          ),
          Gap.gapMd,

          // ── Field: Tên nguyên liệu ──────────────────────────────────────────
          _ReviewFieldCard(
            label: 'Tên nguyên liệu',
            value: draft.name,
            showEditIcon: true,
            onTap: () => _editName(context, draft.name, controller),
          ),
          Gap.gapSm,

          // ── Row 2: Khối lượng & Giá ─────────────────────────────────────────
          Row(
            children: [
              Expanded(
                child: _ReviewFieldCard(
                  label: 'Khối lượng tịnh',
                  value: '${draft.quantity.round()} ${draft.unit.label}',
                  showEditIcon: true,
                  onTap: () => _editQuantity(context, draft, controller),
                ),
              ),
              const SizedBox(width: Gap.sm),
              Expanded(
                child: _ReviewFieldCard(
                  label: 'Giá',
                  value: draft.priceVnd != null ? formatVnd(draft.priceVnd!) : '—',
                  showEditIcon: true,
                  onTap: () => _editPrice(context, draft.priceVnd, controller),
                ),
              ),
            ],
          ),
          Gap.gapSm,

          // ── Row 3: Ngày đóng gói & Hạn sử dụng ──────────────────────────────
          Row(
            children: [
              Expanded(
                child: _ReviewFieldCard(
                  label: 'Ngày đóng gói',
                  value: draft.packedDate.ddMMyyyyOrDash,
                  showEditIcon: true,
                  onTap: () async {
                    final date = await showDatePicker(
                      context: context,
                      initialDate: draft.packedDate ?? DateTime.now(),
                      firstDate: DateTime(2020),
                      lastDate: DateTime(2030),
                    );
                    if (date != null) controller.setPackedDate(date);
                  },
                ),
              ),
              const SizedBox(width: Gap.sm),
              Expanded(
                child: _ReviewFieldCard(
                  label: 'Hạn sử dụng',
                  value: draft.expiryDate.ddMMyyyyOrDash,
                  flagLabel: draft.isExpiryWarn ? 'Cần kiểm tra' : null,
                  isWarning: draft.isExpiryWarn,
                  showEditIcon: true,
                  onTap: () async {
                    final date = await showDatePicker(
                      context: context,
                      initialDate: draft.expiryDate ?? DateTime.now().add(const Duration(days: 7)),
                      firstDate: DateTime(2020),
                      lastDate: DateTime(2030),
                    );
                    if (date != null) controller.setExpiryDate(date);
                  },
                ),
              ),
            ],
          ),
          Gap.gapMd,

          // ── Field: Tầng bảo quản ────────────────────────────────────────────
          Text(
            'Tầng bảo quản',
            style: context.text.labelMedium?.copyWith(
              fontWeight: FontWeight.w600,
              color: sweep.textSecondary,
            ),
          ),
          Gap.gapXs,
          Wrap(
            spacing: Gap.xs,
            runSpacing: Gap.xs,
            children: StorageTier.values.map((tier) {
              final selected = draft.storageTier == tier;
              return ChoiceChip(
                label: Text(tier.label),
                selected: selected,
                showCheckmark: false,
                selectedColor: BrandPalette.green100,
                backgroundColor: context.colors.surface,
                side: BorderSide(
                  color: selected ? BrandPalette.green700 : sweep.hairline,
                ),
                labelStyle: TextStyle(
                  color: selected ? BrandPalette.green800 : sweep.textSecondary,
                  fontWeight: FontWeight.w600,
                  fontSize: 12,
                ),
                shape: const StadiumBorder(),
                onSelected: (_) => controller.setStorageTier(tier),
              );
            }).toList(),
          ),
          Gap.gapMd,

          // ── Field: Danh mục ─────────────────────────────────────────────────
          _ReviewFieldCard(
            label: 'Danh mục',
            value: draft.category,
            showDropdownIcon: true,
            onTap: () => _editCategory(context, draft.category, controller),
          ),
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
            onPressed: () async {
              try {
                await controller.saveToPantry();
                if (!context.mounted) return;
                AppSnack.show(context, 'Đã thêm ${draft.name} vào kho!');
                context.go(Routes.pantry);
              } catch (e) {
                if (!context.mounted) return;
                AppSnack.show(context, 'Lỗi lưu nguyên liệu: $e');
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: BrandPalette.green700,
              foregroundColor: Colors.white,
              minimumSize: const Size.fromHeight(50),
              shape: const RoundedRectangleBorder(borderRadius: Radii.brMd),
            ),
            child: const Text(
              'Thêm vào kho',
              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _editName(
    BuildContext context,
    String initial,
    LabelReviewController controller,
  ) async {
    final textController = TextEditingController(text: initial);
    final result = await showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Tên nguyên liệu'),
        content: TextField(
          controller: textController,
          autofocus: true,
          decoration: const InputDecoration(hintText: 'Nhập tên nguyên liệu'),
        ),
        actions: [
          TextButton(
            onPressed: () => ctx.pop(),
            child: const Text('Hủy'),
          ),
          ElevatedButton(
            onPressed: () => ctx.pop(textController.text.trim()),
            child: const Text('Lưu'),
          ),
        ],
      ),
    );
    if (result != null && result.isNotEmpty) {
      controller.setName(result);
    }
  }

  Future<void> _editQuantity(
    BuildContext context,
    ParsedItemDraft draft,
    LabelReviewController controller,
  ) async {
    final qtyController = TextEditingController(text: draft.quantity.toString());
    var selectedUnit = draft.unit;

    await showDialog<void>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setState) => AlertDialog(
          title: const Text('Khối lượng tịnh'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: qtyController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Số lượng'),
              ),
              const SizedBox(height: Gap.md),
              DropdownButtonFormField<MeasurementUnit>(
                initialValue: selectedUnit,
                decoration: const InputDecoration(labelText: 'Đơn vị'),
                items: MeasurementUnit.values.map((u) {
                  return DropdownMenuItem(value: u, child: Text(u.label));
                }).toList(),
                onChanged: (u) {
                  if (u != null) setState(() => selectedUnit = u);
                },
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => ctx.pop(),
              child: const Text('Hủy'),
            ),
            ElevatedButton(
              onPressed: () {
                final qty = double.tryParse(qtyController.text.trim());
                if (qty != null && qty > 0) {
                  controller.setQuantity(qty);
                  controller.setUnit(selectedUnit);
                }
                ctx.pop();
              },
              child: const Text('Lưu'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _editPrice(
    BuildContext context,
    int? initialPrice,
    LabelReviewController controller,
  ) async {
    final textController = TextEditingController(
      text: initialPrice != null ? initialPrice.toString() : '',
    );
    final result = await showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Giá mua (VNĐ)'),
        content: TextField(
          controller: textController,
          keyboardType: TextInputType.number,
          autofocus: true,
          decoration: const InputDecoration(hintText: 'Ví dụ: 18000'),
        ),
        actions: [
          TextButton(
            onPressed: () => ctx.pop(),
            child: const Text('Hủy'),
          ),
          ElevatedButton(
            onPressed: () => ctx.pop(textController.text.trim()),
            child: const Text('Lưu'),
          ),
        ],
      ),
    );
    if (result != null) {
      final p = int.tryParse(result);
      controller.setPrice(p);
    }
  }

  Future<void> _editCategory(
    BuildContext context,
    String current,
    LabelReviewController controller,
  ) async {
    const categories = ['Rau củ', 'Thịt & Hải sản', 'Gia vị', 'Trứng & Sữa', 'Đồ khô', 'Khác'];
    final result = await showModalBottomSheet<String>(
      context: context,
      builder: (ctx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Padding(
              padding: EdgeInsets.all(Gap.md),
              child: Text(
                'Chọn danh mục',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
            ),
            ...categories.map(
              (cat) => ListTile(
                title: Text(cat),
                trailing: cat == current ? const Icon(Icons.check, color: BrandPalette.green700) : null,
                onTap: () => ctx.pop(cat),
              ),
            ),
          ],
        ),
      ),
    );
    if (result != null) {
      controller.setCategory(result);
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Review Field Card Component
// ─────────────────────────────────────────────────────────────────────────────

class _ReviewFieldCard extends StatelessWidget {
  const _ReviewFieldCard({
    required this.label,
    required this.value,
    this.flagLabel,
    this.isWarning = false,
    this.showEditIcon = false,
    this.showDropdownIcon = false,
    this.onTap,
  });

  final String label;
  final String value;
  final String? flagLabel;
  final bool isWarning;
  final bool showEditIcon;
  final bool showDropdownIcon;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              label,
              style: context.text.labelMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: sweep.textSecondary,
              ),
            ),
            if (flagLabel != null) ...[
              const SizedBox(width: Gap.xs),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                decoration: BoxDecoration(
                  color: BrandPalette.warnSoon.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(999),
                ),
                child: Text(
                  flagLabel!,
                  style: const TextStyle(
                    color: BrandPalette.warnSoon,
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ],
          ],
        ),
        const SizedBox(height: 6),
        Material(
          color: context.colors.surface,
          borderRadius: Radii.brMd,
          child: InkWell(
            onTap: onTap,
            borderRadius: Radii.brMd,
            child: Container(
              height: 46,
              padding: const EdgeInsets.symmetric(horizontal: Gap.md),
              decoration: BoxDecoration(
                borderRadius: Radii.brMd,
                border: Border.all(
                  color: isWarning ? BrandPalette.warnSoon : sweep.hairline,
                  width: isWarning ? 2 : 1,
                ),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      value,
                      style: context.text.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w500,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  if (showEditIcon)
                    Icon(
                      Icons.edit_outlined,
                      size: 16,
                      color: sweep.textTertiary,
                    ),
                  if (showDropdownIcon)
                    Icon(
                      Icons.keyboard_arrow_down_rounded,
                      size: 20,
                      color: sweep.textTertiary,
                    ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}
