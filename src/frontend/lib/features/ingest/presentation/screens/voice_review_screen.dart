// lib/features/ingest/presentation/screens/voice_review_screen.dart
// I-07 Kiểm tra kết quả từ giọng nói
// Design: VoiceReview.dc.html

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_dialog.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
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

    return EmeraldSystemOverlay(
      child: Scaffold(
        backgroundColor: context.colors.surface,
        body: Column(
          children: [
            EmeraldSplitHeader(
              title: l10n.voiceReviewTitle,
              trailing: EmeraldHeaderPill(label: '${state.items.length} món'),
              onBack: () => context.pop(),
            ),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(
                  Gap.lg,
                  Gap.xs,
                  Gap.lg,
                  Gap.xxl * 2,
                ),
                children: [
                  if (state.transcript.isNotEmpty) ...[
                    Container(
                      padding: const EdgeInsets.all(Gap.md),
                      decoration: BoxDecoration(
                        color: context.colors.surfaceContainerLowest,
                        borderRadius: Radii.brXl,
                        border: Border.all(color: sweep.hairline),
                        boxShadow: Shadows.e1,
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
                                color: context.colors.primary,
                                fontWeight: FontWeight.w700,
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
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  if (state.needsReview) ...[
                    Gap.gapSm,
                    Semantics(
                      liveRegion: true,
                      child: Container(
                        padding: const EdgeInsets.all(Gap.sm + 2),
                        decoration: BoxDecoration(
                          color: sweep.soon.bg,
                          borderRadius: Radii.brLg,
                          border: Border.all(
                            color: sweep.soon.fg.withValues(alpha: 0.35),
                          ),
                        ),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Icon(
                              AppIcons.warning,
                              size: 18,
                              color: sweep.soon.fg,
                            ),
                            const SizedBox(width: Gap.xs + 2),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Cần kiểm tra lại kết quả',
                                    style: context.text.labelMedium?.copyWith(
                                      color: sweep.soon.fg,
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
                      unsupported: !state.items[i].isSupported,
                      onQuantityChanged: (qty) => controller.updateItem(
                        i,
                        state.items[i].copyWith(quantity: qty),
                      ),
                      onUnitChanged: (unit) => controller.updateItem(
                        i,
                        state.items[i].copyWith(unit: unit),
                      ),
                      onNameChanged: (name) {
                        controller.renameItem(i, name);
                        controller.rematchItem(i);
                      },
                      onDelete: () => controller.removeItem(i),
                    ),
                    Padding(
                      padding: const EdgeInsets.fromLTRB(
                        Gap.sm,
                        Gap.xs,
                        Gap.sm,
                        0,
                      ),
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
                        Icon(
                          AppIcons.add,
                          size: 17,
                          color: context.colors.primary,
                        ),
                        const SizedBox(width: Gap.xs),
                        Text(
                          l10n.scanAddRow,
                          style: context.text.labelLarge?.copyWith(
                            color: context.colors.primary,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
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
              color: context.colors.surfaceContainerLowest,
              border: Border(top: BorderSide(color: sweep.hairline)),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (state.hasUnsupported) ...[
                  Text(
                    l10n.scanRemoveUnsupportedHint,
                    textAlign: TextAlign.center,
                    style: context.text.bodySmall?.copyWith(
                      color: context.colors.error,
                    ),
                  ),
                  const SizedBox(height: Gap.xs),
                ],
                FilledButton(
                  onPressed: state.items.isEmpty || state.hasUnsupported
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
                  style: FilledButton.styleFrom(
                    backgroundColor: sweep.ctaWarm,
                    foregroundColor: sweep.onCtaWarm,
                    disabledBackgroundColor: sweep.subtleFill,
                    disabledForegroundColor: sweep.textTertiary,
                    minimumSize: const Size.fromHeight(50),
                    shape: const RoundedRectangleBorder(
                      borderRadius: Radii.brMd,
                    ),
                  ),
                  child: Text(
                    l10n.voiceAddCount(state.items.length),
                    style: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ],
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
    required this.unsupported,
  });

  final ParsedItemDraft item;
  final ValueChanged<double> onQuantityChanged;
  final ValueChanged<MeasurementUnit> onUnitChanged;
  final ValueChanged<String> onNameChanged;
  final VoidCallback onDelete;
  final bool unsupported;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final qty = item.quantity == item.quantity.roundToDouble()
        ? item.quantity.round().toString()
        : item.quantity.toStringAsFixed(1);

    final row = Container(
      padding: const EdgeInsets.symmetric(
        horizontal: Gap.sm,
        vertical: Gap.xs + 2,
      ),
      decoration: BoxDecoration(
        color: context.colors.surface,
        borderRadius: Radii.brMd,
        border: Border.all(
          color: unsupported ? context.colors.error : sweep.hairline,
          width: unsupported ? 1.5 : 1,
        ),
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
                    AppIcons.chevronDown,
                    size: 15,
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
              AppIcons.close,
              size: 17,
              color: sweep.textTertiary,
            ),
            onPressed: onDelete,
          ),
        ],
      ),
    );
    if (!unsupported) return row;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        row,
        Padding(
          padding: const EdgeInsets.fromLTRB(Gap.sm, 4, Gap.sm, 0),
          child: Text(
            context.l10n.ingredientUnsupportedRetry,
            style: context.text.bodySmall?.copyWith(
              color: context.colors.error,
            ),
          ),
        ),
      ],
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
      builder: (ctx) => AppDialog(
        title: title,
        tone: AppDialogTone.primary,
        cancelLabel: context.l10n.commonCancel,
        confirmLabel: context.l10n.commonSave,
        onCancel: () => ctx.pop(),
        onConfirm: () => ctx.pop(textController.text.trim()),
        content: TextField(
          controller: textController,
          autofocus: true,
          keyboardType: number ? TextInputType.number : null,
        ),
      ),
    );
  }
}
