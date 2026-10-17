import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/core/widgets/primary_button.dart';
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
          return AlertDialog(
            title: const Text('Cảm ơn bạn!'),
            content: const Text(
              'Đánh giá và đóng góp ý kiến của bạn đã được ghi nhận. SweepFood sẽ không ngừng hoàn thiện để phục vụ bạn tốt hơn.',
            ),
            actions: [
              FilledButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Đóng'),
              ),
            ],
          );
        }

        return AlertDialog(
          title: const Text('Đánh giá ứng dụng'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  'Bạn cảm thấy trải nghiệm sử dụng SweepFood như thế nào?',
                  textAlign: TextAlign.center,
                ),
                Gap.gapMd,
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    for (int i = 1; i <= 5; i++)
                      IconButton(
                        icon: Icon(
                          i <= _rating
                              ? Icons.star_rounded
                              : Icons.star_outline_rounded,
                          color: Colors.amber,
                          size: 36,
                        ),
                        onPressed: state.isLoading
                            ? null
                            : () => setState(() => _rating = i.toDouble()),
                      ),
                  ],
                ),
                Gap.gapSm,
                TextField(
                  controller: _feedbackController,
                  maxLines: 3,
                  enabled: !state.isLoading,
                  decoration: const InputDecoration(
                    hintText: 'Nhập ý kiến đóng góp hoặc phản hồi của bạn (tùy chọn)...',
                    border: OutlineInputBorder(),
                  ),
                ),
                if (state.errorMessage != null) ...[
                  Gap.gapSm,
                  Text(
                    state.errorMessage!,
                    style: context.text.bodySmall
                        ?.copyWith(color: context.colors.error),
                  ),
                ],
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: state.isLoading ? null : () => Navigator.pop(context),
              child: const Text('Bỏ qua'),
            ),
            PrimaryButton(
              label: 'Gửi đánh giá',
              expand: false,
              loading: state.isLoading,
              onPressed: () async {
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
            ),
          ],
        );
      },
    );
  }
}
