import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/recipe_image.dart';
import 'package:sweepfood/features/dishes/data/repositories/dish_repository_impl.dart';
import 'package:sweepfood/features/dishes/domain/entities/dish.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/features/suggestions/presentation/controllers/suggestion_list_controller.dart';

class DishPickResult {
  const DishPickResult({
    required this.dishId,
    required this.name,
    required this.servings,
    this.imageUrl,
  });

  final String dishId;
  final String name;
  final double servings;
  final String? imageUrl;
}

enum _PickerTab { suggestions, catalog }

/// M-02 Gán món vào ô (Concept B · Format 1 Crisp Sheet).
class DishPickerSheet extends ConsumerStatefulWidget {
  const DishPickerSheet({super.key});

  static Future<DishPickResult?> show(BuildContext context) {
    return showAppBottomSheet<DishPickResult>(
      context,
      builder: (_) => const DishPickerSheet(),
    );
  }

  @override
  ConsumerState<DishPickerSheet> createState() => _DishPickerSheetState();
}

class _DishPickerSheetState extends ConsumerState<DishPickerSheet> {
  _PickerTab _tab = _PickerTab.suggestions;
  final TextEditingController _searchController = TextEditingController();

  List<Dish> _searchResults = [];
  bool _searching = false;
  String? _searchError;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _doSearch(String query) async {
    setState(() {
      _searching = true;
      _searchError = null;
    });

    final repo = ref.read(dishRepositoryProvider);
    final res = await repo.searchRecipes(query: query.trim());

    if (!mounted) return;
    setState(() {
      _searching = false;
      res.fold(
        (err) => _searchError = 'Không thể tải danh sách món lúc này.',
        (dishes) => _searchResults = dishes,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final asyncSuggestions = ref.watch(suggestionListControllerProvider);

    return SheetBody(
      icon: AppIcons.chefHat,
      title: l10n.mealPlanPickDish,
      subtitle: l10n.mealPlanPickDishSub,
      child: SizedBox(
        height: 460,
        child: Column(
          children: [
            SheetSegmentedControl<_PickerTab>(
              selected: _tab,
              options: const [
                (
                  value: _PickerTab.suggestions,
                  label: 'Gợi ý AI',
                  icon: AppIcons.chefHat,
                ),
                (
                  value: _PickerTab.catalog,
                  label: 'Thư viện món',
                  icon: AppIcons.search,
                ),
              ],
              onChanged: (next) => setState(() => _tab = next),
            ),
            Gap.gapSm,
            Expanded(
              child: _tab == _PickerTab.suggestions
                  ? AsyncValueWidget<List<DishSuggestion>>(
                      value: asyncSuggestions,
                      data: (list) {
                        if (list.isEmpty) {
                          return Center(
                            child: Text(
                              'Chưa có gợi ý món nào từ tủ lạnh hiện tại.',
                              textAlign: TextAlign.center,
                              style: context.text.bodyMedium?.copyWith(
                                color: sweep.textSecondary,
                              ),
                            ),
                          );
                        }
                        return SheetGroupCard(
                          child: ListView.separated(
                            itemCount: list.length,
                            separatorBuilder: (_, __) =>
                                Divider(height: 1, color: sweep.hairline),
                            itemBuilder: (context, i) {
                              final s = list[i];
                              return _DishPickRow(
                                name: s.dish.name,
                                subtitle: s.dish.shortMeta(l10n),
                                imageUrl: s.dish.imageUrl,
                                scoreBadge: '${s.score}đ',
                                onTap: () => Navigator.of(context).pop(
                                  DishPickResult(
                                    dishId: s.id,
                                    name: s.dish.name,
                                    servings: s.dish.servings.toDouble(),
                                    imageUrl: s.dish.imageUrl,
                                  ),
                                ),
                              );
                            },
                          ),
                        );
                      },
                    )
                  : Column(
                      children: [
                        TextField(
                          controller: _searchController,
                          decoration: InputDecoration(
                            hintText: 'Tìm kiếm công thức món ăn...',
                            prefixIcon: const Icon(AppIcons.search, size: 18),
                            suffixIcon: IconButton(
                              icon: const Icon(AppIcons.arrowRight, size: 18),
                              onPressed: () =>
                                  _doSearch(_searchController.text),
                            ),
                            isDense: true,
                          ),
                          onSubmitted: _doSearch,
                        ),
                        Gap.gapSm,
                        Expanded(
                          child: _searching
                              ? const Center(
                                  child: CircularProgressIndicator.adaptive(),
                                )
                              : _searchError != null
                              ? Center(child: Text(_searchError!))
                              : _searchResults.isEmpty
                              ? Center(
                                  child: Text(
                                    _searchController.text.isEmpty
                                        ? 'Nhập từ khóa và bấm tìm kiếm để duyệt công thức.'
                                        : 'Không tìm thấy công thức nào phù hợp.',
                                    textAlign: TextAlign.center,
                                    style: context.text.bodyMedium?.copyWith(
                                      color: sweep.textSecondary,
                                    ),
                                  ),
                                )
                              : SheetGroupCard(
                                  child: ListView.separated(
                                    itemCount: _searchResults.length,
                                    separatorBuilder: (_, __) => Divider(
                                      height: 1,
                                      color: sweep.hairline,
                                    ),
                                    itemBuilder: (context, i) {
                                      final dish = _searchResults[i];
                                      return _DishPickRow(
                                        name: dish.name,
                                        subtitle:
                                            '${dish.cookTimeMin} phút · ${dish.servings} phần ăn',
                                        imageUrl: dish.imageUrl,
                                        onTap: () => Navigator.of(context).pop(
                                          DishPickResult(
                                            dishId: dish.id,
                                            name: dish.name,
                                            servings: dish.servings.toDouble(),
                                            imageUrl: dish.imageUrl,
                                          ),
                                        ),
                                      );
                                    },
                                  ),
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

class _DishPickRow extends StatelessWidget {
  const _DishPickRow({
    required this.name,
    required this.subtitle,
    required this.onTap,
    this.imageUrl,
    this.scoreBadge,
  });

  final String name;
  final String subtitle;
  final VoidCallback onTap;
  final String? imageUrl;
  final String? scoreBadge;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    return InkWell(
      onTap: () {
        AppHaptics.selection();
        onTap();
      },
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: Gap.md,
          vertical: Gap.sm + 3,
        ),
        child: Row(
          children: [
            ClipRRect(
              borderRadius: Radii.brMd,
              child: RecipeImage(
                imageUrl: imageUrl,
                width: 46,
                height: 46,
                iconSize: 20,
              ),
            ),
            const SizedBox(width: Gap.sm + 2),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    name,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: context.text.titleSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: context.text.bodySmall?.copyWith(
                      color: sweep.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: Gap.xs),
            if (scoreBadge != null)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: sweep.heroSurface,
                  borderRadius: BorderRadius.circular(Radii.pill),
                ),
                child: Text(
                  scoreBadge!,
                  style: AppTypography.tabular(
                    context.text.labelSmall?.copyWith(
                      letterSpacing: 0,
                      color: sweep.onHeroSurface,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              )
            else
              Icon(AppIcons.chevronRight, size: 17, color: sweep.textTertiary),
          ],
        ),
      ),
    );
  }
}
