import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/extensions/date_time_x.dart';
import 'package:sweepfood/features/pantry/domain/entities/freshness_estimate.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/freshness_controller.dart';
import 'package:sweepfood/features/pantry/presentation/widgets/freshness_preview_sheet.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

/// The three ways an item gets an expiry date, in one place:
///
/// 1. a date read by OCR / ASR (shown, editable),
/// 2. a date typed by the user ("Nhập hạn"),
/// 3. a FreshCheck estimate ("Kiểm tra hạn nhanh") — offered only when the item
///    is matched to a catalog ingredient that FreshCheck supports.
///
/// There is no automatic guess: without any of the three the item stays
/// without an expiry. A manual date and a FreshCheck estimate are mutually
/// exclusive; [onChanged] always receives the resulting pair.
class ExpiryFreshnessRow extends ConsumerWidget {
  const ExpiryFreshnessRow({
    required this.itemName,
    required this.storageTier,
    required this.expiryDate,
    required this.freshness,
    required this.onChanged,
    this.masterIngredientId,
    this.allowFreshness = true,
    this.needsReview = false,
    super.key,
  });

  final String itemName;
  final StorageTier storageTier;
  final DateTime? expiryDate;
  final FreshnessEstimate? freshness;

  /// Catalog id from the smart parser; `null` hides FreshCheck.
  final String? masterIngredientId;

  /// `false` for editing an already-saved item (assessments run on new items).
  final bool allowFreshness;

  /// The OCR read this date with low confidence.
  final bool needsReview;

  final void Function(DateTime? expiry, FreshnessEstimate? freshness) onChanged;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final id = masterIngredientId;
    final hasAnyExpiry = expiryDate != null || freshness != null;
    final freshCheckSupported =
        allowFreshness &&
        id != null &&
        (hasAnyExpiry ||
            !ref.watch(freshnessQuestionsProvider(id)).hasError);

    final chips = <Widget>[];
    if (expiryDate != null) {
      chips.add(
        InputChip(
          avatar: const Icon(Icons.event_rounded, size: 16),
          label: Text('Hạn: ${expiryDate!.ddMMyyyy}'),
          onPressed: () => _pickDate(context),
          onDeleted: () => onChanged(null, null),
        ),
      );
    } else if (freshness != null) {
      chips.add(
        InputChip(
          avatar: const Icon(Icons.health_and_safety_outlined, size: 16),
          label: Text(_summary(freshness!)),
          onPressed: () => _openFreshCheck(context),
          onDeleted: () => onChanged(null, null),
        ),
      );
    } else {
      chips.add(
        ActionChip(
          avatar: const Icon(Icons.edit_calendar_rounded, size: 16),
          label: const Text('Nhập hạn'),
          onPressed: () => _pickDate(context),
        ),
      );
      if (freshCheckSupported) {
        chips.add(
          ActionChip(
            avatar: const Icon(Icons.health_and_safety_outlined, size: 16),
            label: const Text('Kiểm tra hạn nhanh'),
            onPressed: () => _openFreshCheck(context),
          ),
        );
      }
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'HẠN SỬ DỤNG',
          style: context.text.labelSmall,
        ),
        const SizedBox(height: Gap.xxs),
        Wrap(spacing: Gap.xs, runSpacing: Gap.xxs, children: chips),
        if (!hasAnyExpiry) ...[
          const SizedBox(height: Gap.xxs),
          Text(
            freshCheckSupported
                ? 'Chưa có hạn — nhập hạn in trên bao bì hoặc kiểm tra nhanh bằng FreshCheck.'
                : 'Chưa có hạn — nhập hạn in trên bao bì.',
            style: context.text.bodySmall?.copyWith(
              color: context.sweep.textSecondary,
            ),
          ),
        ] else if (needsReview && expiryDate != null) ...[
          const SizedBox(height: Gap.xxs),
          Text(
            'Hạn đọc từ ảnh có thể chưa chính xác — hãy kiểm tra lại.',
            style: context.text.bodySmall?.copyWith(color: Colors.orange),
          ),
        ],
      ],
    );
  }

  Future<void> _pickDate(BuildContext context) async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: expiryDate ?? now,
      firstDate: DateTime(now.year - 1),
      lastDate: DateTime(now.year + 10),
    );
    if (picked != null) onChanged(picked, null);
  }

  Future<void> _openFreshCheck(BuildContext context) async {
    final estimate = await FreshnessPreviewSheet.show(
      context,
      masterIngredientId: masterIngredientId!,
      itemName: itemName,
      storageTier: storageTier,
      initialAnswers: freshness?.answers,
    );
    if (estimate != null) onChanged(null, estimate);
  }

  static String _summary(FreshnessEstimate e) {
    final min = e.remainingDaysMin;
    final max = e.remainingDaysMax;
    final span = (min != null && max != null)
        ? (min == max ? 'còn $min ngày' : 'còn $min–$max ngày')
        : e.expiresAt.ddMMyyyy;
    return 'FreshCheck: $span (≈ ${e.expiresAt.ddMM})';
  }
}
