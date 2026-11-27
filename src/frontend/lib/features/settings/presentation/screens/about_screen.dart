import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/config/app_constants.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_logo.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
import 'package:sweepfood/features/settings/presentation/widgets/settings_group.dart';

/// P-06 Giới thiệu & dữ liệu (Concept B · Format 1).
class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;

    return EmeraldSystemOverlay(
      child: Scaffold(
        backgroundColor: cs.surface,
        body: Column(
          children: [
            EmeraldSplitHeader(title: l10n.aboutTitle),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(
                  Gap.lg,
                  Gap.sm,
                  Gap.lg,
                  Gap.xxl,
                ),
                children: [
                  Center(
                    child: Column(
                      children: [
                        const AppLogo(size: 64),
                        Gap.gapSm,
                        Text(
                          AppConstants.appName,
                          style: context.text.titleLarge?.copyWith(
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          l10n.aboutVersion,
                          style: context.text.bodySmall?.copyWith(
                            color: sweep.textSecondary,
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
                        icon: AppIcons.utensils,
                        label: l10n.aboutNutritionData,
                        trailing: l10n.aboutNutritionSource,
                      ),
                      SettingsRow(
                        icon: AppIcons.snowflake,
                        label: l10n.aboutShelfLifeData,
                        trailing: 'FoodKeeper',
                      ),
                    ],
                  ),
                  Gap.gapMd,
                  Container(
                    padding: const EdgeInsets.all(Gap.md),
                    decoration: BoxDecoration(
                      color: sweep.soon.bg,
                      borderRadius: Radii.brXl,
                      border: Border.all(
                        color: sweep.soon.fg.withValues(alpha: 0.25),
                      ),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Icon(AppIcons.warning, size: 18, color: sweep.soon.fg),
                        const SizedBox(width: Gap.sm),
                        Expanded(
                          child: Text(
                            l10n.aboutDisclaimer,
                            style: context.text.bodySmall?.copyWith(
                              color: sweep.soon.fg,
                              height: 1.5,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
