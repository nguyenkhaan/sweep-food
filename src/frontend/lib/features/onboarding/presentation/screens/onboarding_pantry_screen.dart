import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_text_button.dart';
import 'package:sweepfood/core/widgets/primary_button.dart';
import 'package:sweepfood/features/ingest/presentation/screens/add_entry_chooser_sheet.dart';
import 'package:sweepfood/features/onboarding/domain/entities/onboarding_state.dart';
import 'package:sweepfood/features/onboarding/presentation/controllers/onboarding_controller.dart';
import 'package:sweepfood/features/onboarding/presentation/widgets/onboarding_progress.dart';

/// A-06 Onboarding · Hướng dẫn nhập kho lần đầu. Both CTAs mark onboarding done;
/// "Thêm nguyên liệu đầu tiên" drops the user into AddEntryChooser.
class OnboardingPantryScreen extends ConsumerWidget {
  const OnboardingPantryScreen({super.key});

  static const _methods = [
    (
      icon: Icons.center_focus_strong_outlined,
      route: '${Routes.pantry}/${Routes.scanCamera}',
    ),
    (
      icon: Icons.mic_none_rounded,
      route: '${Routes.pantry}/${Routes.scanVoiceCapture}',
    ),
    (
      icon: Icons.keyboard_outlined,
      route: '${Routes.pantry}/${Routes.addIngredient}',
    ),
  ];

  Future<void> _finish(WidgetRef ref, BuildContext context, String to) async {
    await ref.read(onboardingControllerProvider.notifier).complete();
    if (context.mounted) context.go(to);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final scheme = theme.colorScheme;
    final l10n = context.l10n;
    final methodLabels = [
      l10n.onbMethodScan,
      l10n.onbMethodVoice,
      l10n.onbMethodManual,
    ];

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
                  width: double.infinity,
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
                l10n.onbPantryTitle,
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
              Gap.gapXs,
              Text(
                l10n.onbPantryBody,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: scheme.onSurfaceVariant,
                  height: 1.5,
                ),
              ),
              Gap.gapMd,
              Row(
                children: [
                  for (final (i, m) in _methods.indexed) ...[
                    if (i != 0) Gap.gapXs,
                    Expanded(
                      child: _MethodChip(
                        icon: m.icon,
                        label: methodLabels[i],
                        onTap: () => _finish(ref, context, m.route),
                      ),
                    ),
                  ],
                ],
              ),
              Gap.gapLg,
              PrimaryButton(
                label: l10n.onbPantryCta,
                icon: Icons.add_rounded,
                onPressed: () async {
                  await ref
                      .read(onboardingControllerProvider.notifier)
                      .complete();
                  if (!context.mounted) return;
                  context.go(Routes.pantry);
                  showAddEntryChooser(context);
                },
              ),
              Gap.gapXxs,
              Center(
                child: AppTextButton(
                  label: l10n.onbLater,
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
  const _MethodChip({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scheme = theme.colorScheme;
    return Material(
      color: scheme.surface,
      borderRadius: Radii.brMd,
      child: InkWell(
        onTap: onTap,
        borderRadius: Radii.brMd,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: Gap.sm),
          decoration: BoxDecoration(
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
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
