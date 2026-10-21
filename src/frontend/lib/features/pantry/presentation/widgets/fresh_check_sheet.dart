import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/core/widgets/primary_button.dart';
import 'package:sweepfood/features/pantry/domain/entities/freshness_answer_set.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/freshness_controller.dart';
import 'package:sweepfood/features/pantry/presentation/widgets/freshness_questions_form.dart';

/// Modal bottom sheet cho tính năng FreshCheck (Đánh giá cảm quan thực phẩm).
class FreshCheckSheet extends ConsumerStatefulWidget {
  const FreshCheckSheet({required this.item, super.key});

  final PantryItem item;

  static Future<void> show(BuildContext context, PantryItem item) {
    return showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      builder: (ctx) => Padding(
        // Lift the sheet above the keyboard while typing a "Khác" answer.
        padding: EdgeInsets.only(bottom: MediaQuery.viewInsetsOf(ctx).bottom),
        child: FreshCheckSheet(item: item),
      ),
    );
  }

  @override
  ConsumerState<FreshCheckSheet> createState() => _FreshCheckSheetState();
}

class _FreshCheckSheetState extends ConsumerState<FreshCheckSheet> {
  FreshnessAnswerSet _answers = const FreshnessAnswerSet();
  Map<String, String> _axisErrors = const {};
  bool _initialized = false;

