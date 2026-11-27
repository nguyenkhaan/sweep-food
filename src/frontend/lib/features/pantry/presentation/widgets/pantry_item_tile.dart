import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/core/widgets/pantry_item_card.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

/// Adapts a [PantryItem] entity onto the shared [PantryItemCard] presentation
/// widget (K-01, H-01 "Cần dùng sớm").
class PantryItemTile extends StatelessWidget {
  const PantryItemTile({
    required this.item,
    this.onTap,
    this.onMore,
    this.selected,
    this.onSelectedChanged,
    super.key,
  });

  final PantryItem item;
  final VoidCallback? onTap;
  final VoidCallback? onMore;
  final bool? selected;
  final ValueChanged<bool?>? onSelectedChanged;

  @override
  Widget build(BuildContext context) {
    return PantryItemCard(
      name: item.name,
      subtitle: [
        item.quantityLabel,
        if (item.category.trim().isNotEmpty) item.category.trim(),
      ].join(' · '),
      daysUntilExpiry: item.daysUntilExpiry,
      tier: item.storageTier,
      category: item.category,
      referenceShelfLifeDays: item.referenceShelfLifeDays,
      leadingIcon: AppIcons.forCategory(item.category, fallbackName: item.name),
      selected: selected,
      onSelectedChanged: onSelectedChanged,
      onTap: onTap,
      onMore: onMore,
    );
  }
}

/// Icon for a tier (used by the detail screen chips).
IconData tierIcon(StorageTier tier) => AppIcons.forTier(tier);
