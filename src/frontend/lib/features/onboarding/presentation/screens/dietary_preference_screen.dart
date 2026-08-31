import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/app_text_button.dart';
import 'package:frontend/core/widgets/primary_button.dart';
import 'package:frontend/features/onboarding/domain/entities/onboarding_state.dart';
import 'package:frontend/features/onboarding/presentation/controllers/onboarding_controller.dart';
import 'package:frontend/features/onboarding/presentation/widgets/onboarding_progress.dart';
import 'package:frontend/shared/domain/dietary_preference.dart';
import 'package:go_router/go_router.dart';

/// A-05 Onboarding · Ưu tiên dinh dưỡng (N-01). Skippable.
class DietaryPreferenceScreen extends ConsumerStatefulWidget {
  const DietaryPreferenceScreen({super.key});

  @override
  ConsumerState<DietaryPreferenceScreen> createState() =>
      _DietaryPreferenceScreenState();
}

class _DietaryPreferenceScreenState
    extends ConsumerState<DietaryPreferenceScreen> {
  DietaryPreference _selected = DietaryPreference.balanced;

  void _next({DietaryPreference? save}) {
    if (save != null) {
      ref.read(dietaryPreferenceControllerProvider.notifier).set(save);
    }
    context.push(Routes.onboardingPantry);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(Gap.xl, Gap.md, Gap.xl, Gap.xl),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const OnboardingProgress(step: OnboardingStep.dietaryPreference),
              Gap.gapXl,
              Text(
                l10n.onbDietTitle,
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
              Gap.gapXs,
              Text(
                l10n.onbDietSubtitle,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              Gap.gapLg,
              Expanded(
                child: ListView.separated(
                  itemCount: DietaryPreference.values.length,
                  separatorBuilder: (_, __) => Gap.gapSm,
                  itemBuilder: (context, i) {
                    final pref = DietaryPreference.values[i];
                    return _PreferenceCard(
                      preference: pref,
                      selected: pref == _selected,
                      onTap: () => setState(() => _selected = pref),
                    );
                  },
                ),
              ),
              Gap.gapMd,
              PrimaryButton(
                label: l10n.commonContinue,
                onPressed: () => _next(save: _selected),
              ),
              Gap.gapXxs,
              Center(
                child: AppTextButton(label: l10n.commonSkip, onPressed: _next),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _PreferenceCard extends StatelessWidget {
  const _PreferenceCard({
    required this.preference,
    required this.selected,
    required this.onTap,
  });

  final DietaryPreference preference;
  final bool selected;
  final VoidCallback onTap;

  static const _icons = {
    DietaryPreference.balanced: Icons.balance_rounded,
    DietaryPreference.highProtein: Icons.egg_alt_outlined,
    DietaryPreference.lowCalorie: Icons.local_fire_department_outlined,
    DietaryPreference.moreVeg: Icons.eco_outlined,
  };

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final theme = Theme.of(context);
    return InkWell(
      onTap: onTap,
      borderRadius: Radii.brLg,
      child: Container(
        padding: const EdgeInsets.all(Gap.md),
        decoration: BoxDecoration(
          color: selected ? scheme.primaryContainer : scheme.surface,
          borderRadius: Radii.brLg,
          border: Border.all(
            color: selected ? scheme.primary : scheme.outlineVariant,
            width: selected ? 1.5 : 1,
          ),
        ),
        child: Row(
          children: [
            Icon(
              _icons[preference],
              color: selected ? scheme.primary : scheme.onSurfaceVariant,
            ),
            Gap.gapSm,
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    preference.label(context.l10n),
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  Gap.gapXxs,
                  Text(
                    preference.description(context.l10n),
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: scheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              selected
                  ? Icons.radio_button_checked_rounded
                  : Icons.radio_button_unchecked_rounded,
              color: selected ? scheme.primary : scheme.outline,
            ),
          ],
        ),
      ),
    );
  }
}
