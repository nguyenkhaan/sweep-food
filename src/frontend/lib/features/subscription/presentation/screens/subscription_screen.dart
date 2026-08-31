import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/async_value_widget.dart';
import 'package:frontend/core/widgets/primary_button.dart';
import 'package:frontend/features/subscription/domain/entities/subscription.dart';
import 'package:frontend/features/subscription/presentation/controllers/subscription_controller.dart';
import 'package:go_router/go_router.dart';

/// P-02 Gói dịch vụ — current plan + a nudge to the interest-capture paywall.
class SubscriptionScreen extends ConsumerWidget {
  const SubscriptionScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final async = ref.watch(subscriptionControllerProvider);

    return Scaffold(
      appBar: AppBar(title: Text(l10n.settingsPlan)),
      body: AsyncValueWidget<Subscription>(
        value: async,
        data: (sub) => ListView(
          padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.md, Gap.lg, Gap.xxl),
          children: [
            Container(
              padding: const EdgeInsets.all(Gap.md),
              decoration: BoxDecoration(
                color: context.colors.primaryContainer,
                borderRadius: Radii.brLg,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    l10n.subCurrentPlan,
                    style: context.text.labelSmall?.copyWith(
                      color: context.colors.onPrimaryContainer.withValues(
                        alpha: 0.8,
                      ),
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    sub.tier.label(l10n),
                    style: context.text.titleMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: context.colors.onPrimaryContainer,
                    ),
                  ),
                  Gap.gapSm,
                  for (final perk in sub.perks)
                    Padding(
                      padding: const EdgeInsets.only(bottom: Gap.xxs),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Icon(
                            Icons.check_rounded,
                            size: 16,
                            color: context.colors.onPrimaryContainer,
                          ),
                          Gap.gapXs,
                          Expanded(
                            child: Text(
                              perk,
                              style: context.text.bodySmall?.copyWith(
                                color: context.colors.onPrimaryContainer,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ),
            Gap.gapLg,
            PrimaryButton(
              label: sub.premiumInterestRegistered
                  ? l10n.subInterestRegistered
                  : l10n.subInterestCta,
              icon: sub.premiumInterestRegistered ? Icons.check_rounded : null,
              onPressed: sub.premiumInterestRegistered
                  ? null
                  : () => context.push(Routes.paywall),
            ),
            Gap.gapMd,
            Text(
              l10n.subDisclaimer,
              style: context.text.bodySmall?.copyWith(
                color: context.sweep.textTertiary,
                height: 1.5,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
