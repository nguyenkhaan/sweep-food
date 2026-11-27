import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_dialog.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/features/settings/presentation/controllers/rating_controller.dart';

class RatingDialog extends ConsumerStatefulWidget {
  const RatingDialog({super.key});

  static Future<void> show(BuildContext context) {
    return showDialog<void>(
      context: context,
      builder: (_) => const RatingDialog(),
    );
  }

  @override
  ConsumerState<RatingDialog> createState() => _RatingDialogState();
}

class _RatingDialogState extends ConsumerState<RatingDialog> {
  double _rating = 5.0;
  final TextEditingController _feedbackController = TextEditingController();

  @override
  void dispose() {
    _feedbackController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final controller = ref.watch(ratingControllerProvider);

    return ValueListenableBuilder<RatingSubmitState>(
      valueListenable: controller,
      builder: (context, state, _) {
        if (state.isSuccess) {
          return AppDialog(
            icon: AppIcons.check,
            tone: AppDialogTone.primary,
            title: 'Cảm ơn bạn!',
            message:
                'Đánh giá và đóng góp ý kiến của bạn đã được ghi nhận. SweepFood sẽ không ngừng hoàn thiện để phục vụ bạn tốt hơn.',
            confirmLabel: 'Đóng',
            onConfirm: () => Navigator.pop(context),
          );
        }

        return AppDialog(
          title: 'Đánh giá ứng dụng',
          message: 'Bạn cảm thấy trải nghiệm sử dụng SweepFood như thế nào?',
          tone: AppDialogTone.warm,
          cancelLabel: 'Bỏ qua',
          confirmLabel: 'Gửi đánh giá',
          loading: state.isLoading,
          onCancel: () => Navigator.pop(context),
          onConfirm: () async {
            final ok = await controller.submitRating(
              rating: _rating,
              feedback: _feedbackController.text,
            );
            if (ok) {
              if (!context.mounted) return;
              AppSnack.show(context, 'Cảm ơn bạn đã gửi đánh giá!');
              Navigator.pop(context);
            }
          },
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              FittedBox(
                fit: BoxFit.scaleDown,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    for (int i = 1; i <= 5; i++)
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 2),
                        child: InkWell(
                          customBorder: const CircleBorder(),
                          onTap: state.isLoading
                              ? null
                              : () {
                                  AppHaptics.selection();
                                  setState(() => _rating = i.toDouble());
                                },
                          child: AnimatedContainer(
                            duration: AppMotion.resolve(
                              context,
                              context.motion.fast,
                            ),
                            width: 44,
                            height: 44,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: i <= _rating
                                  ? context.sweep.culinaryAccentBg
                                  : context.sweep.subtleFill,
                              border: Border.all(
                                color: i <= _rating
                                    ? context.sweep.ctaWarm
                                    : context.sweep.hairline,
                              ),
                            ),
                            child: Icon(
                              AppIcons.star,
                              color: i <= _rating
                                  ? context.sweep.ctaWarm
                                  : context.sweep.textTertiary,
                              size: 22,
                            ),
                          ),
                        ),
                      ),
                  ],
                ),
              ),
              Gap.gapMd,
              TextField(
                controller: _feedbackController,
                maxLines: 3,
                enabled: !state.isLoading,
                decoration: const InputDecoration(
                  hintText:
                      'Nhập ý kiến đóng góp hoặc phản hồi của bạn (tùy chọn)...',
                ),
              ),
              if (state.errorMessage != null) ...[
                Gap.gapSm,
                Text(
                  state.errorMessage!,
                  style: context.text.bodySmall?.copyWith(
                    color: context.colors.error,
                  ),
                ),
              ],
            ],
          ),
        );
      },
    );
  }
}
