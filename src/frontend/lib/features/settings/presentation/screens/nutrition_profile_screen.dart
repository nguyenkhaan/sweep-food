import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/primary_button.dart';
import 'package:sweepfood/features/catalog/presentation/controllers/ingredient_search_controller.dart';
import 'package:sweepfood/features/settings/presentation/controllers/nutrition_profile_controller.dart';
import 'package:sweepfood/shared/domain/nutrition_profile.dart';
import 'package:sweepfood/shared/widgets/dietary_preference_selector.dart';
import 'package:sweepfood/shared/widgets/nutrition_disclaimer_banner.dart';

/// Settings screen for configuring the user's 5-field Nutrition Profile
/// persisted inside `users.preferences`.
class NutritionProfileScreen extends ConsumerStatefulWidget {
  const NutritionProfileScreen({super.key});

  @override
  ConsumerState<NutritionProfileScreen> createState() =>
      _NutritionProfileScreenState();
}

class _NutritionProfileScreenState
    extends ConsumerState<NutritionProfileScreen> {
  final _dislikedController = TextEditingController();
  final _dislikedFocus = FocusNode();
  String _dislikedQuery = '';

  @override
  void dispose() {
    _dislikedController.dispose();
    _dislikedFocus.dispose();
    super.dispose();
  }

  void _submitDisliked([String? value]) {
    final text = (value ?? _dislikedController.text).trim();
    if (text.isEmpty) return;
    final notifier = ref.read(nutritionProfileControllerProvider.notifier);
    final currentLen = ref
        .read(nutritionProfileControllerProvider)
        .profile
        .dislikedIngredients
        .length;
    if (currentLen >= NutritionProfile.maxDislikedIngredients) {
      context.showSnack(context.l10n.nutritionProfileDislikedLimit);
      return;
    }
    notifier.addDislikedIngredient(text);
    _dislikedController.clear();
    setState(() => _dislikedQuery = '');
  }

  Future<void> _save() async {
    final l10n = context.l10n;
    final ok = await ref
        .read(nutritionProfileControllerProvider.notifier)
        .save(l10n);
    if (!mounted) return;
    if (ok) {
      context.showSnack(l10n.nutritionProfileSaved);
      if (GoRouter.maybeOf(context)?.canPop() ?? false) {
        context.pop();
      } else {
        Navigator.of(context).maybePop();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final formState = ref.watch(nutritionProfileControllerProvider);
    final profile = formState.profile;
    final notifier = ref.read(nutritionProfileControllerProvider.notifier);

    return Scaffold(
      resizeToAvoidBottomInset: true,
      appBar: AppBar(title: Text(l10n.nutritionProfileTitle)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.sm, Gap.lg, Gap.xxl),
        keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
        children: [
          Text(
            l10n.nutritionProfileSubtitle,
            style: context.text.bodyMedium?.copyWith(
              color: context.sweep.textSecondary,
              height: 1.4,
            ),
          ),
          Gap.gapSm,
          const NutritionDisclaimerBanner(),
          Gap.gapLg,

          // ── 1. Household size (1–10) ────────────────────────────────────────
          _SectionCard(
            title: l10n.nutritionProfileHouseholdTitle,
            subtitle: l10n.nutritionProfileHouseholdHint,
            icon: Icons.groups_outlined,
            child: _HouseholdSizePicker(
              value: profile.householdSize,
              onChanged: notifier.setHouseholdSize,
            ),
          ),
          Gap.gapMd,

          // ── 2. Diet mode (5 options, reused from Onboarding) ────────────────
          _SectionHeaderBlock(
            title: l10n.nutritionProfileDietTitle,
            subtitle: l10n.nutritionProfileDietHint,
            icon: Icons.restaurant_outlined,
          ),
          Gap.gapXs,
          DietaryPreferenceSelector(
            selected: profile.diet,
            onChanged: notifier.setDiet,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
          ),
          Gap.gapLg,

          // ── 3. Health conditions (multi-select) ─────────────────────────────
          _SectionCard(
            title: l10n.nutritionProfileHealthTitle,
            subtitle: l10n.nutritionProfileHealthHint,
            icon: Icons.monitor_heart_outlined,
            child: Column(
              children: [
                for (var i = 0; i < HealthCondition.values.length; i++) ...[
                  if (i > 0) Gap.gapXs,
                  _HealthConditionTile(
                    condition: HealthCondition.values[i],
                    selected: profile.healthConditions.contains(
                      HealthCondition.values[i],
                    ),
                    onTap: () => notifier.toggleHealthCondition(
                      HealthCondition.values[i],
                    ),
                  ),
                ],
              ],
            ),
          ),
          Gap.gapMd,

          // ── 4. Food allergies (8 groups, safety-first styling) ──────────────
          _SectionCard(
            title: l10n.nutritionProfileAllergiesTitle,
            subtitle: l10n.nutritionProfileAllergiesHint,
            icon: Icons.shield_outlined,
            accentWarning: profile.allergies.isNotEmpty,
            child: Column(
              children: [
                for (var i = 0; i < AllergyGroup.values.length; i++) ...[
                  if (i > 0) Gap.gapXs,
                  _AllergyGroupTile(
                    group: AllergyGroup.values[i],
                    selected: profile.allergies.contains(
                      AllergyGroup.values[i],
                    ),
                    onTap: () => notifier.toggleAllergy(AllergyGroup.values[i]),
                  ),
                ],
              ],
            ),
          ),
          Gap.gapMd,

          // ── 5. Disliked ingredients (free text + catalog autocomplete) ──────
          _SectionCard(
            title: l10n.nutritionProfileDislikedTitle,
            subtitle: l10n.nutritionProfileDislikedHint,
            icon: Icons.no_food_outlined,
            child: _DislikedIngredientsEditor(
              controller: _dislikedController,
              focusNode: _dislikedFocus,
              query: _dislikedQuery,
              selectedItems: profile.dislikedIngredients,
              onQueryChanged: (q) => setState(() => _dislikedQuery = q.trim()),
              onSubmit: _submitDisliked,
              onRemove: notifier.removeDislikedIngredient,
            ),
          ),
        ],
      ),
      bottomNavigationBar: SafeArea(
        top: false,
        child: Container(
          padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.sm, Gap.lg, Gap.md),
          decoration: BoxDecoration(
            color: context.colors.surface,
            border: Border(top: BorderSide(color: context.sweep.hairline)),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (formState.errorMessage != null) ...[
                Padding(
                  padding: const EdgeInsets.only(bottom: Gap.xs),
                  child: Text(
                    formState.errorMessage!,
                    style: context.text.bodySmall?.copyWith(
                      color: context.colors.error,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
              PrimaryButton(
                label: l10n.nutritionProfileSaveCta,
                loading: formState.isSaving,
                onPressed: _save,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SectionHeaderBlock extends StatelessWidget {
  const _SectionHeaderBlock({
    required this.title,
    required this.subtitle,
    required this.icon,
    this.accentWarning = false,
  });

  final String title;
  final String subtitle;
  final IconData icon;
  final bool accentWarning;

  @override
  Widget build(BuildContext context) {
    final iconColor = accentWarning
        ? context.colors.tertiary
        : context.colors.primary;
    final iconBg = accentWarning
        ? context.colors.tertiaryContainer
        : context.colors.primaryContainer;

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(color: iconBg, borderRadius: Radii.brSm),
          child: Icon(icon, size: 18, color: iconColor),
        ),
        Gap.gapSm,
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: context.text.titleSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                subtitle,
                style: context.text.bodySmall?.copyWith(
                  color: context.sweep.textSecondary,
                  height: 1.35,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _SectionCard extends StatelessWidget {
  const _SectionCard({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.child,
    this.accentWarning = false,
  });

  final String title;
  final String subtitle;
  final IconData icon;
  final Widget child;
  final bool accentWarning;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(Gap.md),
      decoration: BoxDecoration(
        color: context.colors.surfaceContainerLowest,
        borderRadius: Radii.brLg,
        border: Border.all(color: context.sweep.hairline),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _SectionHeaderBlock(
            title: title,
            subtitle: subtitle,
            icon: icon,
            accentWarning: accentWarning,
          ),
          Gap.gapMd,
          child,
        ],
      ),
    );
  }
}

class _HouseholdSizePicker extends StatelessWidget {
  const _HouseholdSizePicker({required this.value, required this.onChanged});

  final int value;
  final ValueChanged<int> onChanged;

  static const _quickPresets = [1, 2, 4, 6];

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final canDecrement = value > NutritionProfile.minHouseholdSize;
    final canIncrement = value < NutritionProfile.maxHouseholdSize;

    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _StepperButton(
              icon: Icons.remove_rounded,
              tooltip: '-',
              enabled: canDecrement,
              onPressed: canDecrement ? () => onChanged(value - 1) : null,
            ),
            SizedBox(
              width: 128,
              child: Column(
                children: [
                  Text(
                    '$value',
                    style: context.text.headlineMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: context.colors.primary,
                      fontFeatures: const [FontFeature.tabularFigures()],
                    ),
                  ),
                  Text(
                    l10n.nutritionProfileHouseholdValue(value),
                    style: context.text.labelSmall?.copyWith(
                      color: context.sweep.textSecondary,
                      letterSpacing: 0,
                    ),
                  ),
                ],
              ),
            ),
            _StepperButton(
              icon: Icons.add_rounded,
              tooltip: '+',
              enabled: canIncrement,
              onPressed: canIncrement ? () => onChanged(value + 1) : null,
            ),
          ],
        ),
        Gap.gapSm,
        Wrap(
          spacing: Gap.xs,
          runSpacing: Gap.xs,
          alignment: WrapAlignment.center,
          children: [
            for (final preset in _quickPresets)
              ChoiceChip(
                label: Text(l10n.nutritionProfileHouseholdValue(preset)),
                selected: value == preset,
                onSelected: (_) => onChanged(preset),
              ),
          ],
        ),
      ],
    );
  }
}

class _StepperButton extends StatelessWidget {
  const _StepperButton({
    required this.icon,
    required this.tooltip,
    required this.enabled,
    required this.onPressed,
  });

  final IconData icon;
  final String tooltip;
  final bool enabled;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      enabled: enabled,
      label: tooltip,
      child: Material(
        color: enabled
            ? context.colors.primaryContainer
            : context.sweep.subtleFill,
        shape: const CircleBorder(),
        clipBehavior: Clip.antiAlias,
        child: InkWell(
          onTap: onPressed,
          child: SizedBox(
            width: 48,
            height: 48,
            child: Icon(
              icon,
              color: enabled
                  ? context.colors.onPrimaryContainer
                  : context.sweep.textTertiary,
            ),
          ),
        ),
      ),
    );
  }
}

class _HealthConditionTile extends StatelessWidget {
  const _HealthConditionTile({
    required this.condition,
    required this.selected,
    required this.onTap,
  });

  final HealthCondition condition;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final scheme = context.colors;
    final sweep = context.sweep;

    return Material(
      color: selected ? scheme.primaryContainer : scheme.surface,
      borderRadius: Radii.brMd,
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Container(
          constraints: const BoxConstraints(minHeight: 52),
          padding: const EdgeInsets.symmetric(
            horizontal: Gap.sm,
            vertical: Gap.sm,
          ),
          decoration: BoxDecoration(
            borderRadius: Radii.brMd,
            border: Border.all(
              color: selected ? scheme.primary : sweep.hairline,
              width: selected ? 1.5 : 1,
            ),
          ),
          child: Row(
            children: [
              Icon(
                selected
                    ? Icons.check_box_rounded
                    : Icons.check_box_outline_blank_rounded,
                size: 22,
                color: selected ? scheme.primary : sweep.textTertiary,
              ),
              Gap.gapSm,
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      condition.label(l10n),
                      style: context.text.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                        color: selected
                            ? scheme.onPrimaryContainer
                            : scheme.onSurface,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      condition.description(l10n),
                      style: context.text.bodySmall?.copyWith(
                        color: selected
                            ? scheme.onPrimaryContainer.withValues(alpha: 0.85)
                            : sweep.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _AllergyGroupTile extends StatelessWidget {
  const _AllergyGroupTile({
    required this.group,
    required this.selected,
    required this.onTap,
  });

  final AllergyGroup group;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final scheme = context.colors;
    final sweep = context.sweep;

    return Material(
      color: selected ? scheme.tertiaryContainer : scheme.surface,
      borderRadius: Radii.brMd,
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Container(
          constraints: const BoxConstraints(minHeight: 52),
          padding: const EdgeInsets.symmetric(
            horizontal: Gap.sm,
            vertical: Gap.sm,
          ),
          decoration: BoxDecoration(
            borderRadius: Radii.brMd,
            border: Border.all(
              color: selected ? scheme.tertiary : sweep.hairline,
              width: selected ? 1.5 : 1,
            ),
          ),
          child: Row(
            children: [
              Icon(
                selected
                    ? Icons.gpp_maybe_rounded
                    : Icons.add_circle_outline_rounded,
                size: 22,
                color: selected ? scheme.tertiary : sweep.textTertiary,
              ),
              Gap.gapSm,
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      group.label(l10n),
                      style: context.text.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                        color: selected
                            ? scheme.onTertiaryContainer
                            : scheme.onSurface,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      group.examples(l10n),
                      style: context.text.bodySmall?.copyWith(
                        color: selected
                            ? scheme.onTertiaryContainer.withValues(alpha: 0.85)
                            : sweep.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _DislikedIngredientsEditor extends ConsumerWidget {
  const _DislikedIngredientsEditor({
    required this.controller,
    required this.focusNode,
    required this.query,
    required this.selectedItems,
    required this.onQueryChanged,
    required this.onSubmit,
    required this.onRemove,
  });

  final TextEditingController controller;
  final FocusNode focusNode;
  final String query;
  final List<String> selectedItems;
  final ValueChanged<String> onQueryChanged;
  final ValueChanged<String?> onSubmit;
  final ValueChanged<String> onRemove;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final suggestionsAsync = query.length >= 2
        ? ref.watch(ingredientSearchProvider(query))
        : null;
    final catalogMatches =
        suggestionsAsync?.asData?.value
            .where(
              (ing) => !selectedItems.any(
                (existing) => existing.toLowerCase() == ing.name.toLowerCase(),
              ),
            )
            .take(5)
            .toList() ??
        const [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: controller,
                focusNode: focusNode,
                textInputAction: TextInputAction.done,
                onChanged: onQueryChanged,
                onSubmitted: onSubmit,
                decoration: InputDecoration(
                  hintText: l10n.nutritionProfileDislikedFieldHint,
                  prefixIcon: const Icon(Icons.search_rounded, size: 20),
                ),
              ),
            ),
            Gap.gapXs,
            SizedBox(
              height: 48,
              child: FilledButton.tonal(
                onPressed: () => onSubmit(null),
                style: FilledButton.styleFrom(
                  minimumSize: const Size(64, 48),
                  padding: const EdgeInsets.symmetric(horizontal: Gap.md),
                ),
                child: Text(l10n.nutritionProfileDislikedAdd),
              ),
            ),
          ],
        ),
        if (catalogMatches.isNotEmpty) ...[
          Gap.gapXs,
          Container(
            decoration: BoxDecoration(
              color: context.colors.surface,
              borderRadius: Radii.brMd,
              border: Border.all(color: context.sweep.hairline),
            ),
            child: Column(
              children: [
                for (var i = 0; i < catalogMatches.length; i++) ...[
                  if (i > 0) Divider(height: 1, color: context.sweep.hairline),
                  ListTile(
                    dense: true,
                    visualDensity: VisualDensity.compact,
                    leading: Icon(
                      Icons.add_rounded,
                      size: 18,
                      color: context.colors.primary,
                    ),
                    title: Text(
                      catalogMatches[i].name,
                      style: context.text.bodyMedium,
                    ),
                    onTap: () => onSubmit(catalogMatches[i].name),
                  ),
                ],
              ],
            ),
          ),
        ],
        Gap.gapSm,
        if (selectedItems.isEmpty)
          Text(
            l10n.nutritionProfileDislikedEmpty,
            style: context.text.bodySmall?.copyWith(
              color: context.sweep.textTertiary,
            ),
          )
        else
          Wrap(
            spacing: Gap.xs,
            runSpacing: Gap.xs,
            children: [
              for (final item in selectedItems)
                InputChip(label: Text(item), onDeleted: () => onRemove(item)),
            ],
          ),
      ],
    );
  }
}
