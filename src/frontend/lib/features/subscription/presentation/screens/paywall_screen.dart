import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/primary_button.dart';
import 'package:sweepfood/features/subscription/presentation/controllers/paywall_controller.dart';

/// G-05 Paywall — MVP is interest capture only ("Nhận thông báo khi ra mắt").
class PaywallScreen extends ConsumerWidget {
  const PaywallScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
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
            l10n.paywallTitle,
            style: context.text.headlineSmall?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          Gap.gapXs,
          Text(
            l10n.paywallSubtitle,
            style: context.text.bodyMedium?.copyWith(
              color: context.sweep.textSecondary,
              height: 1.5,
            ),
          ),
          Gap.gapLg,
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
                  ? l10n.paywallSubmitted
                  : l10n.paywallNotifyMe,
              icon: state.submitted ? Icons.check_rounded : null,
              loading: state.submitting,
              onPressed: state.submitted || state.submitting
                  ? null
                  : ctrl.submitInterest,
            ),
            Gap.gapXs,
            Text(
              l10n.paywallFinePrint,
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
