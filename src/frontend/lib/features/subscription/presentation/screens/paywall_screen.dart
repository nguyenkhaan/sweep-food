import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
import 'package:sweepfood/core/widgets/primary_button.dart';
import 'package:sweepfood/core/widgets/staggered_reveal.dart';
import 'package:sweepfood/core/widgets/tactile_card.dart';
import 'package:sweepfood/features/subscription/presentation/controllers/paywall_controller.dart';

/// G-05 Paywall — MVP is interest capture only ("Nhận thông báo khi ra mắt").
class PaywallScreen extends ConsumerWidget {
  const PaywallScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final state = ref.watch(paywallControllerProvider);
    final ctrl = ref.read(paywallControllerProvider.notifier);

    final benefits = <String>[
      l10n.paywallBenefit1,
      l10n.paywallBenefit2,
      l10n.paywallBenefit3,
      l10n.paywallBenefit4,
      l10n.paywallBenefit5,
      l10n.paywallBenefit6,
    ];

    return EmeraldSystemOverlay(
      child: Scaffold(
        backgroundColor: context.colors.surface,
        body: Column(
          children: [
            EmeraldSplitHeader(
              title: l10n.paywallComparePro,
              subtitle: l10n.paywallTitle,
            ),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(
                  Gap.lg,
                  Gap.xs,
                  Gap.lg,
                  Gap.xxl,
                ),
                children: [
                  StaggeredReveal(
                    index: 0,
                    child: Center(
                      child: ExcludeSemantics(
                        child: SvgPicture.asset(
                          'assets/illustrations/paywall_hero.svg',
                          width: 164,
                          height: 120,
                        ),
                      ),
                    ),
                  ),
                  Gap.gapSm,
                  StaggeredReveal(
                    index: 1,
                    child: Text(
                      l10n.paywallSubtitle,
                      textAlign: TextAlign.center,
                      style: context.text.bodyMedium?.copyWith(
                        color: sweep.textSecondary,
                        height: 1.5,
                      ),
                    ),
                  ),
                  Gap.gapLg,
                  StaggeredReveal(
                    index: 2,
                    child: Row(
                      children: [
                        Expanded(
                          child: TactileCard(
                            color: sweep.subtleFill,
                            padding: const EdgeInsets.all(Gap.sm),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  l10n.paywallCompareFree,
                                  style: context.text.labelMedium?.copyWith(
                                    color: sweep.textSecondary,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                                const SizedBox(height: 2),
                                Text(l10n.tierAll, style: context.text.bodySmall),
                              ],
                            ),
                          ),
                        ),
                        const SizedBox(width: Gap.sm),
                        Expanded(
                          child: TactileCard(
                            color: context.colors.primaryContainer.withValues(
                              alpha: 0.5,
                            ),
                            borderColor: context.colors.primary.withValues(
                              alpha: 0.35,
                            ),
                            padding: const EdgeInsets.all(Gap.sm),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  l10n.paywallComparePro,
                                  style: context.text.labelMedium?.copyWith(
                                    color: context.colors.primary,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  '6+ quyền lợi sớm',
                                  style: context.text.bodySmall?.copyWith(
                                    color: context.colors.onPrimaryContainer,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  Gap.gapMd,
                  StaggeredReveal(
                    index: 3,
                    child: TactileCard(
                      padding: const EdgeInsets.all(Gap.md),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          for (var i = 0; i < benefits.length; i++) ...[
                            if (i > 0) const Divider(height: Gap.md),
                            Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Icon(
                                  AppIcons.checkCircle,
                                  size: 18,
                                  color: context.colors.primary,
                                ),
                                const SizedBox(width: Gap.sm),
                                Expanded(
                                  child: Text(
                                    benefits[i],
                                    style: context.text.bodyMedium?.copyWith(
                                      color: context.colors.onSurface,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ],
                      ),
                    ),
                  ),
                  if (state.error != null) ...[
                    Gap.gapSm,
                    Text(
                      state.error!,
                      style: context.text.bodySmall?.copyWith(
                        color: context.colors.error,
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
        bottomNavigationBar: SafeArea(
          minimum: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.md),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              PrimaryButton(
                label: state.submitted
                    ? l10n.paywallSubmitted
                    : l10n.paywallNotifyMe,
                icon: state.submitted ? AppIcons.check : AppIcons.bell,
                loading: state.submitting,
                onPressed: state.submitted || state.submitting
                    ? null
                    : () {
                        AppHaptics.medium();
                        ctrl.submitInterest();
                      },
              ),
              Gap.gapXs,
              Text(
                l10n.paywallFinePrint,
                style: context.text.labelSmall?.copyWith(
                  letterSpacing: 0,
                  color: sweep.textTertiary,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
