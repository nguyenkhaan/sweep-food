// lib/features/ingest/presentation/screens/receipt_review_screen.dart
// I-05 Kiểm tra danh sách từ hóa đơn
// Design: ReceiptReview.dc.html

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/extensions/date_time_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
import 'package:sweepfood/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_job.dart';
import 'package:sweepfood/features/ingest/presentation/controllers/receipt_review_controller.dart';
import 'package:sweepfood/features/ingest/presentation/widgets/parsed_item_row.dart';
import 'package:sweepfood/features/pantry/presentation/widgets/expiry_freshness_row.dart';
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
    final isEmpty = state.items.isEmpty;
    // "All ticked" means every supported food; unsupported ones stay unticked.
    final supportedIdx = [
      for (var i = 0; i < state.items.length; i++)
        if (state.items[i].isSupported) i,
    ];
    final allSelected =
        supportedIdx.isNotEmpty && supportedIdx.every(state.isSelected);

    return EmeraldSystemOverlay(
      child: Scaffold(
        backgroundColor: context.colors.surface,
        body: Column(
          children: [
            EmeraldSplitHeader(
              title: l10n.reviewReceiptTitle(state.items.length),
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
                        child: Icon(
                          AppIcons.receipt,
                          size: 22,
                          color: context.colors.primary,
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
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          const SizedBox(height: 2),
                          GestureDetector(
                            onTap: () => context.pop(),
                            child: Text(
                              l10n.reviewRetake,
                              style: context.text.bodySmall?.copyWith(
                                color: context.colors.primary,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                  Gap.gapMd,
                  if (isEmpty)
                    _EmptyReceiptResult(job: job)
                  else ...[
                    Row(
                      children: [
                        Text.rich(
                          TextSpan(
                            children: [
                              TextSpan(
                                text: '${state.selectedCount}',
                                style: const TextStyle(
                                  fontWeight: FontWeight.w700,
                                ),
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
                            allSelected
                                ? l10n.reviewDeselectAll
                                : l10n.reviewSelectAll,
                            style: context.text.bodySmall?.copyWith(
                              color: context.colors.primary,
                              fontWeight: FontWeight.w700,
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
                        unsupported: !state.items[i].isSupported,
                        onToggle: () => controller.toggleItem(i),
                        onEdit: () =>
                            _editItem(context, i, state.items[i], controller),
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
                  ],
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
            child: isEmpty
                ? Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      FilledButton.icon(
                        onPressed: () => context.push(
                          '${Routes.pantry}/${Routes.addIngredient}',
                        ),
                        icon: const Icon(AppIcons.add, size: 18),
                        label: Text(l10n.chooserManual),
                        style: FilledButton.styleFrom(
                          backgroundColor: sweep.ctaWarm,
                          foregroundColor: sweep.onCtaWarm,
                          minimumSize: const Size.fromHeight(50),
                          shape: const RoundedRectangleBorder(
                            borderRadius: Radii.brMd,
                          ),
                        ),
                      ),
                      const SizedBox(height: Gap.xs),
                      TextButton.icon(
                        onPressed: () => context.pop(),
                        icon: const Icon(AppIcons.refresh, size: 17),
                        label: Text(l10n.reviewRetake),
                      ),
                    ],
                  )
                : Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      if (state.hasSelectedUnsupported) ...[
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
                        onPressed:
                            state.selectedCount == 0 ||
                                state.hasSelectedUnsupported
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
                                  AppSnack.show(
                                    context,
                                    context.saveErrorMessage(e),
                                  );
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
                          state.selectedCount > 0
                              ? l10n.reviewAddCount(state.selectedCount)
                              : l10n.reviewPickAtLeastOne,
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

    await showAppBottomSheet<void>(
      context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setState) => SheetBody(
          icon: AppIcons.edit,
          title: l10n.reviewEditItem,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              SheetGroupCard(
                padding: const EdgeInsets.all(Gap.md),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    TextField(
                      controller: nameController,
                      decoration: InputDecoration(
                        labelText: l10n.pantryFieldName,
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
                            ),
                          ),
                        ),
                        const SizedBox(width: Gap.sm),
                        Expanded(
                          flex: 3,
                          child: DropdownButtonFormField<MeasurementUnit>(
                            initialValue: selectedUnit,
                            icon: const Icon(AppIcons.chevronDown, size: 18),
                            decoration: InputDecoration(
                              labelText: l10n.reviewUnit,
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
                    DropdownButtonFormField<StorageTier>(
                      initialValue: selectedTier,
                      icon: const Icon(AppIcons.chevronDown, size: 18),
                      decoration: InputDecoration(
                        labelText: l10n.reviewStorageTier,
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
                  ],
                ),
              ),
              Gap.gapMd,
              Row(
                children: [
                  Expanded(
                    flex: 4,
                    child: TextButton.icon(
                      onPressed: () {
                        controller.removeItem(index);
                        ctx.pop();
                      },
                      style: TextButton.styleFrom(
                        foregroundColor: context.colors.error,
                        minimumSize: const Size(0, 48),
                      ),
                      icon: const Icon(AppIcons.trash, size: 16),
                      label: Text(l10n.reviewRemoveItem),
                    ),
                  ),
                  const SizedBox(width: Gap.sm),
                  Expanded(
                    flex: 6,
                    child: SheetWarmButton(
                      icon: AppIcons.check,
                      label: l10n.commonSave,
                      onPressed: () {
                        final qty =
                            double.tryParse(qtyController.text.trim()) ??
                            item.quantity;
                        final newName = nameController.text.trim();
                        final renamed = newName != item.name;
                        controller.updateItem(
                          index,
                          item.copyWith(
                            name: newName,
                            quantity: qty,
                            unit: selectedUnit,
                            // The food group follows the smart-parser match.
                            category: renamed ? '' : item.category,
                            storageTier: selectedTier,
                            isExpiryWarn: false,
                            ingredientId: renamed ? null : item.ingredientId,
                            freshness:
                                renamed || selectedTier != item.storageTier
                                ? null
                                : item.freshness,
                          ),
                        );
                        // Renamed: let the smart parser look at the new name.
                        if (renamed) controller.rematchItem(index);
                        ctx.pop();
                      },
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _EmptyReceiptResult extends StatelessWidget {
  const _EmptyReceiptResult({required this.job});

  final ScanJob job;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final rawText = job.rawText?.trim();

    return Container(
      padding: const EdgeInsets.all(Gap.lg),
      decoration: BoxDecoration(
        color: sweep.subtleFill,
        borderRadius: Radii.brLg,
        border: Border.all(color: sweep.hairline),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            AppIcons.search,
            color: context.colors.primary,
            size: 28,
          ),
          Gap.gapSm,
          Text(
            l10n.reviewReceiptPartialTitle,
            style: context.text.titleMedium?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: Gap.xs),
          Text(
            l10n.reviewReceiptPartialBody,
            style: context.text.bodyMedium?.copyWith(
              color: sweep.textSecondary,
            ),
          ),
          if (rawText != null && rawText.isNotEmpty) ...[
            Gap.gapMd,
            Text(
              l10n.reviewReceiptRawText,
              style: context.text.labelLarge?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: Gap.xs),
            Text(
              rawText,
              maxLines: 8,
              overflow: TextOverflow.ellipsis,
              style: context.text.bodySmall?.copyWith(
                color: sweep.textSecondary,
              ),
            ),
          ],
        ],
      ),
    );
  }
}
