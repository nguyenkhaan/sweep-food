import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/core/widgets/recipe_image.dart';
import 'package:sweepfood/features/favorites/domain/entities/favorite_menu.dart';
import 'package:sweepfood/features/favorites/domain/entities/favorite_recipe.dart';
import 'package:sweepfood/features/favorites/presentation/controllers/favorite_menus_controller.dart';
import 'package:sweepfood/features/favorites/presentation/controllers/favorite_recipes_controller.dart';
import 'package:sweepfood/features/favorites/presentation/widgets/create_edit_menu_dialog.dart';

/// Món & Thực đơn yêu thích (Concept B · Format 1: Emerald Split Hero +
/// Integrated Segmented Pill Tabs + Grouped Hairline Cards).
class FavoritesScreen extends ConsumerStatefulWidget {
  const FavoritesScreen({super.key});

  @override
  ConsumerState<FavoritesScreen> createState() => _FavoritesScreenState();
}

class _FavoritesScreenState extends ConsumerState<FavoritesScreen> {
  int _tabIndex = 0;

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    final sweep = context.sweep;
    final menusAsync = ref.watch(favoriteMenusControllerProvider);
    final showCreateFab =
        _tabIndex == 1 && (menusAsync.asData?.value.isNotEmpty ?? false);

    return EmeraldSystemOverlay(
      child: Scaffold(
        backgroundColor: cs.surface,
        body: Column(
          children: [
            EmeraldSplitHeader(
              title: 'Yêu thích',
              bottom: Container(
                padding: const EdgeInsets.all(4),
                decoration: BoxDecoration(
                  color: sweep.heroSurfaceElevated,
                  borderRadius: Radii.brMd,
                  border: Border.all(
                    color: sweep.onHeroSurface.withValues(alpha: 0.14),
                  ),
                ),
                child: Row(
                  children: [
                    _HeroSegTab(
                      label: 'Món yêu thích',
                      selected: _tabIndex == 0,
                      onTap: () => setState(() => _tabIndex = 0),
                    ),
                    const SizedBox(width: 4),
                    _HeroSegTab(
                      label: 'Thực đơn mẫu',
                      selected: _tabIndex == 1,
                      onTap: () => setState(() => _tabIndex = 1),
                    ),
                  ],
                ),
              ),
            ),
            Expanded(
              child: IndexedStack(
                index: _tabIndex,
                children: const [_FavoriteRecipesTab(), _FavoriteMenusTab()],
              ),
            ),
          ],
        ),
        floatingActionButton: showCreateFab
            ? FloatingActionButton.extended(
                heroTag: 'favorite_menu_fab',
                elevation: 2,
                highlightElevation: 3,
                backgroundColor: sweep.ctaWarm,
                foregroundColor: sweep.onCtaWarm,
                onPressed: () => _createMenu(context, ref),
                icon: const Icon(AppIcons.add, size: 18),
                label: const Text('Tạo thực đơn'),
              )
            : null,
      ),
    );
  }

  static Future<void> _createMenu(BuildContext context, WidgetRef ref) async {
    final res = await CreateEditMenuDialog.show(context);
    if (res != null) {
      await ref
          .read(favoriteMenusControllerProvider.notifier)
          .createMenu(name: res.name, description: res.description);
    }
  }
}

