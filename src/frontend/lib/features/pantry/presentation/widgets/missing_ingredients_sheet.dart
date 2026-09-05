import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list_item.dart';
import 'package:sweepfood/features/shopping_list/presentation/controllers/shopping_list_controller.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

class _RecipeMatch {
  const _RecipeMatch({
    required this.dishName,
    required this.matchedIngredients,
    required this.missingIngredients,
  });

  final String dishName;
  final List<String> matchedIngredients;
  final List<_MissingItem> missingIngredients;
}

class _MissingItem {
  const _MissingItem({
    required this.name,
    required this.quantity,
    required this.unit,
    required this.displayQty,
  });

  final String name;
  final double quantity;
  final MeasurementUnit unit;
  final String displayQty;
}

/// Sheet that calculates and displays missing ingredients for selected pantry items.
class MissingIngredientsSheet extends ConsumerStatefulWidget {
  const MissingIngredientsSheet({
    required this.selectedItems,
    super.key,
  });

  final List<PantryItem> selectedItems;

  static Future<void> show(
    BuildContext context, {
    required List<PantryItem> selectedItems,
  }) {
    return showAppBottomSheet(
      context,
      builder: (_) => MissingIngredientsSheet(selectedItems: selectedItems),
    );
  }

  @override
  ConsumerState<MissingIngredientsSheet> createState() =>
      _MissingIngredientsSheetState();
}

