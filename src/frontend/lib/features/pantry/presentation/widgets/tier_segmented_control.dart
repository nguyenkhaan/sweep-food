import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

/// Horizontal "Tất cả · Ăn liền · Ngăn mát · Ngăn đông · Kệ đồ khô" selector
/// with per-tier icons & counts (K-01). `null` = Tất cả.
class TierSegmentedControl extends StatelessWidget {
  const TierSegmentedControl({
    required this.selected,
    required this.counts,
    required this.onSelected,
    super.key,
  });

  final StorageTier? selected;
  final Map<StorageTier?, int> counts;
  final ValueChanged<StorageTier?> onSelected;

  @override
  Widget build(BuildContext context) {
    Widget chip(StorageTier? tier, String label) {
      final on = tier == selected;
      final count = counts[tier] ?? 0;
      final icon = tier == null ? AppIcons.pantry : AppIcons.forTier(tier);
      final fg = on ? context.colors.onPrimary : context.sweep.textSecondary;

      return Padding(
        padding: const EdgeInsets.only(right: Gap.xs),
        child: ChoiceChip(
          avatar: Icon(icon, size: 15, color: fg),
          label: Text('$label · $count'),
          selected: on,
          onSelected: (_) {
            AppHaptics.selection();
            onSelected(tier);
          },
          showCheckmark: false,
          selectedColor: context.colors.primary,
          backgroundColor: context.colors.surfaceContainerLowest,
          labelStyle: context.text.labelMedium?.copyWith(
            color: fg,
            fontWeight: on ? FontWeight.w700 : FontWeight.w500,
          ),
          side: BorderSide(
            color: on ? context.colors.primary : context.sweep.hairline,
          ),
        ),
      );
    }

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.symmetric(horizontal: Gap.lg),
      child: Row(
        children: [
          chip(null, context.l10n.tierAll),
          for (final t in StorageTier.values)
            chip(t, t.shortLabel(context.l10n)),
        ],
      ),
    );
  }
}
