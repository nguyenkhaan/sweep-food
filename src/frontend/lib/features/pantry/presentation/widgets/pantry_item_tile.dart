import 'package:flutter/material.dart';
import 'package:sweepfood/core/widgets/pantry_item_card.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

const _categoryIcon = <String, IconData>{
  'Rau lá': Icons.grass_rounded,
  'Rau củ': Icons.eco_outlined,
  'Rau gia vị': Icons.spa_outlined,
  'Thịt': Icons.restaurant_rounded,
  'Hải sản': Icons.set_meal_rounded,
  'Đạm': Icons.egg_outlined,
  'Đạm thực vật': Icons.spa_outlined,
  'Sữa': Icons.local_drink_outlined,
  'Ngũ cốc': Icons.rice_bowl_outlined,
  'Gia vị': Icons.science_outlined,
};

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
      subtitle: '${item.quantityLabel} · ${item.category}',
      daysUntilExpiry: item.daysUntilExpiry,
      tier: item.storageTier,
      leadingIcon: _categoryIcon[item.category] ?? Icons.eco_outlined,
      selected: selected,
      onSelectedChanged: onSelectedChanged,
      onTap: onTap,
      onMore: onMore,
    );
  }
}

/// Icon for a tier (used by the detail screen chips).
IconData tierIcon(StorageTier tier) => switch (tier) {
      StorageTier.eatSoon => Icons.local_fire_department_rounded,
      StorageTier.fridge => Icons.kitchen_rounded,
      StorageTier.freezer => Icons.ac_unit_rounded,
      StorageTier.pantryShelf => Icons.inventory_2_rounded,
    };
