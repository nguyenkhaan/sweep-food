import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_colors.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/shared/domain/storage_tier.dart';

const _tierIcon = {
  StorageTier.eatSoon: Icons.local_fire_department_rounded,
  StorageTier.fridge: Icons.kitchen_rounded,
  StorageTier.freezer: Icons.ac_unit_rounded,
  StorageTier.pantryShelf: Icons.inventory_2_rounded,
};

const _tierKind = {
  StorageTier.eatSoon: TierKind.eatSoon,
  StorageTier.fridge: TierKind.fridge,
  StorageTier.freezer: TierKind.freezer,
  StorageTier.pantryShelf: TierKind.pantryShelf,
};

/// Small tinted chip with an icon for a storage tier.
class TierChip extends StatelessWidget {
  const TierChip(this.tier, {this.dense = false, super.key});

  final StorageTier tier;
  final bool dense;

  @override
  Widget build(BuildContext context) {
    final c = context.sweep.tier(_tierKind[tier]!);
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: dense ? 7 : 10,
        vertical: dense ? 2 : 4,
      ),
      decoration: BoxDecoration(
        color: c.bg,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(_tierIcon[tier], size: dense ? 11 : 13, color: c.fg),
          const SizedBox(width: 5),
          Text(
            tier.shortLabel(context.l10n),
            style: context.text.labelMedium?.copyWith(
              color: c.fg,
              fontWeight: FontWeight.w600,
              fontSize: dense ? 10 : 12,
            ),
          ),
        ],
      ),
    );
  }
}
