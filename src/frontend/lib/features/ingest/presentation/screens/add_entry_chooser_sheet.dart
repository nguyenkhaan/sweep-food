// lib/features/ingest/presentation/screens/add_entry_chooser_sheet.dart
// G-03 — Sheet chọn phương thức nhập nguyên liệu (Concept B · Format 1)

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/tactile_card.dart';

/// Mở sheet này thay vì navigate — dùng [showAddEntryChooser].
Future<void> showAddEntryChooser(BuildContext context) {
  return showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    useRootNavigator: true,
    useSafeArea: true,
    showDragHandle: false,
    backgroundColor: Colors.transparent,
    builder: (_) => const AddEntryChooserSheet(),
  );
}

/// G-03 — Bottom sheet chọn phương thức nhập nguyên liệu (Concept B · Format 1:
/// Emerald Hero Scan Card + 2 Bento Shortcuts).
class AddEntryChooserSheet extends StatelessWidget {
  const AddEntryChooserSheet({super.key});

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    final sweep = context.sweep;
    final l10n = context.l10n;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: Radii.brSheet,
        boxShadow: Shadows.e3,
      ),
      child: SafeArea(
        top: false,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.sm, Gap.lg, Gap.xl),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Center(
                  child: Container(
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                      color: sweep.hairline,
                      borderRadius: BorderRadius.circular(Radii.pill),
                    ),
                  ),
                ),
                Gap.gapMd,
                Text(
                  l10n.pantryAddIngredient,
                  style: context.text.titleLarge?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  'Chọn cách nhanh nhất để đưa thực phẩm vào kho',
                  style: context.text.bodySmall?.copyWith(
                    color: sweep.textSecondary,
                  ),
                ),
                Gap.gapMd,
                _HeroScanCard(
                  title: l10n.chooserScanOcr,
                  subtitle: l10n.chooserScanOcrSub,
                  onTap: () {
                    context.pop();
                    context.push(
                      '${Routes.pantry}/${Routes.scanCamera}?mode=label',
                    );
                  },
                ),
                const SizedBox(height: Gap.sm),
                IntrinsicHeight(
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Expanded(
                        child: _BentoOptionCard(
                          icon: AppIcons.mic,
                          iconBg: sweep.culinaryAccentBg,
                          iconFg: sweep.ctaWarm,
                          title: l10n.chooserVoice,
                          subtitle: l10n.chooserVoiceSub,
                          onTap: () {
                            context.pop();
                            context.push(
                              '${Routes.pantry}/${Routes.scanVoiceCapture}',
                            );
                          },
                        ),
                      ),
                      const SizedBox(width: Gap.sm),
                      Expanded(
                        child: _BentoOptionCard(
                          icon: AppIcons.keyboard,
                          iconBg: cs.primaryContainer,
                          iconFg: cs.primary,
                          title: l10n.chooserManual,
                          subtitle: l10n.chooserManualSub,
                          onTap: () {
                            context.pop();
                            context.push(
                              '${Routes.pantry}/${Routes.addIngredient}',
                            );
                          },
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _HeroScanCard extends StatelessWidget {
  const _HeroScanCard({
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final String title;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    return TactileCard(
      color: sweep.heroSurface,
      borderColor: sweep.heroSurfaceElevated,
      padding: const EdgeInsets.all(Gap.md),
      onTap: () {
        AppHaptics.selection();
        onTap();
      },
      child: Row(
        children: [
          Container(
            width: 46,
            height: 46,
            decoration: BoxDecoration(
              color: sweep.heroSurfaceElevated,
              borderRadius: Radii.brMd,
              border: Border.all(
                color: sweep.onHeroSurface.withValues(alpha: 0.16),
              ),
            ),
            child: Icon(AppIcons.scan, size: 22, color: sweep.onHeroSurface),
          ),
          const SizedBox(width: Gap.sm + 4),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: sweep.ctaWarm,
                    borderRadius: BorderRadius.circular(Radii.pill),
                  ),
                  child: Text(
                    'Nhanh nhất',
                    style: context.text.labelSmall?.copyWith(
                      color: sweep.onCtaWarm,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.2,
                    ),
                  ),
                ),
                const SizedBox(height: 5),
                Text(
                  title,
                  style: context.text.titleSmall?.copyWith(
                    color: sweep.onHeroSurface,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  subtitle,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: context.text.bodySmall?.copyWith(
                    color: sweep.onHeroMuted,
                  ),
                ),
              ],
            ),
          ),
          Icon(AppIcons.chevronRight, size: 18, color: sweep.onHeroMuted),
        ],
      ),
    );
  }
}

class _BentoOptionCard extends StatelessWidget {
  const _BentoOptionCard({
    required this.icon,
    required this.iconBg,
    required this.iconFg,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final Color iconBg;
  final Color iconFg;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    final sweep = context.sweep;
    return TactileCard(
      color: cs.surfaceContainerLowest,
      borderColor: sweep.hairline,
      boxShadow: Shadows.e1,
      padding: const EdgeInsets.all(Gap.md - 2),
      onTap: () {
        AppHaptics.selection();
        onTap();
      },
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  color: iconBg,
                  borderRadius: Radii.brMd,
                ),
                child: Icon(icon, size: 19, color: iconFg),
              ),
              const Spacer(),
              Icon(AppIcons.chevronRight, size: 15, color: sweep.textTertiary),
            ],
          ),
          const SizedBox(height: Gap.sm + 2),
          Text(
            title,
            style: context.text.titleSmall?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            subtitle,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: context.text.bodySmall?.copyWith(
              color: sweep.textTertiary,
              height: 1.35,
            ),
          ),
        ],
      ),
    );
  }
}
