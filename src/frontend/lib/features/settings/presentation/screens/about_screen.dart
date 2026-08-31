import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_colors.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/config/app_constants.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/app_snackbar.dart';
import 'package:frontend/features/settings/presentation/widgets/settings_group.dart';

/// P-06 Giới thiệu & dữ liệu — data sources + the estimate/health disclaimer.
class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Scaffold(
      appBar: AppBar(title: Text(l10n.aboutTitle)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.lg, Gap.lg, Gap.xxl),
        children: [
          Center(
            child: Column(
              children: [
                Container(
                  width: 64,
                  height: 64,
                  decoration: BoxDecoration(
                    color: context.colors.primaryContainer,
                    borderRadius: Radii.brLg,
                  ),
                  child: Icon(
                    Icons.eco_rounded,
                    size: 34,
                    color: context.colors.onPrimaryContainer,
                  ),
                ),
                Gap.gapSm,
                Text(
                  AppConstants.appName,
                  style: context.text.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                Text(
                  l10n.aboutVersion,
                  style: context.text.bodySmall?.copyWith(
                    color: context.sweep.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          Gap.gapLg,
          SettingsGroup(
            label: l10n.aboutDataSources,
            rows: [
              SettingsRow(
                icon: Icons.restaurant_rounded,
                label: l10n.aboutNutritionData,
                trailing: l10n.aboutNutritionSource,
              ),
              SettingsRow(
                icon: Icons.ac_unit_rounded,
                label: l10n.aboutShelfLifeData,
                trailing: 'FoodKeeper',
              ),
            ],
          ),
          Gap.gapMd,
          Container(
            padding: const EdgeInsets.all(Gap.md),
            decoration: const BoxDecoration(
              color: BrandPalette.brick100,
              borderRadius: Radii.brLg,
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(
                  Icons.warning_amber_rounded,
                  size: 18,
                  color: BrandPalette.brick500,
                ),
                Gap.gapSm,
                Expanded(
                  child: Text(
                    l10n.aboutDisclaimer,
                    style: context.text.bodySmall?.copyWith(
                      color: BrandPalette.brick500,
                      height: 1.55,
                    ),
                  ),
                ),
              ],
            ),
          ),
          Gap.gapMd,
          SettingsGroup(
            rows: [
              SettingsRow(
                icon: Icons.description_outlined,
                label: l10n.termsOfUse,
                onTap: () => AppSnack.show(context, l10n.willOpenInBrowser),
              ),
              SettingsRow(
                icon: Icons.shield_outlined,
                label: l10n.termsPrivacy,
                onTap: () => AppSnack.show(context, l10n.willOpenInBrowser),
              ),
              SettingsRow(
                icon: Icons.star_outline_rounded,
                label: l10n.aboutRateApp,
                onTap: () => AppSnack.show(context, l10n.aboutThanks),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