class _HeroSegTab extends StatelessWidget {
  const _HeroSegTab({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    return Expanded(
      child: Material(
        color: selected ? sweep.onHeroSurface : Colors.transparent,
        borderRadius: BorderRadius.circular(10),
        child: InkWell(
          borderRadius: BorderRadius.circular(10),
          onTap: () {
            AppHaptics.selection();
            onTap();
          },
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 9, horizontal: 8),
            child: Text(
              label,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              textAlign: TextAlign.center,
              style: context.text.labelLarge?.copyWith(
                fontWeight: FontWeight.w700,
                color: selected ? sweep.heroSurface : sweep.onHeroMuted,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _FavoriteRecipesTab extends ConsumerWidget {
  const _FavoriteRecipesTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(favoriteRecipesControllerProvider);
    final cs = context.colors;

    return RefreshIndicator(
      onRefresh: () =>
          ref.read(favoriteRecipesControllerProvider.notifier).refresh(),
      child: AsyncValueWidget<List<FavoriteRecipe>>(
        value: async,
        onRetry: () => ref.invalidate(favoriteRecipesControllerProvider),
        data: (recipes) {
          if (recipes.isEmpty) {
            return ListView(
              padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xl, Gap.lg, Gap.xxl),
              children: [
                EmptyState(
                  illustrationAsset:
                      'assets/illustrations/empty_favorites.svg',
                  title: 'Chưa có món yêu thích',
                  message:
                      'Khi xem chi tiết món ăn, bấm biểu tượng trái tim để lưu lại vào đây.',
                  icon: AppIcons.heart,
                  actionLabel: 'Khám phá món gợi ý',
                  onAction: () => context.go(Routes.suggestions),
                ),
              ],
            );
          }

          return ListView(
            padding: EdgeInsets.fromLTRB(
              Gap.lg,
              Gap.xs,
              Gap.lg,
              MediaQuery.paddingOf(context).bottom + Gap.xxl,
            ),
            children: [
              Container(
                decoration: BoxDecoration(
                  color: cs.surfaceContainerLowest,
                  borderRadius: Radii.brXl,
                  border: Border.all(color: context.sweep.hairline),
                  boxShadow: Shadows.e1,
                ),
                clipBehavior: Clip.antiAlias,
                child: Column(
                  children: [
                    for (var i = 0; i < recipes.length; i++) ...[
                      _FavoriteRecipeRow(item: recipes[i]),
                      if (i < recipes.length - 1)
                        Divider(
                          height: 1,
                          indent: 78,
                          color: context.sweep.hairline,
                        ),
                    ],
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _FavoriteRecipeRow extends ConsumerWidget {
  const _FavoriteRecipeRow({required this.item});

  final FavoriteRecipe item;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return InkWell(
      onTap: () => context.push('${Routes.suggestions}/dish/${item.recipeId}'),
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: Gap.md,
          vertical: Gap.sm + 2,
        ),
        child: Row(
          children: [
            RecipeImage(
              imageUrl: item.mediaUrl,
              width: 52,
              height: 52,
              iconSize: 22,
              iconColor: context.sweep.textTertiary,
              borderRadius: Radii.brMd,
            ),
            const SizedBox(width: Gap.sm + 2),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.recipeName,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: context.text.titleSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  if (item.recipeDescription.isNotEmpty) ...[
                    const SizedBox(height: 2),
                    Text(
                      item.recipeDescription,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: context.text.bodySmall?.copyWith(
                        color: context.sweep.textSecondary,
                      ),
                    ),
                  ],
                ],
              ),
            ),
            IconButton(
              icon: Icon(AppIcons.heart, size: 20, color: context.sweep.expired.fg),
              tooltip: 'Bỏ lưu',
              onPressed: () async {
                AppHaptics.selection();
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
          ],
        ),
      ),
    );
  }
}

class _FavoriteMenusTab extends ConsumerWidget {
  const _FavoriteMenusTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(favoriteMenusControllerProvider);
    final cs = context.colors;

    return RefreshIndicator(
      onRefresh: () =>
          ref.read(favoriteMenusControllerProvider.notifier).refresh(),
      child: AsyncValueWidget<List<FavoriteMenu>>(
        value: async,
        onRetry: () => ref.invalidate(favoriteMenusControllerProvider),
        data: (menus) {
          if (menus.isEmpty) {
            return ListView(
              padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xl, Gap.lg, Gap.xxl),
              children: [
                EmptyState(
                  illustrationAsset:
                      'assets/illustrations/empty_favorites.svg',
                  title: 'Chưa có thực đơn mẫu nào',
                  message:
                      'Tạo thực đơn mẫu để nhóm các món ăn yêu thích cho các dịp khác nhau.',
                  icon: AppIcons.bookOpen,
                  actionLabel: 'Tạo thực đơn mới',
                  onAction: () => _FavoritesScreenState._createMenu(context, ref),
                ),
              ],
            );
          }

          return ListView(
            padding: EdgeInsets.fromLTRB(
              Gap.lg,
              Gap.xs,
              Gap.lg,
              MediaQuery.paddingOf(context).bottom + 96,
            ),
            children: [
              Container(
                decoration: BoxDecoration(
                  color: cs.surfaceContainerLowest,
                  borderRadius: Radii.brXl,
                  border: Border.all(color: context.sweep.hairline),
                  boxShadow: Shadows.e1,
                ),
                clipBehavior: Clip.antiAlias,
                child: Column(
                  children: [
                    for (var i = 0; i < menus.length; i++) ...[
                      InkWell(
                        onTap: () =>
                            context.push('/favorites/menu/${menus[i].id}'),
                        child: Padding(
                          padding: const EdgeInsets.symmetric(
                            horizontal: Gap.md,
                            vertical: Gap.sm + 4,
                          ),
                          child: Row(
                            children: [
                              Container(
                                width: 42,
                                height: 42,
                                decoration: BoxDecoration(
                                  color: cs.primaryContainer,
                                  borderRadius: Radii.brMd,
                                ),
                                child: Icon(
                                  AppIcons.bookOpen,
                                  size: 19,
                                  color: cs.primary,
                                ),
                              ),
                              const SizedBox(width: Gap.sm + 2),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      menus[i].name,
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                      style: context.text.titleSmall?.copyWith(
                                        fontWeight: FontWeight.w700,
                                      ),
                                    ),
                                    if (menus[i].description != null &&
                                        menus[i].description!.isNotEmpty) ...[
                                      const SizedBox(height: 2),
                                      Text(
                                        menus[i].description!,
                                        maxLines: 2,
                                        overflow: TextOverflow.ellipsis,
                                        style: context.text.bodySmall?.copyWith(
                                          color: context.sweep.textSecondary,
                                        ),
                                      ),
                                    ],
                                  ],
                                ),
                              ),
                              Icon(
                                AppIcons.chevronRight,
                                size: 17,
                                color: context.sweep.textTertiary,
                              ),
                            ],
                          ),
                        ),
                      ),
                      if (i < menus.length - 1)
                        Divider(
                          height: 1,
                          indent: 68,
                          color: context.sweep.hairline,
                        ),
                    ],
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
