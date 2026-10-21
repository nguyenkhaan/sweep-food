// lib/features/ingest/presentation/screens/voice_review_screen.dart
// I-07 Kiểm tra kết quả từ giọng nói
// Design: VoiceReview.dc.html

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_colors.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_job.dart';
import 'package:sweepfood/features/ingest/presentation/controllers/voice_capture_controller.dart';
import 'package:sweepfood/features/pantry/presentation/widgets/expiry_freshness_row.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

/// I-07 — Kiểm tra & chỉnh sửa danh sách bóc tách từ giọng nói.
class VoiceReviewScreen extends ConsumerWidget {
  const VoiceReviewScreen({required this.job, super.key});

  final ScanJob job;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final state = ref.watch(voiceCaptureControllerProvider(job));
    final controller = ref.read(voiceCaptureControllerProvider(job).notifier);
    final sweep = context.sweep;

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          onPressed: () => context.pop(),
          icon: const Icon(Icons.arrow_back_rounded),
        ),
        title: Text(l10n.voiceReviewTitle),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.xxl * 3),
        children: [
          if (state.transcript.isNotEmpty) ...[
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
                  GestureDetector(
                    onTap: () => context.pushReplacement(
                      '${Routes.pantry}/${Routes.scanVoiceCapture}',
                    ),
                    child: Text(
                      l10n.voiceRerecord,
                      style: context.text.bodySmall?.copyWith(
                        color: BrandPalette.green700,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            Gap.gapMd,
          ],
          Text(
            l10n.voiceParsedCount(state.items.length),
            style: context.text.labelMedium?.copyWith(
              color: sweep.textSecondary,
              fontWeight: FontWeight.w600,
            ),
          ),
          if (state.needsReview) ...[
            Gap.gapSm,
            Semantics(
              liveRegion: true,
              child: Container(
                padding: const EdgeInsets.all(Gap.sm),
                decoration: BoxDecoration(
                  color: BrandPalette.warnSoon.withValues(alpha: 0.12),
                  borderRadius: Radii.brMd,
                  border: Border.all(
                    color: BrandPalette.warnSoon.withValues(alpha: 0.45),
                  ),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(
                      Icons.warning_amber_rounded,
                      size: 20,
                      color: BrandPalette.warnSoon,
                    ),
                    const SizedBox(width: Gap.xs),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Cần kiểm tra lại kết quả',
                            style: context.text.labelMedium?.copyWith(
                              color: BrandPalette.warnSoon,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          if (state.suspectedMissingCount > 0)
                            Text(
                              'Có thể thiếu ${state.suspectedMissingCount} nguyên liệu so với câu đã nghe. Hãy thêm dòng hoặc ghi lại.',
                              style: context.text.bodySmall?.copyWith(
                                color: sweep.textSecondary,
                              ),
                            ),
                          if (state.hasSuspiciousQuantity)
                            Text(
                              'Có số lượng bất thường. Hãy chạm vào số lượng để kiểm tra trước khi thêm.',
                              style: context.text.bodySmall?.copyWith(
                                color: sweep.textSecondary,
                              ),
                            ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
          Gap.gapSm,
          for (var i = 0; i < state.items.length; i++) ...[
            _VoiceItemRow(
              item: state.items[i],
              onQuantityChanged: (qty) => controller.updateItem(
                i,
                state.items[i].copyWith(quantity: qty),
              ),
              onUnitChanged: (unit) =>
                  controller.updateItem(i, state.items[i].copyWith(unit: unit)),
              onNameChanged: (name) => controller.renameItem(i, name),
              onDelete: () => controller.removeItem(i),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(Gap.sm, Gap.xs, Gap.sm, 0),
              child: ExpiryFreshnessRow(
                itemName: state.items[i].name,
                storageTier: state.items[i].storageTier,
                expiryDate: state.items[i].expiryDate,
                freshness: state.items[i].freshness,
                masterIngredientId: state.items[i].ingredientId,
                onChanged: (expiry, freshness) =>
                    controller.setItemExpiry(i, expiry, freshness),
              ),
            ),
            const SizedBox(height: Gap.sm),
          ],
          const SizedBox(height: Gap.xs),
          GestureDetector(
            onTap: () => controller.addItem(kBlankVoiceDraft),
            child: Row(
              children: [
                const Icon(
                  Icons.add_rounded,
                  size: 18,
                  color: BrandPalette.green700,
                ),
                const SizedBox(width: Gap.xs),
                Text(
                  l10n.scanAddRow,
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
                      AppSnack.show(
                        context,
                        context.l10n.scanAddedCountToPantry(count),
                      );
                      context.go(Routes.pantry);
                    } on Object catch (e) {
                      if (!context.mounted) return;
                      AppSnack.show(context, context.saveErrorMessage(e));
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
              l10n.voiceAddCount(state.items.length),
              style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
            ),
          ),
        ),
      ),
    );
  }
}

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
    final qty = item.quantity == item.quantity.roundToDouble()
        ? item.quantity.round().toString()
        : item.quantity.toStringAsFixed(1);

    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: Gap.sm,
        vertical: Gap.xs + 2,
      ),
      decoration: BoxDecoration(
        color: context.colors.surface,
        borderRadius: Radii.brMd,
        border: Border.all(color: sweep.hairline),
      ),
      child: Row(
        children: [
          GestureDetector(
            onTap: () async {
              final res = await _prompt(
                context,
                context.l10n.pantryStatQuantity,
                qty,
                number: true,
              );
              final parsed = double.tryParse(res ?? '');
              if (parsed != null && parsed > 0) onQuantityChanged(parsed);
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
                qty,
                style: context.text.titleSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ),
          const SizedBox(width: Gap.xs),
          PopupMenuButton<MeasurementUnit>(
            initialValue: item.unit,
            onSelected: onUnitChanged,
            itemBuilder: (_) => MeasurementUnit.values
                .map((u) => PopupMenuItem(value: u, child: Text(u.label)))
                .toList(),
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
          Expanded(
            child: GestureDetector(
              onTap: () async {
                final res = await _prompt(
                  context,
                  context.l10n.pantryFieldName,
                  item.name,
                );
                if (res != null && res.isNotEmpty) onNameChanged(res);
              },
              child: Text(
                item.name.isEmpty ? context.l10n.scanNoName : item.name,
                style: context.text.titleSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ),
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

  Future<String?> _prompt(
    BuildContext context,
    String title,
    String initial, {
    bool number = false,
  }) {
    final textController = TextEditingController(text: initial);
    return showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(title),
        content: TextField(
          controller: textController,
          autofocus: true,
          keyboardType: number ? TextInputType.number : null,
        ),
        actions: [
          TextButton(
            onPressed: () => ctx.pop(),
            child: Text(context.l10n.commonCancel),
          ),
          ElevatedButton(
            onPressed: () => ctx.pop(textController.text.trim()),
            child: Text(context.l10n.commonSave),
          ),
        ],
      ),
    );
  }
}
