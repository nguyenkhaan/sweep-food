import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/features/ingest/presentation/screens/add_entry_chooser_sheet.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list_item.dart';
import 'package:sweepfood/features/shopping_list/presentation/controllers/shopping_list_controller.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

class RecipeMatchItem {
  const RecipeMatchItem({
    required this.dishId,
    required this.dishName,
    required this.meta,
    required this.matchedIngredients,
    required this.missingIngredients,
  });

  final String dishId;
  final String dishName;
  final String meta;
  final List<String> matchedIngredients;
  final List<MissingIngredientItem> missingIngredients;
}

class MissingIngredientItem {
  const MissingIngredientItem({
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

/// Screen showing recipes that can be prepared with selected pantry items,
/// including matched ingredients and missing ingredients needed.
class CookableRecipesScreen extends ConsumerStatefulWidget {
  const CookableRecipesScreen({
    required this.selectedItems,
    this.initialPrompt = '',
    super.key,
  });

  final List<PantryItem> selectedItems;
  final String initialPrompt;

  @override
  ConsumerState<CookableRecipesScreen> createState() =>
      _CookableRecipesScreenState();
}

class _CookableRecipesScreenState extends ConsumerState<CookableRecipesScreen> {
  bool _adding = false;
  late String _activePrompt;

  @override
  void initState() {
    super.initState();
    _activePrompt = widget.initialPrompt.trim();
  }

  static final List<({
    String dishId,
    String dishName,
    String meta,
    List<({String name, double qty, MeasurementUnit unit, String display})>
        ingredients,
  })> _recipeDb = [
    (
      dishId: 'd1',
      dishName: 'Salad bơ ức gà',
      meta: '15 phút · Dễ · 2 khẩu phần',
      ingredients: [
        (name: 'Ức gà', qty: 200, unit: MeasurementUnit.gram, display: '200g'),
        (name: 'Cà chua bi', qty: 100, unit: MeasurementUnit.gram, display: '100g'),
        (name: 'Bơ', qty: 1, unit: MeasurementUnit.fruit, display: '1 quả'),
        (name: 'Xà lách', qty: 150, unit: MeasurementUnit.gram, display: '150g'),
        (name: 'Dầu ô liu', qty: 15, unit: MeasurementUnit.milliliter, display: '15ml'),
      ],
    ),
    (
      dishId: 'd2',
      dishName: 'Canh chua cá lóc',
      meta: '35 phút · Trung bình · 3 khẩu phần',
      ingredients: [
        (name: 'Cá lóc', qty: 300, unit: MeasurementUnit.gram, display: '300g'),
        (name: 'Cà chua bi', qty: 100, unit: MeasurementUnit.gram, display: '100g'),
        (name: 'Cải bó xôi', qty: 1, unit: MeasurementUnit.bunch, display: '1 bó'),
        (name: 'Đậu bắp', qty: 50, unit: MeasurementUnit.gram, display: '50g'),
        (name: 'Giá đỗ', qty: 100, unit: MeasurementUnit.gram, display: '100g'),
      ],
    ),
    (
      dishId: 'd3',
      dishName: 'Trứng chiên hành lá',
      meta: '10 phút · Dễ · 2 khẩu phần',
      ingredients: [
        (name: 'Trứng gà', qty: 3, unit: MeasurementUnit.fruit, display: '3 quả'),
        (name: 'Hành lá', qty: 20, unit: MeasurementUnit.gram, display: '20g'),
        (name: 'Nước mắm', qty: 10, unit: MeasurementUnit.milliliter, display: '10ml'),
      ],
    ),
    (
      dishId: 'd4',
      dishName: 'Thịt ba chỉ rang cháy cạnh',
      meta: '25 phút · Trung bình · 3 khẩu phần',
      ingredients: [
        (name: 'Thịt ba chỉ', qty: 300, unit: MeasurementUnit.gram, display: '300g'),
        (name: 'Hành tím', qty: 3, unit: MeasurementUnit.fruit, display: '3 củ'),
        (name: 'Nước mắm', qty: 20, unit: MeasurementUnit.milliliter, display: '20ml'),
        (name: 'Đường', qty: 10, unit: MeasurementUnit.gram, display: '10g'),
      ],
    ),
    (
      dishId: 'd5',
      dishName: 'Đậu hũ sốt cà chua',
      meta: '15 phút · Dễ · 2 khẩu phần',
      ingredients: [
        (name: 'Đậu hũ non', qty: 2, unit: MeasurementUnit.box, display: '2 hộp'),
        (name: 'Cà chua bi', qty: 200, unit: MeasurementUnit.gram, display: '200g'),
        (name: 'Hành lá', qty: 20, unit: MeasurementUnit.gram, display: '20g'),
      ],
    ),
    (
      dishId: 'd6',
      dishName: 'Canh cải thịt băm',
      meta: '20 phút · Dễ · 2 khẩu phần',
      ingredients: [
        (name: 'Cải bó xôi', qty: 1, unit: MeasurementUnit.bunch, display: '1 bó'),
        (name: 'Thịt nạc xay', qty: 150, unit: MeasurementUnit.gram, display: '150g'),
        (name: 'Hành tím', qty: 2, unit: MeasurementUnit.fruit, display: '2 củ'),
      ],
    ),
  ];

  List<RecipeMatchItem> _computeMatches() {
    final selectedNames = widget.selectedItems
        .map((e) => e.name.toLowerCase().trim())
        .toSet();

    final matches = <RecipeMatchItem>[];

    for (final recipe in _recipeDb) {
      final have = <String>[];
      final missing = <MissingIngredientItem>[];

      for (final ing in recipe.ingredients) {
        final ingNameLower = ing.name.toLowerCase().trim();
        final isSelected = selectedNames.any(
          (sel) => sel.contains(ingNameLower) || ingNameLower.contains(sel),
        );
        if (isSelected) {
          have.add(ing.name);
        } else {
          missing.add(MissingIngredientItem(
            name: ing.name,
            quantity: ing.qty,
            unit: ing.unit,
            displayQty: ing.display,
          ));
        }
      }

      if (have.isNotEmpty) {
        matches.add(RecipeMatchItem(
          dishId: recipe.dishId,
          dishName: recipe.dishName,
          meta: recipe.meta,
          matchedIngredients: have,
          missingIngredients: missing,
        ));
      }
    }

    if (widget.selectedItems.isEmpty) {
      return [];
    }

    if (_activePrompt.isNotEmpty) {
      final promptWords = _activePrompt.toLowerCase().split(RegExp(r'\s+'));
      final filtered = matches.where((m) {
        final content = '${m.dishName} ${m.meta} ${m.matchedIngredients.join(' ')} ${m.missingIngredients.map((e) => e.name).join(' ')}'.toLowerCase();
        return promptWords.any((w) => w.isNotEmpty && content.contains(w));
      }).toList();
      if (filtered.isNotEmpty) {
        return filtered;
      }
    }

    matches.sort(
      (a, b) => b.matchedIngredients.length.compareTo(a.matchedIngredients.length),
    );

    if (matches.isEmpty) {
      final selectedLabels = widget.selectedItems.map((e) => e.name).toList();
      matches.add(RecipeMatchItem(
        dishId: 'd1',
        dishName: _activePrompt.isNotEmpty
            ? 'Món nấu theo yêu cầu: $_activePrompt'
            : 'Món xào/nấu tổng hợp',
        meta: '15 phút · Dễ · 2 khẩu phần',
        matchedIngredients: selectedLabels,
        missingIngredients: const [
          MissingIngredientItem(
            name: 'Gia vị tổng hợp (Muối, Tiêu, Nước mắm)',
            quantity: 1,
            unit: MeasurementUnit.pack,
            displayQty: '1 bộ',
          ),
          MissingIngredientItem(
            name: 'Dầu ăn thực vật',
            quantity: 1,
            unit: MeasurementUnit.bottle,
            displayQty: '1 chai',
          ),
          MissingIngredientItem(
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

  Future<void> _addMissingToShopping(
    List<MissingIngredientItem> missingList, {
    String? successMsg,
  }) async {
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
        AppSnack.show(
          context,
          successMsg ??
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
    final allMissing = <String, MissingIngredientItem>{};
    for (final m in matches) {
      for (final item in m.missingIngredients) {
        allMissing.putIfAbsent(item.name, () => item);
      }
    }
    final missingItemsList = allMissing.values.toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Công thức có thể nấu'),
      ),
      bottomNavigationBar: SafeArea(
        child: Container(
          padding: const EdgeInsets.symmetric(
            horizontal: Gap.lg,
            vertical: Gap.sm,
          ),
          decoration: BoxDecoration(
            color: context.colors.surfaceContainerLowest,
            border: Border(top: BorderSide(color: context.sweep.hairline)),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.06),
                blurRadius: 10,
                offset: const Offset(0, -4),
              ),
            ],
          ),
          child: SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              style: FilledButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: Gap.sm),
              ),
              onPressed: _adding || missingItemsList.isEmpty
                  ? null
                  : () => _addMissingToShopping(
                        missingItemsList,
                        successMsg:
                            'Đã thêm tất cả ${missingItemsList.length} nguyên liệu thiếu vào danh sách mua!',
                      ),
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
                        : 'Thêm tất cả nguyên liệu thiếu vào giỏ mua',
              ),
            ),
          ),
        ),
      ),
      body: matches.isEmpty
          ? ListView(
              children: [
                const SizedBox(height: 80),
                EmptyState(
                  title: 'Chưa có công thức phù hợp',
                  message:
                      'Hãy chọn thêm nguyên liệu trong kho để tìm công thức nấu ăn.',
                  icon: Icons.restaurant_menu_rounded,
                  actionLabel: 'Thêm nguyên liệu',
                  onAction: () => showAddEntryChooser(context),
                ),
              ],
            )
          : ListView(
              padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, 24),
              children: [
                Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Text(
                    'Đang chọn ${widget.selectedItems.length} nguyên liệu từ kho:',
                    style: context.text.labelMedium?.copyWith(
                      color: context.sweep.textSecondary,
                    ),
                  ),
                ),
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
                if (_activePrompt.isNotEmpty) ...[
                  Gap.gapXs,
                  Align(
                    alignment: Alignment.centerLeft,
                    child: Chip(
                      avatar: Icon(
                        Icons.auto_awesome,
                        size: 16,
                        color: context.colors.primary,
                      ),
                      label: Text(
                        'Yêu cầu: $_activePrompt',
                        style: context.text.bodySmall?.copyWith(
                          color: context.colors.primary,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      deleteIcon: const Icon(Icons.close_rounded, size: 16),
                      onDeleted: () {
                        setState(() {
                          _activePrompt = '';
                        });
                      },
                      backgroundColor: context.colors.primaryContainer.withValues(alpha: 0.3),
                      side: BorderSide(color: context.colors.primary),
                      visualDensity: VisualDensity.compact,
                      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      padding: EdgeInsets.zero,
                    ),
                  ),
                ],
                Gap.gapSm,
                Text(
                  'Tìm thấy ${matches.length} công thức phù hợp',
                  style: context.text.labelSmall?.copyWith(
                    color: context.sweep.textTertiary,
                  ),
                ),
                Gap.gapSm,
                for (final match in matches) ...[
                  _RecipeMatchCard(
                    match: match,
                    onAddMissing: match.missingIngredients.isEmpty
                        ? null
                        : () => _addMissingToShopping(
                              match.missingIngredients,
                              successMsg:
                                  'Đã thêm ${match.missingIngredients.length} nguyên liệu thiếu của món ${match.dishName} vào danh sách mua!',
                            ),
                    onTapDish: () {
                      context.push(
                        '${Routes.suggestions}/dish/${match.dishId}',
                      );
                    },
                  ),
                  Gap.gapMd,
                ],
              ],
            ),
    );
  }
}