  @override
  Widget build(BuildContext context) {
    final item = widget.item;
    final controller = ref.watch(freshnessControllerProvider);

    return ValueListenableBuilder<FreshnessAssessmentState>(
      valueListenable: controller,
      builder: (context, assessmentState, _) {
        if (item.ingredientId == null) {
          return SheetBody(
            title: 'Đánh giá độ tươi (FreshCheck)',
            subtitle: item.name,
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: Gap.md),
              child: Column(
                children: [
                  Icon(
                    Icons.info_outline_rounded,
                    size: 48,
                    color: context.sweep.textTertiary,
                  ),
                  Gap.gapMd,
                  Text(
                    'Nguyên liệu này được tạo với tên tùy chỉnh, chưa liên kết với danh mục chuẩn nên chưa có bộ câu hỏi cảm quan FreshCheck.',
                    textAlign: TextAlign.center,
                    style: context.text.bodyMedium,
                  ),
                  Gap.gapLg,
                  FilledButton(
                    onPressed: () => Navigator.pop(context),
                    child: const Text('Đã hiểu'),
                  ),
                ],
              ),
            ),
          );
        }

        // If assessment result is already available, show the summary result
        if (assessmentState.result != null) {
          final res = assessmentState.result!;
          final tierColor = res.blocked
              ? Colors.red
              : (res.tier == 'USE_SOON' ? Colors.orange : Colors.green);

          return SheetBody(
            title: 'Kết quả FreshCheck',
            subtitle: item.name,
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(Gap.md),
                    decoration: BoxDecoration(
                      color: tierColor.withValues(alpha: 0.1),
                      borderRadius: Radii.brMd,
                      border: Border.all(color: tierColor),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(
                              res.blocked
                                  ? Icons.warning_amber_rounded
                                  : Icons.check_circle_outline_rounded,
                              color: tierColor,
                            ),
                            Gap.gapSm,
                            Text(
                              res.blocked
                                  ? 'KHÔNG NÊN SỬ DỤNG'
                                  : (res.tier ?? 'AN TOÀN'),
                              style: context.text.titleMedium?.copyWith(
                                color: tierColor,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                        if (res.remainingDaysMax != null) ...[
                          Gap.gapXs,
                          Text(
                            'Thời gian an toàn còn lại: ${res.remainingDaysMin ?? 0} - ${res.remainingDaysMax} ngày',
                            style: context.text.bodyMedium,
                          ),
                        ],
                      ],
                    ),
                  ),
                  if (res.reasonsVi.isNotEmpty) ...[
                    Gap.gapMd,
                    Text(
                      'Đánh giá cảm quan:',
                      style: context.text.titleSmall
                          ?.copyWith(fontWeight: FontWeight.w600),
                    ),
                    Gap.gapXs,
                    for (final r in res.reasonsVi)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 2),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('• '),
                            Expanded(child: Text(r, style: context.text.bodySmall)),
                          ],
                        ),
                      ),
                  ],
                  if (res.storageTipsVi.isNotEmpty) ...[
                    Gap.gapMd,
                    Text(
                      'Khuyến nghị bảo quản:',
                      style: context.text.titleSmall
                          ?.copyWith(fontWeight: FontWeight.w600),
                    ),
                    Gap.gapXs,
                    for (final tip in res.storageTipsVi)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 2),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('💡 '),
                            Expanded(child: Text(tip, style: context.text.bodySmall)),
                          ],
                        ),
                      ),
                  ],
                  Gap.gapLg,
                  PrimaryButton(
                    label: 'Hoàn tất & Cập nhật kho',
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
            ),
          );
        }

        final questionsAsync =
            ref.watch(freshnessQuestionsProvider(item.ingredientId!));

        return SheetBody(
          title: 'Đánh giá độ tươi (FreshCheck)',
          subtitle: 'Kiểm tra trạng thái cảm quan của "${item.name}"',
          child: questionsAsync.when(
            loading: () => const SizedBox(
              height: 200,
              child: Center(child: CircularProgressIndicator.adaptive()),
            ),
            error: (err, _) => Padding(
              padding: const EdgeInsets.symmetric(vertical: Gap.md),
              child: Column(
                children: [
                  Icon(Icons.error_outline_rounded,
                      size: 40, color: context.colors.error),
                  Gap.gapSm,
                  Text(
                    'Chưa có dữ liệu cảm quan cho nguyên liệu này.',
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
            ),
            data: (kb) {
              if (!_initialized) {
                _answers = FreshnessAnswerSet(
                  selected: {for (final q in kb.questions) q.axis: q.defaultValue},
                );
                _initialized = true;
              }

              if (kb.questions.isEmpty) {
                return const Padding(
                  padding: EdgeInsets.all(Gap.md),
                  child: Text('Không có câu hỏi cảm quan cho nguyên liệu này.'),
                );
              }

              return Flexible(
                child: SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      FreshnessQuestionsForm(
                        questions: kb.questions,
                        answers: _answers,
                        axisErrors: _axisErrors,
                        enabled: !assessmentState.isLoading,
                        onChanged: (next) {
                          final stale = next.changedAxesFrom(_answers);
                          setState(() {
                            _axisErrors = {
                              for (final e in _axisErrors.entries)
                                if (!stale.contains(e.key)) e.key: e.value,
                            };
                            _answers = next;
                          });
                        },
                      ),
                      Gap.gapMd,
                      if (assessmentState.errorMessage != null) ...[
                        Text(
                          assessmentState.errorMessage!,
                          style: context.text.bodySmall
                              ?.copyWith(color: context.colors.error),
                        ),
                        Gap.gapSm,
                      ],
                      PrimaryButton(
                        label: 'Gửi đánh giá',
                        loading: assessmentState.isLoading,
                        onPressed: () async {
                          final empty = _answers.emptyOtherAxes;
                          if (empty.isNotEmpty) {
                            setState(() {
                              _axisErrors = {
                                for (final a in empty)
                                  a: 'Vui lòng nhập mô tả cho mục Khác.',
                              };
                            });
                            return;
                          }
                          final res = await controller.submit(
                            batchId: item.id,
                            answers: _answers.selected,
                            otherAnswers: _answers.otherToSend,
                            storageMode: item.storageTier.backendWire,
                            purchasedAt: item.addedAt,
                          );
                          if (!context.mounted) return;
                          if (res == null) {
                            // Per-axis feedback from the backend, if any, goes
                            // under the matching "Khác" box.
                            setState(() {
                              _axisErrors = Map.of(controller.value.axisErrors);
                            });
                            return;
                          }
                          AppSnack.show(
                            context,
                            'Đã cập nhật hạn dùng cho lô thực phẩm.',
                          );
                        },
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        );
      },
    );
  }
}
