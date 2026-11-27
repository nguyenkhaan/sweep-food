import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/formatters/quantity_format.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooking_preview.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list_item.dart';
import 'package:sweepfood/features/shopping_list/presentation/controllers/shopping_list_controller.dart';

/// Bottom sheet displayed when cooking cannot proceed via standard automated FEFO
/// because some ingredients are reported missing.
/// Provides a clear breakdown, allows direct pantry deduction if ingredients exist
/// in the user's pantry under custom names or different units, or quick actions to add to shopping list.
class PostCookMissingSheet extends ConsumerStatefulWidget {
  const PostCookMissingSheet({
    required this.dishName,
    required this.servings,
    required this.missingIngredients,
    this.onCookSuccess,
    this.onReduceServings,
    super.key,
  });

  final String dishName;
  final double servings;
  final List<MissingIngredientPreview> missingIngredients;
  final VoidCallback? onCookSuccess;
  final VoidCallback? onReduceServings;

  static Future<void> show(
    BuildContext context, {
    required String dishName,
    required double servings,
    required List<MissingIngredientPreview> missingIngredients,
    VoidCallback? onCookSuccess,
    VoidCallback? onReduceServings,
  }) {
    return showAppBottomSheet<void>(
      context,
      builder: (_) => PostCookMissingSheet(
        dishName: dishName,
        servings: servings,
        missingIngredients: missingIngredients,
        onCookSuccess: onCookSuccess,
        onReduceServings: onReduceServings,
      ),
    );
  }

  @override
  ConsumerState<PostCookMissingSheet> createState() =>
      _PostCookMissingSheetState();
}

class _PostCookMissingSheetState extends ConsumerState<PostCookMissingSheet> {
  bool _adding = false;
  bool _consuming = false;

  String _normalize(String value) => value
      .toLowerCase()
      .replaceAll(RegExp(r'[^a-z0-9\u00c0-\u024f\u1e00-\u1eff ]'), '')
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim();

  PantryItem? _findPantryMatch(String name, List<PantryItem> activePantry) {
    final norm = _normalize(name);
    for (final p in activePantry) {
      final pNorm = _normalize(p.name);
      if (pNorm == norm || pNorm.contains(norm) || norm.contains(pNorm)) {
        return p;
      }
    }
    return null;
  }

  Future<void> _cookAndDeductFromPantry(List<PantryItem> activePantry) async {
    if (_consuming) return;
    setState(() => _consuming = true);

    try {
      final controller = ref.read(pantryListControllerProvider.notifier);
      int deductedCount = 0;

      for (final item in widget.missingIngredients) {
        final match = _findPantryMatch(item.ingredientName, activePantry);
        if (match != null && match.quantity > 0) {
          final toConsume =
              match.quantity >= item.missingQuantity && item.missingQuantity > 0
              ? item.missingQuantity
              : match.quantity;
          if (toConsume > 0) {
            await controller.consume(match.id, quantityUsed: toConsume);
            deductedCount++;
          }
        }
      }

      if (mounted) {
        Navigator.of(context).pop();
        widget.onCookSuccess?.call();
        AppSnack.show(
          context,
          'Đã ghi nhận nấu món "${widget.dishName}" và cập nhật trừ kho $deductedCount nguyên liệu!',
        );
      }
    } catch (e) {
      if (mounted) {
        AppSnack.show(context, 'Có lỗi khi trừ kho: $e');
      }
    } finally {
      if (mounted) setState(() => _consuming = false);
    }
  }

