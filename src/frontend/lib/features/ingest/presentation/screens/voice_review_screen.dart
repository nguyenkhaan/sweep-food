// lib/features/ingest/presentation/screens/voice_review_screen.dart
// I-07 Kiểm tra kết quả từ giọng nói
// Design: VoiceReview.dc.html

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_colors.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/app_snackbar.dart';
import 'package:frontend/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:frontend/features/ingest/presentation/controllers/voice_capture_controller.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';
import 'package:frontend/shared/domain/storage_tier.dart';
import 'package:go_router/go_router.dart';

/// I-07 — Màn hình kiểm tra & chỉnh sửa danh sách bóc tách từ giọng nói.
class VoiceReviewScreen extends ConsumerWidget {
  const VoiceReviewScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(voiceCaptureControllerProvider);
    final controller = ref.read(voiceCaptureControllerProvider.notifier);
    final sweep = context.sweep;

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          onPressed: () => context.pop(),
          icon: const Icon(Icons.arrow_back_rounded),
        ),
        title: const Text('Kiểm tra kết quả'),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.xxl * 3),
        children: [
          // ── Audio Transcript Box ───────────────────────────────────────────
          Container(
            padding: const EdgeInsets.all(Gap.md),
            decoration: BoxDecoration(
              color: context.colors.surface,
              borderRadius: Radii.brMd,
              border: Border.all(color: sweep.hairline),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '“${state.transcript}”',
                  style: context.text.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w500,
                    height: 1.5,
                  ),
                ),
                const SizedBox(height: Gap.sm),
                Row(
                  children: [
                    GestureDetector(
                      onTap: () {
                        AppSnack.show(context, 'Đang phát lại đoạn thu âm…');
                      },
                      child: Text(
                        'Nghe lại',
                        style: context.text.bodySmall?.copyWith(
                          color: BrandPalette.green700,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    const SizedBox(width: Gap.lg),
                    GestureDetector(
                      onTap: () => context.pop(),
                      child: Text(
                        'Ghi lại',
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
          ),
          Gap.gapMd,

          // ── Caption ────────────────────────────────────────────────────────
          Text(
            'Đã bóc tách ${state.items.length} nguyên liệu',
            style: context.text.labelMedium?.copyWith(
              color: sweep.textSecondary,
              fontWeight: FontWeight.w600,
            ),
          ),
          Gap.gapSm,

          // ── Parsed Items List ──────────────────────────────────────────────
          for (var i = 0; i < state.items.length; i++) ...[
            _VoiceItemRow(
              item: state.items[i],
              onQuantityChanged: (qty) {
                controller.updateItem(i, state.items[i].copyWith(quantity: qty));
              },
              onUnitChanged: (unit) {
                controller.updateItem(i, state.items[i].copyWith(unit: unit));
              },
              onNameChanged: (name) {
                controller.updateItem(i, state.items[i].copyWith(name: name));
              },
              onDelete: () => controller.removeItem(i),
            ),
            const SizedBox(height: Gap.xs + 2),
          ],

          // ── Add row action ─────────────────────────────────────────────────
          const SizedBox(height: Gap.xs),
          GestureDetector(
            onTap: () {
              controller.addItem(
                const ParsedItemDraft(
                  name: 'Nguyên liệu mới',
                  quantity: 1,
                  unit: MeasurementUnit.piece,
                  storageTier: StorageTier.fridge,
                  category: 'Khác',
                ),
              );
            },
            child: Row(
              children: [
                const Icon(
                  Icons.add_rounded,
                  size: 18,
                  color: BrandPalette.green700,
                ),
                const SizedBox(width: Gap.xs),
                Text(
                  'Thêm dòng',
                  style: context.text.labelLarge?.copyWith(
                    color: BrandPalette.green700,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
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
            onPressed: state.items.isEmpty
                ? null
                : () async {
                    try {
                      final count = state.items.length;
                      await controller.saveAllToPantry();
                      if (!context.mounted) return;
                      AppSnack.show(context, 'Đã thêm $count nguyên liệu vào kho!');
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
              'Thêm ${state.items.length} nguyên liệu',
              style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
            ),
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Voice Item Row Component
// ─────────────────────────────────────────────────────────────────────────────

class _VoiceItemRow extends StatelessWidget {
  const _VoiceItemRow({
    required this.item,
    required this.onQuantityChanged,
    required this.onUnitChanged,
    required this.onNameChanged,
    required this.onDelete,
  });

  final ParsedItemDraft item;
  final ValueChanged<double> onQuantityChanged;
  final ValueChanged<MeasurementUnit> onUnitChanged;
  final ValueChanged<String> onNameChanged;
  final VoidCallback onDelete;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;

    final quantityFormatted = item.quantity == item.quantity.roundToDouble()
        ? item.quantity.round().toString()
        : item.quantity.toStringAsFixed(1);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: Gap.sm, vertical: Gap.xs + 2),
      decoration: BoxDecoration(
        color: context.colors.surface,
        borderRadius: Radii.brMd,
        border: Border.all(color: sweep.hairline),
      ),
      child: Row(
        children: [
          // Quantity box
          GestureDetector(
            onTap: () async {
              final textController = TextEditingController(text: quantityFormatted);
              final res = await showDialog<String>(
                context: context,
                builder: (ctx) => AlertDialog(
                  title: const Text('Số lượng'),
                  content: TextField(
                    controller: textController,
                    keyboardType: TextInputType.number,
                    autofocus: true,
                  ),
                  actions: [
                    TextButton(onPressed: () => ctx.pop(), child: const Text('Hủy')),
                    ElevatedButton(
                      onPressed: () => ctx.pop(textController.text.trim()),
                      child: const Text('Lưu'),
                    ),
                  ],
                ),
              );
              if (res != null) {
                final qty = double.tryParse(res);
                if (qty != null && qty > 0) onQuantityChanged(qty);
              }
            },
            child: Container(
              width: 58,
              height: 38,
              alignment: Alignment.center,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(9),
                border: Border.all(color: sweep.hairline),
                color: sweep.subtleFill,
              ),
              child: Text(
                quantityFormatted,
                style: context.text.titleSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ),
          const SizedBox(width: Gap.xs),

          // Unit selector button
          PopupMenuButton<MeasurementUnit>(
            initialValue: item.unit,
            onSelected: onUnitChanged,
            itemBuilder: (_) => MeasurementUnit.values.map((u) {
              return PopupMenuItem(value: u, child: Text(u.label));
            }).toList(),
            child: Container(
              height: 38,
              padding: const EdgeInsets.symmetric(horizontal: 10),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(9),
                border: Border.all(color: sweep.hairline),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    item.unit.label,
                    style: context.text.bodyMedium?.copyWith(
                      color: sweep.textSecondary,
                      fontSize: 13,
                    ),
                  ),
                  const SizedBox(width: 4),
                  Icon(
                    Icons.keyboard_arrow_down_rounded,
                    size: 16,
                    color: sweep.textTertiary,
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(width: Gap.sm),

          // Name (editable)
          Expanded(
            child: GestureDetector(
              onTap: () async {
                final textController = TextEditingController(text: item.name);
                final res = await showDialog<String>(
                  context: context,
                  builder: (ctx) => AlertDialog(
                    title: const Text('Tên nguyên liệu'),
                    content: TextField(
                      controller: textController,
                      autofocus: true,
                    ),
                    actions: [
                      TextButton(onPressed: () => ctx.pop(), child: const Text('Hủy')),
                      ElevatedButton(
                        onPressed: () => ctx.pop(textController.text.trim()),
                        child: const Text('Lưu'),
                      ),
                    ],
                  ),
                );
                if (res != null && res.isNotEmpty) onNameChanged(res);
              },
              child: Text(
                item.name,
                style: context.text.titleSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ),

          // Delete icon
          IconButton(
            visualDensity: VisualDensity.compact,
            icon: Icon(
              Icons.close_rounded,
              size: 18,
              color: sweep.textTertiary,
            ),
            onPressed: onDelete,
          ),
        ],
      ),
    );
  }
}
