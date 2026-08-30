import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/widgets/app_text_button.dart';
import 'package:frontend/core/widgets/primary_button.dart';
import 'package:frontend/features/onboarding/domain/entities/onboarding_state.dart';
import 'package:frontend/features/onboarding/presentation/controllers/onboarding_controller.dart';
import 'package:frontend/features/onboarding/presentation/widgets/onboarding_progress.dart';
import 'package:go_router/go_router.dart';

/// A-06 Onboarding · Hướng dẫn nhập kho lần đầu. Both CTAs mark onboarding done;
/// "Thêm nguyên liệu đầu tiên" drops the user straight into manual add.
class OnboardingPantryScreen extends ConsumerWidget {
  const OnboardingPantryScreen({super.key});

  static const _methods = [
    (icon: Icons.center_focus_strong_outlined, label: 'Quét'),
    (icon: Icons.mic_none_rounded, label: 'Nói'),
    (icon: Icons.keyboard_outlined, label: 'Nhập tay'),
  ];

  Future<void> _finish(WidgetRef ref, BuildContext context, String to) async {
    await ref.read(onboardingControllerProvider.notifier).complete();
    if (context.mounted) context.go(to);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final scheme = theme.colorScheme;

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(Gap.xl, Gap.md, Gap.xl, Gap.xl),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const OnboardingProgress(step: OnboardingStep.firstPantry),
              Gap.gapXl,
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    color: scheme.primaryContainer,
                    borderRadius: Radii.brXl,
                  ),
                  child: Icon(
                    Icons.kitchen_outlined,
                    size: 88,
                    color: scheme.onPrimaryContainer,
                  ),
                ),
              ),
              Gap.gapXl,
              Text(
                'Thêm nguyên liệu chỉ trong vài giây',
                style: theme.textTheme.headlineSmall
                    ?.copyWith(fontWeight: FontWeight.w700),
              ),
              Gap.gapXs,
              Text(
                'Quét tem nhãn hoặc hóa đơn để lấy sẵn tên, khối lượng, hạn dùng. '
                'Bận tay thì đọc bằng giọng nói. Không có bao bì thì nhập tay thật nhanh.',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: scheme.onSurfaceVariant,
                  height: 1.5,
                ),
              ),
              Gap.gapMd,
              Row(
                children: [
                  for (final m in _methods) ...[
                    if (m != _methods.first) Gap.gapXs,
                    Expanded(child: _MethodChip(icon: m.icon, label: m.label)),
                  ],
                ],
              ),
              Gap.gapLg,
              PrimaryButton(
                label: 'Thêm nguyên liệu đầu tiên',
                icon: Icons.add_rounded,
                onPressed: () =>
                    _finish(ref, context, '${Routes.pantry}/${Routes.addIngredient}'),
              ),
              Gap.gapXxs,
              Center(
                child: AppTextButton(
                  label: 'Để sau',
                  onPressed: () => _finish(ref, context, Routes.home),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _MethodChip extends StatelessWidget {
  const _MethodChip({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scheme = theme.colorScheme;
    return Container(
      padding: const EdgeInsets.symmetric(vertical: Gap.sm),
      decoration: BoxDecoration(
        color: scheme.surface,
        borderRadius: Radii.brMd,
        border: Border.all(color: scheme.outlineVariant),
      ),
      child: Column(
        children: [
          Icon(icon, size: 22, color: scheme.primary),
          Gap.gapXxs,
          Text(
            label,
            style: theme.textTheme.labelMedium?.copyWith(
              color: scheme.onSurfaceVariant,
            ),
          ),
        ],
      ),
    );
  }
}
