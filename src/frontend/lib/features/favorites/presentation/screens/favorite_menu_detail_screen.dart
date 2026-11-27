import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_dialog.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/core/widgets/recipe_image.dart';
import 'package:sweepfood/features/favorites/domain/entities/favorite_menu.dart';
import 'package:sweepfood/features/favorites/presentation/controllers/favorite_menus_controller.dart';
import 'package:sweepfood/features/favorites/presentation/widgets/create_edit_menu_dialog.dart';

/// Chi tiết thực đơn mẫu (Concept B · Format 1).
class FavoriteMenuDetailScreen extends ConsumerWidget {
  const FavoriteMenuDetailScreen({required this.menuId, super.key});

  final String menuId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(favoriteMenuDetailControllerProvider(menuId));
    final cs = context.colors;
    final sweep = context.sweep;
    final detail = async.asData?.value;

    return EmeraldSystemOverlay(
      child: Scaffold(
        backgroundColor: cs.surface,
        body: Column(
          children: [
            EmeraldSplitHeader(
              title: detail?.name ?? 'Chi tiết thực đơn',
              subtitle: detail != null
                  ? (detail.description != null && detail.description!.isNotEmpty
                        ? detail.description
                        : '${detail.items.length} món ăn trong thực đơn')
                  : null,
              trailing: PopupMenuButton<String>(
                onSelected: (action) => _handleAction(context, ref, action),
                itemBuilder: (context) => [
                  const PopupMenuItem(
                    value: 'edit',
                    child: Row(
                      children: [
                        Icon(AppIcons.edit, size: 17),
                        SizedBox(width: 10),
                        Text('Sửa thông tin'),
                      ],
                    ),
                  ),
                  PopupMenuItem(
                    value: 'delete',
                    child: Row(
                      children: [
                        Icon(AppIcons.trash, size: 17, color: cs.error),
                        const SizedBox(width: 10),
                        Text('Xóa thực đơn', style: TextStyle(color: cs.error)),
                      ],
                    ),
                  ),
                ],
                child: Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: sweep.heroSurfaceElevated,
                    borderRadius: Radii.brMd,
                    border: Border.all(
                      color: sweep.onHeroSurface.withValues(alpha: 0.16),
                    ),
                  ),
                  child: Icon(
                    AppIcons.moreVertical,
                    size: 19,
                    color: sweep.onHeroSurface,
                  ),
                ),
              ),
            ),
            Expanded(
              child: AsyncValueWidget<FavoriteMenuDetail>(
                value: async,
                onRetry: () => ref.invalidate(
                  favoriteMenuDetailControllerProvider(menuId),
                ),
                data: (d) => RefreshIndicator(
                  onRefresh: () => ref
                      .read(
                        favoriteMenuDetailControllerProvider(menuId).notifier,
                      )
                      .refresh(),
                  child: d.items.isEmpty
                      ? ListView(
                          padding: const EdgeInsets.fromLTRB(
                            Gap.lg,
                            Gap.xl,
                            Gap.lg,
                            Gap.xxl,
                          ),
                          children: [
                            EmptyState(
                              illustrationAsset:
                                  'assets/illustrations/empty_favorites.svg',
                              title: 'Thực đơn chưa có món nào',
                              message:
                                  'Vào chi tiết món ăn và bấm "Lưu vào thực đơn mẫu" để thêm món vào đây.',
                              icon: AppIcons.utensils,
                              actionLabel: 'Xem món gợi ý',
                              onAction: () => context.go(Routes.suggestions),
                            ),
                          ],
                        )
                      : ListView(
                          padding: EdgeInsets.fromLTRB(
                            Gap.lg,
                            Gap.xs,
                            Gap.lg,
                            MediaQuery.paddingOf(context).bottom + Gap.xxl,
                          ),
                          children: [
                            Padding(
                              padding: const EdgeInsets.only(
                                left: 4,
                                bottom: Gap.xs + 2,
                              ),
                              child: Text(
                                '${d.items.length} MÓN ĂN TRONG THỰC ĐƠN',
                                style: context.text.labelSmall?.copyWith(
                                  letterSpacing: 0.7,
                                  fontWeight: FontWeight.w800,
                                  color: sweep.textTertiary,
                                ),
                              ),
                            ),
                            Container(
                              decoration: BoxDecoration(
                                color: cs.surfaceContainerLowest,
                                borderRadius: Radii.brXl,
                                border: Border.all(color: sweep.hairline),
                                boxShadow: Shadows.e1,
                              ),
                              clipBehavior: Clip.antiAlias,
                              child: Column(
                                children: [
                                  for (var i = 0; i < d.items.length; i++) ...[
                                    InkWell(
                                      onTap: () => context.push(
                                        '${Routes.suggestions}/dish/${d.items[i].recipeId}',
                                      ),
                                      child: Padding(
                                        padding: const EdgeInsets.symmetric(
                                          horizontal: Gap.md,
                                          vertical: Gap.sm + 2,
                                        ),
                                        child: Row(
                                          children: [
                                            RecipeImage(
                                              imageUrl: d.items[i].mediaUrl,
                                              width: 48,
                                              height: 48,
                                              iconSize: 22,
                                              iconColor: sweep.textTertiary,
                                              borderRadius: Radii.brMd,
                                            ),
                                            const SizedBox(width: Gap.sm + 2),
                                            Expanded(
                                              child: Column(
                                                crossAxisAlignment:
                                                    CrossAxisAlignment.start,
                                                children: [
                                                  Text(
                                                    d.items[i].recipeName,
                                                    maxLines: 1,
                                                    overflow:
                                                        TextOverflow.ellipsis,
                                                    style: context
                                                        .text
                                                        .titleSmall
                                                        ?.copyWith(
                                                          fontWeight:
                                                              FontWeight.w700,
                                                        ),
                                                  ),
                                                  if (d
                                                      .items[i]
                                                      .recipeDescription
                                                      .isNotEmpty) ...[
                                                    const SizedBox(height: 2),
                                                    Text(
                                                      d
                                                          .items[i]
                                                          .recipeDescription,
                                                      maxLines: 1,
                                                      overflow:
                                                          TextOverflow.ellipsis,
                                                      style: context
                                                          .text
                                                          .bodySmall
                                                          ?.copyWith(
                                                            color: sweep
                                                                .textSecondary,
                                                          ),
                                                    ),
                                                  ],
                                                ],
                                              ),
                                            ),
                                            IconButton(
                                              icon: Icon(
                                                AppIcons.close,
                                                size: 18,
                                                color: sweep.textTertiary,
                                              ),
                                              tooltip: 'Gỡ khỏi thực đơn',
                                              onPressed: () async {
                                                AppHaptics.selection();
                                                await ref
                                                    .read(
                                                      favoriteMenuDetailControllerProvider(
                                                        menuId,
                                                      ).notifier,
                                                    )
                                                    .removeRecipe(d.items[i].id);
                                                if (context.mounted) {
                                                  AppSnack.show(
                                                    context,
                                                    'Đã gỡ "${d.items[i].recipeName}" khỏi thực đơn',
                                                  );
                                                }
                                              },
                                            ),
                                          ],
                                        ),
                                      ),
                                    ),
                                    if (i < d.items.length - 1)
                                      Divider(
                                        height: 1,
                                        indent: 74,
                                        color: sweep.hairline,
                                      ),
                                  ],
                                ],
                              ),
                            ),
                          ],
                        ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _handleAction(
    BuildContext context,
    WidgetRef ref,
    String action,
  ) async {
    final detail = ref
        .read(favoriteMenuDetailControllerProvider(menuId))
        .asData
        ?.value;
    if (detail == null) return;
    if (action == 'edit') {
      final res = await CreateEditMenuDialog.show(
        context,
        title: 'Sửa thực đơn',
        actionLabel: 'Lưu',
        initialName: detail.name,
        initialDescription: detail.description,
      );
      if (res != null) {
        await ref
            .read(favoriteMenusControllerProvider.notifier)
            .updateMenu(
              menuId,
              name: res.name,
              description: res.description,
            );
      }
    } else if (action == 'delete') {
      final confirm = await showAppConfirmDialog(
        context,
        title: 'Xóa thực đơn?',
        message: 'Bạn có chắc muốn xóa thực đơn "${detail.name}"?',
        cancelLabel: 'Hủy',
        confirmLabel: 'Xóa',
        destructive: true,
      );
      if (confirm == true && context.mounted) {
        await ref
            .read(favoriteMenusControllerProvider.notifier)
            .deleteMenu(menuId);
        if (context.mounted) {
          Navigator.of(context).pop();
          AppSnack.show(context, 'Đã xóa thực đơn');
        }
      }
    }
  }
}
