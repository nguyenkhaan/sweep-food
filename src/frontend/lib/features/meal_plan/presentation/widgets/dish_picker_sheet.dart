import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
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

/// M-02 Gán món vào ô — chọn từ gợi ý thông minh hoặc tìm kiếm trong thư viện công thức.
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

class _DishPickerSheetState extends ConsumerState<DishPickerSheet>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController;
  final TextEditingController _searchController = TextEditingController();

  List<Dish> _searchResults = [];
  bool _searching = false;
  String? _searchError;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
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
    final asyncSuggestions = ref.watch(suggestionListControllerProvider);

    return SheetBody(
      title: l10n.mealPlanPickDish,
      subtitle: l10n.mealPlanPickDishSub,
      child: SizedBox(
        height: 480,
        child: Column(
          children: [
            TabBar(
              controller: _tabController,
              tabs: const [
                Tab(icon: Icon(Icons.auto_awesome_rounded, size: 18), text: 'Gợi ý AI'),
                Tab(icon: Icon(Icons.search_rounded, size: 18), text: 'Thư viện món'),
              ],
            ),
            Gap.gapSm,
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  // Tab 1: AI Suggestions
                  AsyncValueWidget<List<DishSuggestion>>(
                    value: asyncSuggestions,
                    data: (list) {
                      if (list.isEmpty) {
                        return const Center(
                          child: Text('Chưa có gợi ý món nào từ tủ lạnh hiện tại.'),
                        );
                      }
                      return ListView.separated(
                        itemCount: list.length,
                        separatorBuilder: (_, __) => const Divider(height: 1),
                        itemBuilder: (context, i) {
                          final s = list[i];
                          return ListTile(
                            contentPadding: EdgeInsets.zero,
                            leading: const Icon(Icons.restaurant_rounded),
                            title: Text(s.dish.name),
                            subtitle: Text(s.dish.shortMeta(l10n)),
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
                      );
                    },
                  ),

                  // Tab 2: Catalog Search
                  Column(
                    children: [
                      TextField(
                        controller: _searchController,
                        decoration: InputDecoration(
                          hintText: 'Tìm kiếm công thức món ăn...',
                          prefixIcon: const Icon(Icons.search_rounded),
                          suffixIcon: IconButton(
                            icon: const Icon(Icons.arrow_forward_rounded),
                            onPressed: () => _doSearch(_searchController.text),
                          ),
                          isDense: true,
                          border: const OutlineInputBorder(),
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
                                        ),
                                      )
                                    : ListView.separated(
                                        itemCount: _searchResults.length,
                                        separatorBuilder: (_, __) =>
                                            const Divider(height: 1),
                                        itemBuilder: (context, i) {
                                          final dish = _searchResults[i];
                                          return ListTile(
                                            contentPadding: EdgeInsets.zero,
                                            leading: const Icon(
                                                Icons.menu_book_rounded),
                                            title: Text(dish.name),
                                            subtitle: Text(
                                              '${dish.cookTimeMin} phút · ${dish.servings} phần ăn',
                                            ),
                                            onTap: () =>
                                                Navigator.of(context).pop(
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
                    ],
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
