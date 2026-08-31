import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/primary_button.dart';
import 'package:frontend/features/subscription/domain/entities/plan_option.dart';
import 'package:frontend/features/subscription/presentation/controllers/paywall_controller.dart';
import 'package:frontend/features/subscription/presentation/widgets/plan_option_card.dart';

/// G-05 Paywall — MVP is interest capture only ("Nhận thông báo khi ra mắt").
class PaywallScreen extends ConsumerWidget {
  const PaywallScreen({super.key});

  static const _benefits = [
    'Kho nguyên liệu không giới hạn',
    'Quét tem & hóa đơn không giới hạn',
    'Lập thực đơn tuần & danh sách mua sắm',
    'Mục tiêu dinh dưỡng theo ngày',
    'Báo cáo thực phẩm đã tiết kiệm',
    'Chia sẻ tủ bếp cho tối đa 4 người',
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(paywallControllerProvider);
    final ctrl = ref.read(paywallControllerProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.close_rounded),
          onPressed: () => Navigator.of(context).maybePop(),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(Gap.lg, 0, Gap.lg, Gap.xxl),
        children: [
          Text(
            'SweepFood Premium sắp ra mắt',
            style: context.text.headlineSmall
                ?.copyWith(fontWeight: FontWeight.w700),
          ),
          Gap.gapXs,
          Text(
            'Hiện tại bạn đang dùng miễn phí tất cả tính năng. Đăng ký để được '
            'báo khi Premium chính thức và nhận ưu đãi sớm.',
            style: context.text.bodyMedium?.copyWith(
              color: context.sweep.textSecondary,
              height: 1.5,
            ),
          ),
          Gap.gapLg,
          for (final b in _benefits)
            Padding(
              padding: const EdgeInsets.only(bottom: Gap.xs),
              child: Row(
                children: [
                  Icon(
                    Icons.check_circle_rounded,
                    size: 18,
                    color: context.colors.primary,
                  ),
                  Gap.gapXs,
                  Expanded(child: Text(b, style: context.text.bodyMedium)),
                ],
              ),
            ),
          Gap.gapMd,
          for (final p in PlanOption.all)
            Padding(
              padding: const EdgeInsets.only(bottom: Gap.xs),
              child: PlanOptionCard(
                plan: p,
                selected: state.selectedPlanId == p.id && !p.comingSoon,
                onTap: () => ctrl.selectPlan(p.id),
              ),
            ),
          if (state.error != null) ...[
            Gap.gapSm,
            Text(
              state.error!,
              style: TextStyle(color: context.colors.error, fontSize: 13),
            ),
          ],
        ],
      ),
      bottomNavigationBar: SafeArea(
        minimum: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.md),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            PrimaryButton(
              label: state.submitted
                  ? 'Đã ghi nhận — cảm ơn bạn!'
                  : 'Nhận thông báo khi ra mắt',
              icon: state.submitted ? Icons.check_rounded : null,
              loading: state.submitting,
              onPressed: state.submitted || state.submitting
                  ? null
                  : ctrl.submitInterest,
            ),
            Gap.gapXs,
            Text(
              'Chưa tính phí · giá & gói đang trong giai đoạn kiểm chứng',
              style: context.text.labelSmall?.copyWith(
                color: context.sweep.textTertiary,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
