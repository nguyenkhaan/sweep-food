import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_text_button.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
import 'package:sweepfood/features/onboarding/presentation/controllers/onboarding_controller.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';
import 'package:sweepfood/shared/widgets/dietary_preference_selector.dart';
import 'package:sweepfood/shared/widgets/nutrition_disclaimer_banner.dart';

/// A-05 Onboarding · Chọn chế độ ăn (Concept B · Format 1).
class DietaryPreferenceScreen extends ConsumerStatefulWidget {
  const DietaryPreferenceScreen({super.key});

  @override
  ConsumerState<DietaryPreferenceScreen> createState() =>
      _DietaryPreferenceScreenState();
}

class _DietaryPreferenceScreenState
    extends ConsumerState<DietaryPreferenceScreen> {
  late DietaryPreference _selected;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _selected =
        ref.read(dietaryPreferenceControllerProvider) ??
        DietaryPreference.balanced;
  }

  Future<void> _next({DietaryPreference? save}) async {
    if (_saving) return;
    if (save != null) {
      setState(() => _saving = true);
      await ref.read(dietaryPreferenceControllerProvider.notifier).set(save);
      if (!mounted) return;
      setState(() => _saving = false);
    }
    if (mounted) {
      context.push(Routes.onboardingPantry);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final cs = context.colors;
    final sweep = context.sweep;

    return EmeraldSystemOverlay(
      child: Scaffold(
        backgroundColor: cs.surface,
        body: Column(
          children: [
            EmeraldSplitHeader(
              title: l10n.onbDietTitle,
              subtitle: l10n.onbDietSubtitle,
              showBack: false,
              trailing: const EmeraldHeaderPill(label: '1 / 2'),
              bottom: ClipRRect(
                borderRadius: BorderRadius.circular(Radii.pill),
                child: LinearProgressIndicator(
                  value: 0.5,
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
                    Gap.xs,
                    Gap.lg,
                    Gap.md,
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Expanded(
                        child: DietaryPreferenceSelector(
                          selected: _selected,
                          onChanged: (pref) => setState(() => _selected = pref),
                        ),
                      ),
                      Gap.gapSm,
                      const NutritionDisclaimerBanner(compact: true),
                      Gap.gapSm,
                      SizedBox(
                        height: 50,
                        child: FilledButton(
                          style: FilledButton.styleFrom(
                            backgroundColor: sweep.ctaWarm,
                            foregroundColor: sweep.onCtaWarm,
                            shape: const RoundedRectangleBorder(
                              borderRadius: Radii.brMd,
                            ),
                          ),
                          onPressed: _saving
                              ? null
                              : () => _next(save: _selected),
                          child: _saving
                              ? SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2.2,
                                    color: sweep.onCtaWarm,
                                  ),
                                )
                              : Text(
                                  l10n.commonContinue,
                                  style: const TextStyle(
                                    fontSize: 15,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                        ),
                      ),
                      Gap.gapXxs,
                      Center(
                        child: AppTextButton(
                          label: l10n.commonSkip,
                          onPressed: _saving ? null : () => _next(),
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
