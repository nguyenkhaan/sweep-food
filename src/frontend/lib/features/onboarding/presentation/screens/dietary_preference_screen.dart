import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_text_button.dart';
import 'package:sweepfood/core/widgets/primary_button.dart';
import 'package:sweepfood/features/onboarding/domain/entities/onboarding_state.dart';
import 'package:sweepfood/features/onboarding/presentation/controllers/onboarding_controller.dart';
import 'package:sweepfood/features/onboarding/presentation/widgets/onboarding_progress.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';
import 'package:sweepfood/shared/widgets/dietary_preference_selector.dart';
import 'package:sweepfood/shared/widgets/nutrition_disclaimer_banner.dart';

/// A-05 Onboarding · Chọn chế độ ăn (5 lựa chọn gồm Ăn chay). Skippable.
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
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.md, Gap.lg, Gap.lg),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const OnboardingProgress(step: OnboardingStep.dietaryPreference),
              Gap.gapLg,
              Text(
                l10n.onbDietTitle,
                style: context.text.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
              Gap.gapXxs,
              Text(
                l10n.onbDietSubtitle,
                style: context.text.bodyMedium?.copyWith(
                  color: context.sweep.textSecondary,
                ),
              ),
              Gap.gapMd,
              Expanded(
                child: DietaryPreferenceSelector(
                  selected: _selected,
                  onChanged: (pref) => setState(() => _selected = pref),
                ),
              ),
              Gap.gapSm,
              const NutritionDisclaimerBanner(compact: true),
              Gap.gapSm,
              PrimaryButton(
                label: l10n.commonContinue,
                loading: _saving,
                onPressed: () => _next(save: _selected),
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
    );
  }
}
