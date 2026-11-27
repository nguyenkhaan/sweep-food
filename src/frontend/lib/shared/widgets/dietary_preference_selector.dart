import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';

/// Reusable 5-option dietary mode picker shared by Onboarding (A-05) and the
/// Nutrition Profile screen in Settings.
class DietaryPreferenceSelector extends StatelessWidget {
  const DietaryPreferenceSelector({
    required this.selected,
    required this.onChanged,
    this.shrinkWrap = false,
    this.physics,
    super.key,
  });

  final DietaryPreference selected;
  final ValueChanged<DietaryPreference> onChanged;
  final bool shrinkWrap;
  final ScrollPhysics? physics;

  static const _icons = <DietaryPreference, IconData>{
    DietaryPreference.balanced: AppIcons.scale,
    DietaryPreference.highProtein: AppIcons.egg,
    DietaryPreference.lowCalorie: AppIcons.flame,
    DietaryPreference.moreVeg: AppIcons.sprout,
    DietaryPreference.vegetarian: AppIcons.leaf,
  };

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      shrinkWrap: shrinkWrap,
      physics: physics,
      itemCount: DietaryPreference.values.length,
      separatorBuilder: (_, __) => Gap.gapXs,
      itemBuilder: (context, index) {
        final preference = DietaryPreference.values[index];
        return _DietaryOptionCard(
          preference: preference,
          icon: _icons[preference] ?? AppIcons.utensils,
          selected: preference == selected,
          onTap: () => onChanged(preference),
        );
      },
    );
  }
}

class _DietaryOptionCard extends StatelessWidget {
  const _DietaryOptionCard({
    required this.preference,
    required this.icon,
    required this.selected,
    required this.onTap,
  });

  final DietaryPreference preference;
  final IconData icon;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final scheme = context.colors;
    final sweep = context.sweep;
    final l10n = context.l10n;

    return Semantics(
      selected: selected,
      button: true,
      label: preference.label(l10n),
      child: Material(
        color: selected
            ? scheme.primaryContainer
            : scheme.surfaceContainerLowest,
        borderRadius: Radii.brLg,
        clipBehavior: Clip.antiAlias,
        child: InkWell(
          onTap: onTap,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 160),
            constraints: const BoxConstraints(minHeight: 64),
            padding: const EdgeInsets.all(Gap.md),
            decoration: BoxDecoration(
              borderRadius: Radii.brLg,
              border: Border.all(
                color: selected ? scheme.primary : sweep.hairline,
                width: selected ? 1.5 : 1,
              ),
            ),
            child: Row(
              children: [
                Container(
                  width: 38,
                  height: 38,
                  decoration: BoxDecoration(
                    color: selected
                        ? scheme.primary.withValues(alpha: 0.14)
                        : sweep.subtleFill,
                    borderRadius: Radii.brSm,
                  ),
                  child: Icon(
                    icon,
                    size: 20,
                    color: selected ? scheme.primary : sweep.textSecondary,
                  ),
                ),
                Gap.gapSm,
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Wrap(
                        spacing: Gap.xs,
                        runSpacing: Gap.xxs,
                        crossAxisAlignment: WrapCrossAlignment.center,
                        children: [
                          Text(
                            preference.label(l10n),
                            style: context.text.titleSmall?.copyWith(
                              fontWeight: FontWeight.w700,
                              color: selected
                                  ? scheme.onPrimaryContainer
                                  : scheme.onSurface,
                            ),
                          ),
                          if (preference.isHardFilter)
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: Gap.xs,
                                vertical: 2,
                              ),
                              decoration: BoxDecoration(
                                color: selected
                                    ? scheme.primary
                                    : scheme.primaryContainer,
                                borderRadius: BorderRadius.circular(Radii.pill),
                              ),
                              child: Text(
                                l10n.nutritionProfileHardFilterTag,
                                style: context.text.labelSmall?.copyWith(
                                  letterSpacing: 0,
                                  fontWeight: FontWeight.w700,
                                  color: selected
                                      ? scheme.onPrimary
                                      : scheme.onPrimaryContainer,
                                ),
                              ),
                            ),
                        ],
                      ),
                      const SizedBox(height: 3),
                      Text(
                        preference.description(l10n),
                        style: context.text.bodySmall?.copyWith(
                          color: selected
                              ? scheme.onPrimaryContainer.withValues(
                                  alpha: 0.85,
                                )
                              : sweep.textSecondary,
                          height: 1.35,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: Gap.xs),
                Icon(
                  selected ? AppIcons.checkCircle : AppIcons.circle,
                  size: 20,
                  color: selected ? scheme.primary : sweep.textTertiary,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
