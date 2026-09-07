import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/features/favorites/domain/entities/favorite_menu.dart';
import 'package:sweepfood/features/favorites/domain/entities/favorite_recipe.dart';
import 'package:sweepfood/features/favorites/presentation/controllers/favorite_menus_controller.dart';
import 'package:sweepfood/features/favorites/presentation/controllers/favorite_recipes_controller.dart';
import 'package:sweepfood/features/favorites/presentation/widgets/create_edit_menu_dialog.dart';

class FavoritesScreen extends ConsumerStatefulWidget {
  const FavoritesScreen({super.key});

  @override
  ConsumerState<FavoritesScreen> createState() => _FavoritesScreenState();
}

class _FavoritesScreenState extends ConsumerState<FavoritesScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabCtrl;

  @override
  void initState() {
    super.initState();
    _tabCtrl = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Món & Thực đơn yêu thích'),
        bottom: TabBar(
          controller: _tabCtrl,
          tabs: const [
            Tab(text: 'Món yêu thích'),
            Tab(text: 'Thực đơn mẫu'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabCtrl,
        children: const [
          _FavoriteRecipesTab(),
          _FavoriteMenusTab(),
        ],
      ),
    );
  }
}

class _FavoriteRecipesTab extends ConsumerWidget {
  const _FavoriteRecipesTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(favoriteRecipesControllerProvider);

    return RefreshIndicator(
      onRefresh: () => ref.read(favoriteRecipesControllerProvider.notifier).refresh(),
      child: AsyncValueWidget<List<FavoriteRecipe>>(
        value: async,
        onRetry: () => ref.invalidate(favoriteRecipesControllerProvider),
        data: (recipes) {
          if (recipes.isEmpty) {
            return ListView(
              children: [
                const SizedBox(height: 100),
                EmptyState(
                  title: 'Chưa có món yêu thích',
                  message: 'Khi xem chi tiết món ăn, bấm biểu tượng trái tim để lưu lại vào đây.',
                  icon: Icons.favorite_border_rounded,
                  actionLabel: 'Khám phá món gợi ý',
                  onAction: () => context.go(Routes.suggestions),
                ),
              ],
            );
          }

          return ListView.separated(
            padding: const EdgeInsets.all(Gap.md),
            itemCount: recipes.length,
            separatorBuilder: (_, __) => const SizedBox(height: Gap.sm),
            itemBuilder: (context, idx) {
              final item = recipes[idx];
              return Card(
                elevation: 0,
                shape: RoundedRectangleBorder(
                  borderRadius: Radii.brMd,
                  side: BorderSide(color: context.sweep.hairline),
                ),
                child: ListTile(
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: Gap.md,
                    vertical: Gap.xs,
                  ),
                  leading: ClipRRect(
                    borderRadius: Radii.brSm,
                    child: Container(
                      width: 52,
                      height: 52,
                      color: context.sweep.subtleFill,
                      child: item.mediaUrl != null && item.mediaUrl!.isNotEmpty
                          ? Image.network(
                              item.mediaUrl!,
                              fit: BoxFit.cover,
                              errorBuilder: (_, __, ___) => const Icon(
                                Icons.restaurant_rounded,
                                color: Colors.grey,
                              ),
                            )
                          : const Icon(Icons.restaurant_rounded, color: Colors.grey),
                    ),
                  ),
                  title: Text(item.recipeName, style: context.text.titleSmall),
                  subtitle: item.recipeDescription.isNotEmpty
                      ? Text(
                          item.recipeDescription,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: context.text.bodySmall?.copyWith(
                            color: context.sweep.textSecondary,
                          ),
                        )
                      : null,
                  trailing: IconButton(
                    icon: const Icon(Icons.favorite_rounded, color: Colors.red),
                    tooltip: 'Bỏ lưu',
                    onPressed: () async {
                      await ref
                          .read(favoriteRecipesControllerProvider.notifier)
                          .removeFavorite(item.recipeId);
                      if (context.mounted) {
                        AppSnack.show(
                          context,
                          'Đã gỡ "${item.recipeName}" khỏi yêu thích',
                        );
                      }
                    },
                  ),
                  onTap: () => context.push(
                    '${Routes.suggestions}/dish/${item.recipeId}',
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}

class _FavoriteMenusTab extends ConsumerWidget {
  const _FavoriteMenusTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(favoriteMenusControllerProvider);

    return Scaffold(
      body: RefreshIndicator(
        onRefresh: () => ref.read(favoriteMenusControllerProvider.notifier).refresh(),
        child: AsyncValueWidget<List<FavoriteMenu>>(
          value: async,
          onRetry: () => ref.invalidate(favoriteMenusControllerProvider),
          data: (menus) {
            if (menus.isEmpty) {
              return ListView(
                children: [
                  const SizedBox(height: 100),
                  EmptyState(
                    title: 'Chưa có thực đơn mẫu nào',
                    message: 'Tạo thực đơn mẫu để nhóm các món ăn yêu thích cho các dịp khác nhau.',
                    icon: Icons.menu_book_rounded,
                    actionLabel: 'Tạo thực đơn mới',
                    onAction: () async {
                      final res = await CreateEditMenuDialog.show(context);
                      if (res != null) {
                        await ref
                            .read(favoriteMenusControllerProvider.notifier)
                            .createMenu(name: res.name, description: res.description);
                      }
                    },
                  ),
                ],
              );
            }

            return ListView.separated(
              padding: const EdgeInsets.fromLTRB(Gap.md, Gap.md, Gap.md, 96),
              itemCount: menus.length,
              separatorBuilder: (_, __) => const SizedBox(height: Gap.sm),
              itemBuilder: (context, idx) {
                final menu = menus[idx];
                return Card(
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    borderRadius: Radii.brMd,
                    side: BorderSide(color: context.sweep.hairline),
                  ),
                  child: ListTile(
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: Gap.md,
                      vertical: Gap.sm,
                    ),
                    leading: Container(
                      width: 44,
                      height: 44,
                      decoration: BoxDecoration(
                        color: context.colors.primaryContainer,
                        borderRadius: Radii.brMd,
                      ),
                      child: Icon(
                        Icons.menu_book_rounded,
                        color: context.colors.onPrimaryContainer,
                      ),
                    ),
                    title: Text(menu.name, style: context.text.titleSmall),
                    subtitle: menu.description != null && menu.description!.isNotEmpty
                        ? Text(
                            menu.description!,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: context.text.bodySmall?.copyWith(
                              color: context.sweep.textSecondary,
                            ),
                          )
                        : null,
                    trailing: const Icon(Icons.chevron_right_rounded),
                    onTap: () => context.push('/favorites/menu/${menu.id}'),
                  ),
                );
              },
            );
          },
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          final res = await CreateEditMenuDialog.show(context);
          if (res != null) {
            await ref
                .read(favoriteMenusControllerProvider.notifier)
                .createMenu(name: res.name, description: res.description);
          }
        },
        icon: const Icon(Icons.add_rounded),
        label: const Text('Tạo thực đơn'),
      ),
    );
  }
}
