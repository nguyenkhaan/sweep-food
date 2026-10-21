import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/extensions/date_time_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/core/widgets/primary_button.dart';
import 'package:sweepfood/features/pantry/data/datasources/freshness_remote_data_source.dart';
import 'package:sweepfood/features/pantry/data/models/freshness_dto.dart';
import 'package:sweepfood/features/pantry/domain/entities/freshness_answer_set.dart';
import 'package:sweepfood/features/pantry/domain/entities/freshness_estimate.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/freshness_controller.dart';
import 'package:sweepfood/features/pantry/presentation/widgets/freshness_questions_form.dart';
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
    this.initialOtherAnswers,
    super.key,
  });

  final String masterIngredientId;
  final String itemName;
  final StorageTier storageTier;
  final Map<String, String>? initialAnswers;
  final Map<String, String>? initialOtherAnswers;

  /// Resolves to the accepted estimate, or `null` when dismissed.
  static Future<FreshnessEstimate?> show(
    BuildContext context, {
    required String masterIngredientId,
    required String itemName,
    required StorageTier storageTier,
    Map<String, String>? initialAnswers,
    Map<String, String>? initialOtherAnswers,
  }) {
    return showModalBottomSheet<FreshnessEstimate>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      builder: (ctx) => Padding(
        // Lift the sheet above the keyboard while typing a "Khác" answer.
        padding: EdgeInsets.only(bottom: MediaQuery.viewInsetsOf(ctx).bottom),
        child: FreshnessPreviewSheet(
          masterIngredientId: masterIngredientId,
          itemName: itemName,
          storageTier: storageTier,
          initialAnswers: initialAnswers,
          initialOtherAnswers: initialOtherAnswers,
        ),
      ),
    );
  }

  @override
  ConsumerState<FreshnessPreviewSheet> createState() =>
      _FreshnessPreviewSheetState();
}

class _FreshnessPreviewSheetState extends ConsumerState<FreshnessPreviewSheet> {
  FreshnessAnswerSet _answers = const FreshnessAnswerSet();
  Map<String, String> _axisErrors = const {};
  bool _initialized = false;
  bool _loading = false;
  String? _error;
  FreshnessPreviewDto? _result;

  void _onAnswersChanged(FreshnessAnswerSet next) {
    final stale = next.changedAxesFrom(_answers);
    setState(() {
      _axisErrors = {
        for (final e in _axisErrors.entries)
          if (!stale.contains(e.key)) e.key: e.value,
      };
      _answers = next;
      _result = null;
    });
  }

  Future<void> _preview() async {
    final empty = _answers.emptyOtherAxes;
    if (empty.isNotEmpty) {
      setState(() {
        _axisErrors = {for (final a in empty) a: 'Vui lòng nhập mô tả cho mục Khác.'};
      });
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
      _axisErrors = const {};
    });
    try {
      final result = await ref
          .read(freshnessRemoteDataSourceProvider)
          .preview(
            masterIngredientId: widget.masterIngredientId,
            storageMode: widget.storageTier.backendWire,
            answers: _answers.selected,
            otherAnswers: _answers.otherToSend,
          );
      if (!mounted) return;
      setState(() {
        _result = result;
        _loading = false;
      });
    } on FreshnessClarificationException catch (e) {
      if (!mounted) return;
      setState(() {
        _axisErrors = e.axisErrors;
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
        answers: Map<String, String>.of(_answers.selected),
        otherAnswers: _answers.otherToSend,
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

    return SafeArea(
      top: false,
      child: FractionallySizedBox(
        heightFactor: 0.9,
        child: SheetBody(
          title: 'Kiểm tra hạn nhanh (FreshCheck)',
          subtitle: widget.itemName,
          child: Expanded(
            child: questionsAsync.when(
              loading: () => const SizedBox(
                height: 200,
                child: Center(child: CircularProgressIndicator.adaptive()),
              ),
              error: (_, _) => const _Message(
                icon: Icons.info_outline_rounded,
                text:
                    'Nguyên liệu này chưa có bộ câu hỏi cảm quan FreshCheck. '
                    'Bạn có thể nhập hạn sử dụng thủ công.',
              ),
              data: (kb) {
                if (!_initialized) {
                  final other = <String, String>{
                    ...?widget.initialOtherAnswers,
                  };
                  _answers = FreshnessAnswerSet(
                    other: other,
                    selected: {
                      for (final q in kb.questions)
                        if (!other.containsKey(q.axis))
                          q.axis:
                              widget.initialAnswers?[q.axis] ?? q.defaultValue,
                    },
                  );
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
                      FreshnessQuestionsForm(
                        questions: kb.questions,
                        answers: _answers,
                        axisErrors: _axisErrors,
                        enabled: !_loading,
                        onChanged: _onAnswersChanged,
                      ),
                      Gap.gapMd,
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
                      if (result == null ||
                          result.expiresAt == null ||
                          result.blocked)
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
          ),
        ),
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
