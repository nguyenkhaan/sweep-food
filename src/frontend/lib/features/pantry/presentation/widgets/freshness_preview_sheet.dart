import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/extensions/date_time_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/core/widgets/primary_button.dart';
import 'package:sweepfood/features/pantry/data/models/freshness_dto.dart';
import 'package:sweepfood/features/pantry/domain/entities/freshness_estimate.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/freshness_controller.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

/// FreshCheck before an item is saved: the user answers the sensory questions,
/// sees the estimated expiry, and accepts it. Nothing is written to the
/// backend here — the accepted [FreshnessEstimate] travels with the draft and
/// is recorded through the batch assessment once the item is saved.
class FreshnessPreviewSheet extends ConsumerStatefulWidget {
  const FreshnessPreviewSheet({
    required this.masterIngredientId,
    required this.itemName,
    required this.storageTier,
    this.initialAnswers,
    super.key,
  });

  final String masterIngredientId;
  final String itemName;
  final StorageTier storageTier;
  final Map<String, String>? initialAnswers;

  /// Resolves to the accepted estimate, or `null` when dismissed.
  static Future<FreshnessEstimate?> show(
    BuildContext context, {
    required String masterIngredientId,
    required String itemName,
    required StorageTier storageTier,
    Map<String, String>? initialAnswers,
  }) {
    return showModalBottomSheet<FreshnessEstimate>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => FreshnessPreviewSheet(
        masterIngredientId: masterIngredientId,
        itemName: itemName,
        storageTier: storageTier,
        initialAnswers: initialAnswers,
      ),
    );
  }

  @override
  ConsumerState<FreshnessPreviewSheet> createState() =>
      _FreshnessPreviewSheetState();
}

class _FreshnessPreviewSheetState extends ConsumerState<FreshnessPreviewSheet> {
  final Map<String, String> _answers = {};
  bool _initialized = false;
  bool _loading = false;
  String? _error;
  FreshnessPreviewDto? _result;

  Future<void> _preview() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final result = await ref
          .read(freshnessRemoteDataSourceProvider)
          .preview(
            masterIngredientId: widget.masterIngredientId,
            storageMode: widget.storageTier.backendWire,
            answers: _answers,
          );
      if (!mounted) return;
      setState(() {
        _result = result;
        _loading = false;
      });
    } on Object {
      if (!mounted) return;
      setState(() {
        _error = 'Không thể ước tính hạn lúc này. Vui lòng thử lại.';
        _loading = false;
      });
    }
  }

  void _accept(FreshnessPreviewDto result) {
    Navigator.pop(
      context,
      FreshnessEstimate(
        answers: Map<String, String>.of(_answers),
        expiresAt: result.expiresAt!,
        remainingDaysMin: result.remainingDaysMin,
        remainingDaysMax: result.remainingDaysMax,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final questionsAsync = ref.watch(
      freshnessQuestionsProvider(widget.masterIngredientId),
    );

    return SheetBody(
      title: 'Kiểm tra hạn nhanh (FreshCheck)',
      subtitle: widget.itemName,
      child: questionsAsync.when(
        loading: () => const SizedBox(
          height: 200,
          child: Center(child: CircularProgressIndicator.adaptive()),
        ),
        error: (_, _) => const _Message(
          icon: Icons.info_outline_rounded,
          text: 'Nguyên liệu này chưa có bộ câu hỏi cảm quan FreshCheck. '
              'Bạn có thể nhập hạn sử dụng thủ công.',
        ),
        data: (kb) {
          if (!_initialized) {
            for (final q in kb.questions) {
              _answers[q.axis] =
                  widget.initialAnswers?[q.axis] ?? q.defaultValue;
            }
            _initialized = true;
          }
          if (kb.questions.isEmpty) {
            return const _Message(
              icon: Icons.info_outline_rounded,
              text: 'Không có câu hỏi cảm quan cho nguyên liệu này.',
            );
          }
          final result = _result;
          return SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                for (final q in kb.questions) ...[
                  Text(
                    q.questionVi,
                    style: context.text.titleSmall?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Gap.gapXs,
                  Wrap(
                    spacing: Gap.xs,
                    runSpacing: 4,
                    children: [
                      for (final opt in q.options)
                        ChoiceChip(
                          label: Text(opt.labelVi),
                          selected: _answers[q.axis] == opt.value,
                          onSelected: _loading
                              ? null
                              : (selected) {
                                  if (!selected) return;
                                  setState(() {
                                    _answers[q.axis] = opt.value;
                                    _result = null;
                                  });
                                },
                        ),
                    ],
                  ),
                  Gap.gapMd,
                ],
                if (_error != null) ...[
                  Text(
                    _error!,
                    style: context.text.bodySmall?.copyWith(
                      color: context.colors.error,
                    ),
                  ),
                  Gap.gapSm,
                ],
                if (result != null) ...[
                  _ResultCard(result: result),
                  Gap.gapMd,
                ],
                if (result == null || result.expiresAt == null || result.blocked)
                  PrimaryButton(
                    label: result == null
                        ? 'Xem hạn ước tính'
                        : 'Tính lại',
                    loading: _loading,
                    onPressed: _preview,
                  )
                else
                  PrimaryButton(
                    label: 'Dùng hạn này (${result.expiresAt!.ddMMyyyy})',
                    onPressed: () => _accept(result),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _ResultCard extends StatelessWidget {
  const _ResultCard({required this.result});

  final FreshnessPreviewDto result;

  @override
  Widget build(BuildContext context) {
    final blocked = result.blocked;
    final noEstimate = !blocked && result.expiresAt == null;
    final color = blocked || noEstimate ? Colors.red : Colors.green;
    final min = result.remainingDaysMin;
    final max = result.remainingDaysMax;

    final headline = blocked
        ? 'Không nên sử dụng'
        : noEstimate
            ? 'Chưa đủ cơ sở để ước tính hạn'
            : 'Hạn ước tính: ${result.expiresAt!.ddMMyyyy}';

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(Gap.md),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: Radii.brMd,
        border: Border.all(color: color),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            headline,
            style: context.text.titleSmall?.copyWith(
              color: color,
              fontWeight: FontWeight.bold,
            ),
          ),
          if (!blocked && min != null && max != null) ...[
            Gap.gapXs,
            Text(
              min == max ? 'Còn khoảng $min ngày' : 'Còn khoảng $min–$max ngày',
              style: context.text.bodyMedium,
            ),
          ],
          for (final reason in result.reasonsVi) ...[
            Gap.gapXs,
            Text('• $reason', style: context.text.bodySmall),
          ],
          for (final tip in result.storageTipsVi) ...[
            Gap.gapXs,
            Text('💡 $tip', style: context.text.bodySmall),
          ],
        ],
      ),
    );
  }
}

class _Message extends StatelessWidget {
  const _Message({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: Gap.md),
      child: Column(
        children: [
          Icon(icon, size: 40, color: context.sweep.textTertiary),
          Gap.gapSm,
          Text(
            text,
            textAlign: TextAlign.center,
            style: context.text.bodyMedium,
          ),
          Gap.gapMd,
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Đóng'),
          ),
        ],
      ),
    );
  }
}