class _MissingIngredientsSheetState
    extends ConsumerState<MissingIngredientsSheet> {
  bool _adding = false;

  static final List<({
    String dishName,
    List<({String name, double qty, MeasurementUnit unit, String display})>
        ingredients,
  })> _recipeDb = [
    (
      dishName: 'Salad bơ ức gà',
      ingredients: [
        (name: 'Ức gà', qty: 200, unit: MeasurementUnit.gram, display: '200g'),
        (name: 'Cà chua bi', qty: 100, unit: MeasurementUnit.gram, display: '100g'),
        (name: 'Bơ', qty: 1, unit: MeasurementUnit.fruit, display: '1 quả'),
        (name: 'Xà lách', qty: 150, unit: MeasurementUnit.gram, display: '150g'),
        (name: 'Dầu ô liu', qty: 15, unit: MeasurementUnit.milliliter, display: '15ml'),
      ],
    ),
    (
      dishName: 'Canh chua cá lóc',
      ingredients: [
        (name: 'Cá lóc', qty: 300, unit: MeasurementUnit.gram, display: '300g'),
        (name: 'Cà chua bi', qty: 100, unit: MeasurementUnit.gram, display: '100g'),
        (name: 'Cải bó xôi', qty: 1, unit: MeasurementUnit.bunch, display: '1 bó'),
        (name: 'Đậu bắp', qty: 50, unit: MeasurementUnit.gram, display: '50g'),
        (name: 'Giá đỗ', qty: 100, unit: MeasurementUnit.gram, display: '100g'),
      ],
    ),
    (
      dishName: 'Trứng chiên hành lá',
      ingredients: [
        (name: 'Trứng gà', qty: 3, unit: MeasurementUnit.fruit, display: '3 quả'),
        (name: 'Hành lá', qty: 20, unit: MeasurementUnit.gram, display: '20g'),
        (name: 'Nước mắm', qty: 10, unit: MeasurementUnit.milliliter, display: '10ml'),
      ],
    ),
    (
      dishName: 'Thịt ba chỉ rang cháy cạnh',
      ingredients: [
        (name: 'Thịt ba chỉ', qty: 300, unit: MeasurementUnit.gram, display: '300g'),
        (name: 'Hành tím', qty: 3, unit: MeasurementUnit.fruit, display: '3 củ'),
        (name: 'Nước mắm', qty: 20, unit: MeasurementUnit.milliliter, display: '20ml'),
        (name: 'Đường', qty: 10, unit: MeasurementUnit.gram, display: '10g'),
      ],
    ),
    (
      dishName: 'Đậu hũ sốt cà chua',
      ingredients: [
        (name: 'Đậu hũ non', qty: 2, unit: MeasurementUnit.box, display: '2 hộp'),
        (name: 'Cà chua bi', qty: 200, unit: MeasurementUnit.gram, display: '200g'),
        (name: 'Hành lá', qty: 20, unit: MeasurementUnit.gram, display: '20g'),
      ],
    ),
    (
      dishName: 'Canh cải thịt băm',
      ingredients: [
        (name: 'Cải bó xôi', qty: 1, unit: MeasurementUnit.bunch, display: '1 bó'),
        (name: 'Thịt nạc xay', qty: 150, unit: MeasurementUnit.gram, display: '150g'),
        (name: 'Hành tím', qty: 2, unit: MeasurementUnit.fruit, display: '2 củ'),
      ],
    ),
  ];

  List<_RecipeMatch> _computeMatches() {
    final selectedNames = widget.selectedItems
        .map((e) => e.name.toLowerCase().trim())
        .toSet();

    final matches = <_RecipeMatch>[];

    for (final recipe in _recipeDb) {
      final have = <String>[];
      final missing = <_MissingItem>[];

      for (final ing in recipe.ingredients) {
        final ingNameLower = ing.name.toLowerCase().trim();
        final isSelected = selectedNames.any(
          (sel) => sel.contains(ingNameLower) || ingNameLower.contains(sel),
        );
        if (isSelected) {
          have.add(ing.name);
        } else {
          missing.add(_MissingItem(
            name: ing.name,
            quantity: ing.qty,
            unit: ing.unit,
            displayQty: ing.display,
          ));
        }
      }

      if (have.isNotEmpty) {
        matches.add(_RecipeMatch(
          dishName: recipe.dishName,
          matchedIngredients: have,
          missingIngredients: missing,
        ));
      }
    }

    matches.sort(
      (a, b) => b.matchedIngredients.length.compareTo(a.matchedIngredients.length),
    );

    if (matches.isEmpty) {
      final selectedLabels = widget.selectedItems.map((e) => e.name).toList();
      matches.add(_RecipeMatch(
        dishName: 'Món xào/nấu tổng hợp',
        matchedIngredients: selectedLabels,
        missingIngredients: const [
          _MissingItem(
            name: 'Gia vị tổng hợp (Muối, Tiêu, Nước mắm)',
            quantity: 1,
            unit: MeasurementUnit.pack,
            displayQty: '1 bộ',
          ),
          _MissingItem(
            name: 'Dầu ăn thực vật',
            quantity: 1,
            unit: MeasurementUnit.bottle,
            displayQty: '1 chai',
          ),
          _MissingItem(
            name: 'Tỏi & Hành khô',
            quantity: 100,
            unit: MeasurementUnit.gram,
            displayQty: '100g',
          ),
        ],
      ));
    }

    return matches;
  }

  Future<void> _addMissingToShopping(List<_MissingItem> missingList) async {
    if (_adding || missingList.isEmpty) return;
    setState(() => _adding = true);

    try {
      final controller = ref.read(shoppingListControllerProvider.notifier);
      for (final item in missingList) {
        await controller.addManualItem(
          ShoppingListItemDraft(
            name: item.name,
            quantity: item.quantity,
            unit: item.unit,
          ),
        );
      }
      if (mounted) {
        Navigator.of(context).pop();
        AppSnack.show(
          context,
          'Đã thêm ${missingList.length} nguyên liệu thiếu vào danh sách mua sắm!',
        );
      }
    } catch (e) {
      if (mounted) {
        AppSnack.show(context, 'Có lỗi khi thêm vào danh sách mua: $e');
      }
    } finally {
      if (mounted) setState(() => _adding = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final matches = _computeMatches();
    final allMissing = <String, _MissingItem>{};
    for (final m in matches) {
      for (final item in m.missingIngredients) {
        allMissing.putIfAbsent(item.name, () => item);
      }
    }
    final missingItemsList = allMissing.values.toList();

    return SheetBody(
      title: 'Phân tích nguyên liệu thiếu',
      subtitle:
          'Dựa trên ${widget.selectedItems.length} món bạn đã chọn trong kho',
      child: ConstrainedBox(
        constraints: BoxConstraints(
          maxHeight: MediaQuery.sizeOf(context).height * 0.65,
        ),
        child: Column(
          children: [
            Wrap(
              spacing: Gap.xs,
              runSpacing: Gap.xxs,
              children: [
                for (final item in widget.selectedItems)
                  Chip(
                    avatar: const Icon(
                      Icons.check_circle_rounded,
                      size: 16,
                      color: Colors.green,
                    ),
                    label: Text(
                      item.name,
                      style: context.text.bodySmall?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    backgroundColor: context.sweep.subtleFill,
                    visualDensity: VisualDensity.compact,
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    padding: EdgeInsets.zero,
                  ),
              ],
            ),
            Gap.gapSm,
            const Divider(height: 1),
            Gap.gapSm,
            Expanded(
              child: ListView.separated(
                itemCount: matches.length,
                separatorBuilder: (_, __) => Gap.gapMd,
                itemBuilder: (context, index) {
                  final match = matches[index];
                  return Container(
                    padding: const EdgeInsets.all(Gap.md),
                    decoration: BoxDecoration(
                      color: context.sweep.subtleFill,
                      borderRadius: Radii.brMd,
                      border: Border.all(color: context.sweep.hairline),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(
                              Icons.restaurant_menu_rounded,
                              size: 18,
                              color: Colors.teal,
                            ),
                            const SizedBox(width: Gap.xs),
                            Expanded(
                              child: Text(
                                match.dishName,
                                style: context.text.titleSmall?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: Gap.xs,
                                vertical: 2,
                              ),
                              decoration: BoxDecoration(
                                color: match.missingIngredients.isEmpty
                                    ? Colors.green.withValues(alpha: 0.15)
                                    : Colors.orange.withValues(alpha: 0.15),
                                borderRadius: BorderRadius.circular(Radii.pill),
                              ),
                              child: Text(
                                match.missingIngredients.isEmpty
                                    ? 'Đủ nguyên liệu'
                                    : 'Thiếu ${match.missingIngredients.length} món',
                                style: context.text.labelSmall?.copyWith(
                                  color: match.missingIngredients.isEmpty
                                      ? Colors.green.shade800
                                      : Colors.orange.shade800,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                            ),
                          ],
                        ),
                        Gap.gapXs,
                        Text(
                          'Đã có: ${match.matchedIngredients.join(", ")}',
                          style: context.text.bodySmall?.copyWith(
                            color: Colors.green.shade700,
                          ),
                        ),
                        if (match.missingIngredients.isNotEmpty) ...[
                          const SizedBox(height: 4),
                          Text(
                            'Cần bổ sung:',
                            style: context.text.labelSmall?.copyWith(
                              color: context.sweep.textSecondary,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 2),
                          for (final missing in match.missingIngredients)
                            Padding(
                              padding: const EdgeInsets.only(left: 4, top: 2),
                              child: Row(
                                children: [
                                  const Icon(
                                    Icons.remove_circle_outline_rounded,
                                    size: 14,
                                    color: Colors.deepOrange,
                                  ),
                                  const SizedBox(width: 6),
                                  Expanded(
                                    child: Text(
                                      '${missing.name} (${missing.displayQty})',
                                      style: context.text.bodySmall?.copyWith(
                                        color: context.colors.onSurface,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                        ],
                      ],
                    ),
                  );
                },
              ),
            ),
            Gap.gapSm,
            SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                onPressed: _adding || missingItemsList.isEmpty
                    ? null
                    : () => _addMissingToShopping(missingItemsList),
                icon: _adding
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.add_shopping_cart_rounded, size: 18),
                label: Text(
                  _adding
                      ? 'Đang thêm...'
                      : missingItemsList.isEmpty
                          ? 'Đã đủ nguyên liệu'
                          : 'Thêm  nguyên liệu thiếu vào danh sách mua',
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}