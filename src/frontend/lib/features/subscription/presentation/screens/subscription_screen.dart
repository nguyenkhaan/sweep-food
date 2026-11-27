import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
import 'package:sweepfood/features/subscription/domain/entities/subscription.dart';
import 'package:sweepfood/features/subscription/presentation/controllers/subscription_controller.dart';

/// P-02 Gói dịch vụ (Concept B · Format 1).
class SubscriptionScreen extends ConsumerWidget {
  const SubscriptionScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final cs = context.colors;
    final sweep = context.sweep;
    final async = ref.watch(subscriptionControllerProvider);

    return EmeraldSystemOverlay(
      child: Scaffold(
        backgroundColor: cs.surface,
        body: Column(
          children: [
            EmeraldSplitHeader(title: l10n.settingsPlan),
            Expanded(
              child: AsyncValueWidget<Subscription>(
                value: async,
                data: (sub) => ListView(
                  padding: const EdgeInsets.fromLTRB(
                    Gap.lg,
                    Gap.xs,
                    Gap.lg,
                    Gap.xxl,
                  ),
                  children: [
                    Container(
                      padding: const EdgeInsets.all(Gap.md),
                      decoration: BoxDecoration(
                        color: cs.surfaceContainerLowest,
                        borderRadius: Radii.brXl,
                        border: Border.all(color: sweep.hairline),
                        boxShadow: Shadows.e1,
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Container(
                                width: 40,
                                height: 40,
                                decoration: BoxDecoration(
                                  color: cs.primaryContainer,
                                  borderRadius: Radii.brMd,
                                ),
                                child: Icon(
                                  AppIcons.award,
                                  size: 20,
                                  color: cs.primary,
                                ),
                              ),
                              const SizedBox(width: Gap.sm + 2),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      l10n.subCurrentPlan.toUpperCase(),
                                      style: context.text.labelSmall?.copyWith(
                                        letterSpacing: 0.7,
                                        fontWeight: FontWeight.w800,
                                        color: sweep.textTertiary,
                                      ),
                                    ),
                                    const SizedBox(height: 2),
                                    Text(
                                      sub.tier.label(l10n),
                                      style: context.text.titleMedium?.copyWith(
                                        fontWeight: FontWeight.w800,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                          Gap.gapMd,
                          Divider(height: 1, color: sweep.hairline),
                          Gap.gapMd,
                          for (final perk in sub.perks)
                            Padding(
                              padding: const EdgeInsets.only(bottom: Gap.xs + 2),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Icon(
                                    AppIcons.checkCircle,
                                    size: 16,
                                    color: cs.primary,
                                  ),
                                  const SizedBox(width: Gap.sm),
                                  Expanded(
                                    child: Text(
                                      perk,
                                      style: context.text.bodyMedium,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                        ],
                      ),
                    ),
                    Gap.gapLg,
                    SizedBox(
                      height: 50,
                      child: FilledButton.icon(
                        style: FilledButton.styleFrom(
                          backgroundColor: sweep.ctaWarm,
                          foregroundColor: sweep.onCtaWarm,
                          disabledBackgroundColor: sweep.subtleFill,
                          disabledForegroundColor: sweep.textTertiary,
                          shape: const RoundedRectangleBorder(
                            borderRadius: Radii.brMd,
                          ),
                        ),
                        icon: Icon(
                          sub.premiumInterestRegistered
                              ? AppIcons.check
                              : AppIcons.crown,
                          size: 18,
                        ),
                        label: Text(
                          sub.premiumInterestRegistered
                              ? l10n.subInterestRegistered
                              : l10n.subInterestCta,
                          style: const TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        onPressed: sub.premiumInterestRegistered
                            ? null
                            : () => context.push(Routes.paywall),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