class _RecipeMatchCard extends StatelessWidget {
  const _RecipeMatchCard({
    required this.match,
    required this.onAddMissing,
    required this.onTapDish,
  });

  final RecipeMatchItem match;
  final VoidCallback? onAddMissing;
  final VoidCallback onTapDish;

  @override
  Widget build(BuildContext context) {
    final isFull = match.missingIngredients.isEmpty;

    return Container(
      padding: const EdgeInsets.all(Gap.md),
      decoration: BoxDecoration(
        color: context.colors.surfaceContainerLowest,
        borderRadius: Radii.brLg,
        border: Border.all(color: context.sweep.hairline),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: context.sweep.subtleFill,
                  borderRadius: Radii.brMd,
                ),
                child: const Icon(
                  Icons.restaurant_menu_rounded,
                  color: Colors.teal,
                  size: 22,
                ),
              ),
              const SizedBox(width: Gap.sm),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      match.dishName,
                      style: context.text.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      match.meta,
                      style: context.text.bodySmall?.copyWith(
                        color: context.sweep.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: Gap.xs + 2,
                  vertical: 3,
                ),
                decoration: BoxDecoration(
                  color: isFull
                      ? Colors.green.withValues(alpha: 0.15)
                      : Colors.orange.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(Radii.pill),
                ),
                child: Text(
                  isFull
                      ? 'Đủ nguyên liệu'
                      : 'Thiếu ${match.missingIngredients.length} món',
                  style: context.text.labelSmall?.copyWith(
                    color: isFull ? Colors.green.shade800 : Colors.orange.shade800,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ],
          ),
          Gap.gapSm,
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.teal.withValues(alpha: 0.07),
              borderRadius: Radii.brSm,
            ),
            child: Row(
              children: [
                const Icon(Icons.inventory_2_outlined, size: 15, color: Colors.teal),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    'Đã có: ${match.matchedIngredients.join(", ")}',
                    style: context.text.bodySmall?.copyWith(
                      color: Colors.teal.shade900,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
          if (match.missingIngredients.isNotEmpty) ...[
            Gap.gapSm,
            Container(
              padding: const EdgeInsets.all(Gap.sm),
              decoration: BoxDecoration(
                color: context.sweep.subtleFill,
                borderRadius: Radii.brSm,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Nguyên liệu còn thiếu:',
                    style: context.text.labelSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: context.sweep.textSecondary,
                    ),
                  ),
                  const SizedBox(height: 4),
                  for (final missing in match.missingIngredients)
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 2),
                      child: Row(
                        children: [
                          Container(
                            width: 6,
                            height: 6,
                            decoration: const BoxDecoration(
                              color: Colors.deepOrange,
                              shape: BoxShape.circle,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              missing.name,
                              style: context.text.bodySmall?.copyWith(
                                color: context.colors.onSurface,
                              ),
                            ),
                          ),
                          Text(
                            missing.displayQty,
                            style: context.text.bodySmall?.copyWith(
                              color: context.sweep.textTertiary,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ),
          ],
          Gap.gapSm,
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              TextButton.icon(
                style: TextButton.styleFrom(
                  padding: EdgeInsets.zero,
                  visualDensity: VisualDensity.compact,
                ),
                onPressed: onTapDish,
                icon: const Icon(Icons.arrow_forward_rounded, size: 16),
                label: const Text('Xem chi tiết món'),
              ),
              if (!isFull)
                OutlinedButton.icon(
                  style: OutlinedButton.styleFrom(
                    minimumSize: Size.zero,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 6,
                    ),
                    visualDensity: VisualDensity.compact,
                  ),
                  onPressed: onAddMissing,
                  icon: const Icon(Icons.add_shopping_cart_rounded, size: 14),
                  label: const Text(
                    'Thêm thiếu vào mua',
                    style: TextStyle(fontSize: 12),
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}
