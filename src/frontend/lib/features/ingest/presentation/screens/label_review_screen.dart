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
import 'package:frontend/core/widgets/confidence_field.dart';
import 'package:frontend/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:frontend/features/ingest/domain/entities/scan_job.dart';
import 'package:frontend/features/ingest/presentation/controllers/label_review_controller.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';
import 'package:frontend/shared/domain/storage_tier.dart';
import 'package:go_router/go_router.dart';

/// I-03 — Kiểm tra & chỉnh sửa thông tin bóc tách từ tem nhãn OCR.
class LabelReviewScreen extends ConsumerWidget {
  const LabelReviewScreen({required this.job, super.key});

  final ScanJob job;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final draft = ref.watch(labelReviewControllerProvider(job));
    final controller = ref.read(labelReviewControllerProvider(job).notifier);
    final sweep = context.sweep;
    final fieldCount = job.fieldCount ?? 0;

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          onPressed: () => context.pop(),
          icon: const Icon(Icons.arrow_back_rounded),
        ),
        title: Text(l10n.reviewLabelTitle),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.xxl * 3),
        children: [
          _Thumbnail(onRetake: () => context.pop()),
          Gap.gapMd,
          if (fieldCount > 0) ...[
            _Banner(text: l10n.reviewFieldsRead(fieldCount)),
            Gap.gapMd,
          ],
          ConfidenceField(
            label: l10n.pantryFieldName,
            value: draft.name.isEmpty ? '—' : draft.name,
            onTap: () => _editName(context, draft.name, controller),
          ),
          Gap.gapSm,
          Row(
            children: [
              Expanded(
                child: ConfidenceField(
                  label: l10n.reviewNetWeight,
                  value: '${draft.quantity.round()} ${draft.unit.label}',
                  onTap: () => _editQuantity(context, draft, controller),
                ),
              ),
              const SizedBox(width: Gap.sm),
              Expanded(
                child: ConfidenceField(
                  label: l10n.pantryStatPrice,
                  value: draft.priceVnd != null
                      ? formatVnd(draft.priceVnd!)
                      : '—',
                  onTap: () => _editPrice(context, draft.priceVnd, controller),
                ),
              ),
            ],
          ),
          Gap.gapSm,
          Row(
            children: [
              Expanded(
                child: ConfidenceField(
                  label: l10n.reviewPackedDate,
                  value: draft.packedDate.ddMMyyyyOrDash,
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
                child: ConfidenceField(
                  label: l10n.pantryFieldExpiry,
                  value: draft.expiryDate.ddMMyyyyOrDash,
                  needsReview: draft.isExpiryWarn,
                  onTap: () async {
                    final date = await showDatePicker(
                      context: context,
                      initialDate:
                          draft.expiryDate ??
                          DateTime.now().add(const Duration(days: 7)),
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
          Text(
            l10n.reviewStorageTier,
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
                label: Text(tier.label(l10n)),
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
          ConfidenceField(
            label: l10n.reviewCategory,
            value: draft.category.isEmpty ? l10n.catOther : draft.category,
            trailingIcon: Icons.keyboard_arrow_down_rounded,
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
            onPressed: !draft.isValid
                ? null
                : () async {
                    try {
                      await controller.saveToPantry();
                      if (!context.mounted) return;
                      AppSnack.show(
                        context,
                        context.l10n.scanAddedToPantry(draft.name),
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
              l10n.pantryAddToPantry,
              style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
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
    final result = await _promptText(
      context,
      title: context.l10n.pantryFieldName,
      initial: initial,
      hint: context.l10n.reviewNameHint,
    );
    if (result != null && result.isNotEmpty) controller.setName(result);
  }

  Future<void> _editQuantity(
    BuildContext context,
    ParsedItemDraft draft,
    LabelReviewController controller,
  ) async {
    final qtyController = TextEditingController(
      text: draft.quantity == 0 ? '' : draft.quantity.toString(),
    );
    var selectedUnit = draft.unit;
    final l10n = context.l10n;

    await showDialog<void>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setState) => AlertDialog(
          title: Text(l10n.reviewNetWeight),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: qtyController,
                keyboardType: TextInputType.number,
                decoration: InputDecoration(labelText: l10n.pantryStatQuantity),
              ),
              const SizedBox(height: Gap.md),
              DropdownButtonFormField<MeasurementUnit>(
                initialValue: selectedUnit,
                decoration: InputDecoration(labelText: l10n.reviewUnit),
                items: MeasurementUnit.values
                    .map(
                      (u) => DropdownMenuItem(value: u, child: Text(u.label)),
                    )
                    .toList(),
                onChanged: (u) {
                  if (u != null) setState(() => selectedUnit = u);
                },
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => ctx.pop(),
              child: Text(l10n.commonCancel),
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
              child: Text(l10n.commonSave),
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
    final result = await _promptText(
      context,
      title: context.l10n.reviewPurchasePrice,
      initial: initialPrice?.toString() ?? '',
      hint: context.l10n.reviewPriceHint,
      number: true,
    );
    if (result != null) controller.setPrice(int.tryParse(result));
  }

  Future<void> _editCategory(
    BuildContext context,
    String current,
    LabelReviewController controller,
  ) async {
    final l10n = context.l10n;
    final categories = [
      l10n.catVegetables,
      l10n.catMeatSeafood,
      l10n.catSpices,
      l10n.catDairyEgg,
      l10n.catDryGoods,
      l10n.catOther,
    ];
    final result = await showModalBottomSheet<String>(
      context: context,
      builder: (ctx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Padding(
              padding: const EdgeInsets.all(Gap.md),
              child: Text(
                l10n.reviewPickCategory,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ),
            ...categories.map(
              (cat) => ListTile(
                title: Text(cat),
                trailing: cat == current
                    ? const Icon(Icons.check, color: BrandPalette.green700)
                    : null,
                onTap: () => ctx.pop(cat),
              ),
            ),
          ],
        ),
      ),
    );
    if (result != null) controller.setCategory(result);
  }

  Future<String?> _promptText(
    BuildContext context, {
    required String title,
    required String initial,
    required String hint,
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
          decoration: InputDecoration(hintText: hint),
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

class _Thumbnail extends StatelessWidget {
  const _Thumbnail({required this.onRetake});

  final VoidCallback onRetake;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;

    return Row(
      children: [
        Container(
          width: 64,
          height: 64,
          decoration: BoxDecoration(
            color: sweep.subtleFill,
            border: Border.all(color: sweep.hairline),
            borderRadius: Radii.brMd,
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
              context.l10n.reviewLabelPhoto,
              style: context.text.titleSmall?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 2),
            GestureDetector(
              onTap: onRetake,
              child: Text(
                context.l10n.reviewRetake,
                style: context.text.bodySmall?.copyWith(
                  color: BrandPalette.green700,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _Banner extends StatelessWidget {
  const _Banner({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
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
              text,
              style: context.text.bodySmall?.copyWith(
                color: BrandPalette.green800,
                height: 1.45,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
