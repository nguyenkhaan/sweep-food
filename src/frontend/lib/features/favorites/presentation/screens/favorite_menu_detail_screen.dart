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
import 'package:sweepfood/features/favorites/presentation/controllers/favorite_menus_controller.dart';
import 'package:sweepfood/features/favorites/presentation/widgets/create_edit_menu_dialog.dart';

class FavoriteMenuDetailScreen extends ConsumerWidget {
  const FavoriteMenuDetailScreen({required this.menuId, super.key});

  final String menuId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(favoriteMenuDetailControllerProvider(menuId));

    return Scaffold(
      appBar: AppBar(
        title: async.maybeWhen(
          data: (detail) => Text(detail.name),
          orElse: () => const Text('Chi tiết thực đơn'),
        ),
        actions: [
          PopupMenuButton<String>(
            icon: const Icon(Icons.more_vert_rounded),
            onSelected: (action) async {
              final detail = async.asData?.value;
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
                      .updateMenu(menuId, name: res.name, description: res.description);
                }
              } else if (action == 'delete') {
                final confirm = await showDialog<bool>(
                  context: context,
                  builder: (ctx) => AlertDialog(
                    title: const Text('Xóa thực đơn?'),
                    content: Text('Bạn có chắc muốn xóa thực đơn "${detail.name}"?'),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.of(ctx).pop(false),
                        child: const Text('Hủy'),
                      ),
                      FilledButton(
                        style: FilledButton.styleFrom(backgroundColor: Colors.red),
                        onPressed: () => Navigator.of(ctx).pop(true),
                        child: const Text('Xóa'),
                      ),
                    ],
                  ),
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
            },
            itemBuilder: (_) => const [
              PopupMenuItem(
                value: 'edit',
                child: Row(
                  children: [
                    Icon(Icons.edit_outlined, size: 18),
                    SizedBox(width: 8),
                    Text('Sửa thông tin'),
                  ],
                ),
              ),
              PopupMenuItem(
                value: 'delete',
                child: Row(
                  children: [
                    Icon(Icons.delete_outline_rounded, size: 18, color: Colors.red),
                    SizedBox(width: 8),
                    Text('Xóa thực đơn', style: TextStyle(color: Colors.red)),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: AsyncValueWidget<FavoriteMenuDetail>(
        value: async,
        onRetry: () => ref.invalidate(favoriteMenuDetailControllerProvider(menuId)),
        data: (detail) {
          return RefreshIndicator(
            onRefresh: () => ref
                .read(favoriteMenuDetailControllerProvider(menuId).notifier)
                .refresh(),
            child: ListView(
              padding: const EdgeInsets.all(Gap.md),
              children: [
                if (detail.description != null && detail.description!.isNotEmpty) ...[
                  Text(
                    detail.description!,
                    style: context.text.bodyMedium?.copyWith(
                      color: context.sweep.textSecondary,
                    ),
                  ),
                  Gap.gapMd,
                ],
                Row(
                  children: [
                    Text(
                      '${detail.items.length} món ăn trong thực đơn',
                      style: context.text.titleSmall?.copyWith(
                        color: context.sweep.textTertiary,
                      ),
                    ),
                  ],
                ),
                Gap.gapSm,
                if (detail.items.isEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 60),
                    child: EmptyState(
                      title: 'Thực đơn chưa có món nào',
                      message: 'Vào chi tiết món ăn và bấm "Lưu vào thực đơn mẫu" để thêm món vào đây.',
                      icon: Icons.restaurant_menu_rounded,
                      actionLabel: 'Xem món gợi ý',
                      onAction: () => context.go(Routes.suggestions),
                    ),
                  )
                else
                  for (final item in detail.items)
                    Padding(
                      padding: const EdgeInsets.only(bottom: Gap.sm),
                      child: Card(
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
                              width: 48,
                              height: 48,
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
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                  style: context.text.bodySmall?.copyWith(
                                    color: context.sweep.textSecondary,
                                  ),
                                )
                              : null,
                          trailing: IconButton(
                            icon: const Icon(Icons.close_rounded, size: 18),
                            tooltip: 'Gỡ khỏi thực đơn',
                            onPressed: () async {
                              await ref
                                  .read(
                                    favoriteMenuDetailControllerProvider(menuId).notifier,
                                  )
                                  .removeRecipe(item.id);
                              if (context.mounted) {
                                AppSnack.show(
                                  context,
                                  'Đã gỡ "${item.recipeName}" khỏi thực đơn',
                                );
                              }
                            },
                          ),
                          onTap: () => context.push(
                            '${Routes.suggestions}/dish/${item.recipeId}',
                          ),
                        ),
                      ),
                    ),
              ],
            ),
          );
        },
      ),
    );
  }
}
