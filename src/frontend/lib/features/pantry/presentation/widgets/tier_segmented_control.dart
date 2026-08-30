import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/shared/domain/storage_tier.dart';

/// Horizontal "Tất cả · Ăn liền · Ngăn mát · Ngăn đông · Kệ đồ khô" selector
/// with per-tier counts (K-01). `null` = Tất cả.
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
      return Padding(
        padding: const EdgeInsets.only(right: Gap.xs),
        child: ChoiceChip(
          label: Text('$label  $count'),
          selected: on,
          onSelected: (_) => onSelected(tier),
          showCheckmark: false,
          selectedColor: context.colors.primary,
          labelStyle: context.text.labelMedium?.copyWith(
            color: on ? context.colors.onPrimary : context.sweep.textSecondary,
          ),
          side: BorderSide(color: on ? context.colors.primary : context.sweep.hairline),
        ),
      );
    }

    return SizedBox(
      height: 42,
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: Gap.lg),
        children: [
          chip(null, 'Tất cả'),
          for (final t in StorageTier.values) chip(t, t.shortLabel),
        ],
      ),
    );
  }
}
