import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_text_button.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
import 'package:sweepfood/core/widgets/tactile_card.dart';
import 'package:sweepfood/features/ingest/presentation/screens/add_entry_chooser_sheet.dart';
import 'package:sweepfood/features/onboarding/presentation/controllers/onboarding_controller.dart';

/// A-06 Onboarding · Hướng dẫn nhập kho lần đầu (Concept B · Format 1).
class OnboardingPantryScreen extends ConsumerWidget {
  const OnboardingPantryScreen({super.key});

  static const _methods = [
    (icon: AppIcons.scan, route: '${Routes.pantry}/${Routes.scanCamera}'),
    (icon: AppIcons.mic, route: '${Routes.pantry}/${Routes.scanVoiceCapture}'),
    (
      icon: AppIcons.keyboard,
      route: '${Routes.pantry}/${Routes.addIngredient}',
    ),
  ];

  Future<void> _finish(WidgetRef ref, BuildContext context, String to) async {
    await ref.read(onboardingControllerProvider.notifier).complete();
    if (context.mounted) context.go(to);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cs = context.colors;
    final sweep = context.sweep;
    final l10n = context.l10n;
    final methodLabels = [
      l10n.onbMethodScan,
      l10n.onbMethodVoice,
      l10n.onbMethodManual,
    ];

    return EmeraldSystemOverlay(
      child: Scaffold(
        backgroundColor: cs.surface,
        body: Column(
          children: [
            EmeraldSplitHeader(
              title: l10n.onbPantryTitle,
              subtitle: l10n.onbPantryBody,
              trailing: const EmeraldHeaderPill(label: '2 / 2'),
              bottom: ClipRRect(
                borderRadius: BorderRadius.circular(Radii.pill),
                child: LinearProgressIndicator(
                  value: 1,
                  minHeight: 5,
                  backgroundColor: sweep.onHeroSurface.withValues(alpha: 0.2),
                  valueColor: AlwaysStoppedAnimation(sweep.onHeroSurface),
                ),
              ),
            ),
            Expanded(
              child: SafeArea(
                top: false,
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(
                    Gap.lg,
                    Gap.sm,
                    Gap.lg,
                    Gap.lg,
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Expanded(
                        child: Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(Gap.xl),
                          decoration: BoxDecoration(
                            color: cs.surfaceContainerLowest,
                            borderRadius: Radii.brXl,
                            border: Border.all(color: sweep.hairline),
                            boxShadow: Shadows.e1,
                          ),
                          child: ExcludeSemantics(
                            child: SvgPicture.asset(
                              'assets/illustrations/empty_pantry.svg',
                            ),
                          ),
                        ),
                      ),
                      Gap.gapMd,
                      Row(
                        children: [
                          for (final (i, m) in _methods.indexed) ...[
                            if (i != 0) const SizedBox(width: Gap.xs + 2),
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
                      SizedBox(
                        height: 50,
                        child: FilledButton.icon(
                          style: FilledButton.styleFrom(
                            backgroundColor: sweep.ctaWarm,
                            foregroundColor: sweep.onCtaWarm,
                            shape: const RoundedRectangleBorder(
                              borderRadius: Radii.brMd,
                            ),
                          ),
                          icon: const Icon(AppIcons.add, size: 18),
                          label: Text(
                            l10n.onbPantryCta,
                            style: const TextStyle(
                              fontSize: 15,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          onPressed: () async {
                            await ref
                                .read(onboardingControllerProvider.notifier)
                                .complete();
                            if (!context.mounted) return;
                            context.go(Routes.pantry);
                            showAddEntryChooser(context);
                          },
                        ),
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
            ),
          ],
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
    final cs = context.colors;
    return TactileCard(
      color: cs.surfaceContainerLowest,
      borderColor: context.sweep.hairline,
      boxShadow: Shadows.e1,
      padding: const EdgeInsets.symmetric(vertical: Gap.sm + 4),
      onTap: () {
        AppHaptics.selection();
        onTap();
      },
      child: Column(
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: cs.primaryContainer,
              borderRadius: Radii.brMd,
            ),
            child: Icon(icon, size: 18, color: cs.primary),
          ),
          const SizedBox(height: 6),
          Text(
            label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: context.text.labelMedium?.copyWith(
              color: context.sweep.textSecondary,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}