  Future<void> _addAllToShopping() async {
    if (_adding || widget.missingIngredients.isEmpty) return;
    setState(() => _adding = true);

    try {
      final controller = ref.read(shoppingListControllerProvider.notifier);
      for (final item in widget.missingIngredients) {
        await controller.addManualItem(
          ShoppingListItemDraft(
            name: item.ingredientName,
            quantity: item.missingQuantity,
            unit: item.unit,
          ),
        );
      }
      if (mounted) {
        Navigator.of(context).pop();
        AppSnack.show(
          context,
          'Đã thêm ${widget.missingIngredients.length} nguyên liệu thiếu vào danh sách mua sắm!',
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
    final count = widget.missingIngredients.length;
    final servingsInt = widget.servings.toInt();

    final pantryItems =
        ref.watch(pantryListControllerProvider).asData?.value ??
        const <PantryItem>[];
    final activePantry = pantryItems
        .where((p) => p.status == PantryItemStatus.active && p.quantity > 0)
        .toList();

    final matchedInPantry = <MissingIngredientPreview, PantryItem>{};
    for (final item in widget.missingIngredients) {
      final match = _findPantryMatch(item.ingredientName, activePantry);
      if (match != null) {
        matchedInPantry[item] = match;
      }
    }

    final sweep = context.sweep;
    final hasAnyPantryMatch = matchedInPantry.isNotEmpty;

    return SheetBody(
      icon: hasAnyPantryMatch ? AppIcons.pantry : AppIcons.archive,
      iconBg: hasAnyPantryMatch ? sweep.successBg : sweep.soon.bg,
      iconFg: hasAnyPantryMatch ? sweep.successFg : sweep.soon.fg,
      title: hasAnyPantryMatch
          ? 'Kiểm tra nguyên liệu trong kho'
          : 'Chưa đủ nguyên liệu ($servingsInt phần)',
      subtitle: hasAnyPantryMatch
          ? 'Tìm thấy ${matchedInPantry.length}/$count nguyên liệu có sẵn trong kho của bạn'
          : 'Cần bổ sung $count nguyên liệu để nấu món này',
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            hasAnyPantryMatch
                ? 'Một số nguyên liệu có trong kho nhưng khác đơn vị hoặc tên tùy chỉnh:'
                : 'Kho hiện tại không có đủ số lượng nguyên liệu sau để nấu:',
            style: context.text.bodySmall?.copyWith(
              color: sweep.textSecondary,
            ),
          ),
          const SizedBox(height: Gap.sm),
          SheetGroupCard(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxHeight: 220),
              child: ListView.separated(
                shrinkWrap: true,
                itemCount: widget.missingIngredients.length,
                separatorBuilder: (_, __) =>
                    Divider(height: 1, color: sweep.hairline),
                itemBuilder: (context, index) {
                  final item = widget.missingIngredients[index];
                  final match = matchedInPantry[item];
                  final isAvailable = match != null;

                  return Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: Gap.md,
                      vertical: 11,
                    ),
                    child: Row(
                      children: [
                        Icon(
                          isAvailable
                              ? AppIcons.checkCircle
                              : AppIcons.minus,
                          color: isAvailable
                              ? sweep.successFg
                              : sweep.expired.fg,
                          size: 16,
                        ),
                        const SizedBox(width: Gap.xs + 2),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                item.ingredientName,
                                style: context.text.bodyMedium?.copyWith(
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              if (isAvailable)
                                Text(
                                  'Có sẵn: ${formatQuantity(match.quantity, match.unit)}',
                                  style: context.text.bodySmall?.copyWith(
                                    color: sweep.successFg,
                                    fontSize: 11,
                                  ),
                                ),
                            ],
                          ),
                        ),
                        const SizedBox(width: Gap.xs),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 9,
                            vertical: 3,
                          ),
                          decoration: BoxDecoration(
                            color: isAvailable
                                ? sweep.successBg
                                : sweep.expired.bg,
                            borderRadius: BorderRadius.circular(Radii.pill),
                          ),
                          child: Text(
                            isAvailable
                                ? 'Có trong kho'
                                : 'Thiếu ${formatQuantity(item.missingQuantity, item.unit)}',
                            style: context.text.labelSmall?.copyWith(
                              letterSpacing: 0,
                              color: isAvailable
                                  ? sweep.successFg
                                  : sweep.expired.fg,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
          ),
          const SizedBox(height: Gap.md),
          if (hasAnyPantryMatch) ...[
            SheetWarmButton(
              loading: _consuming,
              icon: AppIcons.utensils,
              label: _consuming
                  ? 'Đang trừ kho...'
                  : 'Xác nhận đã nấu và Trừ kho (${matchedInPantry.length} có sẵn)',
              onPressed: _consuming
                  ? null
                  : () => _cookAndDeductFromPantry(activePantry),
            ),
            const SizedBox(height: Gap.xs + 2),
            SheetCancelButton(
              icon: AppIcons.shopping,
              label: _adding ? 'Đang thêm...' : 'Thêm vào danh sách mua',
              onPressed: _adding ? null : _addAllToShopping,
            ),
          ] else ...[
            SheetWarmButton(
              loading: _adding,
              icon: AppIcons.shopping,
              label: _adding
                  ? 'Đang thêm...'
                  : 'Thêm $count nguyên liệu vào danh sách mua',
              onPressed: _adding ? null : _addAllToShopping,
            ),
          ],
          if (widget.servings > 1 && widget.onReduceServings != null) ...[
            const SizedBox(height: Gap.xs),
            TextButton.icon(
              onPressed: () {
                Navigator.of(context).pop();
                widget.onReduceServings!();
              },
              icon: const Icon(AppIcons.filter, size: 17),
              label: Text(
                'Thử giảm khẩu phần (${widget.servings == 4 ? "2" : "1"} phần)',
              ),
            ),
          ],
        ],
      ),
    );
  }
}
